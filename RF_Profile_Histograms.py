from PostProcessingUtils import PostProcessingUtils, LogPacket_RSRP_SNR, LogPacket_HO
from FilterMask import *
import sys
import matplotlib.pyplot as plt
import pandas as pd

filter_mask[LOG_FILTER] = [0xB821, 0xB8DD]
filter_mask[EVENT_FILTER] = [3188, 3190, 3325, 3368]

RF_Profile = PostProcessingUtils()
RF_Profile.getArgv(sys.argv)
RF_Profile.scanWorkingDir()
if not RF_Profile.skipFitlerLogs():
    RF_Profile.convertToText('RF_Profile_Histograms')
RF_Profile.scanWorkingDir('_flt_text.txt', 'RF_Profile_Histograms')
RF_Profile.initLogPacketList()
LogPkt_All = RF_Profile.getLogPacketList()

HO_START = -35
HO_SUC = -30
HO_F = -20
RLF = -40
RRC_REES = -50
ARFCN = 'arfcn'
PCI = 'pci'
RX0 = 'Rx0'
RX1 = 'Rx1'
RX2 = 'Rx2'
RX3 = 'Rx3'
X_RX0_RSRP = 'x_rx0_rsrp'
Y_RX0_RSRP = 'y_rx0_rsrp'
X_RX1_RSRP = 'x_rx1_rsrp'
Y_RX1_RSRP = 'y_rx1_rsrp'
X_RX2_RSRP = 'x_rx2_rsrp'
Y_RX2_RSRP = 'y_rx2_rsrp'
X_RX3_RSRP = 'x_rx3_rsrp'
Y_RX3_RSRP = 'y_rx3_rsrp'
X_RX0_SNR = 'x_rx0_snr'
Y_RX0_SNR = 'y_rx0_snr'
X_RX1_SNR = 'x_rx1_snr'
Y_RX1_SNR = 'y_rx1_snr'
X_RX2_SNR = 'x_rx2_snr'
Y_RX2_SNR = 'y_rx2_snr'
X_RX3_SNR = 'x_rx3_snr'
Y_RX3_SNR = 'y_rx3_snr'
X_HO_START = 'x_HO_start'
Y_HO_START = 'y_HO_start'
X_HO_SUC = 'x_HO_suc'
Y_HO_SUC = 'y_HO_suc'
X_HO_FAIL = 'x_HO_fail'
Y_HO_FAIL = 'y_HO_fail'
X_RLF = 'x_rlf'
Y_RLF = 'y_rlf'
X_RRC_REES = 'x_rrc_rees'
Y_RRC_REES = 'y_rrc_rees'

RSRP_60 = 'RSRP > -60'
RSRP_60_65 = '-60 > RSRP > -65'
RSRP_65_70 = '-65 > RSRP > -70'
RSRP_70_75 = '-70 > RSRP > -75'
RSRP_75_80 = '-75 > RSRP > -80'
RSRP_80_85 = '-80 > RSRP > -85'
RSRP_85_90 = '-85 > RSRP > -90'
RSRP_90_95 = '-90 > RSRP > -95'
RSRP_95_100 = '-95 > RSRP > -100'
RSRP_100_105 = '-100 > RSRP > -105'
RSRP_105_110 = '-105 > RSRP > -110'
RSRP_110_115 = '-110 > RSRP > -115'
RSRP_115_120 = '-115 > RSRP > -120'
RSRP_120 = 'RSRP < -120'

SNR_30 = 'SNR > 30'
SNR_30_27 = '27 > SNR > 30'
SNR_27_24 = '24 > SNR > 27'
SNR_24_21 = '21 > SNR > 24'
SNR_21_18 = '18 > SNR > 21'
SNR_18_15 = '15 > SNR > 18'
SNR_15_12 = '12 > SNR > 15'
SNR_12_9 = '9 > SNR > 12'
SNR_9_6 = '6 > SNR > 9'
SNR_6_3 = '3 > SNR > 6'
SNR_3_0 = '0 > SNR > 3'
SNR_0_n3 = '0 > SNR > -3'
SNR_n3_n6 = '-3 > SNR > -6'
SNR_n6 = 'SNR < -6'

RSRP_THRES_60 = -60
RSRP_THRES_65 = -65
RSRP_THRES_70 = -70
RSRP_THRES_75 = -75
RSRP_THRES_80 = -80
RSRP_THRES_85 = -85
RSRP_THRES_90 = -90
RSRP_THRES_95 = -95
RSRP_THRES_100 = -100
RSRP_THRES_105 = -105
RSRP_THRES_110 = -110
RSRP_THRES_115 = -115
RSRP_THRES_120 = -120
SNR_THRES_30 = 30
SNR_THRES_27 = 27
SNR_THRES_24 = 24
SNR_THRES_21 = 21
SNR_THRES_18 = 18
SNR_THRES_15 = 15
SNR_THRES_12 = 12
SNR_THRES_9 = 9
SNR_THRES_6 = 6
SNR_THRES_3 = 3
SNR_THRES_0 = 0
SNR_THRES_n3 = -3
SNR_THRES_n6 = -6

