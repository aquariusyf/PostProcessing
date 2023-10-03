#---------------------------------------------------------------------------------------------------------------------------------------------------
# Extract VONR to VOLTE irat KPI from logs (Redirection based)
#---------------------------------------------------------------------------------------------------------------------------------------------------

from PostProcessingUtils import LogPacket, LogPacket_RTP, PostProcessingUtils
from FilterMask import *
from openpyxl import Workbook
from datetime import datetime
import sys
import os

filter_mask[LOG_FILTER] = [0xB821, 0x1568, 0x1569, 0xB0C0, 0xB0EC, 0xB0ED]
filter_mask[EVENT_FILTER] = [3271,3272]

# Convert log to text file with default filter
REDIR_KPI = PostProcessingUtils()
REDIR_KPI.getArgv(sys.argv)
REDIR_KPI.scanWorkingDir() # default is .hdf
if not REDIR_KPI.skipFitlerLogs():
    REDIR_KPI.convertToText('Redir_KPI')
# Initialize log pkt list from filtered text files
REDIR_KPI.scanWorkingDir('_flt_text.txt', 'Redir_KPI')
REDIR_KPI.initLogPacketList()
logPktList_All_Logs = REDIR_KPI.getLogPacketList()

REDIR_START_MARKER = 'NR5G RRC OTA Packet  --  DL_DCCH / RRC Release'
REDIR_MARKER = 'redirectedCarrierInfo eutra'
REDIR_END_MARKER = 'LTE RRC OTA Packet  --  UL_DCCH / RRCConnectionSetupComplete'

# Initialize rows in KPI table
First_Row = ['KPI Field']
Total_IRAT = ['Total Num of Redirection']
AvgControlDelay = ['VONR to VOLTE Control Plane Delay (ms)']
AvgUserDelay = ['VONR to VOLTE User Plane Delay (ms)']
IRATPktLoss = ['Total Num of RTP Loss during Redirection']

MR_To_NRRC_Release = ['Measurement Report to NR RRC Release (ms)']
NRRC_Release_To_TAU_Req = ['NR RRC Release to TAU Request (ms)']
TAU_Req_To_LRRC_Req = ['TAU Request to LTE RRCConnectionRequest (ms)']
LRRC_Req_To_LRRC_Setup = ['LTE RRCConnectionRequest to LTE RRCConnectionSetup (ms)']
LRRC_Setup_To_LRRC_Complete = ['LTE RRCConnectionSetup to LTE RRCConnectionSetupComplete (ms)']
LRRC_Complete_To_TAU_Accept = ['LTE RRCConnectionSetupComplete to TAU Accept (ms)']
TAU_Accept_To_TAU_Complete = ['TAU Accept to TAU Complete (ms)']

# Initialize first row with log names
print(datetime.now().strftime("%H:%M:%S"), '(VONR_to_VOLTE_Redir_KPI) ' + 'Extracting KPI Summary...')
for key in logPktList_All_Logs.keys():
    First_Row.append(key) # Init first row with log names  

