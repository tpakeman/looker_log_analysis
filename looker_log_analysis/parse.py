from json import dumps
import re
from datetime import datetime as dt
LINESTART = re.compile(r'^\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}\:\d{2}\.\d{3} \+\d{4} \[')

# Feed all lines into the line buffer
# Handles two things: multilines, and multi-statements
class LineHandler(object):
    """Handle incoming lines of data, including multi-line sql statements.
    Executes database commmits when the number of statements exceeds a limit"""
    def __init__(self,
                 cursor,
                 connection,
                 index,
                 line_estimate,
                 insert_label,
                 table_name,
                 log,
                 start_time,
                 check_interval,
                 commit_interval,
                 max_statements):
        if int(max_statements) < 1:
            raise ValueError('Max statements must be more than 1')
        self.ct = 1
        self.skipped = 0
        self.start_time = start_time
        self.index = index
        self.line_estimate = line_estimate
        self.insert_label = insert_label
        self.table_name = table_name
        self.buffer = ''
        self.statements = []
        self.max_statements =  int(max_statements)
        self.cursor = cursor
        self.connection = connection
        self.check_interval = int(check_interval)
        self.commit_interval = int(commit_interval)
        self.log = log
        self.sql = None
        self.continuation = False

    def _should_skip(self, text):
        """Logical test for whether a specific line should be skipped"""
        skips = ('#', 'uri', 'org')
        return text.strip().startswith(skips)

    def _check_progress(self):
        if self.ct % self.check_interval == 0:
            elapsed = (dt.now() - self.start_time).total_seconds()
            avg_call_time = elapsed / self.ct
            est_completed_time = avg_call_time * self.line_estimate
            remaining = (est_completed_time - elapsed)
            self.log.info(f"Successfully written {self.ct:,} / ~{self.line_estimate:,} rows (est. {remaining:,.0f} seconds remaining)")
        if self.ct % self.commit_interval == 0:
            self._execute()
            self.connection.commit()
            self.log.debug("Committing")

    def process(self, line, filename):
        if self._should_skip(line):
            return
        if re.match(LINESTART, line):
            # Valid line found - process existing buffer
            data = LineParser(self.buffer, self.index, self.insert_label, self.table_name, filename, self.log)
            if data.success:
                if len(self.statements) == self.max_statements:
                    self._execute()
                else:
                    self.statements.append(data.sql)
                self._check_progress()
                self.index += 1
                self.ct += 1
            else:
                self.skipped += 1
            self.buffer = line
            self.continuation = False
        else:
            # Invalid line - append to previous 
            self.buffer += line
            self.continuation = True

    def _execute(self):
        """Process existing SQL statements and commit them"""
        prefix = f"""INSERT INTO {self.table_name} ("index", "timestamp", "label", "loglevel", "thread", "source", "query", "query_summary") 
        VALUES """
        data = ',\n'.join(self.statements)
        self.sql = prefix + data
        self.cursor.execute(self.sql)
        self.statements = []

    def clean_up(self):
        ## Process any remaining lines in buffer
        if self.continuation:
            data = LineParser(self.buffer, self.index, self.insert_label, self.table_name, filename)
            if data.success:
                self.statements.append(data.sql)
                self.index += 1
                self.ct += 1
            else:
                self.skipped += 1
        self._execute()
        self.continuation = False


class LineParser(object):
    def __init__(self,
                 data,
                 ix,
                 label,
                 table_name,
                 file_name,
                 log):
        self._reset()
        self.data = data.strip()
        if self.data != '':
            self.log = log
            self.data = data
            self.table_name = table_name
            self.file_name = file_name
            self.ix = ix
            self.label = label.replace("'", '"')
            self._parse()

    def _reset(self):
        """Set all components to None and success to False"""
        self.query_summary = None
        self.sql = None
        self.full_sql = None
        self.parts = None
        self.info = None
        self.query = None
        self.ts = None
        self.meta = None
        self.log_level = None
        self.process_id = None
        self.source = None
        self.success = False

    def _parse(self):
        """Parse the data into various attributes. This takes an atomic approach - 
        either the whole line parses or it doesn't. The success flag will be used to
        decide if the resulting SQL should be committed to the database."""
        try:
            self.parts = self.data.split(' :: ')
            self.info = self.parts[0]
            self.query = ' :: '.join(self.parts[1:]).replace("'", '"')
            self.ts, self.meta = self.info.split(' [')
            self.log_level, self.process_id, self.source = self.meta[:-1].split('|')
            if self.source == 'query_summary':
                self._parse_query_summary()
            else:
                self.query_summary = 'NULL'
            self._produce_sql()
            self.success = True
        except (ValueError, IndexError) as e:
            self._reset()
            self.log.debug(f'Error parsing line: {self.file_name}:{self.ix}\t{self.data.strip()}:\n{str(e)}')

    def _parse_query_summary(self):
        """Some Looker log lines contain a detailed query summary breakdown. In these cases
        we parse this out into a dict and save as JSON to be parsed out in Looker later"""
        try:
            self.query_summary = dumps({d.strip().split(':')[0].strip(): d.strip().split(':')[1].strip()
                                    for d in self.query.split(';') if d.strip() != ''}).replace("'", "''")
        except IndexError as e:
            # Catch but don't re-raise - we can still capture the unprocessed line
            self.log.error(f'Error parsing query summary for line {self.ix}: {str(e)}')
            self.query_summary = "NULL"

    def _produce_sql(self):
        """Produce the relevant SQL text to write in a single insert or as part of a larger
        insert"""
        self.sql = f"('{self.ix}', '{self.ts}', '{self.label}', '{self.log_level}', '{self.process_id}', '{self.source}', '{self.query}', '{self.query_summary}')"
        self.full_sql = f"""INSERT INTO {self.table_name} ("index", "timestamp", "label", "loglevel", "thread", "source", "query", "query_summary")
                        VALUES ('{self.ix}', '{self.ts}', '{self.label}', '{self.log_level}', '{self.process_id}', '{self.source}', '{self.query}', '{self.query_summary}')"""
