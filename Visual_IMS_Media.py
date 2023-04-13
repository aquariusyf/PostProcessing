from PostProcessingUtils import LogPacket_Talkspurt, LogPacket_RTP, LogPacket_PHY_BLER, LogPacket_CDRX, PostProcessingUtils
from FilterMask import *
from datetime import datetime
import sys
import matplotlib.pyplot as plt
import pandas as pd

filter_mask[LOG_FILTER] = [0xB821, 0x1568, 0x1569, 0x156A, 0x156C, 0xB800, 0xB801, 0xB808, 
                           0xB809, 0xB80A, 0xB80B, 0xB814, 0x1CD0, 0xB887, 0xB883, 0xB890]

Visual_IMS = PostProcessingUtils()
Visual_IMS.getArgv(sys.argv)
Visual_IMS.scanWorkingDir()
if not Visual_IMS.skipFitlerLogs():
    Visual_IMS.convertToText('Visual_IMS_Media')
Visual_IMS.scanWorkingDir('_flt_text.txt', 'Visual_IMS_Media')
Visual_IMS.initLogPacketList()
LogPkt_All = Visual_IMS.getLogPacketList()
RTP_LogPkt_All = {}
#CDRX_LogPkt_All = {}
Attr_List = []
LogName_List = []
figure, axis = plt.subplots(2, 1)
UE1 = axis[0]
UE2 = axis[1]

TALKSPURT = 10
UL_TALKSPURT = -10
SILENCE = 0.2
UL_SILENCE = -0.2
HO_START = 7
HO_SUC = 9
#CDRX_ON = 17
#CDRX_OFF = 13
UL_VOICE_THRESHOLD = 30
X_TALKSPURT = 'x_TS'
Y_TALKSPURT = 'y_TS'
X_PKT_LOSS = 'x_PktLoss'
Y_PKT_LOSS = 'y_PktLoss'
X_PKT_BURST = 'x_PktBurst'
Y_PKT_BURST = 'y_PktBurst'
X_HO_START = 'x_HO_start'
Y_HO_START = 'y_HO_start'
X_HO_SUC = 'x_HO_suc'
Y_HO_SUC = 'y_HO_suc'
X_CRC_PASS = 'x_CRC_PASS'
Y_CRC_PASS = 'y_CRC_PASS'
X_CRC_FAIL = 'x_CRC_FAIL'
Y_CRC_FAIL = 'y_CRC_FAIL'
X_UL_RTP = 'x_ul_rtp'
Y_UL_RTP = 'y_ul_rtp'
X_UL_NEW_TX = 'x_new_tx'
Y_UL_NEW_TX = 'y_new_tx'
X_UL_RE_TX = 'x_re_tx'
Y_UL_RE_TX = 'y_re_tx'
#X_CDRX = 'x_cdrx'
#Y_CDRX = 'y_cdrx'

for key, value in LogPkt_All.items():
    rtpPktList = []
    #cdrxPktList = []
    for pkt in LogPkt_All[key]:
        if pkt.getPacketCode() == '0x1568' or pkt.getPacketCode() == '0x1569':
           rtpPktList.append(LogPacket_RTP(pkt))
        #if pkt.getPacketCode() == '0xB890':
            #cdrxPktList.append(LogPacket_CDRX(pkt))
    RTP_LogPkt_All[key] = rtpPktList
    #CDRX_LogPkt_All[key] = cdrxPktList
            
