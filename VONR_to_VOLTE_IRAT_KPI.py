#---------------------------------------------------------------------------------------------------------------------------------------------------
# Extract VONR to VOLTE irat KPI from logs
#---------------------------------------------------------------------------------------------------------------------------------------------------

from PostProcessingUtils import LogPacket, LogPacket_RTP, PostProcessingUtils
from FilterMask import *
from openpyxl import Workbook
from datetime import datetime
import sys
import os

filter_mask[LOG_FILTER] = [0xB821, 0x1568, 0x1569, 0xB0C0, 0xB0EC, 0xB0ED]
filter_mask[EVENT_FILTER] = [3270, 1994]

# Convert log to text file with default filter
IRAT_KPI = PostProcessingUtils()
IRAT_KPI.getArgv(sys.argv)
IRAT_KPI.scanWorkingDir() # default is .hdf
if not IRAT_KPI.skipFitlerLogs():
    IRAT_KPI.convertToText('IRAT_KPI')
# Initialize log pkt list from filtered text files
IRAT_KPI.scanWorkingDir('_flt_text.txt', 'IRAT_KPI')
IRAT_KPI.initLogPacketList()
logPktList_All_Logs = IRAT_KPI.getLogPacketList()

# Initialize rows in KPI table
First_Row = ['KPI Field']
Total_IRAT = ['Total Num of IRAT']
AvgControlDelay = ['VONR to VOLTE Control Plane Delay (ms)']
AvgUserDelay = ['VONR to VOLTE User Plane Delay (ms)']
IRATPktLoss = ['Total Num of RTP Loss during IRAT']

MR_To_irat_Cmd = ['Measurement Report to NR HO Command (ms)']
irat_Cmd_To_LRRC_Reconfig = ['NR HO Command to LRRC Reconfig (ms)']
LRRC_Reconfig_To_Config_Complete = ['LRRC Reconfig to LRRC Reconfig Complete (ms)']
Config_Complete_To_TAU_Req = ['LRRC Reconfig Complete to TAU Request (ms)']
TAU_Req_To_TAU_Accept = ['TAU Request to TAU Accept (ms)']
TAU_Accept_To_TAU_Complete = ['TAU Accept to TAU Complete (ms)']

# Initialize first row with log names
print(datetime.now().strftime("%H:%M:%S"), '(VONR_to_VOLTE_IRAT_KPI) ' + 'Extracting KPI Summary...')
for key in logPktList_All_Logs.keys():
    First_Row.append(key) # Init first row with log names  

