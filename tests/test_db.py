import unittest
from modules import db
from modules.config import config
from psycopg2 import OperationalError 
DEFAULT_CONFIG = config()
from tests import setup_tests

class TestDB(unittest.TestCase):
    def test_connection_successful(self):
        self.assertEquals(db.test_connection(DEFAULT_CONFIG), True)   
    
    
    def test_connection_fails(self):
        CUSTOM_CONFIG = config()
        CUSTOM_CONFIG['Connection']['dbname'] = 'doesnotexist'
        with self.assertRaises(OperationalError):
            db.test_connection(CUSTOM_CONFIG)

if __name__ == '__main__':
    unittest.main()
