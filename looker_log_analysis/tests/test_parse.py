import unittest
from unittest import mock
from unittest.mock import Mock, MagicMock, patch
from looker_log_analysis.tests import setup_tests
from looker_log_analysis.parse import LineParser
DEFAULTS = (1, 'some_label', 'some_table', 'some_file')
from looker_log_analysis import db


class TestParsing(unittest.TestCase):  
    def test_empty_fails(self):
        """An empty logline should fail"""
        case = ''
        data = LineParser(case, *DEFAULTS)
        self.assertFalse(data.success)
    
    def test_simple_passes(self):
        case = """2021-04-28 23:59:57.643 +0000 [INFO|13757da|periodic] :: (0.004027s) Periodic job 'connection_hub_status_update' completed"""
        data = LineParser(case, *DEFAULTS)
        self.assertTrue(data.success)
    
    def test_malformed_line(self):
        case = """Periodic job 'connection_hub_status_update' completed"""
        data = LineParser(case, *DEFAULTS)
        self.assertFalse(data.success)

    # @patch('psycopg2')
    def test_read_multiline(self):
        # single line, triple line, single line
        db.parse_files('looker_log_analysis/tests/data/multiline', 'foo')
        # print(mock_connection)

if __name__ == '__main__':
    unittest.main()
