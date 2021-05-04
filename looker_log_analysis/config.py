import os
from configparser import ConfigParser

def config(file_path=os.path.join('looker_log_analysis', 'config.ini')):
    conf = ConfigParser()
    conf.read(file_path)
    return conf
