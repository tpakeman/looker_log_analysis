import logging
import os
from datetime import datetime as dt
from config import CONFIG
LOG = logging.getLogger(CONFIG['App']['log_name'])
LOGDIR = CONFIG['App']['log_directory']
if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR)

def log(level, text):
    if level.lower() not in ('debug', 'info', 'warn', 'error', 'fatal'):
        raise ValueError('Log level must be one of debug, info, warn, error, fatal')
    levels = {'debug': LOG.debug, 'info': LOG.info, 'warn': LOG.warn, 'error': LOG.error, 'fatal': LOG.fatal}
    logstring = f"{dt.now():%c}\t{text}"
    levels[level.lower()](logstring)

logging.basicConfig(filename=os.path.join('log', f'looker-log-parsing-{dt.now():%Y-%m-%d}.log'), level=logging.INFO)