Plot_Attr_TD = {X_RX0_RSRP: [], Y_RX0_RSRP: [],
                X_RX1_RSRP: [], Y_RX1_RSRP: [],
                X_RX2_RSRP: [], Y_RX2_RSRP: [],
                X_RX3_RSRP: [], Y_RX3_RSRP: [],
                X_RX0_SNR: [], Y_RX0_SNR: [],
                X_RX1_SNR: [], Y_RX1_SNR: [],
                X_RX2_SNR: [], Y_RX2_SNR: [],
                X_RX3_SNR: [], Y_RX3_SNR: [],
                X_HO_START: [], Y_HO_START: [],                        
                X_HO_SUC: [], Y_HO_SUC: [],
                X_HO_FAIL: [], Y_HO_FAIL: [],
                X_RLF: [], Y_RLF: [],
                X_RRC_REES: [], Y_RRC_REES: []}

RSRP_Histogram_Attr = {RSRP_60: 0, RSRP_60_65: 0, RSRP_65_70: 0, RSRP_70_75: 0, 
                       RSRP_75_80: 0, RSRP_80_85: 0, RSRP_85_90: 0, RSRP_90_95: 0,
                       RSRP_95_100: 0, RSRP_100_105: 0, RSRP_105_110: 0, RSRP_110_115: 0,
                       RSRP_115_120: 0, RSRP_120: 0}
SNR_Histogram_Attr = {SNR_30: 0, SNR_30_27: 0, SNR_27_24: 0, SNR_24_21: 0,
                      SNR_21_18: 0, SNR_18_15: 0, SNR_15_12: 0, SNR_12_9: 0,
                      SNR_9_6: 0, SNR_6_3: 0, SNR_3_0: 0, SNR_0_n3: 0,
                      SNR_n3_n6: 0, SNR_n6: 0}

TotalNumHO = 0
TotalNumHOFailure = 0
TotalNumRLF = 0
PCI_All = []

figure, axis = plt.subplots(3, 1)
TD_plot = axis[0]
Histogram_RSRP = axis[1]
Histogram_SNR = axis[2]
figure.tight_layout()

for key in LogPkt_All.keys():
    B8DD_Pkt_List = []
    for pkt in LogPkt_All[key]:
        if pkt.getPacketCode() == '0xB8DD':
            B8DD_Pkt_List.append(LogPacket_RSRP_SNR(pkt))
        if pkt.getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_STARTED_V2':
            Plot_Attr_TD[Y_HO_START].append(HO_START)
            Plot_Attr_TD[X_HO_START].append(pkt.getTimestamp())
            HOpkt = LogPacket_HO(pkt)
            PCI_All.append(HOpkt.getTargetCellInfo()[PCI])
            PCI_All.append(HOpkt.getSourceCellInfo()[PCI])
        elif pkt.getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_SUCCESS':
            Plot_Attr_TD[Y_HO_SUC].append(HO_SUC)
            Plot_Attr_TD[X_HO_SUC].append(pkt.getTimestamp())
            TotalNumHO += 1
        elif pkt.getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_FAILURE_V5':
            Plot_Attr_TD[Y_HO_FAIL].append(HO_F)
            Plot_Attr_TD[X_HO_FAIL].append(pkt.getTimestamp())
            TotalNumHOFailure += 1
        elif pkt.getTitle() == 'Event  --  EVENT_NR5G_RRC_RADIO_LINK_FAILURE_STAT_V7':
            Plot_Attr_TD[Y_RLF].append(RLF)
            Plot_Attr_TD[X_RLF].append(pkt.getTimestamp())
            TotalNumRLF += 1
        elif pkt.getTitle() == 'NR5G RRC OTA Packet  --  UL_CCCH / RRC Reestablishment Req':
            Plot_Attr_TD[Y_RRC_REES].append(RRC_REES)
            Plot_Attr_TD[X_RRC_REES].append(pkt.getTimestamp())
    
    for b8dd_pkt in B8DD_Pkt_List:
        rsrp = b8dd_pkt.getRSRP()
        snr = b8dd_pkt.getSNR()
        
        if(rsrp[RX0] != 'NA'):
            Plot_Attr_TD[Y_RX0_RSRP].append(rsrp[RX0])
            Plot_Attr_TD[X_RX0_RSRP].append(b8dd_pkt.getTimestamp())
        if(rsrp[RX1] != 'NA'):
            Plot_Attr_TD[Y_RX1_RSRP].append(rsrp[RX1])
            Plot_Attr_TD[X_RX1_RSRP].append(b8dd_pkt.getTimestamp())
        if(rsrp[RX2] != 'NA'):
            Plot_Attr_TD[Y_RX2_RSRP].append(rsrp[RX2])
            Plot_Attr_TD[X_RX2_RSRP].append(b8dd_pkt.getTimestamp())    
        if(rsrp[RX3] != 'NA'):
            Plot_Attr_TD[Y_RX3_RSRP].append(rsrp[RX3])
            Plot_Attr_TD[X_RX3_RSRP].append(b8dd_pkt.getTimestamp())
            
        if(snr[RX0] != 'NA'):
            Plot_Attr_TD[Y_RX0_SNR].append(snr[RX0])
            Plot_Attr_TD[X_RX0_SNR].append(b8dd_pkt.getTimestamp())
        if(snr[RX1] != 'NA'):
            Plot_Attr_TD[Y_RX1_SNR].append(snr[RX1])
            Plot_Attr_TD[X_RX1_SNR].append(b8dd_pkt.getTimestamp())
        if(snr[RX2] != 'NA'):
            Plot_Attr_TD[Y_RX2_SNR].append(snr[RX2])
            Plot_Attr_TD[X_RX2_SNR].append(b8dd_pkt.getTimestamp())    
        if(snr[RX3] != 'NA'):
            Plot_Attr_TD[Y_RX3_SNR].append(snr[RX3])
            Plot_Attr_TD[X_RX3_SNR].append(b8dd_pkt.getTimestamp())