# Get VONR to VOLTE KPI
def getIRATKPI(pktList):
    if len(pktList) == 0:
        return [0, 'N/A', 'N/A', 0]    
    
    allIRAT = []
    TotalIRAT = 0
    CPDelay = []
    AvgCPDelay = 'N/A'
    RTP_During_IRAT = []
    UPDelay = []
    AvgUPDelay = 'N/A'
    IRAT_RTP_Loss = 0

    # Find the start and end event of IRAT, the last DL RTP pkt before IRAT, and the first DL RTP after IRAT
    n = 0
    while n < len(pktList):
        IRAT_Pair = []
        RTP_Pair = []
        isIRATSucPointMissing = False
        if pktList[n].getPacketCode() == '0x1FFB' and pktList[n].getTitle() == 'Event  --  EVENT_NR5G_RRC_IRAT_HO_FROM_NR_START': # Find start of IRAT
            if n + 1 < len(pktList): # Check if next pkt index exceed length of pkt list
                for check_start in range(n + 1, len(pktList)): # Check if IRAT suc event is missing
                    if pktList[check_start].getPacketCode() == '0x1FFB' and pktList[check_start].getTitle() == 'Event  --  EVENT_NR5G_RRC_IRAT_HO_FROM_NR_START':
                        isIRATSucPointMissing = True
                        break
                    elif pktList[check_start].getPacketCode() == '0x1FFB' and pktList[check_start].getTitle() == 'Event  --  EVENT_LTE_RRC_STATE_CHANGE_TRIGGER':
                        break
            else:
                isIRATSucPointMissing = True

            if isIRATSucPointMissing: # If IRAT suc event is missing, skip current IRAT
                n += 1
                continue

            IRAT_Pair.append(pktList[n]) # Add start event to IRAT pair
            IRAT_Start_Index = n
            m = IRAT_Start_Index
            while m >= 0: # Find last RTP before IRAT
                if pktList[m].getPacketCode() == '0x1568':
                    RTP_pkt_before_IRAT = LogPacket_RTP(pktList[m]) # Convert to RTP sub-class to get direction and rat type
                    if RTP_pkt_before_IRAT.getDirection() == 'NETWORK_TO_UE' and RTP_pkt_before_IRAT.getRatType() == 'NR5G' and RTP_pkt_before_IRAT.getMediaType() == 'AUDIO':
                        RTP_Pair.append(pktList[m]) # Add RTP pkt before IRAT to RTP pair
                        break
                    else:
                        m -= 1
                        continue
                else:
                    m -= 1
                    continue

            for i in range(IRAT_Start_Index, len(pktList)):
                if pktList[i].getPacketCode() == '0x1FFB' and pktList[i].getTitle() == 'Event  --  EVENT_LTE_RRC_STATE_CHANGE_TRIGGER': # Find end of IRAT
                    IRAT_Pair.append(pktList[i]) # Add suc event to IRAT pair
                    # print('IRAT start: ', IRAT_Pair[0].getTimestamp())
                    # print('IRAT suc: ', IRAT_Pair[1].getTimestamp())
                    if len(IRAT_Pair) != 2: # If IRAT start and end event not in pair, ignore it and reset IRAT pair
                        IRAT_Pair = []
                        break
                    else:
                        allIRAT.append(IRAT_Pair) # Add IRAT pair to allIRAT list
                    IRAT_Pair = [] # Reset IRAT pair
                    IRAT_Suc_Index = i
                    for j in range(IRAT_Suc_Index, len(pktList)):
                        if pktList[j].getPacketCode() == '0x1568': # Find the first DL RTP pkt after IRAT
                            RTP_pkt_after_IRAT = LogPacket_RTP(pktList[j]) # Convert to RTP sub-class to get direction and rat type
                            if RTP_pkt_after_IRAT.getDirection() == 'NETWORK_TO_UE' and RTP_pkt_after_IRAT.getRatType() == 'LTE' and RTP_pkt_after_IRAT.getMediaType() == 'AUDIO':
                                # print('IRAT start: ', RTP_Pair[0].getTimestamp())
                                # print('IRAT suc: ', RTP_Pair[1].getTimestamp())
                                RTP_Pair.append(pktList[j]) # Add RTP pkt after IRAT to RTP pair
                                if len(RTP_Pair) != 2: # If RTP pkt not in pair, ignore it and reset RTP pair
                                    RTP_Pair = []
                                    break
                                else:
                                    RTP_During_IRAT.append(RTP_Pair) # Add RTP pair to RTP_During_IRAT list
                                    rtpPKTLoss = LogPacket_RTP(RTP_Pair[1]).getSequence() - LogPacket_RTP(RTP_Pair[0]).getSequence()
                                    if rtpPKTLoss >= 2: # Check if pkt loss during IRAT
                                        IRAT_RTP_Loss += rtpPKTLoss - 1
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
    
    if len(allIRAT) != 0:
        TotalIRAT = len(allIRAT) # Get total num of IRAT
        for irat in allIRAT:
            CPDelay.append(LogPacket.getDelay(irat[1], irat[0])) # Get CP delays
    if len(RTP_During_IRAT) != 0:
        for rtp in RTP_During_IRAT:
            UPDelay.append(LogPacket.getDelay(rtp[1], rtp[0])) # Get UP delays
    
    # Get avg CP delay
    CPDelayLen = len(CPDelay)
    if CPDelayLen != 0:
        AvgCPDelay = int(sum(CPDelay)/CPDelayLen)

    # Get avg UP delay
    UPDelayLen = len(UPDelay)
    if UPDelayLen != 0:
        AvgUPDelay = int(sum(UPDelay)/UPDelayLen)
    
    return [TotalIRAT, AvgCPDelay, AvgUPDelay, IRAT_RTP_Loss]

