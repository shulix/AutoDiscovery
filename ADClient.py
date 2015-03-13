__author__ = 'shulih'

import socket, sys, time
dest = ('<broadcast>', 5000)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#s.bind(('', 5000))
s.sendto("HPI", dest)
print "Listening for replies; press Ctrl-C to stop."
while 1:
    (buf, address) = s.recvfrom(2048)
    if not len(buf):
        break
    print "Received from %s: %s" % (address, buf)
    time.sleep(2)
    s.sendto("HPI", dest)