for value in Plot_Attr_TD[Y_RX0_RSRP]:
    if value >= RSRP_THRES_60:
        RSRP_Histogram_Attr[RSRP_60] += 1
    elif value < RSRP_THRES_60 and value >= RSRP_THRES_65:
        RSRP_Histogram_Attr[RSRP_60_65] += 1
    elif value < RSRP_THRES_65 and value >= RSRP_THRES_70:
        RSRP_Histogram_Attr[RSRP_65_70] += 1
    elif value < RSRP_THRES_70 and value >= RSRP_THRES_75:
        RSRP_Histogram_Attr[RSRP_70_75] += 1
    elif value < RSRP_THRES_75 and value >= RSRP_THRES_80:
        RSRP_Histogram_Attr[RSRP_75_80] += 1
    elif value < RSRP_THRES_80 and value >= RSRP_THRES_85:
        RSRP_Histogram_Attr[RSRP_80_85] += 1
    elif value < RSRP_THRES_85 and value >= RSRP_THRES_90:
        RSRP_Histogram_Attr[RSRP_85_90] += 1      
    elif value < RSRP_THRES_90 and value >= RSRP_THRES_95:
        RSRP_Histogram_Attr[RSRP_90_95] += 1
    elif value < RSRP_THRES_95 and value >= RSRP_THRES_100:
        RSRP_Histogram_Attr[RSRP_95_100] += 1
    elif value < RSRP_THRES_100 and value >= RSRP_THRES_105:
        RSRP_Histogram_Attr[RSRP_100_105] += 1
    elif value < RSRP_THRES_105 and value >= RSRP_THRES_110:
        RSRP_Histogram_Attr[RSRP_105_110] += 1
    elif value < RSRP_THRES_110 and value >= RSRP_THRES_115:
        RSRP_Histogram_Attr[RSRP_110_115] += 1
    elif value < RSRP_THRES_115 and value >= RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_115_120] += 1
    elif value < RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_120] += 1
        
for value in Plot_Attr_TD[Y_RX1_RSRP]:
    if value >= RSRP_THRES_60:
        RSRP_Histogram_Attr[RSRP_60] += 1
    elif value < RSRP_THRES_60 and value >= RSRP_THRES_65:
        RSRP_Histogram_Attr[RSRP_60_65] += 1
    elif value < RSRP_THRES_65 and value >= RSRP_THRES_70:
        RSRP_Histogram_Attr[RSRP_65_70] += 1
    elif value < RSRP_THRES_70 and value >= RSRP_THRES_75:
        RSRP_Histogram_Attr[RSRP_70_75] += 1
    elif value < RSRP_THRES_75 and value >= RSRP_THRES_80:
        RSRP_Histogram_Attr[RSRP_75_80] += 1
    elif value < RSRP_THRES_80 and value >= RSRP_THRES_85:
        RSRP_Histogram_Attr[RSRP_80_85] += 1
    elif value < RSRP_THRES_85 and value >= RSRP_THRES_90:
        RSRP_Histogram_Attr[RSRP_85_90] += 1      
    elif value < RSRP_THRES_90 and value >= RSRP_THRES_95:
        RSRP_Histogram_Attr[RSRP_90_95] += 1
    elif value < RSRP_THRES_95 and value >= RSRP_THRES_100:
        RSRP_Histogram_Attr[RSRP_95_100] += 1
    elif value < RSRP_THRES_100 and value >= RSRP_THRES_105:
        RSRP_Histogram_Attr[RSRP_100_105] += 1
    elif value < RSRP_THRES_105 and value >= RSRP_THRES_110:
        RSRP_Histogram_Attr[RSRP_105_110] += 1
    elif value < RSRP_THRES_110 and value >= RSRP_THRES_115:
        RSRP_Histogram_Attr[RSRP_110_115] += 1
    elif value < RSRP_THRES_115 and value >= RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_115_120] += 1
    elif value < RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_120] += 1
        