# Get signaling breakdowns #
def getSignalingBreakdown(pktList):
    if len(pktList) == 0:
        return ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']
    
    MR_To_HOCmd = 'N/A'
    HOCmd_To_LRRCReconfig = 'N/A'
    LRRCReconfig_To_LRRCReconfigComplete = 'N/A'
    LRRCReconfigComplete_To_TAUReq = 'N/A'
    TAUReq_To_TAUAccept = 'N/A'
    TAUAccept_To_TAUComplete = 'N/A'
    
    MR = LogPacket()
    HOCmd = LogPacket()
    LRRCReconfig = LogPacket()
    LRRCReconfigComplete = LogPacket()
    TAUReq = LogPacket()
    TAUAccept = LogPacket()
    TAUComplete = LogPacket()
    
    for i in range(0, len(pktList)):
        if pktList[i].getTitle() == 'NR5G RRC OTA Packet  --  DL_DCCH / mobilityFromNRCommand' and pktList[i].containsIE('targetRAT-Type eutra'): # Find NR HO command
            j = i
            j -= 1
            HOCmd = pktList[i]
            while j >= 0:
                if pktList[j].getTitle() == 'NR5G RRC OTA Packet  --  UL_DCCH / MeasurementReport' and pktList[j].containsIE('eutra-PhysCellId'): # Find MR
                    MR = pktList[j]
                    break
                else:
                    j -= 1
            LRRCReconfig_Found = False
            LRRCReconfigComplete_Found = False
            TAUReq_Found = False
            TAU_Accept_Found = False
            for n in range(i, len(pktList)):
                # print(pktList[n].getTitle())
                if pktList[n].getTitle() == 'LTE NAS EMM Plain OTA Outgoing Message  --  Tracking area update complete Msg': # Find TAU Complete
                    TAUComplete = pktList[n]
                    # print('TAU_Complete_Found')
                    break
                elif pktList[n].getTitle() == 'LTE RRC OTA Packet  --  DL_DCCH / RRCConnectionReconfiguration' and pktList[n].containsIE('mobilityControlInfo') and not LRRCReconfig_Found: # Find LTE RRC Reconfig
                    LRRCReconfig_Found = True
                    LRRCReconfig = pktList[n]
                    # print('LRRCReconfig_Found')
                elif pktList[n].getTitle() == 'LTE RRC OTA Packet  --  UL_DCCH / RRCConnectionReconfigurationComplete' and not LRRCReconfigComplete_Found: # Find LTE RRC Reconfig Complete
                    LRRCReconfigComplete_Found = True
                    LRRCReconfigComplete = pktList[n]
                    # print('LRRCReconfigComplete_Found')
                elif pktList[n].getTitle() == 'LTE NAS EMM Plain OTA Outgoing Message  --  Tracking area update request Msg' and not TAUReq_Found: # Find TAU Request
                    TAUReq_Found = True
                    TAUReq = pktList[n]
                    # print('TAUReq_Found')
                elif pktList[n].getTitle() == 'LTE NAS EMM Plain OTA Incoming Message  --  Tracking area update accept Msg' and not TAU_Accept_Found: # Find TAU Accept
                    TAU_Accept_Found = True
                    TAUAccept = pktList[n]
                    # print('TAU_Accept_Found')
    
    # Calculate delays
    if MR.getTitle() != '' and HOCmd.getTitle() != '':
        MR_To_HOCmd = LogPacket.getDelay(HOCmd, MR)
    if HOCmd.getTitle() != '' and LRRCReconfig.getTitle() != '':  
        HOCmd_To_LRRCReconfig = LogPacket.getDelay(LRRCReconfig, HOCmd)
    if LRRCReconfig.getTitle() != '' and LRRCReconfigComplete.getTitle() != '':  
        LRRCReconfig_To_LRRCReconfigComplete = LogPacket.getDelay(LRRCReconfigComplete, LRRCReconfig)
    if LRRCReconfigComplete.getTitle() != '' and TAUReq.getTitle() != '':  
        LRRCReconfigComplete_To_TAUReq = LogPacket.getDelay(TAUReq, LRRCReconfigComplete)
    if TAUReq.getTitle() != '' and TAUAccept.getTitle() != '':  
        TAUReq_To_TAUAccept = LogPacket.getDelay(TAUAccept, TAUReq)
    if TAUAccept.getTitle() != '' and TAUComplete.getTitle() != '':  
        TAUAccept_To_TAUComplete = LogPacket.getDelay(TAUComplete, TAUAccept)

    return [MR_To_HOCmd, HOCmd_To_LRRCReconfig, LRRCReconfig_To_LRRCReconfigComplete, LRRCReconfigComplete_To_TAUReq, TAUReq_To_TAUAccept, TAUAccept_To_TAUComplete]

# Get related KPI and add to corresponding rows
for log in logPktList_All_Logs.values():
    iratKPI = getIRATKPI(log) # Get irat KPI
    Total_IRAT.append(iratKPI[0])
    AvgControlDelay.append(iratKPI[1])
    AvgUserDelay.append(iratKPI[2])
    IRATPktLoss.append(iratKPI[3])
    
    sigBreakdown = getSignalingBreakdown(log)
    MR_To_irat_Cmd.append(sigBreakdown[0])
    irat_Cmd_To_LRRC_Reconfig.append(sigBreakdown[1])
    LRRC_Reconfig_To_Config_Complete.append(sigBreakdown[2])
    Config_Complete_To_TAU_Req.append(sigBreakdown[3])
    TAU_Req_To_TAU_Accept.append(sigBreakdown[4])
    TAU_Accept_To_TAU_Complete.append(sigBreakdown[5])

# Init work book and fill rows with data
wb = Workbook()
ws = wb.active
ws.title = 'VONR_to_VOLTE_IRAT_KPI'
ws.append(First_Row)
ws.append(Total_IRAT)
ws.append(AvgControlDelay)
ws.append(AvgUserDelay)
ws.append(IRATPktLoss)
ws.append(MR_To_irat_Cmd)
ws.append(irat_Cmd_To_LRRC_Reconfig)
ws.append(LRRC_Reconfig_To_Config_Complete)
ws.append(Config_Complete_To_TAU_Req)
ws.append(TAU_Req_To_TAU_Accept)
ws.append(TAU_Accept_To_TAU_Complete)

# Save KPI table to excel
dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'VONR_to_VOLTE_IRAT_KPI_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(IRAT_KPI.workingDir, saveFileName)
print(datetime.now().strftime("%H:%M:%S"), '(VONR_to_VOLTE_IRAT_KPI) ' + 'KPI Summary extracted: ' + savePath)
wb.save(savePath)