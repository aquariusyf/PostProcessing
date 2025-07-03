from FilterMask import *
from PostProcessingUtils import PostProcessingUtils
from datetime import datetime as dt
import sys
import os
import pandas as pd
import numpy as np
import re

filter_mask[LOG_FILTER] = []
filter_mask[EVENT_FILTER] = []
filter_mask[QTRACE_NON_REGEX] = ['Received RTP tstamp= %u, marker = %d, seq = %u, len = %d', 
                                 '[IMS_RED] Received RTP tstamp= %u, marker = %d, seq = %u, len = %d']

# key names
PRIM_TS = 'Timestamp Prim'
PRIM_RTP_TS = 'Prim RTP Timestamp'
PRIM_RTP_SEQ = 'Prim RTP Sequence'
PRIM_RTP_LEN = 'Prim RTP Length'
RED_TS = 'Timestamp Red'
RED_RTP_TS = 'RED RTP Timestamp'
RED_RTP_SEQ = 'RED RTP Sequence'
RED_RTP_LEN = 'RED RTP Length'
LOG_NAME = 'Log Name'

# REs
RE_PRIM = re.compile(r'.*Misc\-ID\:0      Received RTP tstamp= ([\d]+),.*seq = ([\d]+).*len = ([\d]+).*')
RE_RED = re.compile(r'.*Misc\-ID\:0     \[IMS_RED\] Received RTP tstamp= ([\d]+),.*seq = ([\d]+).*len = ([\d]+).*')

red_rtp_delay = PostProcessingUtils()
ARGV = sys.argv
ARGV.append('-qtrace')
red_rtp_delay.getArgv(ARGV)
red_rtp_delay.scanWorkingDir()
if not red_rtp_delay.skipFitlerLogs():
    red_rtp_delay.convertToText('RED_RTP_DELAY')
red_rtp_delay.scanWorkingDir('_flt_text.txt', 'RED_RTP_DELAY')
red_rtp_delay.initLogPacketList()
all_logs = red_rtp_delay.getLogPacketList()
            
data_dict_prim = {PRIM_TS: [], PRIM_RTP_TS: [], PRIM_RTP_SEQ: [], PRIM_RTP_LEN: [], LOG_NAME: []}
data_dict_red = {RED_TS: [], RED_RTP_TS: [], RED_RTP_SEQ: [], RED_RTP_LEN: [], LOG_NAME: []}


for logname, logs in all_logs.items():
    for log in logs:
        for line in log.getContent():
            if RE_PRIM.match(line):
                data_dict_prim[LOG_NAME].append(logname.replace('_flt_text.txt', '').replace('RED_RTP_DELAY', ''))
                data_dict_prim[PRIM_TS].append(log.getTimestamp())
                data_dict_prim[PRIM_RTP_TS].append(RE_PRIM.match(line).groups()[0])
                data_dict_prim[PRIM_RTP_SEQ].append(RE_PRIM.match(line).groups()[1])
                data_dict_prim[PRIM_RTP_LEN].append(RE_PRIM.match(line).groups()[2])
            elif RE_RED.match(line):
                data_dict_red[LOG_NAME].append(logname.replace('_flt_text.txt', '').replace('RED_RTP_DELAY', ''))
                data_dict_red[RED_TS].append(log.getTimestamp())
                data_dict_red[RED_RTP_TS].append(RE_RED.match(line).groups()[0])
                data_dict_red[RED_RTP_SEQ].append(RE_RED.match(line).groups()[1])
                data_dict_red[RED_RTP_LEN].append(RE_RED.match(line).groups()[2])
            
df_prim = pd.DataFrame(data_dict_prim)
df_prim = df_prim.sort_values(by=PRIM_TS)
df_prim['Merge_Tag'] = df_prim[PRIM_RTP_TS] + '_' + df_prim[PRIM_RTP_SEQ]
df_red = pd.DataFrame(data_dict_red)
df_red = df_red.sort_values(by=RED_TS)
df_red['Merge_Tag'] = df_red[RED_RTP_TS] + '_' + df_red[RED_RTP_SEQ]

df_merged = pd.merge(df_prim, df_red, on='Merge_Tag', how='outer')
df_merged = df_merged.sort_values(by=PRIM_TS)

df_merged[RED_TS] = pd.to_datetime(df_merged[RED_TS], format='%H:%M:%S.%f')
df_merged[PRIM_TS] = pd.to_datetime(df_merged[PRIM_TS], format='%H:%M:%S.%f')
df_merged['RED RTP Delay (ms)'] = (df_merged[RED_TS] - df_merged[PRIM_TS])/np.timedelta64(1, 'ms')
df_merged = df_merged.drop(columns=['Merge_Tag', 'Log Name_x'])

dt_string = dt.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'RED_RTP_DELAY_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(red_rtp_delay.workingDir, saveFileName)
with pd.ExcelWriter(savePath, engine='xlsxwriter') as writer:
    df_merged.to_excel(writer, sheet_name = 'sheet1', index = False)