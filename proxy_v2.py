#!/usr/bin/env python
# -*- coding: cp1252 -*-
# <PythonProxy.py>
#
#Copyright (c) <2009> <F�io Domingues - fnds3000 in gmail.com>
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation
#files (the "Software"), to deal in the Software without
#restriction, including without limitation the rights to use,
#copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the
#Software is furnished to do so, subject to the following
#conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.

"""\
Copyright (c) <2009> <F�io Domingues - fnds3000 in gmail.com> <MIT Licence>
"""

import sys
sys.path.append('../dns')
import socket, thread, select, time, random, re
#from dns_common import sendDNSQuery


__version__ = '0.1.0 Draft 1'
BUFLEN = 8192
VERSION = 'Python Proxy/'+__version__
HTTPVER = 'HTTP/1.1'
BR = []
AVG = 0
ALPHA = .5

USAGE = '%s <log> <alpha> <listen-port> <fake-ip> <dns-ip> <dns-port> [<www-ip>]' % (sys.argv[0])
NAME = 'video.cs.cmu.edu'
PORT = 8080

INNER_IP = '0.0.0.0'
DNS_IP = '0.0.0.0'
DNS_PORT = -1
RR_ADDR = ''
LOG_FILE = None

#By JSH 
starttime = time.time() # For synchronizing with netsim
timelist = [] # From *.events, it stores time information
bpslist = [] # From *.events, it stores BW information
listlen = 0 # It is same as the number of fluctuation
currenttime = 0
index = 0
timeunit = 5 # time interval for calculating
lastinterval = -1
lastbw = 0
b = 0
#givendata = []
movDataList = []
thruData = {}
throughputHistoryLoc = ''
movDataLoc = ''
alpha = 0.1

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
        
def getCurrentAP() :
    global currentAP, currenttime,movDataList
    idx = 1
    while len(movDataList) > idx :
        if movDataList[idx].timestamp > currenttime :
            break
        idx = idx + 1
    currentAP = movDayaList[idx - 1].APID
    
    return currentAP
def predict(windowsize):
    global currentAP, currenttime, alpha, thruData
    currentAP = getCurrentAP()
    alen = len(thruData[currentAP])
    res = -1
    for i in range(0, alen) :
        if (thruData[currentAP][i].timestamp >= currenttime - windowsize) & (thruData[currentAP][i].timestamp <= currenttime) :
            if res < 0 :
                res = thruData[currentAP][i].throughput
            else :
                res = res *(1- alpha) + thruData[currentAP][i].throughput * alpha
            
    return res
    

def readFile():
    global movDataLoc, throughputHistoryLoc, movDataList, outputFileLoc, f;
    global thruData, movDataList
    
    if len(sys.argv) < 10 :
        print '<output location> <movement data> <throughput history data>'
        exit(-1)
    
    movDataLoc = sys.argv[8]
    throughputHistoryLoc = sys.argv[9]


    
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




def getBR():
    global currenttime, index
    currenttime = int(time.time() - starttime)
    while index < listlen - 1:
        if currenttime >= timelist[index+1]:
            index += 1
        else:
            break
    #print "BR: ", bpslist[index], "current time: ", currenttime
    bw = predict(20)
    b = 10
    for i in BR:
        if i * 1.5 <= bw:
            b = i
	print 'predicted bw : '
	print b
    return b

