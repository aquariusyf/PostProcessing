from PostProcessingUtils import PostProcessingUtils, LogPacket_RSRP_SNR
from FilterMask import *
from datetime import datetime
import sys
import matplotlib.pyplot as plt
import pandas as pd

filter_mask[LOG_FILTER] = [0xB821, 0xB8DD]

RF_Profile = PostProcessingUtils()
RF_Profile.getArgv(sys.argv)
RF_Profile.scanWorkingDir()
RF_Profile.convertToText()
RF_Profile.scanWorkingDir('_flt_text.txt')
RF_Profile.initLogPacketList()
LogPkt_All = RF_Profile.getLogPacketList()

HO_START = -30
HO_SUC = -40
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

RSRP_70 = 'RSRP > -70'
RSRP_70_85 = '-70 > RSRP > -85'
RSRP_85_95 = '-85 > RSRP > -95'
RSRP_95_105 = '-95 > RSRP > -105'
RSRP_105_120 = '-105 > RSRP > -120'
RSRP_120 = 'RSRP < -120'

SNR_20 = 'SNR > 20'
SNR_15_20 = '15 > SNR > 20'
SNR_10_15 = '10 > SNR > 15'
SNR_5_10 = '5 > SNR > 10'
SNR_0_5 = '0 > SNR > 5'
SNR_0 = 'SNR < 0'

RSRP_THRES_70 = -70
RSRP_THRES_85 = -85
RSRP_THRES_95 = -95
RSRP_THRES_105 = -105
RSRP_THRES_120 = -120
SNR_THRES_20 = 20
SNR_THRES_15 = 15
SNR_THRES_10 = 10
SNR_THRES_5 = 5
SNR_THRES_0 = 0

Plot_Attr_TD = {X_RX0_RSRP: [], Y_RX0_RSRP: [],
                X_RX1_RSRP: [], Y_RX1_RSRP: [],
                X_RX2_RSRP: [], Y_RX2_RSRP: [],
                X_RX3_RSRP: [], Y_RX3_RSRP: [],
                X_RX0_SNR: [], Y_RX0_SNR: [],
                X_RX1_SNR: [], Y_RX1_SNR: [],
                X_RX2_SNR: [], Y_RX2_SNR: [],
                X_RX3_SNR: [], Y_RX3_SNR: [],
                X_HO_START: [], Y_HO_START: [],                        
                X_HO_SUC: [], Y_HO_SUC: []}

RSRP_Histogram_Attr = {RSRP_70: 0, RSRP_70_85: 0, RSRP_85_95: 0, RSRP_95_105: 0, RSRP_105_120: 0, RSRP_120: 0}
SNR_Histogram_Attr = {SNR_20: 0, SNR_15_20: 0, SNR_10_15: 0, SNR_5_10: 0, SNR_0_5: 0, SNR_0: 0}

figure, axis = plt.subplots(3, 1)
TD_plot = axis[0]
Histogram_RSRP = axis[1]
Histogram_SNR = axis[2]

for key in LogPkt_All.keys():
    B8DD_Pkt_List = []
    for pkt in LogPkt_All[key]:
        if pkt.getPacketCode() == '0xB8DD':
            B8DD_Pkt_List.append(LogPacket_RSRP_SNR(pkt))
        if pkt.getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_STARTED_V2':
            Plot_Attr_TD[Y_HO_START].append(HO_START)
            Plot_Attr_TD[X_HO_START].append(pkt.getTimestamp())
        elif pkt.getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_SUCCESS':
            Plot_Attr_TD[Y_HO_SUC].append(HO_SUC)
            Plot_Attr_TD[X_HO_SUC].append(pkt.getTimestamp())

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
    if value >= RSRP_THRES_70:
        RSRP_Histogram_Attr[RSRP_70] += 1
    elif value < RSRP_THRES_70 and value >= RSRP_THRES_85:
        RSRP_Histogram_Attr[RSRP_70_85] += 1
    elif value < RSRP_THRES_85 and value >= RSRP_THRES_95:
        RSRP_Histogram_Attr[RSRP_85_95] += 1
    elif value < RSRP_THRES_95 and value >= RSRP_THRES_105:
        RSRP_Histogram_Attr[RSRP_95_105] += 1
    elif value < RSRP_THRES_105 and value >= RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_105_120] += 1
    elif value < RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_120] += 1
        
for value in Plot_Attr_TD[Y_RX1_RSRP]:
    if value >= RSRP_THRES_70:
        RSRP_Histogram_Attr[RSRP_70] += 1
    elif value < RSRP_THRES_70 and value >= RSRP_THRES_85:
        RSRP_Histogram_Attr[RSRP_70_85] += 1
    elif value < RSRP_THRES_85 and value >= RSRP_THRES_95:
        RSRP_Histogram_Attr[RSRP_85_95] += 1
    elif value < RSRP_THRES_95 and value >= RSRP_THRES_105:
        RSRP_Histogram_Attr[RSRP_95_105] += 1
    elif value < RSRP_THRES_105 and value >= RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_105_120] += 1
    elif value < RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_120] += 1
        
