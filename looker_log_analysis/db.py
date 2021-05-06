
import psycopg2
from datetime import datetime as dt
from log import LOG
from config import config
from helpers import estimate_size
from parse import LineHandler

CONFIG = config()

def connect(config=CONFIG):
    conn_string = ' '.join([f"{k}='{v}'" for k, v in config['Connection'].items()])
    return psycopg2.connect(conn_string)


def test_connection(config=CONFIG):
    """Returns True if the configuration connects successfully"""
    try:
        with connect(config=config):
            return True
    except(psycopg2.OperationalError) as e:
        LOG.error(e)
        raise(e)


def setup(force=False, rebuild=True, config=CONFIG):
    """Tells you if the table specified in config already exists and creates it
     if it is not found. Use force=True to force the deletion and creation of a
     new table. Setting rebuild to False will drop the table with rebuilding it"""
    test_connection()
    table_name = config['DB']['table_name']
    COLS = ['index', 'timestamp', 'label', 'loglevel', 'thread', 'source', 'query', 'query_summary']
    with connect(config=config) as conn:
        cur = conn.cursor()
        if force:
            drop_table(table_name, cur)
            if rebuild:
                cur.execute("""CREATE TABLE {}({} integer PRIMARY KEY,
                                               {} timestamp,
                                               {} text,
                                               {} text,
                                               {} text,
                                               {} text,
                                               {} text,
                                               {} text);""".format(table_name, *COLS))
                LOG.info(f"Successfully created new table {table_name}")
        else:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                r = cur.fetchone()[0]
                LOG.info(f"Existing table {table_name} contains {r:,} rows")
            except(psycopg2.ProgrammingError) as e:
                LOG.warn(str(e))
                setup(force=True, config=config)


def teardown(label=False, config=CONFIG):
    """Pass in a label to drop specific rows from the table, or label=False to
     drop the whole table"""
    table_name = config['DB']['table_name']
    if not label:
        setup(force=True, rebuild=False, config=config)
    else:
        with connect(config=config) as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE label = '{label}'")
            r = cur.fetchone()[0]
            cur.execute(f"DELETE FROM {table_name} WHERE label = '{label}'")
            LOG.info(f"Successfully deleted {r:,} rows with label {label} from {table_name}")


def index_table(table_name, cursor):
    """Use a cursor to add default indexes to a table specified by name"""
    cursor.execute(f"CREATE INDEX {table_name}_index ON {table_name}(index);")
    cursor.execute(f"CREATE INDEX {table_name}_thread ON {table_name}(thread);")
    LOG.info(f"Indexed table {table_name}")


def drop_table(table_name, cursor):
    """Use a cursor to drop a table and associated indexes by name"""
    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    cursor.execute(f"DROP INDEX IF EXISTS {table_name}_index;")
    cursor.execute(f"DROP INDEX IF EXISTS {table_name}_thread;")
    LOG.info(f"Dropped table {table_name}")


def parse_files(files, label, insert=True, config=CONFIG):
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
    table_name = config['DB']['table_name']
    with connect(config=config) as conn:
        cur = conn.cursor()
        est = estimate_size(files, LOG)
        if not insert:
            teardown(config=config)
        setup(config=config)
        cur.execute(f"SELECT MAX(index) FROM {table_name}")
        max_index = cur.fetchone()[0]
        max_index = 0 if max_index is None else max_index
        ix = max_index + 1
        max_statements = CONFIG['App']['statements_per_update']
        check_interval=CONFIG['App']['check_interval']
        commit_interval=CONFIG['App']['commit_interval']
        Handler = LineHandler(cur,
                              conn,
                              ix,
                              est,
                              label,
                              table_name,
                              LOG,
                              dt.now(),
                              check_interval,
                              commit_interval,
                              max_statements)
        for file in files:
            with open(file, 'r', encoding='UTF-8') as f:
                for line in f:
                    Handler.process(line, f)
        Handler.clean_up()
        if Handler.skipped > 0:
            LOG.warn(f"Skipped {Handler.skipped:,} lines and saved output to log")
        if insert:
            LOG.info(f"Successfully inserted {Handler.ct:,} new rows")
        else:
            LOG.info(f"Successfully written {Handler.ct:,} rows")
            index_table(table_name, cur)


def print_labels(config=CONFIG):
    table_name = config['DB']['table_name']
    outstring = ''
    with connect(config=config) as conn:
        cur = conn.cursor()
        try:
            cur.execute(f"SELECT label, COUNT(*) FROM {table_name} GROUP BY 1 ORDER BY 2 DESC")
            for row in cur.fetchall():
                outstring += f"\t{row[0]:>15}:\t{row[1]:<6,} rows\n"
            if outstring != '':
                LOG.info(f"Existing labels in the table:\n{outstring}\nUse --reset --clear (or -rc) and a label to delete it, or --reset on its own to delete all.")
            else:
                LOG.info("The table is empty.")
        except psycopg2.errors.UndefinedTable:
            LOG.error("The table doesn't exist.")
