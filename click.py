#!/usr/bin/python

# This Python CGI script will write the color into a log file
# The log data will be agregated in a separate program and be sent to graphite

import os
import sys
import time
import fcntl
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

# Only allow red, green or blue
if color not in ('red', 'green', 'blue'):
  print "Only 'red', 'green', or 'blue' are allowed."
  sys.exit(1)

# Write the color to the log
log = open("click.log", "a")
fcntl.lockf(log, fcntl.LOCK_EX)
log.write("%d %s\n" % (int(time.time()), color))
log.close()

print """<html>
<body style="background-color: %s;">
</body>
</html>""" % color
