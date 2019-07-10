#!/anaconda3/bin/python
import modules
import argparse

if __name__ == '__main__':
    # This is a simple CLI interface that allows you to run the script with
    parser = argparse.ArgumentParser(description="""Choose one or more looker logfiles and upload them to the postgres database and table specified in `config.json` with a label to distinguish them from other uploads.""")
    parser.add_argument('--reset', '-r', action='store_true', help='Clear the existing table')
    parser.add_argument('--clear', '-c', type=str, help='Use with reset to clear a specific label from the table')

    parser.add_argument('--files', '-f', type=str, nargs='+', help='Add a space separated list of log files.')
    parser.add_argument('--label', '-l', type=str, help='Choose a label to apply to this upload.')
    parser.add_argument('--silent', '-s', action='store_true', help='Surpress printing progress to the terminal. Default is False')
    parser.add_argument('--new', '-n', action='store_true', help='True will create a new table. False will insert into an existing table. Default is False')
    args = parser.parse_args()
    if args.reset:
        if args.clear is None:
            modules.teardown()
        else:
            modules.teardown(label=args.clear)
    else:
        if args.clear is not None:
            parser.error("--clear must be used with the --reset argument")
        elif (args.files is None or args.label is None):
            parser.error("--files and --label are required")
        else:
            modules.parse_files(files=args.files,
                                label=args.label,
                                insert=not args.new,
                                debug=not args.silent)
