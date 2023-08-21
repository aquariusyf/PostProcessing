#---------------------------------------------------------------------------------------------------------------------------------------------------
# Extract N2N, N2L, L2N reselection KPI from logs
#---------------------------------------------------------------------------------------------------------------------------------------------------

from PostProcessingUtils import LogPacket, PostProcessingUtils
from FilterMask import *
from openpyxl import Workbook
from datetime import datetime
import sys
import os

filter_mask[LOG_FILTER] = [0xB821, 0xB0C0, 0xB0ED, 0xB0EC]
filter_mask[EVENT_FILTER] = [3248, 3315, 3269, 3349, 3354]
filter_mask[F3S_NON_REGEX] = []
filter_mask[QTRACE_NON_REGEX] = []

# N2N
# 3248 2023 Feb  7  02:40:23.985  [6C]  0x1FFB  Event  --  EVENT_NR5G_RRC_CELL_RESEL_STARTED_V3
# 3315 2023 Feb  7  02:40:24.040  [3B]  0x1FFB  Event  --  EVENT_NR5G_RRC_CELL_RESEL_SUCCESS_V2
N2N_RESEL_START = 'Event  --  EVENT_NR5G_RRC_CELL_RESEL_STARTED_V3'
N2N_RESEL_END = 'Event  --  EVENT_NR5G_RRC_CELL_RESEL_SUCCESS_V2'

# N2L
# 3269 2023 Feb  7  02:41:54.899  [AD]  0x1FFB  Event  --  EVENT_NR5G_RRC_IRAT_RESEL_FROM_NR_START
# 3349 2023 Feb  7  02:41:55.016  [9D]  0x1FFB  Event  --  EVENT_NR5G_RRC_IRAT_RESEL_FROM_NR_END_V2
N2L_RESEL_START = 'Event  --  EVENT_NR5G_RRC_IRAT_RESEL_FROM_NR_START'
N2L_RESEL_END = 'Event  --  EVENT_NR5G_RRC_IRAT_RESEL_FROM_NR_END_V2'

# L2N
# 3354 2023 Feb 13  02:58:07.641  [7B]  0x1FFB  Event  --  EVENT_NR5G_RRC_STATE_CHANGE_V5 (New RRC state = IRAT_TO_NR5G_STARTED)
# 3354 2023 Feb 13  02:58:07.762  [3A]  0x1FFB  Event  --  EVENT_NR5G_RRC_STATE_CHANGE_V5 (New RRC state = IDLE_CAMPED)
L2N_RESEL_MARKER = 'Event  --  EVENT_NR5G_RRC_STATE_CHANGE_V5'
L2N_RESEL_START = 'New RRC state = IRAT_TO_NR5G_STARTED'
L2N_RESEL_END = 'New RRC state = IDLE_CAMPED'

# Convert log to text file with default filter
Resel_KPI = PostProcessingUtils()
# ARGV = sys.argv
# ARGV.append('qtrace')
Resel_KPI.getArgv(sys.argv)
Resel_KPI.scanWorkingDir() # default is .hdf
if not Resel_KPI.skipFitlerLogs():
    Resel_KPI.convertToText('Resel_KPI')
# Initialize log pkt list from filtered text files
Resel_KPI.scanWorkingDir('_flt_text.txt', 'Resel_KPI')
Resel_KPI.initLogPacketList()
logPktList_All_Logs = Resel_KPI.getLogPacketList()

# KPI Table Rows
First_Row = ['KPI Field']
TotalNumN2NResel = ['Total Num of N2N Reselection']
AVGN2NDelay = ['AVG N2N Reselection Delay(ms)']
MAXN2NDelay = ['MAX N2N Reselection Delay(ms)']
MINN2NDelay = ['MIN N2N Reselection Delay(ms)']
TotalNumN2LResel = ['Total Num of N2L Reselection']
AVGN2LDelay = ['AVG N2L Reselection Delay(ms)']
MAXN2LDelay = ['MAX N2L Reselection Delay(ms)']
MINN2LDelay = ['MIN N2L Reselection Delay(ms)']
TotalNumL2NResel = ['Total Num of L2N Reselection']
AVGL2NDelay = ['AVG L2N Reselection Delay(ms)']
MAXL2NDelay = ['MAX L2N Reselection Delay(ms)']
MINL2NDelay = ['MIN L2N Reselection Delay(ms)']

print(datetime.now().strftime("%H:%M:%S"), '(Reselection_Delay) ' + 'Extracting KPI Summary...')

