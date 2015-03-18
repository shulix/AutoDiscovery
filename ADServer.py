__author__ = 'shulih'
import socket
import traceback
import time
import struct
import datetime
import csv
import re
import errno
from collections import Sequence,defaultdict

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(('', 5000))

open('confFile.txt', 'a').close()
open('ADServer.log', 'a').close()
global leases
leases=[]

def printNlog(logging):
    pdate=ToHumenTime(time.time())+' : '
    print pdate+logging
    f = open('ADServer.log','a')
    f.write(pdate)
    f.write(logging)
    f.write('\n')
    #f.close()


def configure(addr):
    print 'sending configuration to: ', addr
    s.sendto("Go ahead and configure yourself",addr)

def sendMyIPToNode(node,emsip):
    out= 'Send EMS IP to:' + node
    printNlog(out)
    emsRegMsg='emsIP,'.join(emsip)
    s.sendto(emsRegMsg,(node,5000))

def RemoveNode():
    printNlog('Cleaning Server list....')
    for l in leases[:]:
        if int(l[2]) < int(time.time()-60):
            m, s = divmod(int(time.time()) - int(l[2]), 60)
            h, m = divmod(m, 60)
            print 'Last Heart beat from',l[0],'was',"%d Hours %02d Minutes and %02d Seconds" % (h, m, s),'ago'
            out='Removing ' + l[0] + ' from ' + l[1]  + ' pool'
            printNlog(out)
            leases.remove(l)

def ToHumenTime(value):
    v = datetime.datetime.fromtimestamp(value)
    return (v.strftime('%Y-%m-%d %H:%M:%S'))

def WriteConf(nodeList):
    with open("confFile.txt", "w") as f:
        writer = csv.writer(f)
        writer.writerows(nodeList)

def AddToConf(nodeList):
    with open("confFile.txt", "a") as f:
        writer = csv.writer(f)
        writer.writerows('')
        writer.writerows(nodeList)

def ReadConf():
    with open('confFile.txt', 'rU') as f:
        reader = csv.reader(f)
    print reader

def LoadConf():
    printNlog('Loading previous configuration...')
    with open('confFile.txt', 'rU') as f:
        reader = csv.reader(f)
        Savedleases = list(reader)
    for lease in Savedleases:
        try:
            leases.append([lease[0],lease[1],lease[2]])
            print 'Node',lease[0],'added to',lease[1],'pool'
        except IndexError:
            pass

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

def registerNode(address,message):
    t=time.time()
    if not leases:
        leases.append([address[0],message,int(t)])
        out = 'Adding new ' + message + ' with IP ' + address[0] + ' and setting heart beat timer to:' + ToHumenTime(t)
        printNlog(out)
        configure(address)
        AddToConf([[address[0],message,int(t)]])
    if address[0] in zip(*leases)[0]:
         out = 'Node with IP ' + address[0] + ' is already in the pool , resetting its heart beat timer to: ' + ToHumenTime(t)
         printNlog(out)
         locator = buildLocator(leases)
         loc=(locator[address[0]])
         leases[loc[0][0]][2]=int(t)
    elif address[0] not in zip(*leases)[0]:
        out = 'Adding new ' + message + ' with IP ' + address[0] + ' and setting heart beat timer to:' + ToHumenTime(t)
        printNlog(out)
        configure(address)
        AddToConf([[address[0],message,int(t)]])

def IsAlive(address,message):
    result = re.match('Alive', message)
    if result:
        print 'Got Alive from ',address[0]


LoadConf()
printNlog("Listening for broadcasts...")

while 1:
    try:
       # Myip= ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1])
        message, address = s.recvfrom(8192)
        result = re.match('Alive', message)
        if result:
            print 'got alive from', address
            registerNode(address,message)
            s.sendto('Alive',address)
        else:
            out = 'Got message from ' + address[0] + ' requesting role ' + message
            printNlog(out)
            registerNode(address,message)
            s.sendto('Alive',address)
        RemoveNode()
        WriteConf(leases)
        time.sleep(5)
        print "Listening for broadcasts..."
        print''
        s.sendto('Alive',address)
    except socket.error as error:
        if error.errno == errno.WSAECONNRESET:
            pass
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
     traceback.print_exc()