for value in Plot_Attr_TD[Y_RX2_RSRP]:
    if value >= RSRP_THRES_60:
        RSRP_Histogram_Attr[RSRP_60] += 1
    elif value < RSRP_THRES_60 and value >= RSRP_THRES_65:
        RSRP_Histogram_Attr[RSRP_60_65] += 1
    elif value < RSRP_THRES_65 and value >= RSRP_THRES_70:
        RSRP_Histogram_Attr[RSRP_65_70] += 1
    elif value < RSRP_THRES_70 and value >= RSRP_THRES_75:
        RSRP_Histogram_Attr[RSRP_70_75] += 1
    elif value < RSRP_THRES_75 and value >= RSRP_THRES_80:
        RSRP_Histogram_Attr[RSRP_75_80] += 1
    elif value < RSRP_THRES_80 and value >= RSRP_THRES_85:
        RSRP_Histogram_Attr[RSRP_80_85] += 1
    elif value < RSRP_THRES_85 and value >= RSRP_THRES_90:
        RSRP_Histogram_Attr[RSRP_85_90] += 1      
    elif value < RSRP_THRES_90 and value >= RSRP_THRES_95:
        RSRP_Histogram_Attr[RSRP_90_95] += 1
    elif value < RSRP_THRES_95 and value >= RSRP_THRES_100:
        RSRP_Histogram_Attr[RSRP_95_100] += 1
    elif value < RSRP_THRES_100 and value >= RSRP_THRES_105:
        RSRP_Histogram_Attr[RSRP_100_105] += 1
    elif value < RSRP_THRES_105 and value >= RSRP_THRES_110:
        RSRP_Histogram_Attr[RSRP_105_110] += 1
    elif value < RSRP_THRES_110 and value >= RSRP_THRES_115:
        RSRP_Histogram_Attr[RSRP_110_115] += 1
    elif value < RSRP_THRES_115 and value >= RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_115_120] += 1
    elif value < RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_120] += 1
        
for value in Plot_Attr_TD[Y_RX3_RSRP]:
    if value >= RSRP_THRES_60:
        RSRP_Histogram_Attr[RSRP_60] += 1
    elif value < RSRP_THRES_60 and value >= RSRP_THRES_65:
        RSRP_Histogram_Attr[RSRP_60_65] += 1
    elif value < RSRP_THRES_65 and value >= RSRP_THRES_70:
        RSRP_Histogram_Attr[RSRP_65_70] += 1
    elif value < RSRP_THRES_70 and value >= RSRP_THRES_75:
        RSRP_Histogram_Attr[RSRP_70_75] += 1
    elif value < RSRP_THRES_75 and value >= RSRP_THRES_80:
        RSRP_Histogram_Attr[RSRP_75_80] += 1
    elif value < RSRP_THRES_80 and value >= RSRP_THRES_85:
        RSRP_Histogram_Attr[RSRP_80_85] += 1
    elif value < RSRP_THRES_85 and value >= RSRP_THRES_90:
        RSRP_Histogram_Attr[RSRP_85_90] += 1      
    elif value < RSRP_THRES_90 and value >= RSRP_THRES_95:
        RSRP_Histogram_Attr[RSRP_90_95] += 1
    elif value < RSRP_THRES_95 and value >= RSRP_THRES_100:
        RSRP_Histogram_Attr[RSRP_95_100] += 1
    elif value < RSRP_THRES_100 and value >= RSRP_THRES_105:
        RSRP_Histogram_Attr[RSRP_100_105] += 1
    elif value < RSRP_THRES_105 and value >= RSRP_THRES_110:
        RSRP_Histogram_Attr[RSRP_105_110] += 1
    elif value < RSRP_THRES_110 and value >= RSRP_THRES_115:
        RSRP_Histogram_Attr[RSRP_110_115] += 1
    elif value < RSRP_THRES_115 and value >= RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_115_120] += 1
    elif value < RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_120] += 1
        
for value in Plot_Attr_TD[Y_RX0_SNR]:
    if value >= SNR_THRES_30:
        SNR_Histogram_Attr[SNR_30] += 1
    elif value < SNR_THRES_30 and value >= SNR_THRES_27:
        SNR_Histogram_Attr[SNR_30_27] += 1
    elif value < SNR_THRES_27 and value >= SNR_THRES_24:
        SNR_Histogram_Attr[SNR_27_24] += 1
    elif value < SNR_THRES_24 and value >= SNR_THRES_21:
        SNR_Histogram_Attr[SNR_24_21] += 1
    elif value < SNR_THRES_21 and value >= SNR_THRES_18:
        SNR_Histogram_Attr[SNR_21_18] += 1
    elif value < SNR_THRES_18 and value >= SNR_THRES_15:
        SNR_Histogram_Attr[SNR_18_15] += 1
    elif value < SNR_THRES_15 and value >= SNR_THRES_12:
        SNR_Histogram_Attr[SNR_15_12] += 1
    elif value < SNR_THRES_12 and value >= SNR_THRES_9:
        SNR_Histogram_Attr[SNR_12_9] += 1
    elif value < SNR_THRES_9 and value >= SNR_THRES_6:
        SNR_Histogram_Attr[SNR_9_6] += 1
    elif value < SNR_THRES_6 and value >= SNR_THRES_3:
        SNR_Histogram_Attr[SNR_6_3] += 1
    elif value < SNR_THRES_3 and value >= SNR_THRES_0:
        SNR_Histogram_Attr[SNR_3_0] += 1
    elif value < SNR_THRES_0 and value >= SNR_THRES_n3:
        SNR_Histogram_Attr[SNR_0_n3] += 1
    elif value < SNR_THRES_n3 and value >= SNR_THRES_n6:
        SNR_Histogram_Attr[SNR_n3_n6] += 1
    elif value < SNR_THRES_n6:
        SNR_Histogram_Attr[SNR_n6] += 1
        
