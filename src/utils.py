import socket
import struct
import concurrent.futures
import ipaddress
import logging
import re

logger = logging.getLogger("IstanteS7.Utils")

def get_local_ip_adapters():
    """
    Retrieves all active local network adapters and their IPv4 addresses.
    Returns a list of dicts: [{'name': 'Adapter Name', 'ip': '192.168.1.10', 'subnet': '192.168.1.0/24'}]
    """
    import subprocess
    adapters = []
    
    # Run ipconfig to fetch active interfaces and subnets
    try:
        res = subprocess.run(["ipconfig"], capture_output=True, text=True, errors='ignore')
        lines = res.stdout.split('\n')
        
        current_adapter = None
        current_ip = None
        current_mask = None
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            # Adapter title lines on Windows typically don't have leading spaces and end with a colon
            if not line.startswith(" ") and not line.startswith("\t") and line_str.endswith(":"):
                # Save previous adapter if complete
                if current_adapter and current_ip and current_mask:
                    try:
                        net = ipaddress.IPv4Network(f"{current_ip}/{current_mask}", strict=False)
                        adapters.append({
                            "name": current_adapter,
                            "ip": current_ip,
                            "subnet": str(net)
                        })
                    except Exception:
                        pass
                
                current_adapter = line_str[:-1]
                current_ip = None
                current_mask = None
                
            elif "IPv4 Address" in line_str or "Indirizzo IPv4" in line_str:
                parts = line_str.split(":")
                if len(parts) >= 2:
                    current_ip = parts[1].strip().replace("(Preferred)", "").replace("(Preferito)", "")
            elif "Subnet Mask" in line_str or "Maschera di sottorete" in line_str or "Subnet mask" in line_str:
                parts = line_str.split(":")
                if len(parts) >= 2:
                    current_mask = parts[1].strip()
                    
        # Save last adapter
        if current_adapter and current_ip and current_mask:
            try:
                net = ipaddress.IPv4Network(f"{current_ip}/{current_mask}", strict=False)
                adapters.append({
                    "name": current_adapter,
                    "ip": current_ip,
                    "subnet": str(net)
                })
            except Exception:
                pass
                
    except Exception as e:
        logger.warning(f"Error querying ipconfig adapters: {e}")
        
    # Fallback to hostname-based socket lookup if ipconfig yields nothing
    if not adapters:
        try:
            hostname = socket.gethostname()
            ips = socket.gethostbyname_ex(hostname)[2]
            for ip in ips:
                if ip.startswith("127."):
                    continue
                try:
                    net = ipaddress.IPv4Network(f"{ip}/255.255.255.0", strict=False)
                    adapters.append({
                        "name": f"Local Interface ({ip})",
                        "ip": ip,
                        "subnet": str(net)
                    })
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Fallback socket lookup failed: {e}")
            
    # Add localhost Loopback adapter
    adapters.append({
        "name": "Loopback (Localhost)",
        "ip": "127.0.0.1",
        "subnet": "127.0.0.0/24"
    })
    
    return adapters

