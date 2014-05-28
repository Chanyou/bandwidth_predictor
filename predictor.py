#TODO : Predict throughput from
from sklearn import tree

thruData = {}
movDataList = []

movDataLoc = ""
# Time APID
throughputHistoryLoc = ""
# Time APID Throughput
currentTime = 0
currentAP = '0'
outputFileLoc = ""
throughputLimit = 1024*1024*1024
#1GBps
alpha = 0.2

def init():
    global last_throughput
    global alpha
    alpha = 0.1
    last_throughput = 0.1
    
def predict_throughput(throughput):
    global last_throughput
    global alpha
    last_throughput = throughput * alpha + last_throughput * (1-alpha)
    return last_throughput

def add_half():
    global last_throughput
    last_throughput = last_throughput*1.5

def dec_half():
    global last_throughput
    last_throughput = last_throughput*0.5

def predict(windowsize):
    global currentAP, currentTime, alpha
    alen = len(thruData[currentAP])
    res = -1
    for i in range(0, alen) :
        if (thruData[currentAP][i].timestamp >= currentTime - windowsize) & (thruData[currentAP][i].timestamp <= currentTime) :
            if res < 0 :
                res = thruData[currentAP][i].throughput
            else :
                res = res *(1- alpha) + thruData[currentAP][i].throughput * alpha
            
    return res
    
        
    

def readFile():
    global movDataLoc, throughputHistoryLoc, movDataList, outputFileLoc, f;
    global thruData, movDataList
    
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