for value in Plot_Attr_TD[Y_RX1_SNR]:
    if value >= SNR_THRES_30:
        SNR_Histogram_Attr[SNR_30] += 1
    elif value < SNR_THRES_30 and value >= SNR_THRES_27:
        SNR_Histogram_Attr[SNR_30_27] += 1
    elif value < SNR_THRES_27 and value >= SNR_THRES_24:
        SNR_Histogram_Attr[SNR_27_24] += 1
    elif value < SNR_THRES_24 and value >= SNR_THRES_21:
        SNR_Histogram_Attr[SNR_24_21] += 1
    elif value < SNR_THRES_21 and value >= SNR_THRES_18:
        SNR_Histogram_Attr[SNR_21_18] += 1
    elif value < SNR_THRES_18 and value >= SNR_THRES_15:
        SNR_Histogram_Attr[SNR_18_15] += 1
    elif value < SNR_THRES_15 and value >= SNR_THRES_12:
        SNR_Histogram_Attr[SNR_15_12] += 1
    elif value < SNR_THRES_12 and value >= SNR_THRES_9:
        SNR_Histogram_Attr[SNR_12_9] += 1
    elif value < SNR_THRES_9 and value >= SNR_THRES_6:
        SNR_Histogram_Attr[SNR_9_6] += 1
    elif value < SNR_THRES_6 and value >= SNR_THRES_3:
        SNR_Histogram_Attr[SNR_6_3] += 1
    elif value < SNR_THRES_3 and value >= SNR_THRES_0:
        SNR_Histogram_Attr[SNR_3_0] += 1
    elif value < SNR_THRES_0 and value >= SNR_THRES_n3:
        SNR_Histogram_Attr[SNR_0_n3] += 1
    elif value < SNR_THRES_n3 and value >= SNR_THRES_n6:
        SNR_Histogram_Attr[SNR_n3_n6] += 1
    elif value < SNR_THRES_n6:
        SNR_Histogram_Attr[SNR_n6] += 1
        
for value in Plot_Attr_TD[Y_RX2_SNR]:
    if value >= SNR_THRES_30:
        SNR_Histogram_Attr[SNR_30] += 1
    elif value < SNR_THRES_30 and value >= SNR_THRES_27:
        SNR_Histogram_Attr[SNR_30_27] += 1
    elif value < SNR_THRES_27 and value >= SNR_THRES_24:
        SNR_Histogram_Attr[SNR_27_24] += 1
    elif value < SNR_THRES_24 and value >= SNR_THRES_21:
        SNR_Histogram_Attr[SNR_24_21] += 1
    elif value < SNR_THRES_21 and value >= SNR_THRES_18:
        SNR_Histogram_Attr[SNR_21_18] += 1
    elif value < SNR_THRES_18 and value >= SNR_THRES_15:
        SNR_Histogram_Attr[SNR_18_15] += 1
    elif value < SNR_THRES_15 and value >= SNR_THRES_12:
        SNR_Histogram_Attr[SNR_15_12] += 1
    elif value < SNR_THRES_12 and value >= SNR_THRES_9:
        SNR_Histogram_Attr[SNR_12_9] += 1
    elif value < SNR_THRES_9 and value >= SNR_THRES_6:
        SNR_Histogram_Attr[SNR_9_6] += 1
    elif value < SNR_THRES_6 and value >= SNR_THRES_3:
        SNR_Histogram_Attr[SNR_6_3] += 1
    elif value < SNR_THRES_3 and value >= SNR_THRES_0:
        SNR_Histogram_Attr[SNR_3_0] += 1
    elif value < SNR_THRES_0 and value >= SNR_THRES_n3:
        SNR_Histogram_Attr[SNR_0_n3] += 1
    elif value < SNR_THRES_n3 and value >= SNR_THRES_n6:
        SNR_Histogram_Attr[SNR_n3_n6] += 1
    elif value < SNR_THRES_n6:
        SNR_Histogram_Attr[SNR_n6] += 1
        
