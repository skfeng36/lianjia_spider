'''

'''

import logging
from logging import handlers
class Log:

    def __init__(self,exe_path,log_level):
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s" 
        DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p" 
        log_fomater=logging.Formatter(LOG_FORMAT,DATE_FORMAT)                    
        
        fp = handlers.TimedRotatingFileHandler(filename=exe_path+'/logs/house_log',when='h',backupCount=0,encoding='utf-8')
        fp.setLevel(log_level)
        fs = logging.StreamHandler()
        fs.setLevel(log_level)
        fp.setFormatter(log_fomater)
        self.log=logging.getLogger('house_log')
        self.log.setLevel(log_level)
        self.log.addHandler(fp)
        self.log.addHandler(fs)

    def loger(self):
        return self.log
    