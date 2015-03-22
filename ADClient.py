__author__ = 'shulih'
import socket
import sys
import re
import time
import logging
import Harmony

from  logging.handlers import RotatingFileHandler
myips=['10.10.10.1','192.168.1.1']
MyRole='HPI'
PORT=59595
dest = ('<broadcast>', PORT)
global emsip
emsip = '172.16.21.133'
# Create log file with rotation every 20MB
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

# create broadcast UDP socket and bind to all address on port 59595

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.sendto("HPI", dest)
logger.info("Listening for replies; press Ctrl-C to stop.")
Harmony.CreateINFO(myips,MyRole)
while 1:
    (buf, address) = s.recvfrom(2048)
    if not len(buf):
        break
    out =  'Received from: ' + address[0] + ' : '+  buf
    logger.info(out)
    alive = re.match('EMS', buf)
    config = re.match('configure', buf)
    s.sendto("Alive", (emsip,PORT))
    if config:
        print 'configuring myself as ' + buf
    if alive:
            logger.info('sending alive to ems')
            s.sendto("HPI", dest)
            time.sleep(6)


