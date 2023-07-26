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
Other_Row = {}
for n in range(1, 101):
    Other_Row[n] = [n]

RE_PING = re.compile(r'.* time=(.*) ms')

# PING 14.119.104.254 (14.119.104.254) from 10.77.180.118 rmnet_data4: 1472(1500) bytes of data.
# 1480 bytes from 14.119.104.254: icmp_seq=1 ttl=54 time=4302 ms

def getFinalResult(sub1PingList, sub2PingList):
    finalResult = []
    AVG_ping = 'N/A'
    MAX_ping = 'N/A'
    MIN_ping = 'N/A'
    betterPingResultList = []
    if sub1PingList == [] or sub2PingList == []:
        return finalResult, AVG_ping, MAX_ping, MIN_ping
    
    numOfPing = min(len(sub1PingList), len(sub2PingList))
    
    for m in range(0, numOfPing):
        betterPingResult = min(sub1PingList[m], sub2PingList[m])
        betterPingResultList.append(float(betterPingResult))
        finalResult.append('MIN(' + str(sub1PingList[m]) + ', ' + str(sub2PingList[m]) + ') ' + ' => ' + str(betterPingResult))
    if betterPingResultList != []:
        AVG_ping = float(sum(betterPingResultList)/numOfPing)
        MAX_ping = max(betterPingResultList)
        MIN_ping = min(betterPingResultList)
        
    return finalResult, AVG_ping, MAX_ping, MIN_ping

for file in All_Ping_Results:
    fileName = os.path.split(file)[1]
    if 'ping_' not in fileName:
        continue
    First_Row.append(fileName)
    fileLines = []
    openedFile = open(file, 'r') 
    fileLines = openedFile.readlines()
    print(datetime.now().strftime("%H:%M:%S"), '(Extract_RedundantTx_Ping_Result) ' + 'File opened: ' + file)
    openedFile.close()
    
    sub1_start_point_found = False
    sub2_start_point_found = False
    sub1_result = []
    sub2_result = []
    
    for line in fileLines:
        if line == '\n' or line.isspace(): # Skip empty lines
            continue
        line = line.strip()
        if 'PING' in line:
            if not sub1_start_point_found:
                sub1_start_point_found = True
            else:
                sub2_start_point_found = True
        if RE_PING.match(line) and (sub1_start_point_found and not sub2_start_point_found):
            formatFound = RE_PING.match(line)
            pingResult = formatFound.groups()[0].strip()
            sub1_result.append(float(pingResult))
            # print(pingResult)
        elif RE_PING.match(line) and sub2_start_point_found:
            formatFound = RE_PING.match(line)
            pingResult = formatFound.groups()[0].strip()
            sub2_result.append(float(pingResult))
            # print(pingResult)
    
    result = getFinalResult(sub1_result, sub2_result)
    final_ping_result = result[0]
    AVG_ping_result = result[1]
    MAX_ping_result = result[2]
    MIN_ping_result = result[3]
    
    Second_Row.append(AVG_ping_result)
    Thrid_Row.append(MAX_ping_result)
    Fourth_Row.append(MIN_ping_result)
    
    for x in range(0, len(final_ping_result)):
        Other_Row[x+1].append(final_ping_result[x])
        
wb = Workbook()
ws = wb.active
ws.title = 'RedundantTx_Ping_SimResult'
ws.append(First_Row)
ws.append(Second_Row)
ws.append(Thrid_Row)
ws.append(Fourth_Row)
for key in Other_Row.keys():
    ws.append(Other_Row[key])
    
# Save KPI table to excel
dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'Ping++Ping_Result_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(Extract_Ping_Result.workingDir, saveFileName)
print(datetime.now().strftime("%H:%M:%S"), '(Extract_RedundantTx_Ping_Result) ' + 'Result extracted: ' + savePath)
wb.save(savePath)