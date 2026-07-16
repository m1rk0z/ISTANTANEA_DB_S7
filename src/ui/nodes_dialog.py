from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QProgressBar, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon
import time

from utils import get_local_ip_adapters, scan_subnet_port_102
from plc_comm import PLCClient
from ui.icons import get_custom_icon

# Global reference list to keep QThread instances alive in Python memory until they exit.
# This prevents std::terminate() crashes when QThread objects are garbage collected while active.
_active_threads = []

def get_mac_address(ip):
    import subprocess
    import re
    try:
        output = subprocess.check_output(f"arp -a {ip}", shell=True, timeout=1.0).decode('utf-8', errors='ignore')
        match = re.search(r"([0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2})", output)
        if match:
            return match.group(1).replace('-', ':').upper()
    except Exception:
        pass
    return "N/A"

class ScanWorker(QThread):
    # Signals to communicate with the UI
    progress_update = pyqtSignal(int, int, str)  # current, total, ip
    node_found = pyqtSignal(str, dict)           # ip, plc_info
    scan_finished = pyqtSignal(list)             # list of active (ip, info) tuples

    def __init__(self, subnet, simulate=False):
        super().__init__()
        self.subnet = subnet
        self.simulate = simulate
        self.is_cancelled = False

    def run(self):
        _active_threads.append(self)
        try:
            found_nodes = []
            
            if self.simulate:
                # Simulate a realistic scan of 254 hosts with mock PLC discovery
                mock_hosts = 254
                mock_plcs = {
                    10: {"ModuleTypeName": "CPU 315-2 PN/DP", "SerialNumber": "00:1A:2B:3C:4D:5E", "ASName": "MAIN_STATION", "ModuleName": "CPU315", "MACAddress": "00:1A:2B:3C:4D:5E"},
                    25: {"ModuleTypeName": "CPU 414-3 PN/DP", "SerialNumber": "00:1A:2B:3C:4D:5F", "ASName": "LINE_A_CONTROLLER", "ModuleName": "CPU414", "MACAddress": "00:1A:2B:3C:4D:5F"},
                    105: {"ModuleTypeName": "CPU 317-2 DP", "SerialNumber": "00:1A:2B:3C:4D:60", "ASName": "PACKAGING_PLC", "ModuleName": "CPU317", "MACAddress": "00:1A:2B:3C:4D:60"}
                }
                
                # Subnet base
                parts = self.subnet.split('.')
                base_ip = f"{parts[0]}.{parts[1]}.{parts[2]}"
                
                for i in range(1, mock_hosts + 1):
                    if self.is_cancelled:
                        break
                    ip = f"{base_ip}.{i}"
                    time.sleep(0.01)  # scan speed
                    
                    # Emit progress
                    self.progress_update.emit(i, mock_hosts, ip)
                    
                    if i in mock_plcs:
                        time.sleep(0.1) # connection latency
                        if self.is_cancelled:
                            break
                        self.node_found.emit(ip, mock_plcs[i])
                        found_nodes.append((ip, mock_plcs[i]))
                        
                if not self.is_cancelled:
                    self.scan_finished.emit(found_nodes)
                return

            # REAL SCAN: Scan TCP port 102
            try:
                # Step 1: Scan for open port 102
                def local_progress(curr, total, ip_scanned):
                    if not self.is_cancelled:
                        self.progress_update.emit(curr, total, ip_scanned)

                if self.is_cancelled:
                    return
                active_ips = scan_subnet_port_102(self.subnet, progress_callback=local_progress, is_cancelled_fn=lambda: self.is_cancelled)
                
                # Step 2: Attempt connection to fetch CPU info
                for ip in active_ips:
                    if self.is_cancelled:
                        break
                    
                    connected_slot = None
                    temp_client = PLCClient(simulate=False)
                    
                    connected_rack = 0
                    connected_slot = None
                    # Try slots sequentially across Rack 0 and Rack 1 to support H-CPUs
                    for rack in [0, 1]:
                        for slot in [2, 3, 1]:
                            try:
                                temp_client.connect(ip, rack=rack, slot=slot)
                                if temp_client.is_connected():
                                    connected_rack = rack
                                    connected_slot = slot
                                    break
                            except Exception:
                                pass
                        if connected_slot is not None:
                            break
                            
                    if connected_slot is not None:
                        try:
                            if self.is_cancelled:
                                break
                            try:
                                info = temp_client.get_cpu_info()
                            except Exception:
                                # Fallback: Guess CPU type based on connected slot
                                if connected_slot == 3:
                                    info = {"ModuleTypeName": "S7-400 CPU", "SerialNumber": "N/A", "ASName": "S7-400 Station", "ModuleName": "CPU400"}
                                elif connected_slot == 2:
                                    info = {"ModuleTypeName": "S7-300 CPU", "SerialNumber": "N/A", "ASName": "S7-300 Station", "ModuleName": "CPU300"}
                                else:
                                    info = {"ModuleTypeName": "S7-1200/1500 CPU", "SerialNumber": "N/A", "ASName": "S7-1200/1500 Station", "ModuleName": "CPU1200/1500"}
                                    
                            # Resolve MAC Address
                            info["MACAddress"] = get_mac_address(ip)
                            # Save Rack and Slot
                            info["Rack"] = connected_rack
                            info["Slot"] = connected_slot
                            
                            self.node_found.emit(ip, info)
                            found_nodes.append((ip, info))
                            temp_client.disconnect()
                        except Exception:
                            pass
                    else:
                        # Fallback if connection totally failed but port 102 was open
                        unknown_info = {
                            "ModuleTypeName": "Unknown S7 Device", 
                            "SerialNumber": "N/A", 
                            "ASName": "N/A", 
                            "ModuleName": "N/A",
                            "MACAddress": get_mac_address(ip)
                        }
                        self.node_found.emit(ip, unknown_info)
                        found_nodes.append((ip, unknown_info))
                        
                if not self.is_cancelled:
                    self.scan_finished.emit(found_nodes)
            except Exception as e:
                # Emit empty list on error
                if not self.is_cancelled:
                    self.scan_finished.emit([])
        finally:
            if self in _active_threads:
                _active_threads.remove(self)