# Get VONR to VOLTE KPI
def getRedirKPI(pktList):
    if len(pktList) == 0:
        return [0, 'N/A', 'N/A', 0]    
    
    allRedir = []
    TotalRedir = 0
    CPDelay = []
    AvgCPDelay = 'N/A'
    RTP_During_Redir = []
    UPDelay = []
    AvgUPDelay = 'N/A'
    Redir_RTP_Loss = 0

    # Find the start and end event of Redirection, the last DL RTP pkt before Redirection, and the first DL RTP after Redirection
    n = 0
    while n < len(pktList):
        Redir_Pair = []
        RTP_Pair = []
        isLRRCCompleteMissing = False
        if pktList[n].getPacketCode() == '0xB821' and pktList[n].getTitle() == REDIR_START_MARKER and pktList[n].containsIE(REDIR_MARKER): # Find start of Redirection
            if n + 1 < len(pktList): # Check if next pkt index exceed length of pkt list
                for check_start in range(n + 1, len(pktList)): # Check if Redirection suc event is missing
                    if pktList[check_start].getPacketCode() == '0xB821' and pktList[check_start].getTitle() == REDIR_START_MARKER:
                        isLRRCCompleteMissing = True
                        break
                    elif pktList[check_start].getPacketCode() == '0xB0C0' and pktList[check_start].getTitle() == REDIR_END_MARKER:
                        break
            else:
                isLRRCCompleteMissing = True

            if isLRRCCompleteMissing: # If Redirection suc event is missing, skip current Redirection
                n += 1
                continue

            Redir_Pair.append(pktList[n]) # Add start event to Redirection pair
            Redir_Start_Index = n
            m = Redir_Start_Index
            while m >= 0: # Find last RTP before Redirection
                if pktList[m].getPacketCode() == '0x1568':
                    RTP_pkt_before_IRAT = LogPacket_RTP(pktList[m]) # Convert to RTP sub-class to get direction and rat type
                    if RTP_pkt_before_IRAT.getDirection() == 'NETWORK_TO_UE' and RTP_pkt_before_IRAT.getRatType() == 'NR5G' and RTP_pkt_before_IRAT.getMediaType() == 'AUDIO':
                        RTP_Pair.append(pktList[m]) # Add RTP pkt before Redirection to RTP pair
                        break
                    else:
                        m -= 1
                        continue
                else:
                    m -= 1
                    continue

            for i in range(Redir_Start_Index, len(pktList)):
                if pktList[i].getPacketCode() == '0xB0C0' and pktList[i].getTitle() == REDIR_END_MARKER: # Find end of Redirection
                    Redir_Pair.append(pktList[i]) # Add suc event to IRAT pair
                    # print('IRAT start: ', IRAT_Pair[0].getTimestamp())
                    # print('IRAT suc: ', IRAT_Pair[1].getTimestamp())
                    if len(Redir_Pair) != 2: # If Redirection start and end event not in pair, ignore it and reset Redirection pair
                        Redir_Pair = []
                        break
                    else:
                        allRedir.append(Redir_Pair) # Add Redirection pair to allRedir list
                    Redir_Pair = [] # Reset Redir pair
                    Redir_Suc_Index = i
                    for j in range(Redir_Suc_Index, len(pktList)):
                        if pktList[j].getPacketCode() == '0x1568': # Find the first DL RTP pkt after Redirection
                            RTP_pkt_after_IRAT = LogPacket_RTP(pktList[j]) # Convert to RTP sub-class to get direction and rat type
                            if RTP_pkt_after_IRAT.getDirection() == 'NETWORK_TO_UE' and RTP_pkt_after_IRAT.getRatType() == 'LTE' and RTP_pkt_after_IRAT.getMediaType() == 'AUDIO':
                                # print('IRAT start: ', RTP_Pair[0].getTimestamp())
                                # print('IRAT suc: ', RTP_Pair[1].getTimestamp())
                                RTP_Pair.append(pktList[j]) # Add RTP pkt after Redirection to RTP pair
                                if len(RTP_Pair) != 2: # If RTP pkt not in pair, ignore it and reset RTP pair
                                    RTP_Pair = []
                                    break
                                else:
                                    RTP_During_Redir.append(RTP_Pair) # Add RTP pair to RTP_During_Redir list
                                    rtpPKTLoss = LogPacket_RTP(RTP_Pair[1]).getSequence() - LogPacket_RTP(RTP_Pair[0]).getSequence()
                                    if rtpPKTLoss >= 2: # Check if pkt loss during Redirection
                                        Redir_RTP_Loss += rtpPKTLoss - 1
                                RTP_Pair = [] # Reset RTP pair
                                break
                            else:
                                continue
                        else:
                            continue
                    break
                else:
                    continue
            n += 1
        else:
            n += 1
            continue
    
    if len(allRedir) != 0:
        TotalRedir = len(allRedir) # Get total num of Redirection
        for redir in allRedir:
            CPDelay.append(LogPacket.getDelay(redir[1], redir[0])) # Get CP delays
    if len(RTP_During_Redir) != 0:
        for rtp in RTP_During_Redir:
            UPDelay.append(LogPacket.getDelay(rtp[1], rtp[0])) # Get UP delays
    
    # Get avg CP delay
    CPDelayLen = len(CPDelay)
    if CPDelayLen != 0:
        AvgCPDelay = int(sum(CPDelay)/CPDelayLen)

    # Get avg UP delay
    UPDelayLen = len(UPDelay)
    if UPDelayLen != 0:
        AvgUPDelay = int(sum(UPDelay)/UPDelayLen)
    
    return [TotalRedir, AvgCPDelay, AvgUPDelay, Redir_RTP_Loss]

