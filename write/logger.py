import logging as log
import platform as pf
import os

# start_oic_logger will start the logging process by declaring the logger and
# filename. This should be called once.
def start_oic_logger():
    filename_log = 'oic_log.log'
    if pf.platform().startswith('Windows'):
        logfilename = os.path.join(os.getenv('HOMEDRIVE'), os.getenv('HOMEPATH'), filename_log)
    else:
        logfilename = os.path.join(os.getenv('HOME'), filename_log)
    log.basicConfig(
        level=log.DEBUG,
        format="%(asctime)s : %(levelname)s : %(filename)s[%(lineno)d] : %(message)s",
        filename=logfilename,
        filemode='w',
    )
    print("Log File:", logfilename)
    log.info('Logging Started...')
