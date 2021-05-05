from json import dumps
import re
from log import LOG

class LineParser(object):
    def __init__(self,
                 data,
                 ix,
                 label,
                 table_name,
                 file_name):
        self.data = data
        # Strip ?
        self.table_name = table_name
        self.file_name = file_name
        self.ix = ix
        self.label = label.replace("'", '"')
        self.query_summary = None
        self.sql = None
        self.parts = None
        self.info = None
        self.query = None
        self.ts = None
        self.meta = None
        self.log_level = None
        self.process_id = None
        self.source = None
        self.has_query_summary = 'query_summary' in self.data
        self.success = False
        self._parse()

    def _parse(self):
        if self.data.strip() == '':
            self.success = False
        else:
            try:
                self.parts = self.data.split(' :: ')
                self.info = self.parts[0]
                self.query = ' :: '.join(self.parts[1:]).replace("'", '"')
                self.ts, self.meta = self.info.split(' [')
                self.log_level, self.process_id, self.source = self.meta[:-1].split('|')
                self.success = True
                self._produce_sql()
            except ValueError as e:
                self.success = False
                ## Making logfiles too big
                LOG.debug(f'Error parsing line: {self.file_name}:{self.ix}\t{self.data.strip()}:\n{str(e)}')
                # print(e, self.data)
                # raise(e)

    def _produce_sql(self):
        if self.has_query_summary:
            self._produce_sql_with_query_summary()
        else:
            self._produce_default_sql()

    def _produce_sql_with_query_summary(self):
        try:
            self.query_summary = dumps({d.strip().split(':')[0].strip(): d.strip().split(':')[1].strip()
                                        for d in self.query.split(';') if d.strip() != ''}).replace("'", "''")
            self.sql = f"""INSERT INTO {self.table_name} ("index", "timestamp", "label", "loglevel", "thread", "source", "query", "query_summary")
                            VALUES ('{self.ix}', '{self.ts}', '{self.label}', '{self.log_level}', '{self.process_id}', '{self.source}', '{self.query}', '{self.query_summary}')"""
        except IndexError:
            self._produce_default_sql()

    def _produce_default_sql(self):
        self.sql = f"""INSERT INTO {self.table_name} ("index", "timestamp", "label", "loglevel", "thread", "source", "query")
                        VALUES ('{self.ix}', '{self.ts}', '{self.label}', '{self.log_level}', '{self.process_id}', '{self.source}', '{self.query}')"""
