from flatterned_log_packet.flatterned_0x1568 import LogPacket_0x1568
from flatterned_log_packet.flatterned_0x1569 import LogPacket_0x1569
from flatterned_log_packet.flatterned_0x1E9C import LogPacket_0x1E9C
from flatterned_log_packet.flatterned_0x156B import LogPacket_0x156B
from flatterned_log_packet.flatterned_0x156C import LogPacket_0x156C
from flatterned_log_packet.flatterned_event_3188 import LogPacket_3188
from FilterMask import *
from PostProcessingUtils import PostProcessingUtils
from datetime import datetime as dt
import sys
import os
import pandas as pd
import numpy as np

filter_mask[LOG_FILTER] = [0x1568, 0x1569, 0x1E9C, 0x156B, 0x156C]
filter_mask[EVENT_FILTER] = [3188, 3190]

# key names
TS = 'Timestamp'
EVENT = 'Event'
DIRECTION = 'Direction'
HO_ADPT = 'HO Adapt'
INET_TECH = 'inet tech'
LINK_STATE = 'Link State'
LINK_SETUP_TIME = 'Link Setup Time'
EXP_PLAYOUT_CNT = 'Exp Playout Count'
RECEIVED_RED_FRAME_CNT = 'Received Red Frame Count'
PLAYED_FRAME_CNT_PRIM = 'Played Frame Count Prim'
PLAYED_FRAME_CNT_RED = 'Played Frame Count Red'
DISCARD_RED_FRAME_CNT = 'Discard Red Frame Count'
UNDERFLOW_RED_FRAME_CNT = 'Underflow Red Frame Count'
TOTAL_DEQ_ATTEMPT_WITHIN_INTERVAL = 'Total DeQ Attempt Within Interval'
DEQ_AGGR_FAIL_CNT = 'DeQ Aggr Fail Count'
DEQ_PRIM_FAIL_CNT = 'DeQ Prim Fail Count'
RED_USEFULNESS = 'Red Usefulness'
PRIM_PKT_LOSS_IN_LONG_WIN = 'Prim Pkt Loss in Long Win'
TX_RTP_CNT_PRIM = 'Tx RTP Count Prim'
TX_RTP_CNT_RED = 'Tx RTP Count Red'
LOG_NAME = 'Log Name'
NUM_LOST = 'Num of Pkt Lost'
SEQUENCE = 'Sequence'
CODEC_TYPE = 'Codec'
LOST_TYPE = 'Lost Type'
RAT_TYPE = 'RAT Type'
RTP_TS = 'RTP Timestamp'
MEDIA_TYPE = 'Media Type'
PAYLOAD_SIZE = 'Payload Size'
FRAME_RECEIVE_TIME = 'Frame Receive Time'
ENQ_RESULT = 'EnQ Result'
IS_REDUNDANT = 'Is Redundant'
FRAME_DELAY = 'Frame Delay'
Q_SIZE = 'Q Size'
DEQ_DELTA = 'DeQ Delta'
TARGET_DELAY = 'Target Delay'
DEQ_STATE = 'DeQ State'
RED_ENQ_STATUS = 'RED EnQ Status'
SOURCE_PCI = 'Source PCI'
SOURCE_ARFCN = 'Source ARFCN'
TARGET_PCI = 'Target PCI'
TARGET_ARFCN = 'Target ARFCN'

test = PostProcessingUtils()
test.getArgv(sys.argv)
test.scanWorkingDir()
if not test.skipFitlerLogs():
    test.convertToText('RTP_RED_')
test.scanWorkingDir('_flt_text.txt', 'RTP_RED_')
test.initLogPacketList()
all_logs = test.getLogPacketList()
            
data_dict_0x1E9C = {TS: [], EVENT: [], DIRECTION: [], HO_ADPT: [], INET_TECH: [], LINK_STATE: [], LINK_SETUP_TIME: [], EXP_PLAYOUT_CNT: [], RECEIVED_RED_FRAME_CNT: [],
                    PLAYED_FRAME_CNT_PRIM: [], PLAYED_FRAME_CNT_RED: [], DISCARD_RED_FRAME_CNT: [], UNDERFLOW_RED_FRAME_CNT: [], TOTAL_DEQ_ATTEMPT_WITHIN_INTERVAL: [], 
                    DEQ_AGGR_FAIL_CNT: [], DEQ_PRIM_FAIL_CNT: [], RED_USEFULNESS: [], PRIM_PKT_LOSS_IN_LONG_WIN: [], TX_RTP_CNT_PRIM: [], TX_RTP_CNT_RED:[], LOG_NAME: []}