# Get signaling breakdowns #
def getSignalingBreakdown(pktList):
    if len(pktList) == 0:
        return ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']
    
    MR_To_NRRC_Rel = 'N/A'
    NRRC_Rel_To_TAUReq = 'N/A'
    TAUReq_To_RRCReq = 'N/A'
    RRCReq_To_RRCSetup = 'N/A'
    RRCSetup_To_RRCComplete = 'N/A'
    RRCComplete_To_TAUAccept = 'N/A'
    TAUAccept_To_TAUComplete = 'N/A'
    
    MR = LogPacket()
    NRRC_Rel = LogPacket()
    TAUReq = LogPacket()
    RRCReq = LogPacket()
    RRCSetup = LogPacket()
    RRCComplete = LogPacket()
    TAUAccept = LogPacket()
    TAUComplete = LogPacket()
    
    for i in range(0, len(pktList)):
        if pktList[i].getTitle() == REDIR_START_MARKER and pktList[i].containsIE(REDIR_MARKER): # Find NR RRC Release with redir info
            j = i
            j -= 1
            NRRC_Rel = pktList[i]
            while j >= 0:
                if pktList[j].getTitle() == 'NR5G RRC OTA Packet  --  UL_DCCH / MeasurementReport' and pktList[j].containsIE('eutra-PhysCellId'): # Find MR
                    MR = pktList[j]
                    break
                else:
                    j -= 1
            TAUReq_Found = False
            RRCReq_Found = False
            RRCSetup_Found = False
            RRCComplete_Found = False
            TAU_Accept_Found = False
            for n in range(i, len(pktList)):
                # print(pktList[n].getTitle())
                if pktList[n].getTitle() == 'LTE NAS EMM Plain OTA Outgoing Message  --  Tracking area update complete Msg': # Find TAU Complete
                    TAUComplete = pktList[n]
                    # print('TAU_Complete_Found')
                    break
                elif pktList[n].getTitle() == 'LTE RRC OTA Packet  --  UL_CCCH / RRCConnectionRequest' and not RRCReq_Found: # Find LTE RRC Connection Request
                    RRCReq_Found = True
                    RRCReq = pktList[n]
                    # print('LRRCReconfig_Found')
                elif pktList[n].getTitle() == 'LTE RRC OTA Packet  --  DL_CCCH / RRCConnectionSetup' and not RRCSetup_Found: # Find LTE RRC Connection Setup
                    RRCSetup_Found = True
                    RRCSetup = pktList[n]
                    # print('LRRCReconfigComplete_Found')
                elif pktList[n].getTitle() == 'LTE RRC OTA Packet  --  UL_DCCH / RRCConnectionSetupComplete' and not RRCComplete_Found: # Find LTE RRC Connection Setup Complete
                    RRCComplete_Found = True
                    RRCComplete = pktList[n]
                elif pktList[n].getTitle() == 'LTE NAS EMM Plain OTA Outgoing Message  --  Tracking area update request Msg' and not TAUReq_Found: # Find TAU Request
                    TAUReq_Found = True
                    TAUReq = pktList[n]
                    # print('TAUReq_Found')
                elif pktList[n].getTitle() == 'LTE NAS EMM Plain OTA Incoming Message  --  Tracking area update accept Msg' and not TAU_Accept_Found: # Find TAU Accept
                    TAU_Accept_Found = True
                    TAUAccept = pktList[n]
                    # print('TAU_Accept_Found')
    
    # Calculate delays
    if MR.getTitle() != '' and NRRC_Rel.getTitle() != '':
        MR_To_NRRC_Rel = LogPacket.getDelay(NRRC_Rel, MR)
    if NRRC_Rel.getTitle() != '' and TAUReq.getTitle() != '':  
        NRRC_Rel_To_TAUReq = LogPacket.getDelay(TAUReq, NRRC_Rel)
    if TAUReq.getTitle() != '' and RRCReq.getTitle() != '':  
        TAUReq_To_RRCReq = LogPacket.getDelay(RRCReq, TAUReq)
    if RRCReq.getTitle() != '' and RRCSetup.getTitle() != '':
        RRCReq_To_RRCSetup = LogPacket.getDelay(RRCSetup, RRCReq)
    if RRCSetup.getTitle() != '' and RRCComplete.getTitle() != '':  
        RRCSetup_To_RRCComplete = LogPacket.getDelay(RRCComplete, RRCSetup)
    if RRCComplete.getTitle() != '' and TAUAccept.getTitle() != '':  
        TAUReq_To_TAUAccept = LogPacket.getDelay(TAUAccept, RRCComplete)
    if TAUAccept.getTitle() != '' and TAUComplete.getTitle() != '':  
        TAUAccept_To_TAUComplete = LogPacket.getDelay(TAUComplete, TAUAccept)

    return [MR_To_NRRC_Rel, NRRC_Rel_To_TAUReq, TAUReq_To_RRCReq, 
            RRCReq_To_RRCSetup, RRCSetup_To_RRCComplete, 
            TAUReq_To_TAUAccept, TAUAccept_To_TAUComplete]