for value in Plot_Attr_TD[Y_RX2_RSRP]:
    if value >= RSRP_THRES_70:
        RSRP_Histogram_Attr[RSRP_70] += 1
    elif value < RSRP_THRES_70 and value >= RSRP_THRES_85:
        RSRP_Histogram_Attr[RSRP_70_85] += 1
    elif value < RSRP_THRES_85 and value >= RSRP_THRES_95:
        RSRP_Histogram_Attr[RSRP_85_95] += 1
    elif value < RSRP_THRES_95 and value >= RSRP_THRES_105:
        RSRP_Histogram_Attr[RSRP_95_105] += 1
    elif value < RSRP_THRES_105 and value >= RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_105_120] += 1
    elif value < RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_120] += 1
        
for value in Plot_Attr_TD[Y_RX3_RSRP]:
    if value >= RSRP_THRES_70:
        RSRP_Histogram_Attr[RSRP_70] += 1
    elif value < RSRP_THRES_70 and value >= RSRP_THRES_85:
        RSRP_Histogram_Attr[RSRP_70_85] += 1
    elif value < RSRP_THRES_85 and value >= RSRP_THRES_95:
        RSRP_Histogram_Attr[RSRP_85_95] += 1
    elif value < RSRP_THRES_95 and value >= RSRP_THRES_105:
        RSRP_Histogram_Attr[RSRP_95_105] += 1
    elif value < RSRP_THRES_105 and value >= RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_105_120] += 1
    elif value < RSRP_THRES_120:
        RSRP_Histogram_Attr[RSRP_120] += 1
        
for value in Plot_Attr_TD[Y_RX0_SNR]:
    if value >= SNR_THRES_20:
        SNR_Histogram_Attr[SNR_20] += 1
    elif value < SNR_THRES_20 and value >= SNR_THRES_15:
        SNR_Histogram_Attr[SNR_15_20] += 1
    elif value < SNR_THRES_15 and value >= SNR_THRES_10:
        SNR_Histogram_Attr[SNR_10_15] += 1
    elif value < SNR_THRES_10 and value >= SNR_THRES_5:
        SNR_Histogram_Attr[SNR_5_10] += 1
    elif value < SNR_THRES_5 and value >= SNR_THRES_0:
        SNR_Histogram_Attr[SNR_0_5] += 1
    elif value < SNR_THRES_0:
        SNR_Histogram_Attr[SNR_0] += 1
        
for value in Plot_Attr_TD[Y_RX1_SNR]:
    if value >= SNR_THRES_20:
        SNR_Histogram_Attr[SNR_20] += 1
    elif value < SNR_THRES_20 and value >= SNR_THRES_15:
        SNR_Histogram_Attr[SNR_15_20] += 1
    elif value < SNR_THRES_15 and value >= SNR_THRES_10:
        SNR_Histogram_Attr[SNR_10_15] += 1
    elif value < SNR_THRES_10 and value >= SNR_THRES_5:
        SNR_Histogram_Attr[SNR_5_10] += 1
    elif value < SNR_THRES_5 and value >= SNR_THRES_0:
        SNR_Histogram_Attr[SNR_0_5] += 1
    elif value < SNR_THRES_0:
        SNR_Histogram_Attr[SNR_0] += 1
        
for value in Plot_Attr_TD[Y_RX2_SNR]:
    if value >= SNR_THRES_20:
        SNR_Histogram_Attr[SNR_20] += 1
    elif value < SNR_THRES_20 and value >= SNR_THRES_15:
        SNR_Histogram_Attr[SNR_15_20] += 1
    elif value < SNR_THRES_15 and value >= SNR_THRES_10:
        SNR_Histogram_Attr[SNR_10_15] += 1
    elif value < SNR_THRES_10 and value >= SNR_THRES_5:
        SNR_Histogram_Attr[SNR_5_10] += 1
    elif value < SNR_THRES_5 and value >= SNR_THRES_0:
        SNR_Histogram_Attr[SNR_0_5] += 1
    elif value < SNR_THRES_0:
        SNR_Histogram_Attr[SNR_0] += 1
        
for value in Plot_Attr_TD[Y_RX3_SNR]:
    if value >= SNR_THRES_20:
        SNR_Histogram_Attr[SNR_20] += 1
    elif value < SNR_THRES_20 and value >= SNR_THRES_15:
        SNR_Histogram_Attr[SNR_15_20] += 1
    elif value < SNR_THRES_15 and value >= SNR_THRES_10:
        SNR_Histogram_Attr[SNR_10_15] += 1
    elif value < SNR_THRES_10 and value >= SNR_THRES_5:
        SNR_Histogram_Attr[SNR_5_10] += 1
    elif value < SNR_THRES_5 and value >= SNR_THRES_0:
        SNR_Histogram_Attr[SNR_0_5] += 1
    elif value < SNR_THRES_0:
        SNR_Histogram_Attr[SNR_0] += 1


