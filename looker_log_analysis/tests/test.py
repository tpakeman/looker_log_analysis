import modules
from os import path

if __name__ == '__main__':
    # Path to a local looker instance logfile
    # This can also be a list of logfiles
    logfile = path.join(path.expanduser('~'), 'looker', 'log', 'looker.log')
    modules.parse_files(files=logfile,
                        label='test_upload', # Something descriptive
                        insert=True)         # Use the existing table