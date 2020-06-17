from os.path import getmtime
# QUERY SUMMARIES


def parse_query_summary_from_logs(files, log_pattern=None, debug=False):
    """Parse looker logs and return a dictionary of query_summaries.

    Input a logfile or array of logfiles and this parses
    the query performance and returns a dictionary optimised for analysis
    in pandas.

    ---------------------------------------------------------------------------
    INPUT
    ---------------------------------------------------------------------------
    files -> str or list:       A filename or a list of filenames to parse for
                                query summaries. This should be absolute paths
                                for the most reliable behaviour. A single file
                                is allowed but a list is preferred.

    log_pattern -> (raw) str:   Default is None
                                Pass in a filename pattern to only include matches
                                the search. Will be compiled in regex so should
                                be a raw string of the format r"some_pattern"

    ---------------------------------------------------------------------------
    OUTPUT
    ---------------------------------------------------------------------------
    query_dict -> dict:         A python dict optimised for analysis in pandas.
                                The format is: {ix: {k: v, k: v}, ix: {k: v...}}
    """
    query_dict = {}
    if not isinstance(files, list):
        files = [files]
    if log_pattern:
        import re
        log_pattern = re.compile(log_pattern)
        files = [f for f in files if re.match(log_pattern, f) is not None]
    files.sort(key=lambda x: getmtime(x))
    for file in files:
        try:
            with open(file, 'r', encoding='UTF-8') as f:
                if debug:
                    print("Successfully parsed {}".format(file))
                for line in f:
                    if '|query_summary] :: event' in line:
                        info, q_data = line.split(' :: ')
                        ts, meta = info.split(' [')
                        log_level, process_id, _ = meta[:-1].split('|')
                        q_data = {d.strip().split(':')[0].strip(): d.strip().split(':')[1].strip()
                                  for d in q_data.split(';') if d.strip() != ''}
                        q_data['process_id'] = process_id
                        q_data['filename'] = file
                        query_dict[ts] = q_data
        except UnicodeDecodeError as e:
            if debug:
                print("Skipped {} due to encoding error".format(file))
            continue
    return query_dict


def query_summary_to_csv(in_data, outfile, debug=False):
    """Saves the query data to a csv file specified by outfile.
    Note: the json data is optimised for analysis in pandas
    with an index column which is why this may look unusual."""
    import csv
    fieldnames = list(set([k for v in in_data.values() for k in v.keys()]))
    fieldnames.reverse()
    fieldnames.append('index')
    fieldnames.reverse()
    with open(outfile, 'w') as f:
        csvwriter = csv.DictWriter(f, fieldnames)
        csvwriter.writeheader()
        for k, v in in_data.items():
            csvwriter.writerow({'index': k, **v})
    if debug:
        print("-" * 40)
        print("Successfully written data to {}".format(outfile))


def query_summary_to_json(in_data, outfile, debug=False):
    """Saves the query data to a json file specified by outfile"""
    import json
    with open(outfile, 'w') as f:
        f.write(json.dumps(in_data))
    if debug:
        print("-" * 40)
        print("Successfully written data to {}".format(outfile))


# Helper function
def logs_to_csv(in_directory, out_file, log_pattern=None, debug=False):
    """Pass a directory containing looker logs, a csv file to write to and a
    pattern to match logfiles against."""
    import os
    out_dir = os.path.dirname(out_file)
    if not os.path.exists(out_dir):
        if debug:
            "{} not found. Creating.".format(out_dir)
        os.makedirs(out_dir)
    files = [os.path.join(in_directory, f) for f in os.listdir(in_directory)]
    log_data = parse_query_summary_from_logs(files, log_pattern, debug)
    query_summary_to_csv(log_data, out_file, debug)


# Helper function
def logs_to_json(in_directory, out_file, log_pattern=None, debug=False):
    """Pass a directory containing looker logs, a csv file to write to and a
    pattern to match logfiles against."""
    import os
    out_dir = os.path.dirname(out_file)
    if not os.path.exists(out_dir):
        if debug:
            "{} not found. Creating.".format(out_dir)
        os.makedirs(out_dir)
    files = [os.path.join(in_directory, f) for f in os.listdir(in_directory)]
    log_data = parse_query_summary_from_logs(files, log_pattern, debug)
    query_summary_to_json(log_data, out_file, debug)


# Split out the logs more fully
    # This is a much larger set of lines to read so regex is too slow
def parse_full_logs(files,
                    log_pattern=None,
                    debug=False):
    ct = 0
    log_dict = {}
    sources, threads = [], []
    if not isinstance(files, list):
        files = [files]
    files.sort(key=lambda x: getmtime(x))
    for file in files:
        try:
            with open(file, 'r', encoding='UTF-8') as f:
                if debug:
                    print("Successfully parsed {}".format(file))
                for line in f:
                    try:
                        ct += 1
                        if log_pattern is None:
                            info, query = line.split(' :: ')
                            ts, meta = info.split(' [')
                            log_level, process_id, source = meta[:-1].split('|')
                            log_dict[ts] = {"rownum": ct, "log_level": log_level, 'source': source, 'process_id': process_id, 'query': query, 'filename': file}
                            sources.append(source)
                            threads.append(process_id)
                        elif log_pattern in line:
                            info, query = line.split(' :: ')
                            ts, meta = info.split(' [')
                            log_level, process_id, source = meta[:-1].split('|')
                            log_dict[ts] = {"rownum": ct, "log_level": log_level, 'source': source, 'process_id': process_id, 'query': query, 'filename': file}
                            sources.append(source)
                            threads.append(process_id)
                    except (IndexError, ValueError) as e:
                        continue
        except UnicodeDecodeError as e:
            if debug:
                print("Skipped {} due to encoding error".format(file))
            continue
    return log_dict, {'sources': list(set(sources)), 'threads': list(set(threads))}


def parse_logs_for_specific_lines(logfiles,
                                  linetarget,
                                  lineoffset=50,
                                  type='preceding'):
    """Run through the logfiles and return those at a specific offset before
    or after a specific line."""
    pass


# Helper function
def full_logs_to_json(in_directory,
                      out_file=None,
                      log_pattern=None,
                      outtype='save',
                      debug=False):
    """Pass a directory containing looker logs, a csv file to write to and a
    pattern to match logfiles against."""
    import os
    if out_file is not None:
        out_dir = os.path.dirname(out_file)
        if not os.path.exists(out_dir):
            if debug:
                "{} not found. Creating.".format(out_dir)
            os.makedirs(out_dir)
    files = [os.path.join(in_directory, f) for f in os.listdir(in_directory)]
    log_data, info = parse_full_logs(files, log_pattern, debug)
    if outtype == 'save':
        query_summary_to_json(log_data, out_file, debug)
        return info
    elif outtype == 'return':
        return log_data, info
    else:
        raise ValueError("Please specify outtype 'save' or 'return'")


def parse_data_for_item(data, value, key='thread'):
    """ TO DO - make this multi-purpose"""
    return {k: v for k, v in data.items() if v[key] == value}