data_dict_0x1569 = {TS: [], LOST_TYPE: [], NUM_LOST: [], SEQUENCE: [], CODEC_TYPE: [], LOG_NAME: []}
data_dict_0x1568 = {TS: [], RAT_TYPE: [], DIRECTION: [], MEDIA_TYPE: [], CODEC_TYPE: [], PAYLOAD_SIZE: [], SEQUENCE: [], RTP_TS: [], LOG_NAME: []}
data_dict_0x156B = {TS: [], RTP_TS: [], SEQUENCE: [], FRAME_RECEIVE_TIME: [], ENQ_RESULT: [], IS_REDUNDANT: [], LOG_NAME: []}
data_dict_0x156C = {TS: [], RTP_TS: [], SEQUENCE: [], FRAME_RECEIVE_TIME: [], DEQ_STATE: [], FRAME_DELAY: [], TARGET_DELAY: [], Q_SIZE: [], DEQ_DELTA: [], IS_REDUNDANT: [], 
                    RED_ENQ_STATUS: [], LOG_NAME: []}
data_dict_3188 = {TS: [], EVENT: [], SOURCE_PCI: [], SOURCE_ARFCN: [], TARGET_PCI: [], TARGET_ARFCN: [], LOG_NAME: []}

for logname, logs in all_logs.items():
    for log in logs:
        log_1E9C = LogPacket_0x1E9C(log)
        if log_1E9C.isValidPkt():
            data_dict_0x1E9C[TS].append(log_1E9C.getTimestamp())
            data_dict_0x1E9C[EVENT].append(log_1E9C.getEvent())
            data_dict_0x1E9C[DIRECTION].append(log_1E9C.getDirection())
            data_dict_0x1E9C[HO_ADPT].append(log_1E9C.getHOAdapt())
            data_dict_0x1E9C[INET_TECH].append(log_1E9C.getInetTech())
            data_dict_0x1E9C[LINK_STATE].append(log_1E9C.getLinkState())
            data_dict_0x1E9C[LINK_SETUP_TIME].append(log_1E9C.getLinkSetupTime())
            data_dict_0x1E9C[EXP_PLAYOUT_CNT].append(log_1E9C.getExpPlayoutCount())
            data_dict_0x1E9C[RECEIVED_RED_FRAME_CNT].append(log_1E9C.getReceivedRedFrameCount())
            data_dict_0x1E9C[PLAYED_FRAME_CNT_PRIM].append(log_1E9C.getPlayedFrameCountPrim())
            data_dict_0x1E9C[PLAYED_FRAME_CNT_RED].append(log_1E9C.getPlayedFrameCountRed())
            data_dict_0x1E9C[DISCARD_RED_FRAME_CNT].append(log_1E9C.getDiscardRedFrameCount())
            data_dict_0x1E9C[UNDERFLOW_RED_FRAME_CNT].append(log_1E9C.getUnderflowRedFrameCount())
            data_dict_0x1E9C[TOTAL_DEQ_ATTEMPT_WITHIN_INTERVAL].append(log_1E9C.getTotalDeQAttempsWithinInterval())
            data_dict_0x1E9C[DEQ_AGGR_FAIL_CNT].append(log_1E9C.getDeQAggrFailCount())
            data_dict_0x1E9C[DEQ_PRIM_FAIL_CNT].append(log_1E9C.getDeQPrimFailCount())
            data_dict_0x1E9C[RED_USEFULNESS].append(log_1E9C.getRedUsefulness())
            data_dict_0x1E9C[PRIM_PKT_LOSS_IN_LONG_WIN].append(log_1E9C.getPrimPktLossInLongWin())
            data_dict_0x1E9C[TX_RTP_CNT_PRIM].append(log_1E9C.getTxRtpCountPrim())
            data_dict_0x1E9C[TX_RTP_CNT_RED].append(log_1E9C.getTxRtpCountRed())
            data_dict_0x1E9C[LOG_NAME].append(logname.replace('_flt_text.txt', '').replace('RTP_RED_', ''))
            
        log_1569 = LogPacket_0x1569(log)
        if log_1569.isValidPkt():
            data_dict_0x1569[TS].append(log_1569.getTimestamp())
            data_dict_0x1569[LOST_TYPE].append(log_1569.getLostType())
            data_dict_0x1569[NUM_LOST].append(log_1569.getNumLost())
            data_dict_0x1569[SEQUENCE].append(log_1569.getSequence())
            data_dict_0x1569[CODEC_TYPE].append(log_1569.getCodecType())
            data_dict_0x1569[LOG_NAME].append(logname.replace('_flt_text.txt', '').replace('RTP_RED_', ''))
            
        log_1568 = LogPacket_0x1568(log)
        if log_1568.isValidPkt():
            data_dict_0x1568[TS].append(log_1568.getTimestamp())
            data_dict_0x1568[RAT_TYPE].append(log_1568.getRatType())
            data_dict_0x1568[DIRECTION].append(log_1568.getDirection())
            data_dict_0x1568[MEDIA_TYPE].append(log_1568.getMediaType())
            data_dict_0x1568[CODEC_TYPE].append(log_1568.getCodecType())
            data_dict_0x1568[PAYLOAD_SIZE].append(log_1568.getPayloadSize())
            data_dict_0x1568[SEQUENCE].append(log_1568.getSequence())
            data_dict_0x1568[RTP_TS].append(log_1568.getRTP_TS())
            data_dict_0x1568[LOG_NAME].append(logname.replace('_flt_text.txt', '').replace('RTP_RED_', ''))
            
        log_156B = LogPacket_0x156B(log)
        if log_156B.isValidPkt():
            data_dict_0x156B[TS].append(log_156B.getTimestamp())
            data_dict_0x156B[RTP_TS].append(log_156B.getRTP_TS())
            data_dict_0x156B[SEQUENCE].append(log_156B.getSequence())
            data_dict_0x156B[FRAME_RECEIVE_TIME].append(log_156B.getFrameReceiveTime())
            data_dict_0x156B[ENQ_RESULT].append(log_156B.getEnQResult())
            data_dict_0x156B[IS_REDUNDANT].append(log_156B.getIsRedundant())
            data_dict_0x156B[LOG_NAME].append(logname.replace('_flt_text.txt', '').replace('RTP_RED_', ''))
            
        log_156C = LogPacket_0x156C(log)
        if log_156C.isValidPkt():
            data_dict_0x156C[TS].append(log_156C.getTimestamp())
            data_dict_0x156C[RTP_TS].append(log_156C.getRTP_TS())
            data_dict_0x156C[SEQUENCE].append(log_156C.getSequence())
            data_dict_0x156C[FRAME_RECEIVE_TIME].append(log_156C.getFrameReceiveTime())
            data_dict_0x156C[DEQ_STATE].append(log_156C.getDeQState())
            data_dict_0x156C[FRAME_DELAY].append(log_156C.getFrameDelay())
            data_dict_0x156C[TARGET_DELAY].append(log_156C.getTargetDelay())
            data_dict_0x156C[Q_SIZE].append(log_156C.getQSize())
            data_dict_0x156C[DEQ_DELTA].append(log_156C.getDeQDelta())
            data_dict_0x156C[IS_REDUNDANT].append(log_156C.getIsRedundant())
            data_dict_0x156C[RED_ENQ_STATUS].append(log_156C.getRedEnQStatus())
            data_dict_0x156C[LOG_NAME].append(logname.replace('_flt_text.txt', '').replace('RTP_RED_', ''))
            
        log_3188 = LogPacket_3188(log)
        if log_3188.isValidPkt():
            data_dict_3188[TS].append(log_3188.getTimestamp())
            data_dict_3188[EVENT].append(log_3188.getEvent())
            data_dict_3188[SOURCE_PCI].append(log_3188.getSourcePCI())
            data_dict_3188[SOURCE_ARFCN].append(log_3188.getSourceARFCN())
            data_dict_3188[TARGET_PCI].append(log_3188.getTargetPCI())
            data_dict_3188[TARGET_ARFCN].append(log_3188.getTargetARFCN())
            data_dict_3188[LOG_NAME].append(logname.replace('_flt_text.txt', '').replace('RTP_RED_', ''))
            


