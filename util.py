import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

def getTimeStamp(params_time) :
    
    logger.info(' == Before getTimeStamp : stime- {}, etime- {} '.format(params_time['stime'], params_time['etime']))

    stimestamp = time.mktime(datetime.strptime(params_time['stime'], '%Y-%m-%d').timetuple())
    etimestamp = time.mktime(datetime.strptime(params_time['etime'], '%Y-%m-%d').timetuple())

    if etimestamp <= stimestamp :
        return -1
    else :
        params_time['stime'] = round(stimestamp)*1000
        params_time['etime'] = round(etimestamp)*1000
        logger.info(' == After getTimeStamp : stime- {}, etime- {} '.format(params_time['stime'], params_time['etime']))
        return 0

        