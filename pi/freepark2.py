#!/usr/bin/env python3

import urllib.request
import argparse
import signal
import sys
import time
import logging

from rpi_rf import RFDevice

rfdevice = None

id1State = "fr"
id2State = "fr"
id1OldState = "fr"
id2OldState = "fr"

histo = {"999" : 0} 

def exithandler(signal, frame):
    rfdevice.cleanup()
    sys.exit(0)

logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s', )

parser = argparse.ArgumentParser(description='Receives a decimal code via a 433/315MHz GPIO device')
parser.add_argument('-g', dest='gpio', type=int, default=27,
                    help="GPIO pin (Default: 27)")
args = parser.parse_args()

signal.signal(signal.SIGINT, exithandler)
rfdevice = RFDevice(args.gpio)
rfdevice.enable_rx()
timestamp = None
logging.info("Listening for codes on GPIO " + str(args.gpio))

while True:
  if rfdevice.rx_code_timestamp != timestamp:
    timestamp = rfdevice.rx_code_timestamp
    logging.info(str(rfdevice.rx_code) +
        " [pulselength " + str(rfdevice.rx_pulselength) +
        ", protocol " + str(rfdevice.rx_proto) + "]")
    pos = rfdevice.rx_code / 1000
    dist = rfdevice.rx_code & 1000

  if pos != "0":
    dist = int(distStr)
    if dist < 400:
      if pos == "1":
        if dist < 10:
          id1State = "oc"
          print("Pos 1 occupied")
        else:
          id1State = "fr"
          print("Pos 1 free")
      else:
        if dist < 10:
          id2State = "oc"
          print("Pos 2 occupied")
        else:
          id2State = "fr"
          print("Pos 2  free")
      if id1OldState != id1State or id2OldState != id2State:
        f = urllib.request.urlopen("http://www.virvetech.se/freepark/parksim_sse.php?id1State="+id1State+"&id2State="+id2State)
        print("state changed")
      id1OldState = id1State
      id2OldState = id2State  
    if str(dist) in histo:
      histo[str(dist)] = histo[str(dist)] + 1
    else:
      histo[str(dist)] = 1
    for x,y in histo.items():
      print(x,y)
  else:
    print(serialStr)
  time.sleep(0.01)
  rfdevice.cleanup()


