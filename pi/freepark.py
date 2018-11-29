#!/usr/bin/env python3

# Freepark - Application that checks status of wireless 
# parking spot sensors communicating over 433 MHz.
# Sensors are based on Arduino boards with US distance meters.
# Status is sent to cloud service at http://www.virvetech.se/freepark
# 
# Git repo: https://github.com/ftjerneld/freepark.git
import urllib.request
import signal
import sys
import time
import logging

from rpi_rf import RFDevice

rfdevice = None
rxGpioPin = 27
noOfParkSpots = 2

parkSpot = ["free" for x in range(noOfParkSpots+1)]
parkSpotOld = ["free" for x in range(noOfParkSpots+1)]

histo = {"999" : 0} 
rxData = 0
pos = 0
dist = 999

def exithandler(signal, frame):
    rfdevice.cleanup()
    sys.exit(0)

# Show distance statistics, same counter for all spots
def showHisto():
    if rxData > 1000 and rxProto == 1:
      if str(dist) in histo:
        histo[str(dist)] = histo[str(dist)] + 1
      else:
        histo[str(dist)] = 1
      for x,y in histo.items():
        print(x,y)

# Simple filter to find valid RF frames
def validRxFrame():
    return (pos != 0 and rxData > 999 and rxData < 3000 and rxProto == 1)

# Check if parking spot status has changed
def parkingStatusChanged(pos,dist):
    if dist < 10:
      parkSpot[pos] = "occupied"
      #print("Pos " + str(pos) + " occupied")
    else:
      parkSpot[pos] = "free"
      #print("Pos " + str(pos) + " free")
    if parkSpot[pos] != parkSpotOld[pos]:
      print("Pos " + str(pos) + " " + parkSpot[pos])
      parkSpotOld[pos] = parkSpot[pos]
      return True
    else:
      return False

# Initialize logger
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s', )

signal.signal(signal.SIGINT, exithandler)

# Set up rf device on GPIO
rfdevice = RFDevice(rxGpioPin)
rfdevice.enable_rx()
timestamp = None
logging.info("Listening for codes on GPIO " + str(rxGpioPin))

while True:
  # Read value from RF receiver
  if rfdevice.rx_code_timestamp != timestamp:
    timestamp = rfdevice.rx_code_timestamp
    rxData = rfdevice.rx_code
    rxProto = rfdevice.rx_proto
    rxPulseLength = rfdevice.rx_pulselength
    logging.info(str(rxData) + ", " + str(rxPulseLength) + ", " + str(rxProto))

    # Position x 1000 is embedded in rx value
    pos = rxData // 1000

    # Distance is remainder after dividing rx value by 1000
    dist = rxData % 1000

  if validRxFrame():
    if parkingStatusChanged(pos,dist):
      f = urllib.request.urlopen("http://www.virvetech.se/freepark/parksim_sse.php?id1State="+parkSpot[1][0:2]+"&id2State="+parkSpot[2][0:2])
      #f = urllib.request.urlopen("http://www.virvetech.se/freepark/parksim_sse.php?id"+str(pos)+"State="+parkSpot[pos])
      print("state changed")
    #showHisto()

  time.sleep(0.01)
rfdevice.cleanup()


