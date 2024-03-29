import os
import time
import socket
import datetime

LOG_FILE = "click.log"
LAST_SEND_DATETIME = datetime.datetime(1980,1,1)
# Graphite database resolution in seconds
# (smallest interval configured for data timestamps)
GRAPHITE_RESOLUTION = 5
# Go back only 60 seconds in the logs
MINIMUM_TIMESTAMP = int(time.time()) - (int(time.time()) % GRAPHITE_RESOLUTION) - 60

def main():
    data = []
    # Graphite allow for data to be sent for past event
    # so we can safely resend all log data each time
    # we start this program. (Graphite will overwrite
    # the data.)
    last_read_position = 0

    while True:
        filesize = os.stat(LOG_FILE).st_size
        if filesize > last_read_position:
            logfile = open(LOG_FILE, 'r')
            logfile.seek(last_read_position)
            for line in logfile:
               entry_time, color = line.strip().split()
               entry_time = int(entry_time)
               if entry_time > MINIMUM_TIMESTAMP:
                   data.append((entry_time, color))
            last_read_position = logfile.tell()
        data = send_data(data)
        time.sleep(1)

def send_data(data):
    if not data:
        return data

    # example data_by_timestamp structure:
    # {
    #  1365422440: {'blue': 1, 'green': 1, 'red': 1},
    #  1365422445: {'blue': 2, 'green': 1},
    # }
    data_by_timestamp = {}

    for entry_time, color in data:
        modtimestamp = entry_time - (entry_time % GRAPHITE_RESOLUTION)
        data_by_timestamp.setdefault(modtimestamp, {}).\
                          setdefault(color, 0)
        data_by_timestamp[modtimestamp][color] += 1
    
    current_time = int(time.time())
    current_mod_timestamp = current_time - (current_time % GRAPHITE_RESOLUTION)

    for timestamp, colordata in data_by_timestamp.iteritems():
        if timestamp < current_mod_timestamp:
            send_message(colordata, timestamp)

    # Keep only unsent data
    return filter(lambda (timestamp, color): timestamp >= current_mod_timestamp, data)

def send_message(colordata, timestamp):
    # Message format example:
    #  threecolors.red 3 1365435860
    #  threecolors.green 4 1365435860
    #  threecolors.blue 2 1365435860
    graphitelines = ["threecolors.%s %d %d" % (color, count, timestamp) for color, count in colordata.iteritems()]
    data = '\n'.join(graphitelines) + '\n'
    sock = socket.socket()
    sock.connect(("127.0.0.1", 12003)) 
    sock.sendall(data) 
    sock.close()
    print data
    print

if __name__ == '__main__':
    main()

