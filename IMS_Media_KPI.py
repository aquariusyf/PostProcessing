#---------------------------------------------------------------------------------------------------------------------------------------------------
# Extract IMS Media and N2N handover KPI from logs
#---------------------------------------------------------------------------------------------------------------------------------------------------

from PostProcessingUtils import LogPacket, LogPacket_RTP, LogPacket_Talkspurt, PostProcessingUtils
from FilterMask import *
from openpyxl import Workbook
from datetime import datetime
import sys
import os
import re

filter_mask[LOG_FILTER] = [0xB821, 0x1568, 0x1569, 0x156A, 
                           0x156C, 0xB800, 0xB801, 0xB808, 
                           0xB809, 0xB80A, 0xB80B, 0xB814, 
                           0xB890, 0x1CD0]
filter_mask[EVENT_FILTER] = [3188, 3190]

# Convert log to text file with default filter
IMS_KPI = PostProcessingUtils()
IMS_KPI.getArgv(sys.argv)
IMS_KPI.scanWorkingDir() # default is .hdf
if not IMS_KPI.skipFitlerLogs():
    IMS_KPI.convertToText('IMS_Media_KPI')
# Initialize log pkt list from filtered text files
IMS_KPI.scanWorkingDir('_flt_text.txt', 'IMS_Media_KPI')
IMS_KPI.initLogPacketList()
logPktList_All_Logs = IMS_KPI.getLogPacketList()
logPktList_All_TS_Logs = {}
logPktList_All_RTP_Logs = {}

# Initialize rows in KPI table
First_Row = ['KPI Field']
TotalNumRTP = ['Total Num of DL RTP Packets Elapsed']
TotalNumVoiceRTP = ['Total Num of Voice Packets Received']
TotalNumSilenceRTP = ['Total Num of Silence Packets Received']
TotalRTPLoss = ['Total RTP Loss']
TotalRTPLossInTS = ['Total RTP Loss (In Talkspurt)']
TotalRTPLossRate = ['Total RTP Loss Rate']
TotalRTPLossRateInTS = ['Total RTP Loss Rate (In Talkspurt)']
NWLoss = ['Network Loss']
QDJ_Underflow = ['QDJ Underflow']
QDJ_OPT2 = ['QDJ Optimization 2']
QDJ_Redundant = ['QDJ Redundant']
QDJ_Stale_Dropped = ['QDJ Stale Dropped']
QDJ_Reset = ['QDJ Reset']
QDJ_ENQ_Delayed = ['QDJ Enqueue Delayed']
QDJ_Out_Of_Order = ['QDJ Out of Order']
RTP_Discard = ['RTP Discard']
NumRTPBurst = ['Total RTP Packet Burst Occurrence']
MaxRTPBurst = ['Max Num of Packets in Burst']
AvgJitter = ['Avg Inter Jitter']
MaxJitter = ['Max Inter Jitter']
MinJitter = ['Min Inter Jitter']
AvgFrameDelay = ['Avg Frame Delay (In Talkspurt)']
MaxFrameDelay = ['Max Frame Delay (In Talkspurt)']
MinFrameDelay = ['Min Frame Delay (In Talkspurt)']
AvgTargetDelay = ['Avg Target Delay (In Talkspurt)']
MaxTargetDelay = ['Max Target Delay (In Talkspurt)']
MinTargetDelay = ['Min Target Delay (In Talkspurt)']
AvgQsize = ['Avg Q Size (In Talkspurt)']
MaxQsize = ['Max Q Size (In Talkspurt)']
MinQsize = ['Min Q Size (In Talkspurt)']
TotalHandover = ['Total Num of Handover']
HandoverPktLoss = ['Total Num of RTP Loss during HO']
AvgControlDelay = ['Avg Control Plane Handover Delay (ms)']
MaxControlDelay = ['Max Control Plane Handover Delay (ms)']
MinControlDelay = ['Min Control Plane Handover Delay (ms)']
AvgUserDelay = ['Avg User Plane Handover Delay (ms)']
MaxUserDelay = ['Max User Plane Handover Delay (ms)']
MinUserDelay = ['Min User Plane Handover Delay (ms)']
HandoverInTS = ['Total Num of Handover (In Talkspurt)']
HandoverPktLoss_TS = ['Total Num of RTP Loss during HO (In Talkspurt)']
AvgControlDelay_TS = ['Avg Control Plane Handover Delay (In Talkspurt) (ms)']
MaxControlDelay_TS = ['Max Control Plane Handover Delay (In Talkspurt) (ms)']
MinControlDelay_TS = ['Min Control Plane Handover Delay (In Talkspurt) (ms)']
AvgUserDelay_TS = ['Avg User Plane Handover Delay (In Talkspurt) (ms)']
MaxUserDelay_TS = ['Max User Plane Handover Delay (In Talkspurt) (ms)']
MinUserDelay_TS = ['Min User Plane Handover Delay (In Talkspurt) (ms)']


