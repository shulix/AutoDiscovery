__author__ = 'shulih'
global emsip
emsip = '172.16.21.133'
import socket
import sys
import re
import time
import logging
from  logging.handlers import RotatingFileHandler


LOGFILE='ADClient.log'
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOGFILE)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
handler = RotatingFileHandler(LOGFILE, maxBytes=20*1024*1024,backupCount=5)
logger.addHandler(handler)
dest = ('<broadcast>', 5000)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.sendto("HPI", dest)
logger.info("Listening for replies; press Ctrl-C to stop.")
while 1:
    (buf, address) = s.recvfrom(2048)
    if not len(buf):
        break
    out =  'Received from: ' + address[0] + ' : '+  buf
    logger.info(out)
    alive = re.match('Alive', buf)
    s.sendto("Alive", (emsip,5000))
    if alive:
        while 1:
            logger.info('sending alive to ems')
            s.sendto("Alive", dest)
            time.sleep(10)