TD_plot.plot(pd.to_datetime(Plot_Attr_TD[X_RX0_RSRP]), Plot_Attr_TD[Y_RX0_RSRP], label = "Rx0_RSRP", color='red', marker='.')
TD_plot.plot(pd.to_datetime(Plot_Attr_TD[X_RX1_RSRP]), Plot_Attr_TD[Y_RX1_RSRP], label = "Rx1_RSRP", color='green', marker='.')
TD_plot.plot(pd.to_datetime(Plot_Attr_TD[X_RX2_RSRP]), Plot_Attr_TD[Y_RX2_RSRP], label = "Rx2_RSRP", color='orange', marker='.')
TD_plot.plot(pd.to_datetime(Plot_Attr_TD[X_RX3_RSRP]), Plot_Attr_TD[Y_RX3_RSRP], label = "Rx3_RSRP", color='blue', marker='.')

TD_plot.plot(pd.to_datetime(Plot_Attr_TD[X_RX0_SNR]), Plot_Attr_TD[Y_RX0_SNR], label = "Rx0_SNR", color='orangered', marker='.')
TD_plot.plot(pd.to_datetime(Plot_Attr_TD[X_RX1_SNR]), Plot_Attr_TD[Y_RX1_SNR], label = "Rx1_SNR", color='greenyellow', marker='.')
TD_plot.plot(pd.to_datetime(Plot_Attr_TD[X_RX2_SNR]), Plot_Attr_TD[Y_RX2_SNR], label = "Rx2_SNR", color='gold', marker='.')
TD_plot.plot(pd.to_datetime(Plot_Attr_TD[X_RX3_SNR]), Plot_Attr_TD[Y_RX3_SNR], label = "Rx3_SNR", color='cyan', marker='.')
            
TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_HO_START]), Plot_Attr_TD[Y_HO_START], label = "HO Start", color='black', marker='>')
TD_plot.scatter(pd.to_datetime(Plot_Attr_TD[X_HO_SUC]), Plot_Attr_TD[Y_HO_SUC], label = "HO Success", color='black', marker='s')

TD_plot.legend(loc='upper right')
TD_plot.set_title('RSRP/SNR in TD')
TD_plot.grid(True)

b1 = Histogram_RSRP.bar(RSRP_70, RSRP_Histogram_Attr[RSRP_70], color='deepskyblue')
b2 = Histogram_RSRP.bar(RSRP_70_85, RSRP_Histogram_Attr[RSRP_70_85], color='deepskyblue')
b3 = Histogram_RSRP.bar(RSRP_85_95, RSRP_Histogram_Attr[RSRP_85_95], color='deepskyblue')
b4 = Histogram_RSRP.bar(RSRP_95_105, RSRP_Histogram_Attr[RSRP_95_105], color='deepskyblue')
b5 = Histogram_RSRP.bar(RSRP_105_120, RSRP_Histogram_Attr[RSRP_105_120], color='deepskyblue')
b6 = Histogram_RSRP.bar(RSRP_120, RSRP_Histogram_Attr[RSRP_120], color='deepskyblue')

Histogram_RSRP.set_title('RSRP Histogram')
Histogram_RSRP.grid(True)
Histogram_RSRP.bar_label(b1, label_type='edge')
Histogram_RSRP.bar_label(b2, label_type='edge')
Histogram_RSRP.bar_label(b3, label_type='edge')
Histogram_RSRP.bar_label(b4, label_type='edge')
Histogram_RSRP.bar_label(b5, label_type='edge')
Histogram_RSRP.bar_label(b6, label_type='edge')

b7 = Histogram_SNR.bar(SNR_20, SNR_Histogram_Attr[SNR_20], color='tomato')
b8 = Histogram_SNR.bar(SNR_15_20, SNR_Histogram_Attr[SNR_15_20], color='tomato')
b9 = Histogram_SNR.bar(SNR_10_15, SNR_Histogram_Attr[SNR_10_15], color='tomato')
b10 = Histogram_SNR.bar(SNR_5_10, SNR_Histogram_Attr[SNR_5_10], color='tomato')
b11 = Histogram_SNR.bar(SNR_0_5, SNR_Histogram_Attr[SNR_0_5], color='tomato')
b12 = Histogram_SNR.bar(SNR_0, SNR_Histogram_Attr[SNR_0], color='tomato')

Histogram_SNR.set_title('SNR Histogram')
Histogram_SNR.grid(True)
Histogram_SNR.bar_label(b7, label_type='edge')
Histogram_SNR.bar_label(b8, label_type='edge')
Histogram_SNR.bar_label(b9, label_type='edge')
Histogram_SNR.bar_label(b10, label_type='edge')
Histogram_SNR.bar_label(b11, label_type='edge')
Histogram_SNR.bar_label(b12, label_type='edge')

plt.show()