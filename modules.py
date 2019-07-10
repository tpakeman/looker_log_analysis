import psycopg2
import json

COLS = ['index', 'timestamp', 'label', 'loglevel', 'thread', 'source', 'query', 'query_summary']


with open('config.json', 'r') as f:
    CONFIG = json.loads(f.read())


def test_connection(config=CONFIG):
    """Returns True if the configuration connects successfully"""
    try:
        with psycopg2.connect("dbname='{dbname}' user='{user}' host='{host}'".format(**config)) as _:
            return True
    except(psycopg2.OperationalError) as e:
        print(e)
        return False


def setup(config=CONFIG, force=False, rebuild=True, debug=False):
    """Tells you if the table specified in config already exists and creates it
     if it is not found. Use force=True to force the deletion and creation of a
     new table. Setting rebuild to False will drop the table with rebuilding it"""
    if not test_connection(config):
        return False
    table_name = config['table_name']
    with psycopg2.connect("dbname='{dbname}' user='{user}' host='{host}'".format(**config)) as conn:
        cur = conn.cursor()
        if force:
            cur.execute("DROP TABLE IF EXISTS {};".format(table_name))
            cur.execute("DROP INDEX IF EXISTS {}_index;".format(table_name))
            cur.execute("DROP INDEX IF EXISTS {}_thread;".format(table_name))
            if rebuild:
                cur.execute("""CREATE TABLE {}({} integer PRIMARY KEY,
                                               {} timestamp,
                                               {} text,
                                               {} text,
                                               {} text,
                                               {} text,
                                               {} text,
                                               {} text);""".format(table_name, *COLS))
                if debug:
                    print("Successfully created new table {}".format(table_name))
            conn.commit()
        else:
            try:
                cur.execute("SELECT COUNT(*) FROM {}".format(table_name))
                r = cur.fetchone()[0]
                if debug:
                    print("Exising table {} contains {:,} rows".format(table_name, r))
            except(psycopg2.ProgrammingError):
                setup(config, force=True, debug=debug)
            conn.commit()


def teardown(config=CONFIG, label=False, debug=False):
    """Pass in a label to drop specific rows from the table, or label=False to
     drop the whole table"""
    table_name = config['table_name']
    if not label:
        setup(config, force=True, rebuild=False, debug=debug)
    else:
        with psycopg2.connect("dbname='{dbname}' user='{user}' host='{host}'".format(**config)) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM {} WHERE label = '{}'".format(table_name, label))
            r = cur.fetchone()[0]
            cur.execute("DELETE FROM {} WHERE label = '{}'".format(table_name, label))
            if debug:
                print("Successfully deleted {:,} rows with label {} from {}".format(r, label, table_name))
            conn.commit()


def parse(cur, conn, line, ix, ct, table_name, label, total, debug):
    """Parse a log line into a postgres update statement"""
    parts = line.split(' :: ')
    info = parts[0]
    query = ' :: '.join(parts[1:])
    ts, meta = info.split(' [')
    log_level, process_id, source = meta[:-1].split('|')
    if 'query_summary' in line:
        try:
            q_data = json.dumps({d.strip().split(':')[0].strip(): d.strip().split(':')[1].strip()
                                 for d in query.split(';') if d.strip() != ''})
            s = """INSERT INTO {} ("index", "timestamp", "label", "loglevel", "thread", "source", "query", "query_summary")
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(table_name, ix, ts, label, log_level, process_id, source, query.replace("'", '"'), q_data.replace("'", "''"))
            cur.execute(s)
        except IndexError:
            s = """INSERT INTO {} ("index", "timestamp", "label", "loglevel", "thread", "source", "query")
                    VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(table_name, ix, ts, label, log_level, process_id, source, query.replace("'", '"'))
            cur.execute(s)
    else:
        s = """INSERT INTO {} ("index", "timestamp", "label", "loglevel", "thread", "source", "query")
        VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(table_name, ix, ts, label, log_level, process_id, source, query.replace("'", '"'))
        cur.execute(s)
    if debug:
        if ct % 10000 == 0:
            if debug:
                print("Successfully written {:,}{} rows".format(ct, total))
    if ct % 100000 == 0:
        conn.commit()
        if debug:
            print("Committing")


def parse_files(files, label, config=CONFIG, insert=True, debug=False):
    """Pass in an array of logfiles and this will insert them into a Postgres table.

    Input
    -----------------------------------
    files         Path to logfile or array of paths to logfiles
    label         A label for the logfiles (Useful if you want to separate logs
                  from multiple Looker instances)
    config        A dictionary containing connection config information
    insert        True to insert new rows, False to drop and make a fresh table
    debug         True to print the progress

    Output
    -----------------------------------
    True

    """
    if not isinstance(files, list):
        files = [files]
    skipped = 0
    skiplines = ''
    table_name = config['table_name']
    with psycopg2.connect("dbname='{dbname}' user='{user}' host='{host}'".format(**config)) as conn:
        cur = conn.cursor()
        ix = 0 # For indexing the rows
        ct = 0 # For counting the rows inserted
        total = ''
        if debug:
            est = 0 # For estimating the progress
            for file in files:
                with open(file, 'r', encoding='UTF-8') as f:
                    for line in f:
                        est += 1
            total = " / ~{:,}".format(est)
            print("Approx. {:,} log lines will be parsed".format(est))
        if not insert:
            teardown(config, debug=debug)
        setup(config, debug=debug)
        cur.execute("SELECT MAX(index) FROM {}".format(table_name))
        max_index = cur.fetchone()[0]
        max_index = 0 if max_index is None else max_index
        ix = max_index
        parse_line = ''
        for file in files:
            with open(file, 'r', encoding='UTF-8') as f:
                for rawline in f:
                    if rawline.strip().startswith('#'):
                        continue
                    elif rawline.strip().startswith('uri'):
                        continue
                    elif rawline.strip().startswith('org'):
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
                                      total=total,
                                      debug=debug)
                            except ValueError:
                                skipped += 1
                                skiplines += '{}:{}\t{}\n'.format(file, ix, line)
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
                  total=total,
                  debug=debug)
        except Exception:
            skipped += 1
            skiplines += '{}:{}\t{}\n'.format(file, ix, parse_line)
        conn.commit()
        if skipped > 0:
            with open('errors.txt', 'w') as f:
                f.write(skiplines)
        if debug:
            if insert:
                print("Successfully inserted {:,} new rows".format(ct))
            else:
                print("Successfully written {:,} rows".format(ct))
            if skipped > 0:
                print("Skipped {:,} lines and saved output to 'errors.txt'".format(skipped))
        if not insert:
            cur.execute("CREATE INDEX {0}_index ON {0}(index);".format(table_name))
            cur.execute("CREATE INDEX {0}_thread ON {0}(thread);".format(table_name))
            conn.commit()


def print_labels(config=CONFIG):
    table_name = config['table_name']
    with psycopg2.connect("dbname='{dbname}' user='{user}' host='{host}'".format(**config)) as conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT label FROM {} GROUP BY 1".format(table_name))
            r = [row[0] for row in cur.fetchall()]
            conn.commit()
            if r == []:
                print("The table is empty.")
            else:
                print("Existing labels in the table:\n{}\nUse --reset --clear and a label to delete it, or --reset on its own to delete all.".format(r))
        except psycopg2.errors.UndefinedTable:
            print("The table doesn't exist.")
