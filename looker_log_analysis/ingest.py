
import psycopg2
import json
from looker_log_analysis.log import log
from looker_log_analysis.config import CONFIG
from looker_log_analysis.parse import LineParser

def connect():
    conn_string = ' '.join([f"{k}='{v}'" for k, v in CONFIG['Connection'].items()])
    return connect()


def test_connection():
    """Returns True if the configuration connects successfully"""
    try:
        with connect():
            return True
    except(psycopg2.OperationalError) as e:
        log('error', e)
        raise(e)


def setup(force=False, rebuild=True):
    """Tells you if the table specified in config already exists and creates it
     if it is not found. Use force=True to force the deletion and creation of a
     new table. Setting rebuild to False will drop the table with rebuilding it"""
    test_connection()
    table_name = CONFIG['DB']['table_name']
    COLS = ['index', 'timestamp', 'label', 'loglevel', 'thread', 'source', 'query', 'query_summary']
    with connect() as conn:
        cur = conn.cursor()
        if force:
            cur.execute(f"DROP TABLE IF EXISTS {table_name};")
            cur.execute(f"DROP INDEX IF EXISTS {table_name}_index;")
            cur.execute(f"DROP INDEX IF EXISTS {table_name}_thread;")
            if rebuild:
                cur.execute("""CREATE TABLE {}({} integer PRIMARY KEY,
                                               {} timestamp,
                                               {} text,
                                               {} text,
                                               {} text,
                                               {} text,
                                               {} text,
                                               {} text);""".format(table_name, *COLS))
                log('info', f"Successfully created new table {table_name}")
            conn.commit()
        else:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                r = cur.fetchone()[0]
                log('info', f"Exising table {table_name} contains {r:,} rows")
            except(psycopg2.ProgrammingError):
                setup(force=True)
            conn.commit()


def teardown(label=False):
    """Pass in a label to drop specific rows from the table, or label=False to
     drop the whole table"""
    table_name = CONFIG['DB']['table_name']
    if not label:
        setup(force=True, rebuild=False)
    else:
        with connect() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE label = '{label}'")
            r = cur.fetchone()[0]
            cur.execute(f"DELETE FROM {table_name} WHERE label = '{label}'")
            log('info', f"Successfully deleted {r:,} rows with label {label} from {table_name}")
            conn.commit()


def parse(cur, conn, line, ix, ct, table_name, label, total):
    """Parse a log line into a postgres update statement"""
    data = LineParser(line, ix, label, table_name)
    cur.execute(data.sql)
    if ct % 10000 == 0:
        log('info', f"Successfully written {ct:,}{total} rows")
    if ct % 100000 == 0:
        conn.commit()
        log('debug', "Committing")


def should_skip(line_text):
    skips = ('#', 'uri', 'org')
    return line_text.strip().startswith(skips)


def index_table(table_name, cursor):
    cursor.execute(f"CREATE INDEX {table_name}_index ON {table_name}(index);")
    cursor.execute(f"CREATE INDEX {table_name}_thread ON {table_name}(thread);")


def parse_files(files, label, insert=True):
    """Pass in an array of logfiles and this will insert them into a Postgres table.

    Input
    -----------------------------------
    files         Path to logfile or array of paths to logfiles
    label         A label for the logfiles (Useful if you want to separate logs
                  from multiple Looker instances)
    config        A dictionary containing connection config information
    insert        True to insert new rows, False to drop and make a fresh table

    Output
    -----------------------------------
    True

    """
    if not isinstance(files, list):
        files = [files]
    skipped = 0
    table_name = CONFIG['DB']['table_name']
    with connect() as conn:
        cur = conn.cursor()
        ix = 0 # For indexing the rows
        ct = 0 # For counting the rows inserted
        total = ''
        est = 0 # For estimating the progress
        for file in files:
            with open(file, 'r', encoding='UTF-8') as f:
                for line in f:
                    est += 1
        total = f" / ~{est:,}"
        log('info', f"Approx. {est:,} log lines will be parsed")
        if not insert:
            teardown()
        setup()
        cur.execute(f"SELECT MAX(index) FROM {table_name}")
        max_index = cur.fetchone()[0]
        max_index = 0 if max_index is None else max_index
        ix = max_index
        parse_line = ''
        for file in files:
            with open(file, 'r', encoding='UTF-8') as f:
                for rawline in f:
                    if should_skip(rawline):
                        continue
                    elif rawline.strip().startswith('2'):
                        if parse_line != '':
                            try:
                                ix += 1
                                ct += 1
                                parse(cur=cur,
                                      conn=conn,
                                      line=parse_line,
                                      ix=ix,
                                      ct=ct,
                                      table_name=table_name,
                                      label=label,
                                      total=total)
                            except ValueError:
                                skipped += 1
                                log('error', 'Error parsing line')
                                log('error', f'{file}:{ix}\t{line}\n')
                                continue
                        parse_line = rawline
                    else:
                        parse_line += rawline
                        continue
        try:
            ix += 1
            ct += 1
            parse(cur=cur,
                  conn=conn,
                  line=parse_line,
                  ix=ix,
                  ct=ct,
                  table_name=table_name,
                  label=label,
                  total=total)
        except Exception:
            skipped += 1
            log('error', 'Unhandled error')
            log('error', f'{file}:{ix}\t{line}\n')
        conn.commit()
        if insert:
            log('info', f"Successfully inserted {ct:,} new rows")
        else:
            log('info', f"Successfully written {ct:,} rows")
        if skipped > 0:
            log('warn', f"Skipped {skipped:,} lines and saved output to log")
        if not insert:
            index_table(table_name, cur)
            conn.commit()


def print_labels():
    table_name = CONFIG['DB']['table_name']
    with connect() as conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT label FROM {} GROUP BY 1".format(table_name))
            r = [row[0] for row in cur.fetchall()]
            conn.commit()
            if r == []:
                log('info', "The table is empty.")
            else:
                log('info', f"Existing labels in the table:\n{r}\nUse --reset --clear and a label to delete it, or --reset on its own to delete all.")
        except psycopg2.errors.UndefinedTable:
            log('error', "The table doesn't exist.")
