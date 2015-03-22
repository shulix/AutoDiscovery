#!/bin/python
__author__ = 'shulih'
import sys
import socket
import traceback
import time
import Harmony
import datetime
import csv
import re
import errno
import logging
from  logging.handlers import RotatingFileHandler
from collections import Sequence,defaultdict

CONF_FILE = 'Harmony.conf'
open(CONF_FILE, 'a').close()
LOGFILE = 'ADServer.log'
PORT=59595
global nodes
nodes=[]
heart_beat_timeout = 180
my_ip= ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1])
# Create log file with rotation every 20MB

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
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(('', PORT))

# create configuration file 

def ConfigureNode():
    out ='Running Harmony configurator'
    logger.info(out)


def sendMyIPToNode(node,emsip):
    out= 'Send EMS IP to:' + node
    logger.info(out)
    emsRegMsg='emsIP,'.join(emsip)
    s.sendto(emsRegMsg,(node,PORT))

def RemoveNode():
    logger.info('Cleaning Server list....')
    for node in nodes[:]:
        if int(node[2]) < int(time.time()- heart_beat_timeout):
            m, s = divmod(int(time.time()) - int(node[2]), 60)
            h, m = divmod(m, 60)
            d, h = divmod(h,24)
            out = 'Last Heart beat from ' + node[0] +' was ' + str(d) + ' days ' + str(h) + ' hours ' + str(m) + ' minutes and ' + str(s) + ' seconds ago'
            logger.info(out)
            out='Removing ' + node[0] + ' from ' + node[1]  + ' pool'
            logger.info(out)
            nodes.remove(node)

def EpochToHumenTime(value):
    v = datetime.datetime.fromtimestamp(value)
    return (v.strftime('%Y-%m-%d %H:%M:%S'))

def WriteToConfigurationFile(nodeList):
    with open(CONF_FILE, "w") as f:
        writer = csv.writer(f)
        writer.writerows(nodeList)

def AddToConfigurationFile(nodeList):
    with open(CONF_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerows('')
        writer.writerows(nodeList)

def ReadConf():
    with open(CONF_FILE, 'rU') as f:
        reader = csv.reader(f)
    print reader

def LoadListFromConfigurationFile():
    logger.info('Loading previous configuration...')
    with open(CONF_FILE, 'rU') as f:
        reader = csv.reader(f)
        nodesfromconfigfile = list(reader)
    for node in nodesfromconfigfile:
        try:
            nodes.append([node[0],node[1],node[2]])
            out = 'Node ' + node[0] + ' added to ' + node[1] +' pool'
            logger.info(out)
        except IndexError:
            logger.error('Node index out of range')


def registerNode(address,message):
    t=time.time()
    if not nodes:
        nodes.append([address[0],message,int(t)])
        out = 'Adding new ' + message + ' with IP ' + address[0] + ' and setting heart beat timer to:' + EpochToHumenTime(t)
        logger.info(out)
        #SendConfigureToNode(address)
        IsAlive(address,'EMS')
        AddToConfigurationFile([[address[0],message,int(t)]])
    if address[0] in zip(*nodes)[0]:
         out = 'Node with IP ' + address[0] + ' is already in the pool , resetting its heart beat timer to: ' + EpochToHumenTime(t)
         logger.info(out)
         locator = Harmony.buildLocator(nodes)
         loc=(locator[address[0]])
         nodes[loc[0][0]][2]=int(t)
    elif address[0] not in zip(*nodes)[0]:
        out = 'Adding new ' + message + ' with IP ' + address[0] + ' and setting heart beat timer to:' + EpochToHumenTime(t)
        logger.info(out)
        #SendConfigureToNode(address)
        IsAlive(address,'EMS')
        AddToConfigurationFile([[address[0],message,int(t)]])

def IsAlive(address,message):
    result = re.match('Alive', message)
    if result:
        out = 'Got Alive From: ' + address[0]
        logger.info(out)
        s.sendto('EMS',address)
        out = 'Sending Alive To: ' + address[0]
        logger.info(out)


Harmony.LoadListFromConfigurationFile()
RemoveNode()

logger.info("Listening for broadcasts...")
while 1:
    try:
        message, address = s.recvfrom(8192)
        result = re.match('Alive', message)
        ems = re.match('EMS', message)
        if result:
            out = 'Got Alive from: ' +  address[0]
            logger.info(out)
            registerNode(address,message)
            s.sendto('EMS',address)
        elif ems:
            print 'got ems from ems'
            pass
        else:
            out = 'Got message from ' + address[0] + ' requesting role ' + message
            logger.info(out)
            registerNode(address,message)
            s.sendto('EMS',address)
        RemoveNode()
        WriteToConfigurationFile(nodes)
        IsAlive(address,message)
        ConfigureNode()
        logger.info('Listening for broadcasts...')
        print''
        sys.stdout.flush()
    except socket.error as error:
        if error.errno == errno.WSAECONNRESET:
            out='Lost connection to: ' + address[0]
            logger.debug(out)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
     traceback.print_exc()
