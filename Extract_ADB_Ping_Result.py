from PostProcessingUtils import PostProcessingUtils
from FilterMask import *
from openpyxl import Workbook
from datetime import datetime
import sys
import os
import re

Extract_Ping_Result = PostProcessingUtils()
Extract_Ping_Result.getArgv(sys.argv)
Extract_Ping_Result.scanWorkingDir('.txt')
All_Ping_Results = Extract_Ping_Result.getFilesPath()

First_Row = ['Ping Result']
Second_Row = ['AVG(ms)']
Thrid_Row = ['MAX(ms)']
Fourth_Row = ['MIN(ms)']
Fifth_Row = ['Pkt Loss %']
Total_Ping_Row = ['Num of Ping']
Other_Row = {}
for n in range(1, 501):
    Other_Row[n] = [n]

# QMAT.Ping: [DEFAULT][Thread 2]180 packets transmitted, 179 received, 0% packet loss, time 273256ms
RE_PING = re.compile(r'.* time=(.*) ms')
RE_PKT_LOSS = re.compile(r'.*received, ([\d]*)% packet loss.*')

# 07-28 11:50:24.933  5668 13230 I QMAT.Ping: [SUB1][Thread 1]40 bytes from 112.53.42.52: icmp_seq=1 ttl=52 time=198 ms
# 07-28 11:50:25.766  5668 13703 I QMAT.Ping: [SUB0][Thread 0]40 bytes from 112.53.42.52: icmp_seq=2 ttl=51 time=27.1 ms

# PING 112.53.42.114 (112.53.42.114) from 10.33.73.212 rmnet_data1: 32(60) bytes of data.
# 40 bytes from 112.53.42.114: icmp_seq=1 ttl=51 time=38.9 ms

def getFinalResult(PingList):
    finalResult = PingList
    AVG_ping = 'N/A'
    MAX_ping = 'N/A'
    MIN_ping = 'N/A'
    numOfPing = 'N/A'
    if PingList == []:
        return finalResult, AVG_ping, MAX_ping, MIN_ping, numOfPing
    numOfPing = len(finalResult)
    AVG_ping = float(sum(finalResult)/numOfPing)
    MAX_ping = max(finalResult)
    MIN_ping = min(finalResult)  
    return finalResult, AVG_ping, MAX_ping, MIN_ping, numOfPing

for file in All_Ping_Results:
    fileName = os.path.split(file)[1]
    if ('adb' not in fileName) and ('ADB' not in fileName):
        continue
    First_Row.append(fileName)
    fileLines = []
    openedFile = open(file, 'r', encoding="utf8")
    print(datetime.now().strftime("%H:%M:%S"), '(Extract_ADB_Ping_Result) ' + 'File opened: ' + file)
    fileLines = openedFile.readlines()
    openedFile.close()
    
    ping_result = []
    pkt_loss = 'N/A'
    
    for line in fileLines:
        if line == '\n' or line.isspace(): # Skip empty lines
            continue
        line = line.strip()
        if RE_PING.match(line):
            pingResult = RE_PING.match(line).groups()[0].strip()
            ping_result.append(float(pingResult))
        elif RE_PKT_LOSS.match(line) and pkt_loss == 'N/A':
            pkt_loss = float(RE_PKT_LOSS.match(line).groups()[0].strip())
    
    result = getFinalResult(ping_result)
    final_ping_result = result[0]
    AVG_ping_result = result[1]
    MAX_ping_result = result[2]
    MIN_ping_result = result[3]
    NUM_of_ping = result[4]
    
    Second_Row.append(AVG_ping_result)
    Thrid_Row.append(MAX_ping_result)
    Fourth_Row.append(MIN_ping_result)
    Fifth_Row.append(pkt_loss)
    Total_Ping_Row.append(NUM_of_ping)
    
    for x in range(0, len(final_ping_result)):
        Other_Row[x+1].append(final_ping_result[x])
        
wb = Workbook()
ws = wb.active
ws.title = 'RedundantTx_Ping_SimResult'
ws.append(First_Row)
ws.append(Second_Row)
ws.append(Thrid_Row)
ws.append(Fourth_Row)
ws.append(Fifth_Row)
ws.append(Total_Ping_Row)
for key in Other_Row.keys():
    ws.append(Other_Row[key])
    
# Save KPI table to excel
dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'ADB_Ping_Result_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(Extract_Ping_Result.workingDir, saveFileName)
print(datetime.now().strftime("%H:%M:%S"), '(Extract_ADB_Ping_Result) ' + 'Result extracted: ' + savePath)
wb.save(savePath)