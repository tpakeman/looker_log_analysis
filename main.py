import modules
import os

if __name__ == '__main__':
    FILES = os.path.join(os.path.expanduser('~'), 'looker', 'log', 'looker.log')
    modules.parse_files(FILES, label='checkout', insert=True, debug=True)