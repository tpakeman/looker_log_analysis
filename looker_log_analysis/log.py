import logging
import os, sys
from datetime import datetime as dt
from config import CONFIG
LOG = logging.getLogger(CONFIG['App']['log_name'])
LOGDIR = CONFIG['App']['log_directory']
if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR)

file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
stdout_format = logging.Formatter('%(levelname)s: %(message)s')

logging.basicConfig(filename=os.path.join('log', f'looker-log-parsing-{dt.now():%Y-%m-%d}.log'),
                    level=logging.INFO,
                    format=file_format)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(stdout_format)
LOG.addHandler(stdout_handler)
