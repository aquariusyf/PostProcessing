from PostProcessingUtils import LogPacket_RTP, LogPacket_PDSCH, PostProcessingUtils
from FilterMask import *
import sys
import matplotlib.pyplot as plt

if __name__=='__main__':
    
    filter_mask[LOG_FILTER] = [0xB821, 0x1568, 0x1569, 0x156A, 0x156C, 0xB800, 0xB801, 0xB808, 
                               0xB809, 0xB80A, 0xB80B, 0xB814, 0x1CD0, 0xB887]
    
    findTS = PostProcessingUtils()
    findTS.getArgv(sys.argv)
    findTS.scanWorkingDir()
    findTS.convertToText()
    findTS.scanWorkingDir('_flt_text.txt')
    findTS.initLogPacketList()
    logPktList = findTS.getLogPacketList()
    PDSCHPktList = []

    x_TS = []
    y_TS = []
    x_PktLoss = []
    y_PktLoss = []
    x_Burst = []
    y_Burst = []
    x_HO_start = []
    y_HO_start = []
    x_HO_suc = []
    y_HO_suc = []
    x_CRC_PASS = []
    y_CRC_PASS = []
    x_CRC_FAIL = []
    y_CRC_FAIL = []

    for key in logPktList.keys():
        for logPkt in logPktList[key]:
            if logPkt.getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_STARTED_V2':
                y_HO_start.append(5)
                x_HO_start.append(logPkt.getAbsTime())
            elif logPkt.getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_SUCCESS':
                y_HO_suc.append(6)
                x_HO_suc.append(logPkt.getAbsTime())
    
    for key in logPktList.keys():
        RtpPktList = []
        for logPkt in logPktList[key]:
            if logPkt.getPacketCode() == '0x1568' or logPkt.getPacketCode() == '0x1569':
                RtpPktList.append(LogPacket_RTP(logPkt))
            elif logPkt.getPacketCode() == '0xB887':
                PDSCHPktList.append(LogPacket_PDSCH(logPkt))
        logPktList[key] = RtpPktList

    
    '''for value in logPktList.values():
        for p in value:
            print(p.getTitle(), p.getDirection(), p.getRatType(), p.getSequence(), p.getRtpTimeStamp(), 
                  p.getMediaType(), p.getCodecType(), p.getPayloadSize(), p.getNumLoss(), 
                  p.getLossSeqNum(), p.getLossType())'''
    
    result = {}
    for value in logPktList.values():
        if len(value) != 0:
            result = LogPacket_RTP.getPacketBurst(value)
        for n in range(0, len(value)):
            # print(pkt.getHeadline() + ' is in talk spurt: ', pkt.isInTalkspurt())
            # if value[n].isInBurst():
                # print(value[n].getDirection() + ' Sequence: ', value[n].getSequence(), value[n].getTimestamp())
            if value[n].isInTalkspurt() and value[n].getPacketCode() == '0x1568' and value[n].getDirection() == 'NETWORK_TO_UE':
                y_TS.append(10)
                x_TS.append(value[n].getAbsTime())
            elif not value[n].isInTalkspurt() and value[n].getPacketCode() == '0x1568' and value[n].getDirection() == 'NETWORK_TO_UE':
                y_TS.append(0)
                x_TS.append(value[n].getAbsTime())
            elif value[n].getPacketCode() == '0x1569':
                y_PktLoss.append(value[n].getNumLoss())
                x_PktLoss.append(value[n].getAbsTime())

    for key, value in result.items():
        # print(key, ': ', value)
        y_Burst.append(value)
        x_Burst.append(key)

    for m in range(0, len(PDSCHPktList)):
        if PDSCHPktList[m].getNumOfPass() != 0:
            y_CRC_PASS.append(PDSCHPktList[m].getNumOfPass()*0.1)
            x_CRC_PASS.append(PDSCHPktList[m].getAbsTime())
        
        if PDSCHPktList[m].getNumOfFail() != 0:
            y_CRC_FAIL.append(PDSCHPktList[m].getNumOfFail()*(-1))
            x_CRC_FAIL.append(PDSCHPktList[m].getAbsTime())

    plt.scatter(x_PktLoss, y_PktLoss, label = "Pkt Loss", color='red', marker='x')  
    plt.scatter(x_HO_start, y_HO_start, label = "HO Start", color='blue', marker='>')
    plt.scatter(x_HO_suc, y_HO_suc, label = "HO Success", color='green', marker='o')
    plt.scatter(x_Burst, y_Burst, label = "RTP Burst", color='orange', marker='*')
    plt.scatter(x_CRC_PASS, y_CRC_PASS, label = "PDSCH CRC PASS", color='green', marker='+')
    plt.scatter(x_CRC_FAIL, y_CRC_FAIL, label = "PDSCH CRC FAIL", color='red', marker='X')  
    plt.plot(x_TS, y_TS, label = "Talkspurt")
    # plt.gcf().autofmt_xdate()
    plt.legend()
    plt.xlabel('Time')
    # plt.ylabel('Num of Pkts')
    plt.title('Voice Call Stats')
    plt.grid(True)
    plt.show()