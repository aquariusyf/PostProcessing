#---------------------------------------------------------------------------------------------------------------------------------------------------
# Extract NR CDRX configurations from logs
#---------------------------------------------------------------------------------------------------------------------------------------------------

from PostProcessingUtils import PostProcessingUtils
from FilterMask import *
from openpyxl import Workbook
from datetime import datetime
import sys
import os
import re

filter_mask[LOG_FILTER] = [0xB821]
filter_mask[EVENT_FILTER] = []

# 2024 Jan 22  05:39:31.321  [FA]  0xB821  NR5G RRC OTA Packet  --  DL_DCCH / RRCReconfiguration
# Radio Bearer ID = 1, Physical Cell ID = 244
# Freq = 504990
# drx-Config setup :
# drx-onDurationTimer milliSeconds : ms10,
# drx-InactivityTimer ms10,
# drx-HARQ-RTT-TimerDL 56,
# drx-HARQ-RTT-TimerUL 56,
# drx-RetransmissionTimerDL sl16,
# drx-RetransmissionTimerUL sl16,
# drx-LongCycleStartOffset ms40 : 20,
# drx-Config release : NULL,

# RE
RE_Arfcn = re.compile(r'.*Freq = ([\d]*).*')
RE_Pci = re.compile(r'.*Physical Cell ID = ([\d]*).*')
RE_OnDuration = re.compile(r'.*drx-onDurationTimer milliSeconds : ms([\d]*).*')
RE_InacTimer = re.compile(r'.*drx-InactivityTimer ms([\d]*).*')
RE_LongCycle_Offset = re.compile(r'.*drx-LongCycleStartOffset ms([\d]*) : ([\d]*).*')

CDRX_CONFIG = 'drx-Config'
CDRX_RELEASE = 'drx-Config release : NULL'
TS = 'Timestamp'
ARFCN = 'ARFCN'
PCI = 'PCI'
ONDURATION = 'onDuration(ms)'
INACTIMER = 'InactivityTimer(ms)'
LONGCYCLE = 'LongCycle(ms)'
OFFSET = 'Offset(ms)'
SAME_CELL_ON_OFF = 'Same Cell CDRX ON/OFF'
LOG_NAME = 'LogName'

First_Row = [TS, ARFCN, PCI, ONDURATION, INACTIMER, LONGCYCLE, OFFSET, SAME_CELL_ON_OFF ,LOG_NAME]
Content_Rows = []

# Convert log to text file with default filter
Extract_CDRX_Config = PostProcessingUtils()
Extract_CDRX_Config.getArgv(sys.argv)
Extract_CDRX_Config.scanWorkingDir() # default is .hdf
if not Extract_CDRX_Config.skipFitlerLogs():
    Extract_CDRX_Config.convertToText('Extract_CDRX')
# Initialize log pkt list from filtered text files
Extract_CDRX_Config.scanWorkingDir('_flt_text.txt', 'Extract_CDRX')
Extract_CDRX_Config.initLogPacketList()
logPktList_All_Logs = Extract_CDRX_Config.getLogPacketList()

