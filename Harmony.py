__author__ = 'shulih'

import csv
import logging
from  logging.handlers import RotatingFileHandler
import netifaces as ni
from collections import Sequence,defaultdict
#from netifaces import AF_INET, AF_INET6, AF_LINK, AF_PACKET, AF_BRIDGE


CONF_FILE = 'Harmony.conf'
LOGFILE='Harmony.log'
global nodes
nodes=[]


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOGFILE)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
handler = RotatingFileHandler(LOGFILE, maxBytes=20*1024*1024,backupCount=5)
logger.addHandler(handler)

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

def buildLocator(tree):
    locator = defaultdict(list)
    def fillLocator(tree, locator,location):
        for index,item in enumerate(tree):
            if isinstance(item,basestring):
                locator[item].append(location+(index,))
            elif isinstance(item,Sequence):
                fillLocator(item,locator, location+(index,))
    fillLocator(tree,locator,())
    return locator


def CreateINFO(nodeips,nodetype):
    logger.info('Creating INFO File...')
    TMP_INFO=nodetype+'_INFO'
    #INFO=INFO
    replacements={'MGMT_IP':nodeips[0], 'DATA_IP':nodeips[1], 'SERVER_ROLE':nodetype}
    infile = open(TMP_INFO)
    outfile = open('INFO', 'w')
    for line in infile:
        for src, target in replacements.iteritems():
            line = line.replace(src, target)
        outfile.write(line)
    infile.close()
    outfile.close()

def configure():
    LoadListFromConfigurationFile()
    print nodes
#configure()
#d=('192.168.1.1','10.10.10.1')
#CreateINFO(d,'HPI')