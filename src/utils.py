import socket
import struct
import concurrent.futures
import ipaddress
import logging

logger = logging.getLogger("IstanteS7.Utils")

def get_local_ip_adapters():
    """
    Retrieves all active local network adapters and their IPv4 addresses.
    Returns a list of dicts: [{'name': 'Adapter Name', 'ip': '192.168.1.10', 'subnet': '192.168.1.0/24'}]
    """
    adapters = []
    
    # Method 1: Using standard socket host info (very portable on Windows)
    try:
        hostname = socket.gethostname()
        # Resolve all IPs linked to this hostname
        ips = socket.gethostbyname_ex(hostname)[2]
        
        # Filter out localhost and IPv6-like structures
        for ip in ips:
            if ip.startswith("127."):
                continue
            try:
                # Construct standard /24 subnet as default
                net = ipaddress.IPv4Network(f"{ip}/255.255.255.0", strict=False)
                adapters.append({
                    "name": f"Local Interface ({ip})",
                    "ip": ip,
                    "subnet": str(net)
                })
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Error querying socket host adapters: {e}")
        
    # If no adapters found, add a fallback simulated range
    if not adapters:
        adapters.append({
            "name": "Simulated Loopback (Localhost)",
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

def scan_subnet_port_102(subnet_str, max_workers=50, timeout=0.2, progress_callback=None):
    """
    Scans all IP addresses in the given subnet for port 102.
    progress_callback receives (current_step, total_steps, current_ip)
    """
    try:
        network = ipaddress.IPv4Network(subnet_str, strict=False)
        # Skip network and broadcast address if it's a standard subnet, but scan all for smaller subnets
        hosts = list(network.hosts())
        if not hosts:
            hosts = [network.network_address]
    except Exception as e:
        logger.error(f"Invalid subnet string '{subnet_str}': {e}")
        return []
        
    active_ips = []
    total_hosts = len(hosts)
    
    logger.info(f"Scanning subnet {subnet_str} ({total_hosts} hosts) for open port 102...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map futures
        future_to_ip = {executor.submit(check_ip_port_102, str(ip), timeout): str(ip) for ip in hosts}
        
        completed = 0
        for future in concurrent.futures.as_completed(future_to_ip):
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
