import urllib.request
import serial

ser = serial.Serial('/dev/ttyACM0',9600)
ser.baudrate = 9600

id1State = "fr"
id2State = "fr"
id1OldState = "fr"
id2OldState = "fr"

histo = {"65536" : 0} 

while True:
  serialStr = ser.readline().decode("utf-8")
  paramList = serialStr.split(",")
  while len(paramList) < 2:
    serialStr = ser.readline().decode("utf-8")
    paramList = serialStr.split(",")
    print(paramList)

  print(paramList)
  pos = paramList[0]
  distStr = paramList[1]

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