# Get Rx/Tx link duration
df_0x1E9C = pd.DataFrame(data_dict_0x1E9C)
df_0x1E9C = df_0x1E9C.sort_values(by='Timestamp')

df_0x1E9C_link_duration_Rx = df_0x1E9C[df_0x1E9C[DIRECTION] == 'RX'][[TS, EVENT, LOG_NAME]]
df_0x1E9C_link_duration_Rx['event_start_TS'] = df_0x1E9C_link_duration_Rx[TS].where(df_0x1E9C_link_duration_Rx[EVENT] == 'FLOW_START', None)
df_0x1E9C_link_duration_Rx['event_start_TS'] = df_0x1E9C_link_duration_Rx['event_start_TS'].ffill()
df_0x1E9C_link_duration_Rx['event_stop_TS'] = df_0x1E9C_link_duration_Rx[TS].where(df_0x1E9C_link_duration_Rx[EVENT] == 'FLOW_STOP', None)
df_0x1E9C_link_duration_Rx['event_start_TS'] = pd.to_datetime(df_0x1E9C_link_duration_Rx['event_start_TS'], format='%H:%M:%S.%f')
df_0x1E9C_link_duration_Rx['event_stop_TS'] = pd.to_datetime(df_0x1E9C_link_duration_Rx['event_stop_TS'], format='%H:%M:%S.%f')
df_0x1E9C_link_duration_Rx['Rx Link Duration (ms)'] = (df_0x1E9C_link_duration_Rx['event_stop_TS'] - df_0x1E9C_link_duration_Rx['event_start_TS'])/np.timedelta64(1, 'ms')
df_0x1E9C_link_duration_Rx['event_start_TS'] = df_0x1E9C_link_duration_Rx['event_start_TS'].dt.time
df_0x1E9C_link_duration_Rx['event_stop_TS'] = df_0x1E9C_link_duration_Rx['event_stop_TS'].dt.time
df_0x1E9C_link_duration_Rx = df_0x1E9C_link_duration_Rx[['event_start_TS', 'event_stop_TS', 'Rx Link Duration (ms)', LOG_NAME]].dropna()

