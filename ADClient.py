__author__ = 'shulih'
global emsip
emsip = '172.16.21.133'
import socket, sys,re,time,copy
dest = ('<broadcast>', 5000)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.sendto("HPI", dest)
print "Listening for replies; press Ctrl-C to stop."
while 1:
    (buf, address) = s.recvfrom(2048)
    if not len(buf):
        break
    print "Received from %s: %s" % (address, buf)
    alive = re.match('Alive', buf)
    s.sendto("Alive", (emsip,5000))
    if alive:
        while 1:
            print 'sending alive to ems'
            s.sendto("Alive", dest)
            time.sleep(10)