def check_ip_port_102(ip, timeout=0.2):
    """
    Checks if TCP port 102 (RFC1006 / S7 ISO-on-TCP) is open at target IP.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, 102))
            return result == 0
    except Exception:
        return False

def scan_subnet_port_102(subnet_str, max_workers=50, timeout=0.2, progress_callback=None, is_cancelled_fn=None):
    """
    Scans all IP addresses in the given subnet for port 102.
    progress_callback receives (current_step, total_steps, current_ip)
    is_cancelled_fn is an optional callback returning True if scan should abort.
    """
    try:
        network = ipaddress.IPv4Network(subnet_str, strict=False)
        hosts = list(network.hosts())
        if not hosts:
            hosts = [network.network_address]
    except Exception as e:
        logger.error(f"Invalid subnet string '{subnet_str}': {e}")
        return []
        
    active_ips = []
    total_hosts = len(hosts)
    
    logger.info(f"Scanning subnet {subnet_str} ({total_hosts} hosts) for open port 102...")
    
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    try:
        future_to_ip = {executor.submit(check_ip_port_102, str(ip), timeout): str(ip) for ip in hosts}
        
        completed = 0
        for future in concurrent.futures.as_completed(future_to_ip):
            if is_cancelled_fn and is_cancelled_fn():
                # Abort scan immediately and do not block
                executor.shutdown(wait=False, cancel_futures=True)
                return []
                
            ip = future_to_ip[future]
            completed += 1
            
            try:
                is_open = future.result()
                if is_open:
                    active_ips.append(ip)
                    logger.info(f"Found active S7 port 102 node at: {ip}")
            except Exception as e:
                logger.error(f"Error scanning IP {ip}: {e}")
                
            if progress_callback:
                progress_callback(completed, total_hosts, ip)
    finally:
        executor.shutdown(wait=False)
                
    return active_ips

def parse_s7_data(datatype, db_bytes, byte_offset, bit_offset=0):
    """
    Parses S7 variable datatypes from a raw bytearray.
    """
    if not db_bytes or byte_offset < 0 or byte_offset >= len(db_bytes):
        return None
        
    try:
        if datatype == "BOOL":
            val_byte = db_bytes[byte_offset]
            return bool(val_byte & (1 << bit_offset))
            
        elif datatype == "BYTE":
            return db_bytes[byte_offset]
            
        elif datatype == "CHAR":
            return chr(db_bytes[byte_offset])
            
        elif datatype == "INT":
            if byte_offset + 2 > len(db_bytes): return None
            return struct.unpack(">h", db_bytes[byte_offset:byte_offset+2])[0]
            
        elif datatype == "WORD":
            if byte_offset + 2 > len(db_bytes): return None
            return struct.unpack(">H", db_bytes[byte_offset:byte_offset+2])[0]
            
        elif datatype == "DINT":
            if byte_offset + 4 > len(db_bytes): return None
            return struct.unpack(">i", db_bytes[byte_offset:byte_offset+4])[0]
            
        elif datatype == "DWORD":
            if byte_offset + 4 > len(db_bytes): return None
            return struct.unpack(">I", db_bytes[byte_offset:byte_offset+4])[0]
            
        elif datatype == "REAL":
            if byte_offset + 4 > len(db_bytes): return None
            return struct.unpack(">f", db_bytes[byte_offset:byte_offset+4])[0]
            
        elif datatype == "STRING":
            if byte_offset + 2 > len(db_bytes): return None
            max_len = db_bytes[byte_offset]
            curr_len = db_bytes[byte_offset+1]
            # Safety checks
            if max_len == 0 or max_len > 254: max_len = 254
            if curr_len > max_len: curr_len = max_len
            if byte_offset + 2 + curr_len > len(db_bytes):
                curr_len = len(db_bytes) - byte_offset - 2
            if curr_len < 0: return ""
            
            return db_bytes[byte_offset+2:byte_offset+2+curr_len].decode('utf-8', errors='ignore')
            
        return None
    except Exception as e:
        logger.error(f"Error parsing S7 datatype {datatype} at offset {byte_offset}: {e}")
        return None

def pack_s7_data(datatype, value, byte_offset, bit_offset=0, existing_bytes=None):
    """
    Packs a python value into S7 variable datatype bytes, optionally merging into existing_bytes.
    """
    if existing_bytes is None:
        existing_bytes = bytearray(byte_offset + 8) # pre-allocate buffer with padding
        
    # Ensure bytearray is big enough
    required_size = byte_offset + 4 # standard size, string might expand this
    if datatype in ["INT", "WORD"]:
        required_size = byte_offset + 2
    elif datatype in ["BYTE", "CHAR", "BOOL"]:
        required_size = byte_offset + 1
    elif datatype == "STRING":
        required_size = byte_offset + 2 + (len(str(value)) if value else 0)
        
    if len(existing_bytes) < required_size:
        existing_bytes.extend(bytearray(required_size - len(existing_bytes)))
        
    try:
        if datatype == "BOOL":
            val_bool = bool(int(value) if str(value).isdigit() else value)
            val_byte = existing_bytes[byte_offset]
            if val_bool:
                val_byte |= (1 << bit_offset)
            else:
                val_byte &= ~(1 << bit_offset)
            existing_bytes[byte_offset] = val_byte
            return existing_bytes[byte_offset:byte_offset+1]
            
        elif datatype == "BYTE":
            val_byte = int(value) & 0xFF
            existing_bytes[byte_offset] = val_byte
            return existing_bytes[byte_offset:byte_offset+1]
            
        elif datatype == "CHAR":
            v_str = str(value)
            char_val = ord(v_str[0]) if v_str else 0
            existing_bytes[byte_offset] = char_val & 0xFF
            return existing_bytes[byte_offset:byte_offset+1]
            
        elif datatype == "INT":
            val_bytes = struct.pack(">h", int(value))
            existing_bytes[byte_offset:byte_offset+2] = val_bytes
            return val_bytes
            
        elif datatype == "WORD":
            val_bytes = struct.pack(">H", int(value) & 0xFFFF)
            existing_bytes[byte_offset:byte_offset+2] = val_bytes
            return val_bytes
            
        elif datatype == "DINT":
            val_bytes = struct.pack(">i", int(value))
            existing_bytes[byte_offset:byte_offset+4] = val_bytes
            return val_bytes
            
        elif datatype == "DWORD":
            val_bytes = struct.pack(">I", int(value) & 0xFFFFFFFF)
            existing_bytes[byte_offset:byte_offset+4] = val_bytes
            return val_bytes
            
        elif datatype == "REAL":
            val_bytes = struct.pack(">f", float(value))
            existing_bytes[byte_offset:byte_offset+4] = val_bytes
            return val_bytes
            
        elif datatype == "STRING":
            str_bytes = str(value).encode('utf-8', errors='ignore')
            max_len = existing_bytes[byte_offset] if byte_offset < len(existing_bytes) else 254
            if max_len == 0:
                max_len = 254
            curr_len = min(len(str_bytes), max_len)
            
            # Ensure output fits
            needed_len = byte_offset + 2 + curr_len
            if len(existing_bytes) < needed_len:
                existing_bytes.extend(bytearray(needed_len - len(existing_bytes)))
                
            existing_bytes[byte_offset] = max_len
            existing_bytes[byte_offset+1] = curr_len
            existing_bytes[byte_offset+2:byte_offset+2+curr_len] = str_bytes[:curr_len]
            return existing_bytes[byte_offset:byte_offset+2+curr_len]
            
        return None
    except Exception as e:
        logger.error(f"Error packing S7 datatype {datatype} at offset {byte_offset}: {e}")
        return None

def parse_s7_address(address_str):
    """
    Parses S7 address strings (English notation I, Q, M, DB and German/Italian aliases E, A).
    Returns a dict:
    {
        "valid": True/False,
        "area_code": 0x81 (PE/Inputs), 0x82 (PA/Outputs), 0x83 (MK/Merkers), 0x84 (DB),
        "area_name": "I", "Q", "M", or "DB",
        "db_number": int (0 for I/Q/M),
        "byte_offset": int,
        "bit_offset": int,
        "datatype": "BOOL", "BYTE", "INT", "REAL", etc.,
        "error": None or str
    }
    """
    if not address_str or not isinstance(address_str, str):
        return {"valid": False, "error": "Indirizzo vuoto."}
        
    raw = address_str.strip().upper()
    
    # 1. DB Bit: DB1.DBX0.0 or DB1.X0.0 or DB1.0.0
    m = re.match(r'^DB(\d+)\.(?:DBX|X)?(\d+)\.([0-7])$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x84, "area_name": f"DB{m.group(1)}",
            "db_number": int(m.group(1)), "byte_offset": int(m.group(2)),
            "bit_offset": int(m.group(3)), "datatype": "BOOL", "error": None
        }
        
    # 2. DB Byte: DB1.DBB0 or DB1.B0
    m = re.match(r'^DB(\d+)\.(?:DBB|B)(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x84, "area_name": f"DB{m.group(1)}",
            "db_number": int(m.group(1)), "byte_offset": int(m.group(2)),
            "bit_offset": 0, "datatype": "BYTE", "error": None
        }

    # 3. DB Word: DB1.DBW0 or DB1.W0
    m = re.match(r'^DB(\d+)\.(?:DBW|W)(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x84, "area_name": f"DB{m.group(1)}",
            "db_number": int(m.group(1)), "byte_offset": int(m.group(2)),
            "bit_offset": 0, "datatype": "INT", "error": None
        }

    # 4. DB DWord/Float: DB1.DBD0 or DB1.D0
    m = re.match(r'^DB(\d+)\.(?:DBD|D)(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x84, "area_name": f"DB{m.group(1)}",
            "db_number": int(m.group(1)), "byte_offset": int(m.group(2)),
            "bit_offset": 0, "datatype": "REAL", "error": None
        }
        
    # 5. DB Byte shorthand: DB1.0
    m = re.match(r'^DB(\d+)\.(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x84, "area_name": f"DB{m.group(1)}",
            "db_number": int(m.group(1)), "byte_offset": int(m.group(2)),
            "bit_offset": 0, "datatype": "BYTE", "error": None
        }

    # 6. Inputs (I / PE / E): I0.0, IX0.0, E0.0
    m = re.match(r'^(?:I|IX|PE|E|EX)(\d+)\.([0-7])$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x81, "area_name": "I",
            "db_number": 0, "byte_offset": int(m.group(1)),
            "bit_offset": int(m.group(2)), "datatype": "BOOL", "error": None
        }

    m = re.match(r'^(?:IB|EB)(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x81, "area_name": "I",
            "db_number": 0, "byte_offset": int(m.group(1)),
            "bit_offset": 0, "datatype": "BYTE", "error": None
        }

    m = re.match(r'^(?:IW|EW)(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x81, "area_name": "I",
            "db_number": 0, "byte_offset": int(m.group(1)),
            "bit_offset": 0, "datatype": "INT", "error": None
        }

    m = re.match(r'^(?:ID|ED)(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x81, "area_name": "I",
            "db_number": 0, "byte_offset": int(m.group(1)),
            "bit_offset": 0, "datatype": "REAL", "error": None
        }

    # 7. Outputs (Q / PA / A): Q0.0, QX0.0, A0.0
    m = re.match(r'^(?:Q|QX|PA|A|AX)(\d+)\.([0-7])$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x82, "area_name": "Q",
            "db_number": 0, "byte_offset": int(m.group(1)),
            "bit_offset": int(m.group(2)), "datatype": "BOOL", "error": None
        }

    m = re.match(r'^(?:QB|AB)(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x82, "area_name": "Q",
            "db_number": 0, "byte_offset": int(m.group(1)),
            "bit_offset": 0, "datatype": "BYTE", "error": None
        }

    m = re.match(r'^(?:QW|AW)(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x82, "area_name": "Q",
            "db_number": 0, "byte_offset": int(m.group(1)),
            "bit_offset": 0, "datatype": "INT", "error": None
        }

    m = re.match(r'^(?:QD|AD)(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x82, "area_name": "Q",
            "db_number": 0, "byte_offset": int(m.group(1)),
            "bit_offset": 0, "datatype": "REAL", "error": None
        }

    # 8. Merkers (M / MK): M0.0, MX0.0
    m = re.match(r'^(?:M|MX|MK)(\d+)\.([0-7])$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x83, "area_name": "M",
            "db_number": 0, "byte_offset": int(m.group(1)),
            "bit_offset": int(m.group(2)), "datatype": "BOOL", "error": None
        }

    m = re.match(r'^MB(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x83, "area_name": "M",
            "db_number": 0, "byte_offset": int(m.group(1)),
            "bit_offset": 0, "datatype": "BYTE", "error": None
        }

    m = re.match(r'^MW(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x83, "area_name": "M",
            "db_number": 0, "byte_offset": int(m.group(1)),
            "bit_offset": 0, "datatype": "INT", "error": None
        }

    m = re.match(r'^MD(\d+)$', raw)
    if m:
        return {
            "valid": True, "area_code": 0x83, "area_name": "M",
            "db_number": 0, "byte_offset": int(m.group(1)),
            "bit_offset": 0, "datatype": "REAL", "error": None
        }

    return {"valid": False, "error": f"Sintassi indirizzo '{address_str}' non riconosciuta."}

