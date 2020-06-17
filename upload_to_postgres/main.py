#!/anaconda3/bin/python
import modules
import argparse

if __name__ == '__main__':
    # This is a simple CLI interface that allows you to run the script with
    parser = argparse.ArgumentParser(description="""Choose one or more looker logfiles and upload them to the postgres database and table specified in `config.json` with a label to distinguish them from other uploads.""")
    parser.add_argument('--files', '-f', type=str, nargs='+', help='REQUIRED. Add a space separated list of log files.')
    parser.add_argument('--label', '-l', type=str, help='REQUIRED. Choose a label to apply to this upload.')
    parser.add_argument('--silent', '-s', action='store_true', help='Surpress printing progress to the terminal. Default is False')
    parser.add_argument('--new', '-n', action='store_true', help='Including this will create a new table. Default is to insert into an existing table.')
    parser.add_argument('--print', '-p', action='store_false', help='Print the existing labels in the table')
    parser.add_argument('--reset', '-r', action='store_false', help='Clear the existing table')
    parser.add_argument('--clear', '-c', type=str, help='Use with reset to clear a specific label from the table')
    args = parser.parse_args()
    if not args.print:
        modules.print_labels()
    elif not args.reset:
        if args.clear is None:
            ans = input("This will delete the whole table, proceed?\n[y/n]\n")
            if ans.lower() == 'y':
                modules.teardown(debug=not args.silent)
        else:
            ans = input("This will delete the label '{}' from table, proceed?\n[y/n]\n".format(args.clear))
            if ans.lower() == 'y':
                modules.teardown(label=args.clear, debug=not args.silent)
    else:
        if args.clear is not None:
            parser.error("--clear must be used with the --reset argument")
        elif (args.files is None or args.label is None):
            parser.error("--files and --label are required")
        else:
            if args.new:
                ans = input("The --new argument will wipe the existing table and make a new one, proceed?\n[y/n]\n")
                if ans.lower() == 'y':
                    modules.parse_files(files=args.files,
                                        label=args.label,
                                        insert=not args.new,
                                        debug=not args.silent)
            else:
                modules.parse_files(files=args.files,
                                    label=args.label,
                                    insert=not args.new,
                                    debug=not args.silent)