def getReselectionKPI(pktList):
    if len(pktList) == 0:
        return [0, 'N/A', 'N/A', 'N/A',
                0, 'N/A', 'N/A', 'N/A',
                0, 'N/A', 'N/A', 'N/A']    
    
    TotalN2N = 0
    N2N_Pair = []
    N2N_Markers = []
    N2N_Delay_All = []
    N2N_Delay_AVG = 'N/A'
    N2N_Delay_MAX = 'N/A'
    N2N_Delay_MIN = 'N/A'
    TotalN2L = 0
    N2L_Pair = []
    N2L_Markers = []
    N2L_Delay_All = []
    N2L_Delay_AVG = 'N/A'
    N2L_Delay_MAX = 'N/A'
    N2L_Delay_MIN = 'N/A'
    TotalL2N = 0
    L2N_Pair = []
    L2N_Markers = []
    L2N_Delay_All = []
    L2N_Delay_AVG = 'N/A'
    L2N_Delay_MAX = 'N/A'
    L2N_Delay_MIN = 'N/A'

    # Check N2N markers and get delay
    N2N_Start_Found = False
    for logPkt in pktList:
        if N2N_RESEL_START in logPkt.getTitle():
                N2N_Pair = []
                N2N_Pair.append(logPkt)
                N2N_Start_Found = True
        elif N2N_RESEL_END in logPkt.getTitle():
            if N2N_Start_Found and N2N_Pair != []:
                N2N_Pair.append(logPkt)
                N2N_Markers.append(N2N_Pair)
                N2N_Start_Found = False
            else: # skip current resel if start marker not found
                continue
    for marker in N2N_Markers:
        N2N_Delay_All.append(LogPacket.getDelay(marker[1], marker[0]))
    if N2N_Delay_All != []:
        TotalN2N = len(N2N_Delay_All)
        N2N_Delay_AVG = int(sum(N2N_Delay_All)/TotalN2N)     
        N2N_Delay_MAX = max(N2N_Delay_All)
        N2N_Delay_MIN = min(N2N_Delay_All)

    # Check N2L markers and get delay
    N2L_Start_Found = False
    for logPkt in pktList:
        if N2L_RESEL_START in logPkt.getTitle():
                N2L_Pair = []
                N2L_Pair.append(logPkt)
                N2L_Start_Found = True
        elif N2L_RESEL_END in logPkt.getTitle():
            if N2L_Start_Found and N2L_Pair != []:
                N2L_Pair.append(logPkt)
                N2L_Markers.append(N2L_Pair)
                N2L_Start_Found = False
            else: # skip current resel if start marker not found
                continue
    for marker in N2L_Markers:
        N2L_Delay_All.append(LogPacket.getDelay(marker[1], marker[0]))
    if N2L_Delay_All != []:
        TotalN2L = len(N2L_Delay_All)
        N2L_Delay_AVG = int(sum(N2L_Delay_All)/TotalN2L)     
        N2L_Delay_MAX = max(N2L_Delay_All)
        N2L_Delay_MIN = min(N2L_Delay_All)
        
    # Check L2N markers and get delay
    L2N_Start_Found = False
    for logPkt in pktList:
        if L2N_RESEL_MARKER in logPkt.getTitle():
            if logPkt.containsIE(L2N_RESEL_START):
                L2N_Pair = []
                L2N_Pair.append(logPkt)
                L2N_Start_Found = True
            elif logPkt.containsIE(L2N_RESEL_END):
                if L2N_Start_Found and L2N_Pair != []:
                    L2N_Pair.append(logPkt)
                    L2N_Markers.append(L2N_Pair)
                    L2N_Start_Found = False
                else: # skip current resel if start marker not found
                    continue
        else:
            continue
    for marker in L2N_Markers:
        L2N_Delay_All.append(LogPacket.getDelay(marker[1], marker[0]))
    if L2N_Delay_All != []:
        TotalL2N = len(L2N_Delay_All)
        L2N_Delay_AVG = int(sum(L2N_Delay_All)/TotalL2N)     
        L2N_Delay_MAX = max(L2N_Delay_All)
        L2N_Delay_MIN = min(L2N_Delay_All)
        
    return [TotalN2N, N2N_Delay_AVG, N2N_Delay_MAX, N2N_Delay_MIN,
            TotalN2L, N2L_Delay_AVG, N2L_Delay_MAX, N2L_Delay_MIN,
            TotalL2N, L2N_Delay_AVG, L2N_Delay_MAX, L2N_Delay_MIN]    
    
for key in logPktList_All_Logs.keys():
    First_Row.append(key) # Init first row with log names
    ReselResult = getReselectionKPI(logPktList_All_Logs[key])
    TotalNumN2NResel.append(ReselResult[0])
    AVGN2NDelay.append(ReselResult[1])
    MAXN2NDelay.append(ReselResult[2])
    MINN2NDelay.append(ReselResult[3])
    TotalNumN2LResel.append(ReselResult[4])
    AVGN2LDelay.append(ReselResult[5])
    MAXN2LDelay.append(ReselResult[6])
    MINN2LDelay.append(ReselResult[7])
    TotalNumL2NResel.append(ReselResult[8])
    AVGL2NDelay.append(ReselResult[9])
    MAXL2NDelay.append(ReselResult[10])
    MINL2NDelay.append(ReselResult[11])

# Init work book and fill rows with data
wb = Workbook()
ws = wb.active
ws.title = 'N2N_Handover_KPI'
ws.append(First_Row)
ws.append(TotalNumN2NResel)
ws.append(AVGN2NDelay)
ws.append(MAXN2NDelay)
ws.append(MINN2NDelay)
ws.append(TotalNumN2LResel)
ws.append(AVGN2LDelay)
ws.append(MAXN2LDelay)
ws.append(MINN2LDelay)
ws.append(TotalNumL2NResel)
ws.append(AVGL2NDelay)
ws.append(MAXL2NDelay)
ws.append(MINL2NDelay)

# Save KPI table to excel
dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'Reselection_KPI_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(Resel_KPI.workingDir, saveFileName)
print(datetime.now().strftime("%H:%M:%S"), '(Reselection_Delay) ' + 'KPI Summary extracted: ' + savePath)
wb.save(savePath)