class NodesDialog(QDialog):
    def __init__(self, parent=None, simulate=False):
        super().__init__(parent)
        self.simulate = simulate
        self.selected_ip = None
        self.selected_rack = 0
        self.selected_slot = 2
        self.discovered_nodes = {}
        
        self.setWindowTitle("Nodi Accessibili (Accessible Nodes)")
        self.setMinimumSize(600, 400)
        self.setWindowIcon(get_custom_icon("scan"))
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Subnet Selection Layout
        subnet_layout = QHBoxLayout()
        subnet_layout.addWidget(QLabel("Interfaccia di rete / Sotto-rete:"))
        
        self.adapter_combo = QComboBox()
        self.load_adapters()
        subnet_layout.addWidget(self.adapter_combo, 1)
        
        self.scan_btn = QPushButton("Scansiona")
        self.scan_btn.setIcon(get_custom_icon("scan"))
        self.scan_btn.clicked.connect(self.start_scan)
        subnet_layout.addWidget(self.scan_btn)
        
        layout.addLayout(subnet_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Nodes Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Indirizzo IP", "Modello CPU", "Indirizzo MAC", "Nome Stazione"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemDoubleClicked.connect(self.accept_selected_node)
        layout.addWidget(self.table)
        
        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        self.status_label = QLabel("Pronto per la scansione.")
        bottom_layout.addWidget(self.status_label, 1)
        
        self.ok_btn = QPushButton("Connetti a Selezionato")
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self.accept_selected_node)
        bottom_layout.addWidget(self.ok_btn)
        
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(cancel_btn)
        
        layout.addLayout(bottom_layout)
        
        # Table Selection event
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

    def load_adapters(self):
        self.adapters = get_local_ip_adapters()
        for idx, adapter in enumerate(self.adapters):
            self.adapter_combo.addItem(f"{adapter['name']} ({adapter['subnet']})", idx)

    def start_scan(self):
        idx = self.adapter_combo.currentData()
        if idx is None:
            return
            
        selected_adapter = self.adapters[idx]
        subnet_str = selected_adapter['subnet']
        
        # Set UI state
        self.scan_btn.setEnabled(False)
        self.ok_btn.setEnabled(False)
        self.table.setRowCount(0)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Scansione in corso...")
        
        # Spawn scanner thread
        self.scan_worker = ScanWorker(subnet_str, simulate=self.simulate)
        self.scan_worker.progress_update.connect(self.on_scan_progress)
        self.scan_worker.node_found.connect(self.on_node_found)
        self.scan_worker.scan_finished.connect(self.on_scan_finished)
        self.scan_worker.start()

    def on_scan_progress(self, current, total, ip):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Scansione: controllo {ip}...")

    def on_node_found(self, ip, info):
        self.discovered_nodes[ip] = info
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        ip_item = QTableWidgetItem(ip)
        ip_item.setIcon(get_custom_icon("plc"))
        
        self.table.setItem(row, 0, ip_item)
        self.table.setItem(row, 1, QTableWidgetItem(info.get("ModuleTypeName", "Unknown")))
        self.table.setItem(row, 2, QTableWidgetItem(info.get("MACAddress", "N/A")))
        self.table.setItem(row, 3, QTableWidgetItem(info.get("ASName", "N/A")))

    def on_scan_finished(self, found_nodes):
        self.scan_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        count = len(found_nodes)
        self.status_label.setText(f"Scansione completata. Trovati {count} nodi accessibili.")
        
        if count == 0:
            QMessageBox.information(self, "Scansione terminata", "Nessun PLC Siemens (porta 102) rilevato nella sotto-rete specificata.")
        else:
            self.table.selectRow(0)

    def on_selection_changed(self):
        has_selection = len(self.table.selectedItems()) > 0
        self.ok_btn.setEnabled(has_selection)

    def accept_selected_node(self):
        try:
            selected_rows = self.table.selectionModel().selectedRows()
            if not selected_rows:
                return
                
            row = selected_rows[0].row()
            
            ip_item = self.table.item(row, 0)
            if not ip_item:
                return
            ip = ip_item.text()
            self.selected_ip = ip
            
            # Load exact Rack and Slot detected during scanning
            info = self.discovered_nodes.get(ip, {})
            self.selected_rack = info.get("Rack", 0)
            self.selected_slot = info.get("Slot", 3 if "400" in info.get("ModuleTypeName", "") else (2 if "300" in info.get("ModuleTypeName", "") else 1))
            
            self.accept()
        except Exception as e:
            # Prevent crashes if table has invalid items
            pass

    def done(self, r):
        # Safe cleanup: disconnect signals and force terminate thread if still running
        if hasattr(self, 'scan_worker') and self.scan_worker is not None and self.scan_worker.isRunning():
            self.scan_worker.is_cancelled = True
            try:
                self.scan_worker.progress_update.disconnect()
            except Exception: pass
            try:
                self.scan_worker.node_found.disconnect()
            except Exception: pass
            try:
                self.scan_worker.scan_finished.disconnect()
            except Exception: pass
            
            # Let the thread exit in background, waiting only up to 50ms to keep GUI responsive without PyQt C++ crashes
            self.scan_worker.wait(50)
        super().done(r)
