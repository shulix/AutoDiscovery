__author__ = 'shulih'
import socket, traceback, time, struct, datetime,csv
from collections import Sequence,defaultdict

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(('', 5000))

open('confFile.txt', 'a').close()
global leases
leases=[]

def release(Node): #release a lease after time limit has expired
    def DeleteFromList():
        locator = buildLocator(leases)
        loc=(locator[Node])
        CheckAlive(loc)
        if Node == loc:
            print 'deleting ',loc
    #def DeleteFromFile():
    #with open("confFile.txt", "rU") as f:
     #   reader = csv.reader(f)
     #   for line in reader:
      #      try:
       #         if addr in zip(*line[0]):
        #            print addr,'is',line[0]
         #       else:
          #          print 'not in line'
           # except IndexError:
            #    print''
            #else:
            #    if addr in zip(*line[0]):
            #        print addr,'is',line[0]
            #    else:
            #        print 'not in line'

    #f.close()

    #with open("confFile.txt", "wb") as f:
        #writer = csv.writer(f)
        #writer.writerows(line)
    #f.close()


def configure(addr):
    print 'sending data to ', addr
    print '----------------------------------------------------------------------------'
    s.sendto("Go ahead and configure yourself", addr)

def CheckAlive():
    print 'Cleaning Server list....'
    print '----------------------------------------------------------------------------'
    for Node in leases:
        locator = buildLocator(leases)
        location=(locator[Node[0]])
        for loc in location:
            print 'checking',Node[0]
            LastHBGap=int(time.time()) - int(leases[loc[0]][2])
            if LastHBGap>60:
                print 'Last Heart beat from',Node[0],'was',LastHBGap,'seconds ago'
                print 'deleting',Node[0]
                del leases[loc[0]]



def humenTime(value):
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
    print 'Loading previous configuration...'
    with open('confFile.txt', 'rU') as f:
        reader = csv.reader(f)
        Savedleases = list(reader)
    for lease in Savedleases:
        try:
            leases.append([lease[0],lease[1],lease[2]])
            print 'Node',lease[0],'loaded as',lease[1]
        except IndexError:
            pass

        #WriteConf(lease)

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


LoadConf()

print "Listening for broadcasts..."
#leases.append(['1.1.1.1','HPI',int(time.time())])
while 1:
    try:
        message, address = s.recvfrom(8192)
        print '----------------------------------------------------------------------------'
        print "Got message from %s: %s" % (address, message)
        if not leases:
            t=time.time()
            print 'leases',leases
            leases.append([address[0],message,int(t)])
            print '----------------------------------------------------------------------------'
            print 'Adding new',message,'with IP',address[0],'and setting timer to:',humenTime(t)
            print '----------------------------------------------------------------------------'
            configure(address)
            AddToConf([[address[0],message,int(t)]])
        if address[0] in zip(*leases)[0]:
            t=time.time()
            print '----------------------------------------------------------------------------'
            print 'node ',address[0],' already in list reseting timer to: ',humenTime(t)
            print '----------------------------------------------------------------------------'
            locator = buildLocator(leases)
            loc=(locator[address[0]])
            leases[loc[0][0]][2]=int(t)
            #sendalive(address)
        elif address[0] not in zip(*leases)[0]:
            t=time.time()
            print '----------------------------------------------------------------------------'
            leases.append([address[0],message,int(t)])
            print 'adding new',message,'with IP',address[0],'and setting timer to:',humenTime(t)
            print '----------------------------------------------------------------------------'
            configure(address)
            AddToConf([[address[0],message,int(t)]])
        print leases
        print''
        CheckAlive()
        print leases
        print "Listening for broadcasts..."
        print''
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        traceback.print_exc()