# Initialize sub-class pkt list and first row with log names
print(datetime.now().strftime("%H:%M:%S"), '(IMS_Media_KPI) ' + 'Extracting KPI Summary...')
for key in logPktList_All_Logs.keys():
    TS_Log_Pkts = []
    RTP_Log_Pkts = []
    for pkt in logPktList_All_Logs[key]:
        TS_Log_Pkts.append(LogPacket_Talkspurt(pkt)) # Init talkspurt pkt list from all pkts
        if pkt.getPacketCode() == '0x1568' or pkt.getPacketCode() == '0x1569':
            RTP_Log_Pkts.append(LogPacket_RTP(pkt)) # Init RTP pkt list from all pkts
    if TS_Log_Pkts != []:
        LogPacket_Talkspurt.findTalkspurt(TS_Log_Pkts) # Mark pkts in talkspurt
    else:
        print(datetime.now().strftime("%H:%M:%S"), '(IMS_Media_KPI) ' + 'No log pkt found in: ' + key)
    logPktList_All_TS_Logs[key] = TS_Log_Pkts
    if RTP_Log_Pkts != []:
        LogPacket_Talkspurt.findTalkspurt(RTP_Log_Pkts) # Mark pkts in talkspurt
    else:
        print(datetime.now().strftime("%H:%M:%S"), '(IMS_Media_KPI) ' + 'No RTP pkt found in: ' + key)
    logPktList_All_RTP_Logs[key] = RTP_Log_Pkts
    First_Row.append(key) # Init first row with log names
    
# Get total num of downlink RTP pkts
def getTotalRTP(pktList):
    firstSeq = 0
    lastSeq = 0
    lastSeqSsrc = 0
    if len(pktList) == 0:
        return 0
    
    # Find last DL RTP in log
    j = len(pktList) - 1
    while(j >= 0):
        if pktList[j].getPacketCode() == '0x1568' and pktList[j].getDirection() == 'NETWORK_TO_UE' and pktList[j].getMediaType() == 'AUDIO':
            lastSeq = pktList[j].getSequence()
            lastSeqSsrc = pktList[j].getSsrc()
            #print(lastSeq)
            break
        j -= 1

    # Find first DL RTP in log
    for i in range(0, len(pktList)):
        if pktList[i].getPacketCode() == '0x1568' and pktList[i].getDirection() == 'NETWORK_TO_UE' and pktList[i].getMediaType() == 'AUDIO':
            if pktList[i].getSsrc() == lastSeqSsrc:
                firstSeq = pktList[i].getSequence()
                #print(firstSeq)
                break
            else:
                continue

    if lastSeq >= firstSeq:
        return lastSeq - firstSeq + 1
    else:
        return lastSeq + 65536 - firstSeq + 1

# Get total num of voice and silence downlink RTP pkts
def getTotalVoiceSilenceRTP(pktList):
    totalVoice = 0
    totalSilence = 0
    lastSeqSsrc = 0
    if len(pktList) == 0:
        return [0, 0]

    # Find Ssrc of last DL voice RTP in log
    j = len(pktList) - 1
    while(j >= 0):
        if pktList[j].getPacketCode() == '0x1568' and pktList[j].getDirection() == 'NETWORK_TO_UE' and pktList[j].getMediaType() == 'AUDIO':
            lastSeqSsrc = pktList[j].getSsrc()
            break
        j -= 1

    for pkt in pktList:
        if pkt.getPacketCode() == '0x1568' and pkt.getDirection() == 'NETWORK_TO_UE' and pkt.getMediaType() == 'AUDIO' and pkt.isInTalkspurt() and pkt.getSsrc() == lastSeqSsrc:
            totalVoice += 1
        elif pkt.getPacketCode() == '0x1568' and pkt.getDirection() == 'NETWORK_TO_UE' and pkt.getMediaType() == 'AUDIO' and not pkt.isInTalkspurt() and pkt.getSsrc() == lastSeqSsrc:
            totalSilence += 1
    
    return [totalVoice, totalSilence]

