import unittest
from looker_log_analysis.parse import LineParser
DEFAULTS = (1, 'some_label', 'some_table', 'some_file')
from looker_log_analysis.tests import setup_tests

## Test empty string
## Test failing string
## Test query summary
## Test various log line alternatives
## Test long lines



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
if __name__ == '__main__':
    unittest.main()