# Filter only RRC reconfiguration and get log content
for logName, logPkts in logPktList_All_Logs.items():
    CurrentLogData = []
    for logPkt in logPkts:
        CurrentPktData ={TS: 'N/A', ARFCN: 'N/A', PCI: 'N/A', ONDURATION: 'Release', INACTIMER: 'Release', LONGCYCLE: 'Release', OFFSET: 'Release', SAME_CELL_ON_OFF: 'NO', LOG_NAME: 'N/A'}
        Last_Config = {ARFCN: 'NULL', PCI: 'NULL', ONDURATION: 'NULL'}
        
        if CurrentLogData != []: # Within same log, check last config from last pkt
            Last_Config[ARFCN] = CurrentLogData[len(CurrentLogData) - 1][ARFCN]
            Last_Config[PCI] = CurrentLogData[len(CurrentLogData) - 1][PCI]
            Last_Config[ONDURATION] = CurrentLogData[len(CurrentLogData) - 1][ONDURATION]
        else: # For different log, check last config from last pkt in last log (Last row)
            if Content_Rows != []:
                Last_Config[ARFCN] = Content_Rows[len(Content_Rows) - 1][1]
                Last_Config[PCI] = Content_Rows[len(Content_Rows) - 1][2]
                Last_Config[ONDURATION] = Content_Rows[len(Content_Rows) - 1][3]
                
        if not logPkt.getTitle() == 'NR5G RRC OTA Packet  --  DL_DCCH / RRCReconfiguration':
            continue
        elif not logPkt.containsIE(CDRX_CONFIG):
            continue
        elif logPkt.containsIE(CDRX_RELEASE): # If CDRX is released, keep release in CDRX param field
            logName = logName.replace('_flt_text.txt', '')
            logName = logName.replace('_Extract_CDRX', '')
            CurrentPktData[LOG_NAME] = logName # Append log name
            CurrentPktData[TS] = logPkt.getTimestamp() # Append timestamp
            logContent = logPkt.getContent()
            for line in logContent:
                if RE_Arfcn.match(line):
                    CurrentPktData[ARFCN] = RE_Arfcn.match(line).groups()[0] # Append arfcn
                elif RE_Pci.match(line):
                    CurrentPktData[PCI] = RE_Pci.match(line).groups()[0] # Append pci
                else:
                    continue
            if CurrentPktData[ARFCN] == Last_Config[ARFCN] and CurrentPktData[PCI] == Last_Config[PCI] and Last_Config[ONDURATION] != 'Release': 
                CurrentPktData[SAME_CELL_ON_OFF] = 'YES' # If same cell CDRX ON/OFF, mark this field as YES
        else:
            logName = logName.replace('_flt_text.txt', '')
            logName = logName.replace('_Extract_CDRX', '')
            CurrentPktData[LOG_NAME] = logName # Append log name
            CurrentPktData[TS] = logPkt.getTimestamp() # Append timestamp
            logContent = logPkt.getContent()
            for line in logContent:
                if RE_Arfcn.match(line):
                    CurrentPktData[ARFCN] = RE_Arfcn.match(line).groups()[0] # Append arfcn
                elif RE_Pci.match(line):
                    CurrentPktData[PCI] = RE_Pci.match(line).groups()[0] # Append pci
                elif RE_OnDuration.match(line):
                    CurrentPktData[ONDURATION] = RE_OnDuration.match(line).groups()[0] # Append onDuration
                elif RE_InacTimer.match(line):
                    CurrentPktData[INACTIMER] = RE_InacTimer.match(line).groups()[0] # Append inactivity timer
                elif RE_LongCycle_Offset.match(line):
                    CurrentPktData[LONGCYCLE] = RE_LongCycle_Offset.match(line).groups()[0] # Append long cycle
                    CurrentPktData[OFFSET] = RE_LongCycle_Offset.match(line).groups()[1] # Append offset
                else:
                    continue
            if CurrentPktData[ARFCN] == Last_Config[ARFCN] and CurrentPktData[PCI] == Last_Config[PCI] and Last_Config[ONDURATION] == 'Release':
                CurrentPktData[SAME_CELL_ON_OFF] = 'YES' # If same cell CDRX ON/OFF, mark this field as YES
        
        if CurrentPktData[LOG_NAME] != 'N/A':
            CurrentLogData.append(CurrentPktData)
        else:
            continue
    if CurrentLogData != []:
        for pktData in CurrentLogData:
            singleDataRow = []
            singleDataRow.append(pktData[TS])
            singleDataRow.append(pktData[ARFCN])
            singleDataRow.append(pktData[PCI])
            singleDataRow.append(pktData[ONDURATION])
            singleDataRow.append(pktData[INACTIMER])
            singleDataRow.append(pktData[LONGCYCLE])
            singleDataRow.append(pktData[OFFSET])
            singleDataRow.append(pktData[SAME_CELL_ON_OFF])
            singleDataRow.append(pktData[LOG_NAME])
            Content_Rows.append(singleDataRow)
    else:
        continue

wb = Workbook()
ws = wb.active
ws.title = 'NR_CDRX_Configs'
ws.append(First_Row)
for row in Content_Rows:
    ws.append(row)

# Save table to excel
dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'NR_CDRX_Config_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(Extract_CDRX_Config.workingDir, saveFileName)
print(datetime.now().strftime("%H:%M:%S"), '(Extract_NR_CDRX_Configs) ' + 'KPI Summary extracted: ' + savePath)
wb.save(savePath)