# Get total num of RTP loss of different types, total pkt loss during talkspurt
def getNumRTPLoss(pktList):

    if len(pktList) == 0:
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    LossInTS = 0
    NWLoss = 0
    qdjUnderflow = 0
    qdjOPT2 = 0
    qdjStaleDropped = 0
    qdjRedundant = 0
    qdjReset = 0
    qdjEnQDelayed = 0
    qdjOOO = 0
    rtpDiscard = 0

    for pkt in pktList:
        if pkt.getPacketCode() == '0x1569' and pkt.isInTalkspurt():
            LossInTS += pkt.getNumLoss()
        if pkt.getPacketCode() == '0x1569' and pkt.getLossType() == 'RTP NETWORK LOSS':
            NWLoss += pkt.getNumLoss()
        elif pkt.getPacketCode() == '0x1569' and pkt.getLossType() == 'QDJ UNDERFLOW':
            qdjUnderflow += pkt.getNumLoss()
        elif pkt.getPacketCode() == '0x1569' and pkt.getLossType() == 'QDJ OPTIMIZATION 2':
            qdjOPT2 += pkt.getNumLoss()
        elif pkt.getPacketCode() == '0x1569' and pkt.getLossType() == 'QDJ REDUNDANT':
            qdjRedundant += pkt.getNumLoss()
        elif pkt.getPacketCode() == '0x1569' and pkt.getLossType() == 'QDJ_STALE_DROPPED':
            qdjStaleDropped += pkt.getNumLoss()
        elif pkt.getPacketCode() == '0x1569' and pkt.getLossType() == 'QDJ RESET':
            qdjReset += pkt.getNumLoss()
        elif pkt.getPacketCode() == '0x1569' and pkt.getLossType() == 'QDJ ENQUEUE DELAYED':
            qdjEnQDelayed += pkt.getNumLoss()
        elif pkt.getPacketCode() == '0x1569' and pkt.getLossType() == 'QDJ OUT OF ORDER':
            qdjOOO += pkt.getNumLoss()        
        elif pkt.getPacketCode() == '0x1569' and pkt.getLossType() == 'RTP DISCARD':
            rtpDiscard += pkt.getNumLoss()

    TotalLoss = NWLoss + qdjUnderflow + qdjOPT2 + qdjRedundant + qdjStaleDropped + qdjReset + qdjEnQDelayed + qdjOOO + rtpDiscard
    return [TotalLoss, LossInTS, NWLoss, qdjUnderflow, qdjOPT2, qdjRedundant, qdjStaleDropped, qdjReset, qdjEnQDelayed, qdjOOO, rtpDiscard]