for value in Plot_Attr_TD[Y_RX3_SNR]:
    if value >= SNR_THRES_30:
        SNR_Histogram_Attr[SNR_30] += 1
    elif value < SNR_THRES_30 and value >= SNR_THRES_27:
        SNR_Histogram_Attr[SNR_30_27] += 1
    elif value < SNR_THRES_27 and value >= SNR_THRES_24:
        SNR_Histogram_Attr[SNR_27_24] += 1
    elif value < SNR_THRES_24 and value >= SNR_THRES_21:
        SNR_Histogram_Attr[SNR_24_21] += 1
    elif value < SNR_THRES_21 and value >= SNR_THRES_18:
        SNR_Histogram_Attr[SNR_21_18] += 1
    elif value < SNR_THRES_18 and value >= SNR_THRES_15:
        SNR_Histogram_Attr[SNR_18_15] += 1
    elif value < SNR_THRES_15 and value >= SNR_THRES_12:
        SNR_Histogram_Attr[SNR_15_12] += 1
    elif value < SNR_THRES_12 and value >= SNR_THRES_9:
        SNR_Histogram_Attr[SNR_12_9] += 1
    elif value < SNR_THRES_9 and value >= SNR_THRES_6:
        SNR_Histogram_Attr[SNR_9_6] += 1
    elif value < SNR_THRES_6 and value >= SNR_THRES_3:
        SNR_Histogram_Attr[SNR_6_3] += 1
    elif value < SNR_THRES_3 and value >= SNR_THRES_0:
        SNR_Histogram_Attr[SNR_3_0] += 1
    elif value < SNR_THRES_0 and value >= SNR_THRES_n3:
        SNR_Histogram_Attr[SNR_0_n3] += 1
    elif value < SNR_THRES_n3 and value >= SNR_THRES_n6:
        SNR_Histogram_Attr[SNR_n3_n6] += 1
    elif value < SNR_THRES_n6:
        SNR_Histogram_Attr[SNR_n6] += 1

numRSRP = float(RSRP_Histogram_Attr[RSRP_60] + RSRP_Histogram_Attr[RSRP_60_65] + RSRP_Histogram_Attr[RSRP_65_70] + RSRP_Histogram_Attr[RSRP_70_75]
                + RSRP_Histogram_Attr[RSRP_75_80] + RSRP_Histogram_Attr[RSRP_80_85] + RSRP_Histogram_Attr[RSRP_85_90] + RSRP_Histogram_Attr[RSRP_90_95]
                + RSRP_Histogram_Attr[RSRP_95_100] + RSRP_Histogram_Attr[RSRP_100_105] + RSRP_Histogram_Attr[RSRP_105_110] + RSRP_Histogram_Attr[RSRP_110_115]
                + RSRP_Histogram_Attr[RSRP_115_120] + RSRP_Histogram_Attr[RSRP_120])
numSNR = float(SNR_Histogram_Attr[SNR_30] + SNR_Histogram_Attr[SNR_30_27] + SNR_Histogram_Attr[SNR_27_24] + SNR_Histogram_Attr[SNR_24_21]
                + SNR_Histogram_Attr[SNR_21_18] + SNR_Histogram_Attr[SNR_18_15] + SNR_Histogram_Attr[SNR_15_12] + SNR_Histogram_Attr[SNR_12_9]
                + SNR_Histogram_Attr[SNR_9_6] + SNR_Histogram_Attr[SNR_6_3] + SNR_Histogram_Attr[SNR_3_0] + SNR_Histogram_Attr[SNR_0_n3]
                + SNR_Histogram_Attr[SNR_n3_n6] + SNR_Histogram_Attr[SNR_n6])

if Plot_Attr_TD[X_RX3_RSRP] != [] and Plot_Attr_TD[Y_RX3_RSRP] != []:
    TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_RX3_RSRP], format="%H:%M:%S.%f"), Plot_Attr_TD[Y_RX3_RSRP], label = "Rx3_RSRP", color='red', marker='.')
if Plot_Attr_TD[X_RX2_RSRP] != [] and Plot_Attr_TD[Y_RX2_RSRP] != []:    
    TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_RX2_RSRP], format="%H:%M:%S.%f"), Plot_Attr_TD[Y_RX2_RSRP], label = "Rx2_RSRP", color='orange', marker='.')
if Plot_Attr_TD[X_RX1_RSRP] != [] and Plot_Attr_TD[Y_RX1_RSRP] != []:    
    TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_RX1_RSRP], format="%H:%M:%S.%f"), Plot_Attr_TD[Y_RX1_RSRP], label = "Rx1_RSRP", color='green', marker='.')
if Plot_Attr_TD[X_RX0_RSRP] != [] and Plot_Attr_TD[Y_RX0_RSRP] != []:      
    TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_RX0_RSRP], format="%H:%M:%S.%f"), Plot_Attr_TD[Y_RX0_RSRP], label = "Rx0_RSRP", color='blue', marker='.')

if Plot_Attr_TD[X_RX3_SNR] != [] and Plot_Attr_TD[Y_RX3_SNR] != []:  
    TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_RX3_SNR], format="%H:%M:%S.%f"), Plot_Attr_TD[Y_RX3_SNR], label = "Rx3_SNR", color='orangered', marker=',')
if Plot_Attr_TD[X_RX2_SNR] != [] and Plot_Attr_TD[Y_RX2_SNR] != []:      
    TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_RX2_SNR], format="%H:%M:%S.%f"), Plot_Attr_TD[Y_RX2_SNR], label = "Rx2_SNR", color='gold', marker=',')