# Get related KPI and add to corresponding rows
for log in logPktList_All_Logs.values():
    redirKPI = getRedirKPI(log) # Get redir KPI
    Total_IRAT.append(redirKPI[0])
    AvgControlDelay.append(redirKPI[1])
    AvgUserDelay.append(redirKPI[2])
    IRATPktLoss.append(redirKPI[3])
    
    sigBreakdown = getSignalingBreakdown(log)
    MR_To_NRRC_Release.append(sigBreakdown[0])
    NRRC_Release_To_TAU_Req.append(sigBreakdown[1])
    TAU_Req_To_LRRC_Req.append(sigBreakdown[2])
    LRRC_Req_To_LRRC_Setup.append(sigBreakdown[3])
    LRRC_Setup_To_LRRC_Complete.append(sigBreakdown[4])
    LRRC_Complete_To_TAU_Accept.append(sigBreakdown[5])
    TAU_Accept_To_TAU_Complete.append(sigBreakdown[6])

# Init work book and fill rows with data
wb = Workbook()
ws = wb.active
ws.title = 'VONR_to_VOLTE_IRAT_KPI_Redir'
ws.append(First_Row)
ws.append(Total_IRAT)
ws.append(AvgControlDelay)
ws.append(AvgUserDelay)
ws.append(IRATPktLoss)
ws.append(MR_To_NRRC_Release)
ws.append(NRRC_Release_To_TAU_Req)
ws.append(TAU_Req_To_LRRC_Req)
ws.append(LRRC_Req_To_LRRC_Setup)
ws.append(LRRC_Setup_To_LRRC_Complete)
ws.append(LRRC_Complete_To_TAU_Accept)
ws.append(TAU_Accept_To_TAU_Complete)

# Save KPI table to excel
dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'VONR_to_VOLTE_Redir_KPI_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(REDIR_KPI.workingDir, saveFileName)
print(datetime.now().strftime("%H:%M:%S"), '(VONR_to_VOLTE_Redir_KPI) ' + 'KPI Summary extracted: ' + savePath)
wb.save(savePath)