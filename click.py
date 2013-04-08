#!/usr/bin/python

# This Python CGI script will write the color into a log file
# The log data will be agregated in a separate program and be sent to graphite

import os
import time
import socket
import urlparse

#import cgitb
#cgitb.enable()

print "Content-Type: text/html"
# end of headers
print

# Obtain the 'color' parameter from the URL
query = urlparse.parse_qs(os.environ['QUERY_STRING'])
color = query['color'][0]

sock = socket.socket()
sock.connect(("127.0.0.1", 12003))

now = int(time.time())
sock.sendall("threecolors.%s 1 %d\n" % (color, now))
sock.close()

print "%s it is!" % color