if Plot_Attr_TD[X_RX1_SNR] != [] and Plot_Attr_TD[Y_RX1_SNR] != []:      
    TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_RX1_SNR], format="%H:%M:%S.%f"), Plot_Attr_TD[Y_RX1_SNR], label = "Rx1_SNR", color='greenyellow', marker=',')
if Plot_Attr_TD[X_RX0_SNR] != [] and Plot_Attr_TD[Y_RX0_SNR] != []:     
    TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_RX0_SNR], format="%H:%M:%S.%f"), Plot_Attr_TD[Y_RX0_SNR], label = "Rx0_SNR", color='cyan', marker=',')
            
'''TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_HO_START]), Plot_Attr_TD[Y_HO_START], label = "HO Start", color='black', marker='>')'''
if Plot_Attr_TD[X_HO_SUC] != [] and Plot_Attr_TD[Y_HO_SUC] != []:
    TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_HO_SUC], format="%H:%M:%S.%f"), Plot_Attr_TD[Y_HO_SUC], label = "HO Success", color='black', marker='s')
if Plot_Attr_TD[X_HO_FAIL] != [] and Plot_Attr_TD[Y_HO_FAIL] != []:    
    TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_HO_FAIL], format="%H:%M:%S.%f"), Plot_Attr_TD[Y_HO_FAIL], label = "HO Failure", color='red', marker='x')
if Plot_Attr_TD[X_RLF] != [] and Plot_Attr_TD[Y_RLF] != []:    
    TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_RLF], format="%H:%M:%S.%f"), Plot_Attr_TD[Y_RLF], label = "RLF", color='red', marker='X')
if Plot_Attr_TD[X_RRC_REES] != [] and Plot_Attr_TD[Y_RRC_REES] != []:    
    TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_RRC_REES], format="%H:%M:%S.%f"), Plot_Attr_TD[Y_RRC_REES], label = "RRC Reestablish", color='green', marker="P")

TD_plot.legend(loc='upper right')
TD_plot.set_title('RSRP/SNR in TD (Total ' + str(TotalNumHO) + ' handovers with ' + str(len(list(set(PCI_All)))) +' unique PCIs)')
TD_plot.grid(True, linestyle='dotted')
TD_plot.set_axisbelow(True)

b1 = Histogram_RSRP.bar(RSRP_60, RSRP_Histogram_Attr[RSRP_60], width=1, edgecolor="black", color='cornflowerblue')
b2 = Histogram_RSRP.bar(RSRP_60_65, RSRP_Histogram_Attr[RSRP_60_65], width=1, edgecolor="black", color='cornflowerblue')
b3 = Histogram_RSRP.bar(RSRP_65_70, RSRP_Histogram_Attr[RSRP_65_70], width=1, edgecolor="black", color='cornflowerblue')
b4 = Histogram_RSRP.bar(RSRP_70_75, RSRP_Histogram_Attr[RSRP_70_75], width=1, edgecolor="black", color='cornflowerblue')
b5 = Histogram_RSRP.bar(RSRP_75_80, RSRP_Histogram_Attr[RSRP_75_80], width=1, edgecolor="black", color='cornflowerblue')
b6 = Histogram_RSRP.bar(RSRP_80_85, RSRP_Histogram_Attr[RSRP_80_85], width=1, edgecolor="black", color='cornflowerblue')
b7 = Histogram_RSRP.bar(RSRP_85_90, RSRP_Histogram_Attr[RSRP_85_90], width=1, edgecolor="black", color='cornflowerblue')
b8 = Histogram_RSRP.bar(RSRP_90_95, RSRP_Histogram_Attr[RSRP_90_95], width=1, edgecolor="black", color='cornflowerblue')
b9 = Histogram_RSRP.bar(RSRP_95_100, RSRP_Histogram_Attr[RSRP_95_100], width=1, edgecolor="black", color='cornflowerblue')
b10 = Histogram_RSRP.bar(RSRP_100_105, RSRP_Histogram_Attr[RSRP_100_105], width=1, edgecolor="black", color='cornflowerblue')
b11 = Histogram_RSRP.bar(RSRP_105_110, RSRP_Histogram_Attr[RSRP_105_110], width=1, edgecolor="black", color='cornflowerblue')
b12 = Histogram_RSRP.bar(RSRP_110_115, RSRP_Histogram_Attr[RSRP_110_115], width=1, edgecolor="black", color='cornflowerblue')
b13 = Histogram_RSRP.bar(RSRP_115_120, RSRP_Histogram_Attr[RSRP_115_120], width=1, edgecolor="black", color='cornflowerblue')
b14 = Histogram_RSRP.bar(RSRP_120, RSRP_Histogram_Attr[RSRP_120], width=1, edgecolor="black", color='cornflowerblue')

