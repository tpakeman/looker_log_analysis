from looker_log_analysis import log
from datetime import datetime as dt
import logging, os
test_handler = logging.FileHandler(os.path.join(log.LOGDIR, f'test-output-{dt.now():%Y-%m-%d}.log'))
log.LOG.handlers = [test_handler]