for logName in LogPkt_All.keys():
    Plot_Attr_Single = {X_TALKSPURT: [], Y_TALKSPURT: [],
                        X_PKT_LOSS: [], Y_PKT_LOSS: [],
                        X_PKT_BURST: [], Y_PKT_BURST: [],
                        X_HO_START: [], Y_HO_START: [],
                        X_HO_SUC: [], Y_HO_SUC: [],
                        X_CRC_PASS: [], Y_CRC_PASS: [],
                        X_CRC_FAIL: [], Y_CRC_FAIL: [],
                        X_UL_RTP: [], Y_UL_RTP: [],
                        X_UL_NEW_TX: [], Y_UL_NEW_TX: [],
                        X_UL_RE_TX: [], Y_UL_RE_TX: []}
    RTP_Packet_List = RTP_LogPkt_All[logName]
    PktBurst = LogPacket_RTP.getPacketBurst(RTP_Packet_List)
    Plot_Attr_Single[Y_PKT_BURST] = PktBurst.values()
    for key in PktBurst.keys():
        Plot_Attr_Single[X_PKT_BURST].append(key)
    #CDRX_Packet_List = CDRX_LogPkt_All[logName]
    #AWAKE = 'ONDUR_INACT_TIMER'
    #SLEEP = 'INACTIVE'
    
    LogPacket_Talkspurt.findTalkspurt(RTP_Packet_List)
    for rtpPkt in RTP_Packet_List:
        if rtpPkt.getPacketCode() == '0x1568':
            if rtpPkt.getDirection() == 'NETWORK_TO_UE' and rtpPkt.getMediaType() == 'AUDIO' and rtpPkt.isInTalkspurt():
                Plot_Attr_Single[Y_TALKSPURT].append(TALKSPURT)
                Plot_Attr_Single[X_TALKSPURT].append(rtpPkt.getTimestamp())
            elif rtpPkt.getDirection() == 'NETWORK_TO_UE' and rtpPkt.getMediaType() == 'AUDIO' and not rtpPkt.isInTalkspurt():
                Plot_Attr_Single[Y_TALKSPURT].append(SILENCE)
                Plot_Attr_Single[X_TALKSPURT].append(rtpPkt.getTimestamp())
            elif rtpPkt.getDirection() == 'UE_TO_NETWORK' and rtpPkt.getMediaType() == 'AUDIO':
                if rtpPkt.getPayloadSize() >= 30:
                    Plot_Attr_Single[Y_UL_RTP].append(UL_TALKSPURT)
                    Plot_Attr_Single[X_UL_RTP].append(rtpPkt.getTimestamp())
                else:
                    Plot_Attr_Single[Y_UL_RTP].append(UL_SILENCE)
                    Plot_Attr_Single[X_UL_RTP].append(rtpPkt.getTimestamp())                                      
        elif rtpPkt.getPacketCode() == '0x1569':
            Plot_Attr_Single[Y_PKT_LOSS].append(rtpPkt.getNumLoss())
            Plot_Attr_Single[X_PKT_LOSS].append(rtpPkt.getTimestamp())           
        
    for logPkt in LogPkt_All[logName]:
        if logPkt.getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_STARTED_V2':
            Plot_Attr_Single[Y_HO_START].append(HO_START)
            Plot_Attr_Single[X_HO_START].append(logPkt.getTimestamp())
        elif logPkt.getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_SUCCESS':
            Plot_Attr_Single[Y_HO_SUC].append(HO_SUC)
            Plot_Attr_Single[X_HO_SUC].append(logPkt.getTimestamp())
        elif logPkt.getPacketCode() == '0xB887' or logPkt.getPacketCode() == '0xB883':
             PHYPkt = LogPacket_PHY_BLER(logPkt)
             if PHYPkt.getnumOfPass_PDSCH() != 0:
                Plot_Attr_Single[Y_CRC_PASS].append(PHYPkt.getnumOfPass_PDSCH())
                Plot_Attr_Single[X_CRC_PASS].append(PHYPkt.getTimestamp())
             if PHYPkt.getnumOfFail_PDSCH() != 0:
                Plot_Attr_Single[Y_CRC_FAIL].append(PHYPkt.getnumOfFail_PDSCH())
                Plot_Attr_Single[X_CRC_FAIL].append(PHYPkt.getTimestamp())      
             if PHYPkt.getnumOfNewTx_PUSCH() != 0:
                Plot_Attr_Single[Y_UL_NEW_TX].append(PHYPkt.getnumOfNewTx_PUSCH()*(-1))
                Plot_Attr_Single[X_UL_NEW_TX].append(PHYPkt.getTimestamp())              
             if PHYPkt.getnumOfReTx_PUSCH() != 0:
                Plot_Attr_Single[Y_UL_RE_TX].append(PHYPkt.getnumOfReTx_PUSCH()*(-1))
                Plot_Attr_Single[X_UL_RE_TX].append(PHYPkt.getTimestamp())
    
    '''for logPkt in CDRX_Packet_List:
        cdrx_events = logPkt.getCDRXEvent()
        for timestamp, event in cdrx_events.items():
            if event == AWAKE:
                Plot_Attr_Single[Y_CDRX].append(CDRX_ON)
                Plot_Attr_Single[X_CDRX].append(timestamp)
            elif event == SLEEP:
                Plot_Attr_Single[Y_CDRX].append(CDRX_OFF)
                Plot_Attr_Single[X_CDRX].append(timestamp)'''           
    
    Attr_List.append(Plot_Attr_Single)
    LogName_List.append(logName)