Histogram_RSRP.set_title('RSRP Histogram')
Histogram_RSRP.grid(True, linestyle='dotted')
Histogram_RSRP.set_axisbelow(True)
Histogram_RSRP.tick_params(axis='x', labelrotation=10)
if numRSRP > 0:
    Histogram_RSRP.bar_label(b1, labels=[format(RSRP_Histogram_Attr[RSRP_60]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b2, labels=[format(RSRP_Histogram_Attr[RSRP_60_65]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b3, labels=[format(RSRP_Histogram_Attr[RSRP_65_70]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b4, labels=[format(RSRP_Histogram_Attr[RSRP_70_75]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b5, labels=[format(RSRP_Histogram_Attr[RSRP_75_80]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b6, labels=[format(RSRP_Histogram_Attr[RSRP_80_85]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b7, labels=[format(RSRP_Histogram_Attr[RSRP_85_90]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b8, labels=[format(RSRP_Histogram_Attr[RSRP_90_95]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b9, labels=[format(RSRP_Histogram_Attr[RSRP_95_100]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b10, labels=[format(RSRP_Histogram_Attr[RSRP_100_105]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b11, labels=[format(RSRP_Histogram_Attr[RSRP_105_110]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b12, labels=[format(RSRP_Histogram_Attr[RSRP_110_115]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b13, labels=[format(RSRP_Histogram_Attr[RSRP_115_120]/numRSRP, '.1%')], label_type='edge')
    Histogram_RSRP.bar_label(b14, labels=[format(RSRP_Histogram_Attr[RSRP_120]/numRSRP, '.1%')], label_type='edge')

b15 = Histogram_SNR.bar(SNR_30, SNR_Histogram_Attr[SNR_30], width=1, edgecolor="black", color='cornflowerblue')
b16 = Histogram_SNR.bar(SNR_30_27, SNR_Histogram_Attr[SNR_30_27], width=1, edgecolor="black", color='cornflowerblue')
b17 = Histogram_SNR.bar(SNR_27_24, SNR_Histogram_Attr[SNR_27_24], width=1, edgecolor="black", color='cornflowerblue')
b18 = Histogram_SNR.bar(SNR_24_21, SNR_Histogram_Attr[SNR_24_21], width=1, edgecolor="black", color='cornflowerblue')
b19 = Histogram_SNR.bar(SNR_21_18, SNR_Histogram_Attr[SNR_21_18], width=1, edgecolor="black", color='cornflowerblue')
b20 = Histogram_SNR.bar(SNR_18_15, SNR_Histogram_Attr[SNR_18_15], width=1, edgecolor="black", color='cornflowerblue')
b21 = Histogram_SNR.bar(SNR_15_12, SNR_Histogram_Attr[SNR_15_12], width=1, edgecolor="black", color='cornflowerblue')
b22 = Histogram_SNR.bar(SNR_12_9, SNR_Histogram_Attr[SNR_12_9], width=1, edgecolor="black", color='cornflowerblue')
b23 = Histogram_SNR.bar(SNR_9_6, SNR_Histogram_Attr[SNR_9_6], width=1, edgecolor="black", color='cornflowerblue')
b24 = Histogram_SNR.bar(SNR_6_3, SNR_Histogram_Attr[SNR_6_3], width=1, edgecolor="black", color='cornflowerblue')
b25 = Histogram_SNR.bar(SNR_3_0, SNR_Histogram_Attr[SNR_3_0], width=1, edgecolor="black", color='cornflowerblue')
b26 = Histogram_SNR.bar(SNR_0_n3, SNR_Histogram_Attr[SNR_0_n3], width=1, edgecolor="black", color='cornflowerblue')
b27 = Histogram_SNR.bar(SNR_n3_n6, SNR_Histogram_Attr[SNR_n3_n6], width=1, edgecolor="black", color='cornflowerblue')
b28 = Histogram_SNR.bar(SNR_n6, SNR_Histogram_Attr[SNR_n6], width=1, edgecolor="black", color='cornflowerblue')

Histogram_SNR.set_title('SNR Histogram')
Histogram_SNR.grid(True, linestyle='dotted')
Histogram_SNR.set_axisbelow(True)
Histogram_SNR.tick_params(axis='x', labelrotation=10)
if numSNR > 0:
    Histogram_SNR.bar_label(b15, labels=[format(SNR_Histogram_Attr[SNR_30]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b16, labels=[format(SNR_Histogram_Attr[SNR_30_27]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b17, labels=[format(SNR_Histogram_Attr[SNR_27_24]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b18, labels=[format(SNR_Histogram_Attr[SNR_24_21]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b19, labels=[format(SNR_Histogram_Attr[SNR_21_18]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b20, labels=[format(SNR_Histogram_Attr[SNR_18_15]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b21, labels=[format(SNR_Histogram_Attr[SNR_15_12]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b22, labels=[format(SNR_Histogram_Attr[SNR_12_9]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b23, labels=[format(SNR_Histogram_Attr[SNR_9_6]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b24, labels=[format(SNR_Histogram_Attr[SNR_6_3]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b25, labels=[format(SNR_Histogram_Attr[SNR_3_0]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b26, labels=[format(SNR_Histogram_Attr[SNR_0_n3]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b27, labels=[format(SNR_Histogram_Attr[SNR_n3_n6]/numSNR, '.1%')], label_type='edge')
    Histogram_SNR.bar_label(b28, labels=[format(SNR_Histogram_Attr[SNR_n6]/numSNR, '.1%')], label_type='edge')

plt.show()