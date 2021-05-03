from json import dumps


class LineParser(object):
    def __init__(self, data, ix, label, table_name):
        self.data = data
        self.table_name = table_name
        self.ix = ix
        self.label = label.replace("'", '"')
        self.query_summary = None
        self.sql = None
        self.parts = self.data.split(' :: ')
        self.info = parts[0]
        self.query = ' :: '.join(parts[1:]).replace("'", '"')
        self.ts, self.meta = info.split(' [')
        self.log_level, self.process_id, self.source = meta[:-1].split('|')
        self.has_query_summary = 'query_summary' in self.data
        self._produce_sql()

    def _produce_sql(self):
        if self.has_query_summary:
            self._produce_sql_with_query_summary()
        else:
            self._produce_default_sql()

    def _produce_sql_with_query_summary(self):
        try:
            self.query_summary = dumps({d.strip().split(':')[0].strip(): d.strip().split(':')[1].strip()
                                        for d in query.split(';') if d.strip() != ''}).replace("'", "''")
            self.sql = f"""INSERT INTO {self.table_name} ("index", "timestamp", "label", "loglevel", "thread", "source", "query", "query_summary")
                            VALUES ('{self.ix}', '{self.ts}', '{self.label}', '{self.log_level}', '{self.process_id}', '{self.source}', '{self.query}', '{self.query_summary}')"""
        except IndexError:
            self._produce_default_sql()

    def _produce_default_sql(self):
        self.sql = f"""INSERT INTO {self.table_name} ("index", "timestamp", "label", "loglevel", "thread", "source", "query")
                        VALUES ('{self.ix}', '{self.ts}', '{self.label}', '{self.log_level}', '{self.process_id}', '{self.source}', '{self.query}')"""
