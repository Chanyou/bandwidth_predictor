#Throughput composer
#
#Mobility --> Throughput
#

import sys
import thread, random, re

movDataLoc = ""
# Time APID
throughputHistoryLoc = ""
# Time APID Throughput

outputFileLoc = ""
throughputLimit = 1024*1024*1024
#1GBps

class ThroughputHistory:
    timestamp = 0
    APID = ""
    throughput = 0
    def __init__(self, time, ap, th):
        self.timestamp = time
        self.APID = ap
        self.throughput = th
  
        
        
class MobilityHistory:
    timestamp = 0
    APID= ""
    def __init__(self, time, ap):
        self.timestamp = time
        self.APID = ap
    
movDataList = []
thruData = {}
def composeFile():
    global movDataLoc, throughputHistoryLoc, movDataList, outputFileLoc, f;
    if len(sys.argv) < 3 :
        print '<output location> <movement data> <throughput history data>'
        exit(-1)
    outputFileLoc = sys.argv[1]
    movDataLoc = sys.argv[2]
    throughputHistoryLoc = sys.argv[3]
    
    movData = open(movDataLoc)
    tData = open(throughputHistoryLoc)
    #read Mobility data
    while True:
        line = movData.readline()
        if not line:
            break
        print line
        elems = line.split()
        #time APID
        timestamp = int(elems[0])
        APID = elems[1]
        movDataList.append(MobilityHistory(timestamp, APID))
    #read Throughput data
    while True:
        line = tData.readline()
        if not line:
            break
        print line
        elems = line.split()
        #time APID Throughput
        timestamp = int(elems[0])
        APID = elems[1]
        thru = int(elems[2])
        if thruData.has_key(APID):
            thruData[APID].append(ThroughputHistory(timestamp,APID,thru))
        else :
            thruData[APID] = []
            thruData[APID].append(ThroughputHistory(timestamp,APID,thru))

    #find proper throughput value
    #start at time 0
    currentTime = 0
    f = open(outputFileLoc,"w")
    
    idx = 0
    while len(movDataList) > idx :
        currentTime = movDataList[idx].timestamp
        APID = movDataList[idx].APID
        if len(movDataList) == idx + 1:
            nextMovement = 99999999
        else :
            nextMovement = movDataList[idx+1].timestamp
        if not thruData.has_key(movDataList[idx].APID) :
            write(currentTime, throughputLimit)
        else :
            llen = len(thruData[movDataList[idx].APID])
            tidx = -1
            for i in range(0, llen) :
                if thruData[APID][i].timestamp > currentTime :
                    break
                tidx = i
            if tidx == -1 : # no throughput history
                write(currentTime, throughputLimit)    
            else :
                write(currentTime, thruData[APID][tidx].throughput)
            for i in range(tidx+1, llen) :
                if thruData[APID][i].timestamp >= nextMovement :
                    break
                write(thruData[APID][i].timestamp, thruData[APID][i].throughput)
                
        idx = idx +1
    f.close()
    
lasttime = 0
# write data
def write(timestamp, throughput) :
    global f, lasttime
    f.write("%d link1 %dkbit 0ms\n" %(timestamp - lasttime,throughput))
    lasttime = timestamp
    
composeFile()
