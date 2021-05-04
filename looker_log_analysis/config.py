import os
from configparser import ConfigParser
CONFIG = ConfigParser()
CONFIG.read(os.path.join('looker_log_analysis', 'config.ini'))
