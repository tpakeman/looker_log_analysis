import os
import modules
import argparse

if __name__ == '__main__':
    # This is a simple CLI interface that allows you to run the script with
    parser = argparse.ArgumentParser(description='Input files, label, insert mode and debug mode')
    parser.add_argument('--files', '-f', type=str, nargs='+', default='~/Downloads/looker.log', help='Add a space separated list of log files. Default is ~/Downloads/looker.log')
    parser.add_argument('--label', '-l', type=str, default='test', help='Choose a label to apply to this upload. Default is "test"')
    parser.add_argument('--debug', '-d', action='store_true', help='Print progress to the terminal. Default is False')
    parser.add_argument('--insert', '-i', action='store_true', help='True will insert into an existing table. False will create a new table. Default is False')
    args = parser.parse_args()
    modules.parse_files(files=args.files,
                        label=args.label,
                        insert=args.insert,
                        debug=args.debug)
