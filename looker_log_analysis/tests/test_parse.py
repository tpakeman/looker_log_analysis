from json.decoder import JSONDecodeError
import unittest, json
# from unittest.mock import Mock, MagicMock, patch
from looker_log_analysis.tests import setup_tests # Redirect logging
from looker_log_analysis.parse import LineParser
from looker_log_analysis import db
DEFAULTS = (1, 'some_label', 'some_table', 'some_file')


class TestParsing(unittest.TestCase):  
    def test_empty_data(self):
        """An empty logline should fail"""
        case = ''
        data = LineParser(case, *DEFAULTS)
        self.assertFalse(data.success)
    
    def test_simple_data(self):
        """Should successfully parse a short, simple log line"""
        case = """2021-04-28 23:59:57.643 +0000 [INFO|13757da|periodic] :: (0.004027s) Periodic job 'connection_hub_status_update' completed"""
        data = LineParser(case, *DEFAULTS)
        self.assertTrue(data.success)
        self.assertEqual(data.data,case)
        self.assertEqual(data.info,'2021-04-28 23:59:57.643 +0000 [INFO|13757da|periodic]')
        self.assertEqual(data.query,'(0.004027s) Periodic job "connection_hub_status_update" completed')
        self.assertEqual(data.ts,'2021-04-28 23:59:57.643 +0000')
        self.assertEqual(data.log_level,'INFO')
        self.assertEqual(data.process_id,'13757da')
        self.assertEqual(data.source,'periodic')
        self.assertEqual(data.query_summary,'NULL')
        self.assertEqual(data.sql,f"""INSERT INTO {data.table_name} ("index", "timestamp", "label", "loglevel", "thread", "source", "query", "query_summary") VALUES ('{data.ix}', '{data.ts}', '{data.label}', '{data.log_level}', '{data.process_id}', '{data.source}', '{data.query}', '{data.query_summary}')""")

    def test_data_with_query_summary(self):
        """Should successfully parse a log line containing a query summary"""
        case = """2021-02-24 11:17:58.009 +0000 [INFO|32a09ae|query_summary] :: event: fetch; slug: 1c7c862a2d7293d65c362411c51d73fb; grand_total: 5.19; stream_this: 0.04; stream_others: 0.16;"""
        data = LineParser(case, *DEFAULTS)
        self.assertTrue(data.success)
        self.assertEqual(data.data,case)
        self.assertEqual(data.info,'2021-02-24 11:17:58.009 +0000 [INFO|32a09ae|query_summary]')
        self.assertEqual(data.query,'event: fetch; slug: 1c7c862a2d7293d65c362411c51d73fb; grand_total: 5.19; stream_this: 0.04; stream_others: 0.16;')
        self.assertEqual(data.ts,'2021-02-24 11:17:58.009 +0000')
        self.assertEqual(data.log_level,'INFO')
        self.assertEqual(data.process_id,'32a09ae')
        self.assertEqual(data.source,'query_summary')
        self.assertEqual(data.query_summary,'{"event": "fetch", "slug": "1c7c862a2d7293d65c362411c51d73fb", "grand_total": "5.19", "stream_this": "0.04", "stream_others": "0.16"}')
        try:
            json.loads(data.query_summary)
        except JSONDecodeError:
            self.fail("Query summary should be parsable JSON")
        self.assertEqual(data.sql,f"""INSERT INTO {data.table_name} ("index", "timestamp", "label", "loglevel", "thread", "source", "query", "query_summary") VALUES ('{data.ix}', '{data.ts}', '{data.label}', '{data.log_level}', '{data.process_id}', '{data.source}', '{data.query}', '{data.query_summary}')""")
    
    def test_multiline_data(self):
        """Should successfully parse a log line spanning several lines"""
        case = """2021-02-24 07:03:49.608 +0000 [INFO|3289838|db:looker] :: (0.000190s) INSERT INTO "LICENSE_VALIDATION_RESPONSE" ("STATE", "RESPONSE_CODE", "TIMESTAMP_COMPLETED", "TIMESTAMP_INITIATED", "VALIDATION_TYPE", "INTEGRITY_CHECK") VALUES ('{"licenseKey":"5C3DA0D45EA327F2DF1D","application":"looker","licenseStatus":"in_use","expiresAt":""}', 0, TIMESTAMP '2021-02-24 07:03:49.600957', TIMESTAMP '2021-02-24 07:03:49.171771', 'HTTPS Validation Checker', 'b4LXqOnselO/00hNljmand0xOFYOm/dqnhYyY0+2AGPqVo5mSkfrk+5/NoVI
MFTQTWniuMKXvOxhVUKdrF3e40CKwRqsSaTjN3GhX8HdywdMxOyuCTukE+Fr
FVrJm3pQMuSuiK4jYA0vUUrDFMuq6z+whhJJpl8Qp/yecNXn1MNbLNr2vPK6
oZH1A+o5W6KzQXhy5v+NhQ07HMS25AOj5PU0RTSXaRu3I20z8IC1YB8=')"""
        data = LineParser(case, *DEFAULTS)
        self.assertTrue(data.success)
        self.assertEqual(data.data,case)
        self.assertEqual(data.info,'2021-02-24 07:03:49.608 +0000 [INFO|3289838|db:looker]')
        self.assertEqual(data.query,'''(0.000190s) INSERT INTO "LICENSE_VALIDATION_RESPONSE" ("STATE", "RESPONSE_CODE", "TIMESTAMP_COMPLETED", "TIMESTAMP_INITIATED", "VALIDATION_TYPE", "INTEGRITY_CHECK") VALUES ("{"licenseKey":"5C3DA0D45EA327F2DF1D","application":"looker","licenseStatus":"in_use","expiresAt":""}", 0, TIMESTAMP "2021-02-24 07:03:49.600957", TIMESTAMP "2021-02-24 07:03:49.171771", "HTTPS Validation Checker", "b4LXqOnselO/00hNljmand0xOFYOm/dqnhYyY0+2AGPqVo5mSkfrk+5/NoVI
MFTQTWniuMKXvOxhVUKdrF3e40CKwRqsSaTjN3GhX8HdywdMxOyuCTukE+Fr
FVrJm3pQMuSuiK4jYA0vUUrDFMuq6z+whhJJpl8Qp/yecNXn1MNbLNr2vPK6
oZH1A+o5W6KzQXhy5v+NhQ07HMS25AOj5PU0RTSXaRu3I20z8IC1YB8=")''')
        self.assertEqual(data.ts,'2021-02-24 07:03:49.608 +0000')
        self.assertEqual(data.log_level,'INFO')
        self.assertEqual(data.process_id,'3289838')
        self.assertEqual(data.source,'db:looker')
        self.assertEqual(data.query_summary,'NULL')
        self.assertEqual(data.sql,f"""INSERT INTO {data.table_name} ("index", "timestamp", "label", "loglevel", "thread", "source", "query", "query_summary") VALUES ('{data.ix}', '{data.ts}', '{data.label}', '{data.log_level}', '{data.process_id}', '{data.source}', '{data.query}', '{data.query_summary}')""")
        ...
    def test_malformed_line(self):
        case = """Periodic job 'connection_hub_status_update' completed"""
        data = LineParser(case, *DEFAULTS)
        self.assertFalse(data.success)
        self.assertEqual(data.data,case)
        self.assertEqual(data.info,None)
        self.assertEqual(data.query, None)
        self.assertEqual(data.ts, None)
        self.assertEqual(data.log_level,None)
        self.assertEqual(data.process_id,None)
        self.assertEqual(data.source,None)
        self.assertEqual(data.query_summary,None)
        self.assertEqual(data.sql,None)

    # TO DO - Mock and intercept DB calls to interrogate processing
    def test_read_multiline(self):
        # single line, triple line, single line
        db.parse_files('looker_log_analysis/tests/data/multiline', 'foo')
        # print(mock_connection)

if __name__ == '__main__':
    unittest.main()
