from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QLineEdit, QFileDialog, QMessageBox, 
                             QHeaderView, QCheckBox)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon
import json

from utils import parse_s7_data, pack_s7_data
from ui.icons import get_custom_icon

class DBViewer(QWidget):
    def __init__(self, parent=None, plc_client=None, on_structures_changed=None):
        super().__init__(parent)
        self.plc_client = plc_client
        self.db_number = None
        self.db_size = 0
        self.raw_data = bytearray()
        
        # Callback for when DB structures are updated (so CompareWindow can inherit them)
        self.on_structures_changed = on_structures_changed
        
        # List of dicts representing variables in current DB
        # [{"name": "VarName", "offset": 0.0, "type": "REAL"}]
        self.variables = []
        
        # Monitor timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_plc)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header Controls
        header_layout = QHBoxLayout()
        self.db_label = QLabel("<b>Seleziona un Data Block dall'albero a sinistra</b>")
        header_layout.addWidget(self.db_label, 1)
        
        # Monitoring Control
        self.monitor_checkbox = QCheckBox("Monitor Live (Attivo)")
        self.monitor_checkbox.stateChanged.connect(self.toggle_monitoring)
        self.monitor_checkbox.setEnabled(False)
        header_layout.addWidget(self.monitor_checkbox)
        
        # Refresh Rate
        header_layout.addWidget(QLabel("Intervallo (ms):"))
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["200", "500", "1000", "2000"])
        self.interval_combo.setCurrentIndex(1) # Default 500ms
        self.interval_combo.currentIndexChanged.connect(self.update_monitor_interval)
        header_layout.addWidget(self.interval_combo)
        
        layout.addLayout(header_layout)
        
        # Structure Import/Export Actions
        struct_layout = QHBoxLayout()
        self.import_btn = QPushButton("Importa Struttura (Mappa)...")
        self.import_btn.clicked.connect(self.import_structure)
        self.import_btn.setEnabled(False)
        struct_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("Esporta Struttura (Mappa)...")
        self.export_btn.clicked.connect(self.export_structure)
        self.export_btn.setEnabled(False)
        struct_layout.addWidget(self.export_btn)
        
        struct_layout.addStretch()
        
        self.add_row_btn = QPushButton("Aggiungi Variabile")
        self.add_row_btn.clicked.connect(self.add_variable_row)
        self.add_row_btn.setEnabled(False)
        struct_layout.addWidget(self.add_row_btn)
        
        layout.addLayout(struct_layout)
        
        # Variables Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Nome Variabile", "Tipo Dato", "Offset (Byte.Bit)", "Valore Live", "Nuovo Valore", "Azione"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Table change listener for local edits
        self.table.itemChanged.connect(self.on_table_item_changed)
        
        # Read-Write buttons layout for whole DB
        db_actions_layout = QHBoxLayout()
        self.read_db_btn = QPushButton("Leggi DB Intero")
        self.read_db_btn.clicked.connect(self.read_full_db)
        self.read_db_btn.setEnabled(False)
        db_actions_layout.addWidget(self.read_db_btn)
        
        self.write_db_btn = QPushButton("Scrivi DB Intero (Modificato)")
        self.write_db_btn.clicked.connect(self.write_full_db)
        self.write_db_btn.setEnabled(False)
        db_actions_layout.addWidget(self.write_db_btn)
        
        layout.addLayout(db_actions_layout)

    def set_active_db(self, db_num, size):
        self.db_number = db_num
        self.db_size = size
        self.raw_data = bytearray(size)
        
        self.db_label.setText(f"<b>Visualizzazione DB {db_num}</b> (Dimensione: {size} byte)")
        
        # Enable actions
        self.import_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.add_row_btn.setEnabled(True)
        self.read_db_btn.setEnabled(True)
        self.write_db_btn.setEnabled(True)
        
        # Auto stop monitoring
        self.monitor_checkbox.setChecked(False)
        self.monitor_checkbox.setEnabled(self.plc_client is not None and self.plc_client.is_connected())
        
        # Reload or clear variables
        self.variables = []
        self.table.setRowCount(0)
        
        # Walk up parent chain to resolve MainWindow configuration
        parent_window = self.parent()
        while parent_window and not hasattr(parent_window, 'dbs_structures'):
            parent_window = parent_window.parent()
            
        loaded_vars = []
        if parent_window and hasattr(parent_window, 'dbs_structures') and db_num in parent_window.dbs_structures:
            loaded_vars = list(parent_window.dbs_structures[db_num])
            
        if not loaded_vars:
            # Generate default BYTE rows to show live values directly
            for offset in range(size):
                loaded_vars.append({
                    "name": f"DB{db_num}.DBB{offset}",
                    "type": "BYTE",
                    "offset": float(offset)
                })
                
        # Populate QTableWidget rows
        for var in loaded_vars:
            self.add_variable_row(var["name"], var["type"], var["offset"])
            
        # Read initial values
        self.read_full_db()

    def add_variable_row(self, name="Nuova_Var", dtype="INT", offset=0.0):
        # Prevent item change signals during addition
        self.table.blockSignals(True)
        
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Variable Object
        var = {"name": name, "type": dtype, "offset": offset}
        self.variables.append(var)
        
        # Name item
        name_item = QTableWidgetItem(name)
        self.table.setItem(row, 0, name_item)
        
        # Type ComboBox
        type_combo = QComboBox()
        type_combo.addItems(["BOOL", "BYTE", "CHAR", "INT", "WORD", "DINT", "DWORD", "REAL", "STRING"])
        type_combo.setCurrentText(dtype)
        # Store row inside combobox for indexing
        type_combo.setProperty("row", row)
        type_combo.currentIndexChanged.connect(self.on_type_changed)
        self.table.setCellWidget(row, 1, type_combo)
        
        # Offset item
        offset_item = QTableWidgetItem(str(offset))
        self.table.setItem(row, 2, offset_item)
        
        # Live value item (Read Only)
        live_item = QTableWidgetItem("---")
        live_item.setFlags(live_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 3, live_item)
        
        # Input for writing new value
        write_input = QLineEdit()
        write_input.setProperty("row", row)
        self.table.setCellWidget(row, 4, write_input)
        
        # Action Layout with individual Write and Delete
        action_widget = QWidget()
        act_layout = QHBoxLayout(action_widget)
        act_layout.setContentsMargins(2, 2, 2, 2)
        act_layout.setSpacing(2)
        
        write_btn = QPushButton("Scrivi")
        write_btn.clicked.connect(lambda: self.write_single_variable(row))
        act_layout.addWidget(write_btn)
        
        delete_btn = QPushButton("X")
        delete_btn.setStyleSheet("color: red; font-weight: bold; max-width: 25px;")
        delete_btn.clicked.connect(lambda: self.delete_variable(row))
        act_layout.addWidget(delete_btn)
        
        self.table.setCellWidget(row, 5, action_widget)
        
        self.table.blockSignals(False)
        self.update_live_values()
        
        # Notify main window
        if self.on_structures_changed and self.db_number:
            self.on_structures_changed(self.db_number, self.variables)

    def delete_variable(self, row):
        if row < 0 or row >= len(self.variables):
            return
        
        self.table.blockSignals(True)
        self.table.removeRow(row)
        self.variables.pop(row)
        
        # Re-index remaining widgets properties
        for r in range(self.table.rowCount()):
            combo = self.table.cellWidget(r, 1)
            if combo:
                combo.setProperty("row", r)
            line_edit = self.table.cellWidget(r, 4)
            if line_edit:
                line_edit.setProperty("row", r)
                
        self.table.blockSignals(False)
        
        # Notify main window
        if self.on_structures_changed and self.db_number:
            self.on_structures_changed(self.db_number, self.variables)

    def on_table_item_changed(self, item):
        row = item.row()
        col = item.column()
        
        if row < 0 or row >= len(self.variables):
            return
            
        val = item.text()
        
        if col == 0:  # Name
            self.variables[row]["name"] = val
        elif col == 2:  # Offset
            try:
                self.variables[row]["offset"] = float(val) if "." in val else int(val)
            except ValueError:
                pass
                
        # Parse live values since offset or type might have changed
        self.update_live_values()
        
        # Notify main window
        if self.on_structures_changed and self.db_number:
            self.on_structures_changed(self.db_number, self.variables)

    def on_type_changed(self, idx):
        sender = self.sender()
        if not sender:
            return
        row = sender.property("row")
        if row is not None and 0 <= row < len(self.variables):
            self.variables[row]["type"] = sender.currentText()
            self.update_live_values()
            
            # Notify main window
            if self.on_structures_changed and self.db_number:
                self.on_structures_changed(self.db_number, self.variables)

    def read_full_db(self):
        if not self.db_number:
            return
            
        if not self.plc_client or not self.plc_client.is_connected():
            return
            
        try:
            self.raw_data = self.plc_client.read_db_bytes(self.db_number, self.db_size)
            self.update_live_values()
        except Exception as e:
            QMessageBox.critical(self, "Errore di Lettura", f"Impossibile leggere il DB {self.db_number} dal PLC:\n{str(e)}")

    def write_full_db(self):
        if not self.db_number or not self.raw_data:
            return
            
        if not self.plc_client or not self.plc_client.is_connected():
            QMessageBox.warning(self, "Non Connesso", "Impossibile scrivere. PLC non connesso.")
            return
            
        reply = QMessageBox.question(
            self, "Conferma Scrittura",
            f"Sei sicuro di voler scrivere tutti i valori caricati sul DB {self.db_number} del PLC?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            return
            
        try:
            self.plc_client.write_db_bytes(self.db_number, self.raw_data)
            QMessageBox.information(self, "Scrittura Completata", f"Tutto il DB {self.db_number} è stato scritto nel PLC.")
        except Exception as e:
            QMessageBox.critical(self, "Errore di Scrittura", f"Impossibile scrivere il DB {self.db_number} nel PLC:\n{str(e)}")

    def update_live_values(self):
        if not self.raw_data:
            return
            
        for row, var in enumerate(self.variables):
            offset = var["offset"]
            dtype = var["type"]
            
            offset_str = str(offset)
            if "." in offset_str:
                parts = offset_str.split('.')
                byte_off = int(parts[0])
                bit_off = int(parts[1])
            else:
                byte_off = int(offset)
                bit_off = 0
                
            val = parse_s7_data(dtype, self.raw_data, byte_off, bit_off)
            
            # Put in table
            item = self.table.item(row, 3)
            if item:
                if val is not None:
                    item.setText(str(val))
                    item.setForeground(Qt.GlobalColor.black)
                else:
                    item.setText("Out of Bounds")
                    item.setForeground(Qt.GlobalColor.red)

    def write_single_variable(self, row):
        if not self.db_number:
            return
            
        if not self.plc_client or not self.plc_client.is_connected():
            QMessageBox.warning(self, "Non Connesso", "PLC non connesso.")
            return
            
        var = self.variables[row]
        line_edit = self.table.cellWidget(row, 4)
        if not line_edit:
            return
            
        new_val_str = line_edit.text().strip()
        if not new_val_str:
            QMessageBox.warning(self, "Valore Vuoto", "Specifica un valore da scrivere.")
            return
            
        offset = var["offset"]
        dtype = var["type"]
        
        offset_str = str(offset)
        if "." in offset_str:
            parts = offset_str.split('.')
            byte_off = int(parts[0])
            bit_off = int(parts[1])
        else:
            byte_off = int(offset)
            bit_off = 0
            
        # Parse inputs correctly
        try:
            if dtype == "BOOL":
                if new_val_str.lower() in ["true", "1", "on", "yes"]:
                    new_val = True
                else:
                    new_val = False
            elif dtype in ["BYTE", "INT", "WORD", "DINT", "DWORD"]:
                new_val = int(new_val_str)
            elif dtype == "REAL":
                new_val = float(new_val_str)
            else: # CHAR / STRING
                new_val = new_val_str
        except ValueError:
            QMessageBox.critical(self, "Tipo Errato", f"Il valore inserito '{new_val_str}' non è compatibile con il tipo {dtype}.")
            return
            
        try:
            # We first need to read the existing bytes to preserve bitwise settings (for bools) or other fields
            self.raw_data = self.plc_client.read_db_bytes(self.db_number, self.db_size)
            
            # Pack new data into raw buffer
            pack_bytes = pack_s7_data(dtype, new_val, byte_off, bit_off, self.raw_data)
            
            if pack_bytes is None:
                raise ValueError("Errore durante il packaging dei dati.")
                
            # Write only the modified portion to PLC
            # For BOOL / BYTE / CHAR it is 1 byte, for INT/WORD it's 2, DINT/REAL is 4, STRING is variable
            write_size = len(pack_bytes)
            self.plc_client.write_db_bytes(self.db_number, self.raw_data[byte_off:byte_off+write_size], byte_off)
            
            # Clear input
            line_edit.clear()
            
            # Update local display
            self.update_live_values()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore Scrittura", f"Scrittura della variabile fallita:\n{str(e)}")

    def toggle_monitoring(self, state):
        if state == 2:  # Checked
            interval = int(self.interval_combo.currentText())
            self.timer.start(interval)
            self.read_db_btn.setEnabled(False)
            self.write_db_btn.setEnabled(False)
        else:
            self.timer.stop()
            self.read_db_btn.setEnabled(True)
            self.write_db_btn.setEnabled(True)

    def update_monitor_interval(self, idx):
        if self.timer.isActive():
            interval = int(self.interval_combo.currentText())
            self.timer.start(interval)

    def poll_plc(self):
        if not self.plc_client or not self.plc_client.is_connected():
            self.monitor_checkbox.setChecked(False)
            return
            
        try:
            self.raw_data = self.plc_client.read_db_bytes(self.db_number, self.db_size)
            self.update_live_values()
        except Exception:
            # Silence and stop on connection drop
            self.monitor_checkbox.setChecked(False)

    def export_structure(self):
        if not self.variables:
            QMessageBox.warning(self, "Struttura Vuota", "Non ci sono variabili da esportare.")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Esporta Mappa Struttura", f"Mappa_DB_{self.db_number}.json", "JSON Mappings (*.json)"
        )
        if not filepath:
            return
            
        try:
            with open(filepath, 'w') as f:
                json.dump(self.variables, f, indent=4)
            QMessageBox.information(self, "Mappa Esportata", "La struttura del DB è stata esportata con successo.")
        except Exception as e:
            QMessageBox.critical(self, "Errore Scrittura", f"Impossibile esportare la mappa:\n{str(e)}")

    def import_structure(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Importa Mappa Struttura", "", "JSON Mappings (*.json)"
        )
        if not filepath:
            return
            
        try:
            with open(filepath, 'r') as f:
                imported_vars = json.load(f)
                
            if not isinstance(imported_vars, list):
                raise ValueError("Il file deve contenere una lista JSON di variabili.")
                
            self.table.setRowCount(0)
            self.variables = []
            
            for item in imported_vars:
                name = item.get("name", "Var")
                dtype = item.get("type", "INT")
                offset = item.get("offset", 0.0)
                self.add_variable_row(name, dtype, offset)
                
            QMessageBox.information(self, "Mappa Importata", f"Importate {len(imported_vars)} variabili con successo.")
        except Exception as e:
            QMessageBox.critical(self, "Errore Caricamento", f"Impossibile importare la mappa:\n{str(e)}")