# Get avg/max/min Jitter from 0x1CD0 IMS Media Metrics pkt
def getJitter(pktList):
    if len(pktList) == 0:
        return [0, 0, 0]
    
    sumJT = 0
    allJT = []
    numRecord = 0
    avgJT = 0
    maxJT = 0
    minJT = 0
    UL_RTCP = []
    re_jitterLine = re.compile(r'.*Inter Jitter.*= (.*)$')
    re_RTCP_Direction = re.compile(r'.*UE_TO_NETWORK.*')


    for pkt in pktList:
        if pkt.getPacketCode() != '0x156A':
            continue
        else:
            for line in pkt.getContent():
                if re_RTCP_Direction.match(line):
                    UL_RTCP.append(pkt)

    for rtcp_pkt in UL_RTCP:
        for line in rtcp_pkt.getContent():
            if re_jitterLine.match(line):
                sumJT += int(re_jitterLine.match(line).groups()[0])//16 # Get sum (Jitter measured in RTP timestamp, need to divided by 16)
                numRecord += 1
                allJT.append(int(re_jitterLine.match(line).groups()[0])//16)
    
    if numRecord != 0:
        avgJT = int(sumJT/numRecord) # Get AVG
    if len(allJT) != 0:
        maxJT = max(allJT)
        minJT = min(allJT)

    return [avgJT, maxJT, minJT]

# Get decoder metrices from 0x156C (Frame Delay, Target Delay, Q size)
def getDecoderMetrics(pktList):
    if len(pktList) == 0:
        return [0, 0, 0, 0, 0, 0, 0, 0, 0]

    sumFD = 0
    allFD = []
    FD_record = 0
    AvgFD = 0
    MaxFD = 0
    MinFD = 0
    re_FD = re.compile(r'^Frame Delay.* = (.*)$')
    
    sumTD = 0
    allTD = []
    TD_record = 0
    AvgTD = 0
    MaxTD = 0
    MinTD = 0
    re_TD = re.compile(r'^Target delay.* = (.*)$')
    
    sumQ = 0
    allQ = []
    Q_record = 0
    AvgQ = 0
    MaxQ = 0
    MinQ = 0
    re_Q = re.compile(r'^Q Size.* = (.*)$')

    for pkt in pktList:
        if pkt.getPacketCode() != '0x156C' or not pkt.isInTalkspurt():
            continue
        else:
            for line in pkt.getContent():
                if re_FD.match(line):
                    sumFD += int(re_FD.match(line).groups()[0]) # Get sum
                    FD_record += 1
                    allFD.append(int(re_FD.match(line).groups()[0]))
                elif re_TD.match(line):
                    sumTD += int(re_TD.match(line).groups()[0]) # Get sum
                    TD_record += 1
                    allTD.append(int(re_TD.match(line).groups()[0]))                    
                elif re_Q.match(line):
                    sumQ += int(re_Q.match(line).groups()[0]) # Get sum
                    Q_record += 1
                    allQ.append(int(re_Q.match(line).groups()[0]))
    if FD_record != 0:
        AvgFD = int(sumFD/FD_record) # Get AVG
    if len(allFD) != 0:
        MaxFD = max(allFD)
        MinFD = min(allFD)

    if TD_record != 0:
        AvgTD = int(sumTD/TD_record) # Get AVG
    if len(allTD) != 0:
        MaxTD = max(allTD)
        MinTD = min(allTD)

    if Q_record != 0:
        AvgQ = int(sumQ/Q_record) # Get AVG
    if len(allQ) != 0:
        MaxQ = max(allQ)
        MinQ = min(allQ)

    return [AvgFD, MaxFD, MinFD, AvgTD, MaxTD, MinTD, AvgQ, MaxQ, MinQ]

# Get N2N handover KPI (Total num of HO and HO during talkspurt, CP/UP delay)
def getHandoverKPI(pktList):
    if len(pktList) == 0:
        return [0, 0, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 0, 0]    
    
    allHO = []
    TotalHO = 0
    HO_In_TS = []
    TotalHO_in_TS = 0
    CPDelay = []
    AvgCPDelay = 'N/A'
    MaxCPDelay = 'N/A'
    MinCPDelay = 'N/A'
    RTP_During_HO = []
    UPDelay = []
    AvgUPDelay = 'N/A'
    MaxUPDelay = 'N/A'
    MinUPDelay = 'N/A'
    RTP_During_HO_TS = []
    CPDelay_TS = []
    AvgCPDelay_TS = 'N/A'
    MaxCPDelay_TS = 'N/A'
    MinCPDelay_TS = 'N/A'
    UPDelay_TS = []
    AvgUPDelay_TS = 'N/A'
    MaxUPDelay_TS = 'N/A'
    MinUPDelay_TS = 'N/A'
    HO_RTP_Loss = 0
    HO_RTP_Loss_TS = 0


    # Find the start and end event of HO, the last DL RTP pkt before HO, and the first DL RTP after HO
    n = 0
    while n < len(pktList): 
        HO_Pair = []
        RTP_Pair = []
        isHOSucEventMissing = False
        if pktList[n].getPacketCode() == '0x1FFB' and pktList[n].getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_STARTED_V2': # Find start of HO
            if n + 1 < len(pktList): # Check if next pkt index exceed length of pkt list
                for check_start in range(n + 1, len(pktList)): # Check if HO suc event is missing
                    if pktList[check_start].getPacketCode() == '0x1FFB' and pktList[check_start].getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_STARTED_V2':
                        isHOSucEventMissing = True
                        break
                    elif pktList[check_start].getPacketCode() == '0x1FFB' and pktList[check_start].getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_SUCCESS':
                        break
            else:
                isHOSucEventMissing = True

            if isHOSucEventMissing: # If HO suc event is missing, skip current HO
                n += 1
                continue

            HO_Pair.append(pktList[n]) # Add start event to HO pair
            HO_start_index = n
            m = HO_start_index
            while m >= 0: # Find last RTP before HO
                if pktList[m].getPacketCode() == '0x1568':
                    RTP_pkt_before_HO = LogPacket_RTP(pktList[m]) # Convert to RTP sub-class to get direction
                    if RTP_pkt_before_HO.getDirection() == 'NETWORK_TO_UE' and RTP_pkt_before_HO.getMediaType() == 'AUDIO':
                        RTP_Pair.append(pktList[m]) # Add RTP pkt before HO to RTP pair
                        break
                    else:
                        m -= 1
                        continue
                else:
                    m -= 1
                    continue

            for i in range(HO_start_index, len(pktList)):
                if pktList[i].getPacketCode() == '0x1FFB' and pktList[i].getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_SUCCESS': # Find end of HO
                    HO_Pair.append(pktList[i]) # Add suc event to HO pair
                    # print('HO start: ', HO_Pair[0].getTimestamp())
                    # print('HO suc: ', HO_Pair[1].getTimestamp())
                    if len(HO_Pair) != 2: # If HO start and end event not in pair, ignore it and reset HO pair
                        HO_Pair = []
                        break
                    else:
                        allHO.append(HO_Pair) # Add HO pair to allHO list
                        if HO_Pair[1].isInTalkspurt(): # If HO is during talkspurt, add HO pair to HO_In_TS list
                            HO_In_TS.append(HO_Pair)
                            #print('HO in TS: ' + HO_Pair[0].getTimestamp())
                    HO_Pair = [] # Reset HO pair
                    HO_suc_Index = i
                    for j in range(HO_suc_Index, len(pktList)):
                        if pktList[j].getPacketCode() == '0x1568': # Find the first DL RTP pkt after HO
                            RTP_pkt_after_HO = LogPacket_RTP(pktList[j]) # Convert to RTP sub-class to get direction
                            if RTP_pkt_after_HO.getDirection() == 'NETWORK_TO_UE' and RTP_pkt_after_HO.getMediaType() == 'AUDIO':
                                # print('HO start: ', RTP_Pair[0].getTimestamp())
                                # print('HO suc: ', RTP_Pair[1].getTimestamp())
                                RTP_Pair.append(pktList[j]) # Add RTP pkt after HO to RTP pair
                                if len(RTP_Pair) != 2: # If RTP pkt not in pair, ignore it and reset RTP pair
                                    RTP_Pair = []
                                    break
                                else:
                                    RTP_During_HO.append(RTP_Pair) # Add RTP pair to RTP_During_HO list
                                    rtpPKTLoss = LogPacket_RTP(RTP_Pair[1]).getSequence() - LogPacket_RTP(RTP_Pair[0]).getSequence()
                                    if rtpPKTLoss >= 2: # Check if pkt loss during HO
                                        HO_RTP_Loss += rtpPKTLoss - 1
                                    if RTP_Pair[0].isInTalkspurt() and RTP_Pair[1].isInTalkspurt(): # If during HO, add RTP pair to RTP_During_HO_TS
                                        RTP_During_HO_TS.append(RTP_Pair)
                                        if rtpPKTLoss >= 2: # Check if pkt loss during HO and talkspurt
                                            HO_RTP_Loss_TS += rtpPKTLoss - 1
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
    
    if len(allHO) != 0:
        TotalHO = len(allHO) # Get total num of HO
        for ho in allHO:
            CPDelay.append(LogPacket.getDelay(ho[1], ho[0])) # Get CP delays
    if len(HO_In_TS) != 0:
        TotalHO_in_TS = len(HO_In_TS) # Get total num of HO during talkspurt
        for ho in HO_In_TS:
            CPDelay_TS.append(LogPacket.getDelay(ho[1], ho[0])) # Get CP delays in talkspurt
    if len(RTP_During_HO) != 0:
        for rtp in RTP_During_HO:
            UPDelay.append(LogPacket.getDelay(rtp[1], rtp[0])) # Get UP delays
    if len(RTP_During_HO_TS) != 0:
        for rtp in RTP_During_HO_TS:
            UPDelay_TS.append(LogPacket.getDelay(rtp[1], rtp[0])) # Get UP delays in talkspurt
    
    # Get avg/max/min of CP delay
    CPDelayLen = len(CPDelay)
    if CPDelayLen != 0:
        AvgCPDelay = int(sum(CPDelay)/CPDelayLen)
        MaxCPDelay = max(CPDelay)
        MinCPDelay = min(CPDelay)

    # Get avg/max/min of CP delay in talkspurt
    CPDelayLen_TS = len(CPDelay_TS)
    if CPDelayLen_TS != 0:
        AvgCPDelay_TS = int(sum(CPDelay_TS)/CPDelayLen_TS)
        MaxCPDelay_TS = max(CPDelay_TS)
        MinCPDelay_TS = min(CPDelay_TS)

    # Get avg/max/min of UP delay
    UPDelayLen = len(UPDelay)
    if UPDelayLen != 0:
        AvgUPDelay = int(sum(UPDelay)/UPDelayLen)
        MaxUPDelay = max(UPDelay)
        MinUPDelay = min(UPDelay)

    # Get avg/max/min of UP delay in talkspurt
    UPDelayLen_TS = len(UPDelay_TS)
    if UPDelayLen_TS != 0:
        AvgUPDelay_TS = int(sum(UPDelay_TS)/UPDelayLen_TS)
        MaxUPDelay_TS = max(UPDelay_TS)
        MinUPDelay_TS = min(UPDelay_TS)

    return [TotalHO, TotalHO_in_TS, 
            AvgCPDelay, MaxCPDelay, MinCPDelay, AvgUPDelay, MaxUPDelay, MinUPDelay,
            AvgCPDelay_TS, MaxCPDelay_TS, MinCPDelay_TS, AvgUPDelay_TS, MaxUPDelay_TS, MinUPDelay_TS,
            HO_RTP_Loss, HO_RTP_Loss_TS]

# Get KPI from RTP pkts and add to corresponding rows
for log in logPktList_All_RTP_Logs.values():
    TotalNumRTP.append(getTotalRTP(log)) # Get total num of DL RTP
    
    TotalTalk_Silence = getTotalVoiceSilenceRTP(log) # Get total num of voice and silence RTP
    TotalNumVoiceRTP.append(TotalTalk_Silence[0])
    TotalNumSilenceRTP.append(TotalTalk_Silence[1])

    rtpLoss = getNumRTPLoss(log) # Get num of RTP loss
    TotalRTPLoss.append(rtpLoss[0])
    TotalRTPLossInTS.append(rtpLoss[1])
    NWLoss.append(rtpLoss[2])
    QDJ_Underflow.append(rtpLoss[3])
    QDJ_OPT2.append(rtpLoss[4])
    QDJ_Redundant.append(rtpLoss[5])
    QDJ_Stale_Dropped.append(rtpLoss[6])
    QDJ_Reset.append(rtpLoss[7])
    QDJ_ENQ_Delayed.append(rtpLoss[8])
    QDJ_Out_Of_Order.append(rtpLoss[9])
    RTP_Discard.append(rtpLoss[10])

    rtpBurst = LogPacket_RTP.getPacketBurst(log).values() # Get RTP burst stats
    if len(rtpBurst) != 0:
        NumRTPBurst.append(len(rtpBurst))
        MaxRTPBurst.append(max(rtpBurst))
    else:
        NumRTPBurst.append(0)
        MaxRTPBurst.append(0)

# Get KPI from all pkts and add to corresponding rows
for log in logPktList_All_Logs.values():
    jitters = getJitter(log) # Get jitter KPI
    AvgJitter.append(jitters[0])
    MaxJitter.append(jitters[1])
    MinJitter.append(jitters[2])

# Get talkspurt related KPI and add to corresponding rows
for log in logPktList_All_TS_Logs.values():
    decoderMetrics = getDecoderMetrics(log) # Get decoder metrics
    AvgFrameDelay.append(decoderMetrics[0])
    MaxFrameDelay.append(decoderMetrics[1])
    MinFrameDelay.append(decoderMetrics[2])
    AvgTargetDelay.append(decoderMetrics[3])
    MaxTargetDelay.append(decoderMetrics[4])
    MinTargetDelay.append(decoderMetrics[5])
    AvgQsize.append(decoderMetrics[6])
    MaxQsize.append(decoderMetrics[7])
    MinQsize.append(decoderMetrics[8])

    handoverKPI = getHandoverKPI(log) # Get HO KPI
    TotalHandover.append(handoverKPI[0])
    HandoverInTS.append(handoverKPI[1])
    AvgControlDelay.append(handoverKPI[2])
    MaxControlDelay.append(handoverKPI[3])
    MinControlDelay.append(handoverKPI[4])
    AvgUserDelay.append(handoverKPI[5])
    MaxUserDelay.append(handoverKPI[6])
    MinUserDelay.append(handoverKPI[7])
    AvgControlDelay_TS.append(handoverKPI[8])
    MaxControlDelay_TS.append(handoverKPI[9])
    MinControlDelay_TS.append(handoverKPI[10])
    AvgUserDelay_TS.append(handoverKPI[11])
    MaxUserDelay_TS.append(handoverKPI[12])
    MinUserDelay_TS.append(handoverKPI[13])
    HandoverPktLoss.append(handoverKPI[14])
    HandoverPktLoss_TS.append(handoverKPI[15])

# Calculate RTP loss rate
for i in range(1, len(TotalNumRTP)):
    if TotalNumRTP[i] == 0:
        TotalRTPLossRate.append(0)
    else:
        TotalRTPLossRate.append(float(TotalRTPLoss[i]/TotalNumRTP[i]))

for j in range(1, len(TotalNumVoiceRTP)):
    if TotalNumVoiceRTP[j] == 0:
        TotalRTPLossRateInTS.append(0)
    else:
        TotalRTPLossRateInTS.append(float(TotalRTPLossInTS[j]/TotalNumVoiceRTP[j]))

# Init work book and fill rows with data
wb = Workbook()
ws = wb.active
ws.title = 'IMS_Media_KPI'
ws.append(First_Row)
ws.append(TotalNumRTP)
ws.append(TotalNumVoiceRTP)
ws.append(TotalNumSilenceRTP)
ws.append(TotalRTPLoss)
ws.append(TotalRTPLossRate)
ws.append(TotalRTPLossInTS)
ws.append(TotalRTPLossRateInTS)
ws.append(NWLoss)
ws.append(QDJ_Underflow)
ws.append(QDJ_OPT2)
ws.append(QDJ_Redundant)
ws.append(QDJ_Stale_Dropped)
ws.append(QDJ_Reset)
ws.append(QDJ_ENQ_Delayed)
ws.append(QDJ_Out_Of_Order)
ws.append(RTP_Discard)
ws.append(NumRTPBurst)
ws.append(MaxRTPBurst)
ws.append(AvgJitter)
ws.append(MaxJitter)
ws.append(MinJitter)
ws.append(AvgFrameDelay)
ws.append(MaxFrameDelay)
ws.append(MinFrameDelay)
ws.append(AvgTargetDelay)
ws.append(MaxTargetDelay)
ws.append(MinTargetDelay)
ws.append(AvgQsize)
ws.append(MaxQsize)
ws.append(MinQsize)
ws.append(TotalHandover)
ws.append(HandoverPktLoss)
ws.append(HandoverInTS)
ws.append(HandoverPktLoss_TS)
ws.append(AvgControlDelay)
ws.append(MaxControlDelay)
ws.append(MinControlDelay)
ws.append(AvgControlDelay_TS)
ws.append(MaxControlDelay_TS)
ws.append(MinControlDelay_TS)
ws.append(AvgUserDelay)
ws.append(MaxUserDelay)
ws.append(MinUserDelay)
ws.append(AvgUserDelay_TS)
ws.append(MaxUserDelay_TS)
ws.append(MinUserDelay_TS)

# Save KPI table to excel
dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'IMS_Media_KPI_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(IMS_KPI.workingDir, saveFileName)
print(datetime.now().strftime("%H:%M:%S"), '(IMS_Media_KPI) ' + 'KPI Summary extracted: ' + savePath)
wb.save(savePath)