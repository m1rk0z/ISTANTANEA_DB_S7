import snap7
import logging
import struct
import time

logger = logging.getLogger("IstanteS7.PLCComm")

class PLCCommError(Exception):
    """Custom exception for PLC communication errors."""
    pass

class PLCClient:
    def __init__(self, simulate=False):
        self.simulate = simulate
        self.client = None if simulate else snap7.client.Client()
        self.ip = ""
        self.rack = 0
        self.slot = 2
        self.connected = False
        
        # Simulation Memory
        self.sim_dbs = {
            1: bytearray([i % 256 for i in range(120)]),   # DB1: 120 bytes
            2: bytearray([(i * 3) % 256 for i in range(256)]), # DB2: 256 bytes
            10: bytearray(50),                             # DB10: 50 bytes (all zeros)
            100: bytearray([0x41, 0x42, 0x00, 0x01, 0x00, 0x0A, 0x40, 0x49, 0x0F, 0xDB] + [0]*30) # DB100: 40 bytes with some numbers
        }
        self.sim_inputs = bytearray([0x05, 0x00, 0x12, 0x34] + [0] * 1020)
        self.sim_outputs = bytearray([0x01, 0x00, 0x56, 0x78] + [0] * 1020)
        self.sim_merkers = bytearray([0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0xD2] + [0] * 1012) # MW10=1234 (0x04D2)
        self.sim_cpu_info = {
            "ModuleTypeName": "CPU 315-2 PN/DP (SIM)",
            "SerialNumber": "S7-SIM-12345678",
            "ASName": "SIMATIC-S7-300-STATION",
            "ModuleName": "CPU 315"
        }

    def connect(self, ip, rack=0, slot=2):
        self.ip = ip
        self.rack = rack
        self.slot = slot
        
        if self.simulate:
            logger.info(f"Simulating connection to S7 PLC at {ip} (Rack={rack}, Slot={slot})...")
            time.sleep(0.3)  # Simulate network latency
            self.connected = True
            return True
            
        try:
            logger.info(f"Connecting to S7 PLC at {ip} (Rack={rack}, Slot={slot})...")
            self.client.connect(ip, rack, slot)
            self.connected = self.client.get_connected()
            if not self.connected:
                raise PLCCommError("Failed to establish connection to the PLC.")
            logger.info("Connected successfully.")
            return True
        except Exception as e:
            self.connected = False
            logger.error(f"Connection error: {e}")
            raise PLCCommError(f"Connection failed: {str(e)}")

    def disconnect(self):
        self.connected = False
        if self.simulate:
            logger.info("Simulated disconnection.")
            return
            
        try:
            if self.client and self.client.get_connected():
                self.client.disconnect()
            logger.info("Disconnected successfully.")
        except Exception as e:
            logger.warning(f"Error while disconnecting: {e}")

    def is_connected(self):
        if self.simulate:
            return self.connected
        try:
            return self.client and self.client.get_connected()
        except Exception:
            return False

    def get_cpu_info(self):
        if not self.is_connected():
            raise PLCCommError("Not connected to PLC.")
            
        if self.simulate:
            return self.sim_cpu_info
            
        try:
            info = self.client.get_cpu_info()
            return {
                "ModuleTypeName": info.ModuleTypeName.decode('utf-8', errors='ignore').strip() if isinstance(info.ModuleTypeName, bytes) else str(info.ModuleTypeName),
                "SerialNumber": info.SerialNumber.decode('utf-8', errors='ignore').strip() if isinstance(info.SerialNumber, bytes) else str(info.SerialNumber),
                "ASName": info.ASName.decode('utf-8', errors='ignore').strip() if isinstance(info.ASName, bytes) else str(info.ASName),
                "ModuleName": info.ModuleName.decode('utf-8', errors='ignore').strip() if isinstance(info.ModuleName, bytes) else str(info.ModuleName)
            }
        except Exception as e:
            logger.error(f"Failed to read CPU info: {e}")
            raise PLCCommError(f"Failed to read CPU info: {str(e)}")

    def list_dbs(self, start=1, end=500):
        if not self.is_connected():
            raise PLCCommError("Not connected to PLC.")
            
        if self.simulate:
            time.sleep(0.1)
            return sorted(list(self.sim_dbs.keys()))
            
        # Determine the BlockType code (0x41 for DB)
        block_type = 0x41
        if hasattr(snap7, 'Block') and hasattr(snap7.Block, 'DB'):
            block_type = snap7.Block.DB

        # Method 1: Try official list_blocks_of_type
        try:
            try:
                res = self.client.list_blocks_of_type(block_type)
            except TypeError:
                res = self.client.list_blocks_of_type(block_type, 8192)
            
            if res is not None:
                if hasattr(res, '__iter__'):
                    return sorted(list(res))
                return [res]
        except Exception as e:
            logger.warning(f"list_blocks_of_type failed: {e}. Trying secondary string-based listing...")
            try:
                try:
                    res = self.client.list_blocks_of_type('DB')
                except TypeError:
                    res = self.client.list_blocks_of_type('DB', 8192)
                if res is not None:
                    if hasattr(res, '__iter__'):
                        return sorted(list(res))
                    return [res]
            except Exception as ex:
                logger.warning(f"Secondary block listing also failed: {ex}. Returning empty list for background scanning.")
                return []

    def probe_db_size(self, db_number):
        """
        Fallback method: Probes the DB size by doing a binary search using db_read.
        This is necessary for S7-1200/1500 or security-restricted PLCs where get_block_info fails.
        """
        if not self.is_connected():
            raise PLCCommError("Not connected to PLC.")
            
        logger.info(f"Probing DB {db_number} size using binary search...")
        low = 1
        high = 65535
        detected_size = 0
        
        # Test if DB exists at all by reading 1 byte
        try:
            self.client.db_read(db_number, 0, 1)
        except Exception:
            return 0
            
        while low <= high:
            mid = (low + high) // 2
            try:
                self.client.db_read(db_number, 0, mid)
                detected_size = mid
                low = mid + 1  # Try a larger size
            except Exception:
                high = mid - 1  # Try a smaller size
                
        logger.info(f"Probed DB {db_number} size: {detected_size} bytes")
        return detected_size

    def get_db_size(self, db_number):
        if not self.is_connected():
            raise PLCCommError("Not connected to PLC.")
            
        if self.simulate:
            if db_number in self.sim_dbs:
                return len(self.sim_dbs[db_number])
            return 0
            
        block_type = 0x41
        if hasattr(snap7, 'Block') and hasattr(snap7.Block, 'DB'):
            block_type = snap7.Block.DB

        try:
            info = self.client.get_block_info(block_type, db_number)
            if hasattr(info, 'mc7_size'):
                return info.mc7_size
            elif hasattr(info, 'size'):
                return info.size
            elif hasattr(info, 'load_size'):
                return info.load_size
            else:
                raise PLCCommError("Could not retrieve block size from metadata.")
        except Exception as e:
            logger.info(f"get_block_info failed for DB {db_number}: {e}. Falling back to binary search probe...")
            try:
                probed_size = self.probe_db_size(db_number)
                if probed_size > 0:
                    return probed_size
            except Exception as ex:
                logger.error(f"Failed to probe DB {db_number} size: {ex}")
                
            logger.error(f"Failed to get DB {db_number} size: {e}")
            raise PLCCommError(f"Failed to get DB {db_number} size: {str(e)}")

    def read_db_bytes(self, db_number, size=None):
        if not self.is_connected():
            raise PLCCommError("Not connected to PLC.")
            
        if self.simulate:
            time.sleep(0.05)  # Simulate PLC reading delay
            if db_number not in self.sim_dbs:
                raise PLCCommError(f"Simulated DB {db_number} does not exist.")
            
            # If monitoring, let's fluctuate some values in simulated memory to make it look alive!
            db_data = self.sim_dbs[db_number]
            # DB1 live values fluctuation
            if db_number == 1 and len(db_data) >= 10:
                # Increment an integer counter at offset 0
                val = struct.unpack(">h", db_data[0:2])[0]
                val = (val + 1) % 32767
                db_data[0:2] = struct.pack(">h", val)
                
                # Fluctuate float value at offset 6
                fval = struct.unpack(">f", db_data[6:10])[0]
                # If nan or inf, reset
                if fval < -1000 or fval > 1000 or str(fval) == 'nan':
                    fval = 10.0
                fval += 0.1
                db_data[6:10] = struct.pack(">f", fval)
                
                # Toggle bit at offset 4.0
                db_data[4] ^= 0x01
                
            if size is None:
                return bytearray(db_data)
            return bytearray(db_data[:size])
            
        try:
            if size is None:
                size = self.get_db_size(db_number)
            
            # Perform S7 DB read
            data = self.client.db_read(db_number, 0, size)
            return bytearray(data)
        except Exception as e:
            logger.error(f"Failed to read DB {db_number}: {e}")
            raise PLCCommError(f"Failed to read DB {db_number}: {str(e)}")

    def write_db_bytes(self, db_number, data, start_offset=0):
        if not self.is_connected():
            raise PLCCommError("Not connected to PLC.")
            
        if self.simulate:
            time.sleep(0.08)  # Simulate PLC writing delay
            if db_number not in self.sim_dbs:
                # If creating in simulated environment
                self.sim_dbs[db_number] = bytearray(start_offset + len(data))
            
            # Update simulated memory
            current_len = len(self.sim_dbs[db_number])
            needed_len = start_offset + len(data)
            if needed_len > current_len:
                self.sim_dbs[db_number].extend(bytearray(needed_len - current_len))
                
            self.sim_dbs[db_number][start_offset:needed_len] = data
            logger.info(f"Simulated write of {len(data)} bytes to DB {db_number} at offset {start_offset}")
            return
            
        try:
            # Perform S7 DB write
            self.client.db_write(db_number, start_offset, data)
            logger.info(f"Wrote {len(data)} bytes to DB {db_number} starting at offset {start_offset}")
        except Exception as e:
            logger.error(f"Failed to write DB {db_number}: {e}")
            raise PLCCommError(f"Failed to write DB {db_number}: {str(e)}")

    def read_area_bytes(self, area_code, db_number=0, start_offset=0, size=1):
        """
        Reads bytes from a specific S7 memory area:
        area_code: 0x81 (PE/Inputs), 0x82 (PA/Outputs), 0x83 (MK/Merkers), 0x84 (DB)
        """
        if not self.is_connected():
            raise PLCCommError("Not connected to PLC.")
            
        if self.simulate:
            time.sleep(0.01)
            if area_code == 0x84: # DB
                if db_number not in self.sim_dbs:
                    self.sim_dbs[db_number] = bytearray(max(256, start_offset + size))
                buf = self.sim_dbs[db_number]
            elif area_code == 0x81: # PE (Inputs)
                buf = self.sim_inputs
            elif area_code == 0x82: # PA (Outputs)
                buf = self.sim_outputs
            elif area_code == 0x83: # MK (Merkers)
                buf = self.sim_merkers
            else:
                buf = bytearray(start_offset + size)

            if len(buf) < start_offset + size:
                buf.extend(bytearray(start_offset + size - len(buf)))
                
            return bytearray(buf[start_offset:start_offset + size])

        try:
            data = self.client.read_area(area_code, db_number, start_offset, size)
            return bytearray(data)
        except Exception as e:
            logger.error(f"Failed to read area {hex(area_code)} DB {db_number} offset {start_offset}: {e}")
            raise PLCCommError(f"Read error: {str(e)}")

    def write_area_bytes(self, area_code, db_number=0, start_offset=0, data=b''):
        """
        Writes bytes to a specific S7 memory area.
        """
        if not self.is_connected():
            raise PLCCommError("Not connected to PLC.")
            
        if self.simulate:
            time.sleep(0.02)
            if area_code == 0x84: # DB
                if db_number not in self.sim_dbs:
                    self.sim_dbs[db_number] = bytearray(start_offset + len(data))
                buf = self.sim_dbs[db_number]
            elif area_code == 0x81: # PE (Inputs)
                buf = self.sim_inputs
            elif area_code == 0x82: # PA (Outputs)
                buf = self.sim_outputs
            elif area_code == 0x83: # MK (Merkers)
                buf = self.sim_merkers
            else:
                return

            needed = start_offset + len(data)
            if len(buf) < needed:
                buf.extend(bytearray(needed - len(buf)))
            buf[start_offset:needed] = data
            logger.info(f"Simulated write of {len(data)} bytes to area {hex(area_code)} DB {db_number} offset {start_offset}")
            return

        try:
            self.client.write_area(area_code, db_number, start_offset, data)
            logger.info(f"Wrote {len(data)} bytes to area {hex(area_code)} DB {db_number} offset {start_offset}")
        except Exception as e:
            logger.error(f"Failed to write area {hex(area_code)} DB {db_number} offset {start_offset}: {e}")
            raise PLCCommError(f"Write error: {str(e)}")

