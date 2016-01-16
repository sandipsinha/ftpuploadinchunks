__author__ = 'ssinha'

from conman  import load_config, ConfigLoadError
import sys
from os.path import dirname, join

CONF_DIR =  '/Users/ssinha/pythonplay/oracletest/file_upload/fileupload/conf/oracle.cloud.conf' 
#CONF_DIR =  join( dirname( dirname( __file__ ) ), 'conf' ) 
try:
    config = load_config(  CONF_DIR )
except ConfigLoadError  as e:
    print 'No config file found, exiting', e
    sys.exit(1)
