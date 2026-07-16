import sys
import os
import unittest

# Add src folder to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from plc_comm import PLCClient
from utils import parse_s7_data, pack_s7_data

class TestS7BackupTool(unittest.TestCase):
    def setUp(self):
        # Initialize client in simulation mode for local offline unit testing
        self.client = PLCClient(simulate=True)
        self.client.connect("127.0.0.1")

    def tearDown(self):
        self.client.disconnect()

    def test_connection_and_cpu_info(self):
        self.assertTrue(self.client.is_connected())
        info = self.client.get_cpu_info()
        self.assertEqual(info["ModuleTypeName"], "CPU 315-2 PN/DP (SIM)")
        self.assertEqual(info["SerialNumber"], "S7-SIM-12345678")

    def test_list_dbs(self):
        dbs = self.client.list_dbs()
        self.assertIn(1, dbs)
        self.assertIn(2, dbs)
        self.assertIn(10, dbs)
        self.assertIn(100, dbs)

    def test_db_read_write(self):
        # Read initial simulated DB10 data (should be all zeros)
        size = self.client.get_db_size(10)
        self.assertEqual(size, 50)
        
        data = self.client.read_db_bytes(10, size)
        self.assertEqual(len(data), 50)
        self.assertEqual(data[0], 0)
        
        # Modify some bytes
        data[0] = 0xAA
        data[1] = 0x55
        self.client.write_db_bytes(10, data)
        
        # Read back and check
        data_read = self.client.read_db_bytes(10, size)
        self.assertEqual(data_read[0], 0xAA)
        self.assertEqual(data_read[1], 0x55)

    def test_s7_datatype_parsing(self):
        buffer = bytearray(20)
        
        # Test INT packing and parsing (Big Endian)
        pack_s7_data("INT", 1234, 0, existing_bytes=buffer)
        val_int = parse_s7_data("INT", buffer, 0)
        self.assertEqual(val_int, 1234)
        
        # Test REAL packing and parsing (Big Endian float)
        pack_s7_data("REAL", 3.1415, 2, existing_bytes=buffer)
        val_real = parse_s7_data("REAL", buffer, 2)
        self.assertAlmostEqual(val_real, 3.1415, places=4)
        
        # Test BOOL packing and parsing
        pack_s7_data("BOOL", True, 6, bit_offset=2, existing_bytes=buffer)
        pack_s7_data("BOOL", False, 6, bit_offset=3, existing_bytes=buffer)
        
        val_bool_2 = parse_s7_data("BOOL", buffer, 6, bit_offset=2)
        val_bool_3 = parse_s7_data("BOOL", buffer, 6, bit_offset=3)
        self.assertTrue(val_bool_2)
        self.assertFalse(val_bool_3)
        
        # Test STRING packing and parsing (Siemens format: [max_len, curr_len, chars...])
        buffer_str = bytearray([10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        pack_s7_data("STRING", "HELLO", 0, existing_bytes=buffer_str)
        val_str = parse_s7_data("STRING", buffer_str, 0)
        self.assertEqual(val_str, "HELLO")

if __name__ == '__main__':
    unittest.main()