class ConnectionHandler:
    def __init__(self, connection, address, timeout):
        global AVG, b
        self.client = connection
        self.client_buffer = ''
        self.timeout = timeout
        self.method, self.path, self.protocol = self.get_base_header()
        self.method_others()
        if 'Seg' in self.path:
            t_new = int(8*float(self.cl)/float(self.req_time)/1000)
            AVG = (1-ALPHA)*AVG + ALPHA*t_new

            t = long ((time.time()+0.5)*1000)
            s = ' '.join([str(t),str(self.req_time),str(t_new),str(round(AVG)),str(b),RR_ADDR,self.path])
            print s
            LOG_FILE.write(s+'\n')
            #print self.path + ' --> ' + str(t_new)
            #print AVG
        self.client.close()
        self.target.close()

    def get_base_header(self):
        while 1:
            self.client_buffer += self.client.recv(BUFLEN)
            end = self.client_buffer.find('\n')
            if end!=-1:
                break
        sys.stdout.flush()
        data = (self.client_buffer[:end+1]).split()
        self.client_buffer = self.client_buffer[end+1:]
        return data

    def method_others(self):
        global b
        self._connect_target()
        path = self.path
        sys.stdout.flush()
        path = path.replace('big_buck_bunny.f4m','big_buck_bunny_nolist.f4m')
        b = getBR()     
        path = path.replace('1000',str(b))
        self.path = path

        self.req_start = time.time()
        self.target.send('%s %s %s\n'%(self.method, path, self.protocol)+
                         self.client_buffer)
        self.client_buffer = ''
        self._read_write()
        self.req_time = time.time() - self.req_start

    def _connect_target(self):
        global RR_ADDR
        # name = self.path.split('http://')[1].split('/')[0].split(':')[0]
        # port = 80
        # try:
        #     port = self.path.split('http://')[1].split('/')[0].split(':')[1]
        # except:
        #     pass
        if not RR_ADDR:
            RR_ADDR = sendDNSQuery(NAME, INNER_IP, DNS_IP, DNS_PORT)[1]
        (soc_family, _, _, _, address) = socket.getaddrinfo(RR_ADDR, PORT)[0]
        self.target = socket.socket(soc_family)
        self.target.bind((INNER_IP,0))#random.randrange(3000,10000)))
        self.target.connect(address)

    def _read_write(self):
        time_out_max = self.timeout/3
        count = 0
        self.left = 0
        while 1:
            count += 1
            (recv, _, error) = select.select([self.target], [], [self.target], 3)
            if error:
                break
            if recv:
                data = self.target.recv(BUFLEN)
                if data:
                    data = data.replace('Connection: Keep-Alive','Connection: Close')
                    try:
                        d = data.split('Content-Length: ')[1]
                        self.cl = d.split('\r\n')[0]
                    except:
                        pass
                    self.client.send(data)
                    count = 0

                    if self.left:
                        self.left = self.left - len(data)
                        if self.left <= 0:
                            return
                    if '\r\n\r\n' in data:
                        self.left = int(float(self.cl)) - len(data.split('\r\n\r\n')[1])

            if count == time_out_max:
                break

def start_server(timeout=5, handler=ConnectionHandler):
    global BR, AVG, INNER_IP, DNS_IP, DNS_PORT, LOG_FILE, RR_ADDR, ALPHA

    if len(sys.argv) < 7:
        print USAGE
        exit(-1)

    LOG_FILE = open(sys.argv[1], 'w', 0)
    ALPHA = float(sys.argv[2])
    INNER_IP = sys.argv[4]
    DNS_IP = sys.argv[5]
    DNS_PORT = int(float(sys.argv[6]))
    if len(sys.argv) >= 8:
        RR_ADDR = sys.argv[7]

    
    v = open('/var/www/vod/big_buck_bunny.f4m').read()
    vi = [m.start() for m in re.finditer('bitrate=',v)]
    for i in vi:
        BR.append(int(float(v[i+9:].split('"')[0])))
    BR = sorted(BR)
    #print BR
    AVG = BR[0]
    
    #read_eventdata()  #By JSH

    readFile()
    
    port = int(float(sys.argv[3]))
    soc = socket.socket(socket.AF_INET)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind(('', port))
    print "Serving on %d."% port#debug
    soc.listen(0)
    while 1:
        thread.start_new_thread(handler, soc.accept()+(timeout,))
    soc.close()
    
if __name__ == '__main__':
    start_server()