def plotMediaKPI(Plot_Title = '', Plot_Attributes = {}, Plot_Peer_Side_UL_Attributes = {}, plot = -1):
    if len(Plot_Attributes) == 0 and len(Plot_Peer_Side_UL_Attributes) == 0:
        sys.exit('(Visual_IMS_Media/plotMediaKPI) ' + 'No log packets found or attributes are invalid!') 
    
    if Plot_Attributes != {}:
        #plot.step(pd.to_datetime(Plot_Attributes[X_CDRX]), Plot_Attributes[Y_CDRX], label = "CDRX", color='darkgray', marker='.')
        plot.scatter(pd.to_datetime(Plot_Attributes[X_CRC_PASS]), Plot_Attributes[Y_CRC_PASS], label = "PDSCH CRC PASS", color='limegreen', marker='.')
        plot.scatter(pd.to_datetime(Plot_Attributes[X_CRC_FAIL]), Plot_Attributes[Y_CRC_FAIL], label = "PDSCH CRC FAIL", color='red', marker='.')
        plot.step(pd.to_datetime(Plot_Attributes[X_TALKSPURT]), Plot_Attributes[Y_TALKSPURT], label = "Talkspurt", color='dodgerblue', marker='.')
        plot.scatter(pd.to_datetime(Plot_Attributes[X_HO_START]), Plot_Attributes[Y_HO_START], label = "HO Start", color='black', marker='>')
        plot.scatter(pd.to_datetime(Plot_Attributes[X_HO_SUC]), Plot_Attributes[Y_HO_SUC], label = "HO Success", color='black', marker='s')
        plot.scatter(pd.to_datetime(Plot_Attributes[X_PKT_BURST]), Plot_Attributes[Y_PKT_BURST], label = "DL RTP Burst", color='darkorange', marker='P')
        plot.scatter(pd.to_datetime(Plot_Attributes[X_PKT_LOSS]), Plot_Attributes[Y_PKT_LOSS], label = "DL Pkt Loss", color='red', marker='x')
    if Plot_Peer_Side_UL_Attributes != {}:
        plot.step(pd.to_datetime(Plot_Peer_Side_UL_Attributes[X_UL_RTP]), Plot_Peer_Side_UL_Attributes[Y_UL_RTP], label = "FarEnd UL RTP", color='blueviolet', marker='.' )
        plot.scatter(pd.to_datetime(Plot_Peer_Side_UL_Attributes[X_UL_NEW_TX]), Plot_Peer_Side_UL_Attributes[Y_UL_NEW_TX], label = "FarEnd PUSCH NEW-TX", color='aqua', marker='.')
        plot.scatter(pd.to_datetime(Plot_Peer_Side_UL_Attributes[X_UL_RE_TX]), Plot_Peer_Side_UL_Attributes[Y_UL_RE_TX], label = "FarEnd PUSCH RE-TX", color='red', marker='.')
    plot.legend(loc='upper right')
    plot.set_title(Plot_Title)
    plot.grid(True)

if len(LogName_List) == 0:
    print(datetime.now().strftime("%H:%M:%S"), '(Visual_IMS_Media) ' + 'No filtered text files found!')
elif len(LogName_List) == 1:
    print(datetime.now().strftime("%H:%M:%S"), '(Visual_IMS_Media) ' + 'Found 1 filtered text file only, no peer side plot available')
    plotMediaKPI(LogName_List[0].replace('_flt_text.txt', '_DL'), Attr_List[0], {}, UE1)
    plotMediaKPI(LogName_List[0].replace('_flt_text.txt', '_UL'), {}, Attr_List[0], UE2)
elif len(LogName_List) == 2:
    plotMediaKPI(LogName_List[0].replace('_flt_text.txt', ''), Attr_List[0], Attr_List[1], UE1)
    plotMediaKPI(LogName_List[1].replace('_flt_text.txt', ''), Attr_List[1], Attr_List[0], UE2)
elif len(LogName_List) > 2:
    print(datetime.now().strftime("%H:%M:%S"), '(Visual_IMS_Media) ' + 'More than 2 filtered text files found, will plot for first two')
    plotMediaKPI(LogName_List[0].replace('_flt_text.txt', ''), Attr_List[0], Attr_List[1], UE1)
    plotMediaKPI(LogName_List[1].replace('_flt_text.txt', ''), Attr_List[1], Attr_List[0], UE2)
plt.show()