df_0x1E9C_link_duration_Tx = df_0x1E9C[df_0x1E9C[DIRECTION] == 'TX'][[TS, EVENT, LOG_NAME]]
df_0x1E9C_link_duration_Tx['event_start_TS'] = df_0x1E9C_link_duration_Tx[TS].where(df_0x1E9C_link_duration_Tx[EVENT] == 'FLOW_START', None)
df_0x1E9C_link_duration_Tx['event_start_TS'] = df_0x1E9C_link_duration_Tx['event_start_TS'].ffill()
df_0x1E9C_link_duration_Tx['event_stop_TS'] = df_0x1E9C_link_duration_Tx[TS].where(df_0x1E9C_link_duration_Tx[EVENT] == 'FLOW_STOP', None)
df_0x1E9C_link_duration_Tx['event_start_TS'] = pd.to_datetime(df_0x1E9C_link_duration_Tx['event_start_TS'], format='%H:%M:%S.%f')
df_0x1E9C_link_duration_Tx['event_stop_TS'] = pd.to_datetime(df_0x1E9C_link_duration_Tx['event_stop_TS'], format='%H:%M:%S.%f')
df_0x1E9C_link_duration_Tx['Tx Link Duration (ms)'] = (df_0x1E9C_link_duration_Tx['event_stop_TS'] - df_0x1E9C_link_duration_Tx['event_start_TS'])/np.timedelta64(1, 'ms')
df_0x1E9C_link_duration_Tx['event_start_TS'] = df_0x1E9C_link_duration_Tx['event_start_TS'].dt.time
df_0x1E9C_link_duration_Tx['event_stop_TS'] = df_0x1E9C_link_duration_Tx['event_stop_TS'].dt.time
df_0x1E9C_link_duration_Tx = df_0x1E9C_link_duration_Tx[['event_start_TS', 'event_stop_TS', 'Tx Link Duration (ms)', LOG_NAME]].dropna()

# Get pkt lost stats
df_0x1569 = pd.DataFrame(data_dict_0x1569)
df_0x1569 = df_0x1569.sort_values(by=TS)

# Get RTP stats
df_0x1568 = pd.DataFrame(data_dict_0x1568)
df_0x1568 = df_0x1568.sort_values(by=TS)
df_0x1568_Rx = df_0x1568[df_0x1568[DIRECTION] == 'NETWORK_TO_UE']
df_0x1568_Tx = df_0x1568[df_0x1568[DIRECTION] == 'UE_TO_NETWORK']
df_0x156B = pd.DataFrame(data_dict_0x156B)
df_0x156B = df_0x156B.sort_values(by=TS)
df_0x156C = pd.DataFrame(data_dict_0x156C)
df_0x156C = df_0x156C.sort_values(by=TS)
df_rtp_stats_Rx = pd.merge(df_0x1568_Rx, df_0x156B, on=TS, how='outer')
df_rtp_stats_Rx = df_rtp_stats_Rx.merge(df_0x156C, on=TS, how='outer')
df_rtp_stats_Rx = df_rtp_stats_Rx.sort_values(by=TS)

# Get HO stats
df_3188 = pd.DataFrame(data_dict_3188)
df_3188 = df_3188.sort_values(by=TS)

dt_string = dt.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'Redundant_RTP_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(test.workingDir, saveFileName)
with pd.ExcelWriter(savePath, engine='xlsxwriter') as writer:
    df_0x1E9C.to_excel(writer, sheet_name = '0x1E9C_Data', index = False)
    df_0x1E9C_link_duration_Rx.to_excel(writer, sheet_name = 'Rx_Link_Duration', index = False)
    df_0x1E9C_link_duration_Tx.to_excel(writer, sheet_name = 'Tx_Link_Duration', index = False)
    df_rtp_stats_Rx.to_excel(writer, sheet_name = 'RTP_Rx', index = False)
    df_0x1568_Tx.to_excel(writer, sheet_name = 'RTP_Tx', index = False)
    df_0x1569.to_excel(writer, sheet_name = 'RTP_Lost_Stats', index = False)
    df_3188.to_excel(writer, sheet_name = 'Handover', index = False)