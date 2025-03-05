#---------------------------------------------------------------------------------------------------------------------------------------------------
# Extract NR and LTE serving cell info from logs and merge with FPS data by timestamp
#---------------------------------------------------------------------------------------------------------------------------------------------------

from PostProcessingUtils import PostProcessingUtils
from FilterMask import *
from datetime import datetime
import pandas as pd
import sys
import os
import re

filter_mask[LOG_FILTER] = [0xB974, 0xB193, 0xB064]
filter_mask[EVENT_FILTER] = []
filter_mask[QTRACE_NON_REGEX] = []
filter_mask[KEYWORDS_FILTER] = []

RE_NR_FREQ = re.compile(r'.*Raster Freq = ([\d]+)')
RE_NR_PCI = re.compile(r'.*PCI = ([\d]+)')
RE_NR_RSRP = re.compile(r'.*Cell Quality RSRP = ([\-\.\d]+).*')
RE_NR_RSRQ = re.compile(r'.*Cell Quality RSRQ = ([\-\.\d]+).*')
RE_NR_SNR = re.compile(r'.*Cell Quality SNR = ([\-\.\d]+).*')
RE_LTE_FREQ = re.compile(r'.*E\-ARFCN = ([\d]+)')
RE_LTE_PCI = re.compile(r'.*Physical Cell ID = ([\d]+)')
RE_LTE_RSRP = re.compile(r'.*True Inst Measured RSRP = ([\-\.\d]+).*')
RE_LTE_RSRQ = re.compile(r'.*True Inst RSRQ = ([\-\.\d]+).*')
RE_LTE_SNR = re.compile(r'.*RS SNR Rx\[0\] = ([\-\.\dA-Za-z]+).*')
RE_GRANT_SIZE = re.compile(r'\|[\s\d]+\|[\s\d]+\|.*C\-RNTI\|[\s\d]+\|[\s\d]+\|[\s]*([\d]+)\|.*')

STUCK_THRESHOLD = 0 # Stuck threshold, FPS less than this value will be considered as video stuck
TIMESTAMP = 'Timestamp'
TECH = 'Tech'
FREQUENCY = 'Frequency'
PCI = 'PCI'
RSRP = 'RSRP(dBm)'
RSRQ = 'RSRQ(dB)'
SNR = 'SNR(dB)'
LOG_NAME = 'Log File'
IS_NR_SERVING_CELL = 'Serving Cell Index = SERVING CELL'
IS_LTE_SERVING_CELL = 'Is Serving Cell = 1'
LTE_PKT_MULTIPLE_ENTRY = 'Cells[1]'
GRANT_SIZE = 'Grant Size'
GRANT_SIZE_ACCUM = 'Accumulated Grant Size'

dict_serving_cell_info = {TIMESTAMP: [], TECH: [], FREQUENCY: [], PCI: [], RSRP: [], RSRQ: [], SNR: [], LOG_NAME: []}
dict_grant_size = {TIMESTAMP: [], GRANT_SIZE: []}

serving_cell_info = PostProcessingUtils()
serving_cell_info.getArgv(sys.argv)
serving_cell_info.scanWorkingDir()
if not serving_cell_info.skipFitlerLogs():
    serving_cell_info.convertToText('serving_cell_info')
serving_cell_info.scanWorkingDir('_flt_text.txt', 'serving_cell_info')
serving_cell_info.initLogPacketList()

all_log_pkt = serving_cell_info.getLogPacketList()
for logname, logs in all_log_pkt.items():
    for logpkt in logs:
        if logpkt.getPacketCode() == '0xB974' and logpkt.containsIE(IS_NR_SERVING_CELL): # NR
            for line in logpkt.getContent():
                if RE_NR_FREQ.match(line) and int(RE_NR_FREQ.match(line).groups()[0]) > 0:
                    dict_serving_cell_info[FREQUENCY].append(int(RE_NR_FREQ.match(line).groups()[0]))
                    dict_serving_cell_info[TECH].append(5)
                    dict_serving_cell_info[TIMESTAMP].append(logpkt.getTimestamp())
                    dict_serving_cell_info[LOG_NAME].append(logname)
                elif RE_NR_PCI.match(line) and int(RE_NR_PCI.match(line).groups()[0]) > 0:
                    dict_serving_cell_info[PCI].append(int(RE_NR_PCI.match(line).groups()[0]))
                elif RE_NR_RSRP.match(line):
                    dict_serving_cell_info[RSRP].append(RE_NR_RSRP.match(line).groups()[0])
                elif RE_NR_RSRQ.match(line):
                    dict_serving_cell_info[RSRQ].append(RE_NR_RSRQ.match(line).groups()[0])
                elif RE_NR_SNR.match(line):
                    dict_serving_cell_info[SNR].append(RE_NR_SNR.match(line).groups()[0])
                else:
                    continue
        elif logpkt.getPacketCode() == '0xB193' and logpkt.containsIE(IS_LTE_SERVING_CELL) and not logpkt.containsIE(LTE_PKT_MULTIPLE_ENTRY): # LTE
            LTE_freq_found = False
            LTE_pci_found = False
            LTE_rsrp_found = False
            LTE_rsrq_found = False
            LTE_snr_found = False
            for line in logpkt.getContent():
                if RE_LTE_FREQ.match(line) and int(RE_LTE_FREQ.match(line).groups()[0]) > 0 and not LTE_freq_found:
                    dict_serving_cell_info[FREQUENCY].append(int(RE_LTE_FREQ.match(line).groups()[0]))
                    dict_serving_cell_info[TIMESTAMP].append(logpkt.getTimestamp())
                    dict_serving_cell_info[TECH].append(4)
                    dict_serving_cell_info[LOG_NAME].append(logname)
                    LTE_freq_found = True
                elif RE_LTE_PCI.match(line) and int(RE_LTE_PCI.match(line).groups()[0]) > 0 and LTE_freq_found and not LTE_pci_found:
                    dict_serving_cell_info[PCI].append(int(RE_LTE_PCI.match(line).groups()[0]))
                    LTE_pci_found = True
                elif RE_LTE_RSRP.match(line) and LTE_freq_found and LTE_pci_found and not LTE_rsrp_found:
                    dict_serving_cell_info[RSRP].append(RE_LTE_RSRP.match(line).groups()[0])
                    LTE_rsrp_found = True
                elif RE_LTE_RSRQ.match(line) and LTE_freq_found and LTE_pci_found and LTE_rsrp_found and not LTE_rsrq_found:
                    dict_serving_cell_info[RSRQ].append(RE_LTE_RSRQ.match(line).groups()[0])
                    LTE_rsrq_found = True
                elif RE_LTE_SNR.match(line) and LTE_freq_found and LTE_pci_found and LTE_rsrp_found and LTE_rsrq_found and not LTE_snr_found:
                    dict_serving_cell_info[SNR].append(RE_LTE_SNR.match(line).groups()[0])
                    LTE_snr_found = True
                    break
                else:
                    continue
        elif logpkt.getPacketCode() == '0xB064':
            grant_size_signle_pkt = 0
            for line in logpkt.getContent():
                if RE_GRANT_SIZE.match(line):
                    grant_size_signle_pkt += int(RE_GRANT_SIZE.match(line).groups()[0])
            dict_grant_size[TIMESTAMP].append(logpkt.getTimestamp())
            dict_grant_size[GRANT_SIZE].append(grant_size_signle_pkt)
        else:
            continue

def append_stuck_duration(df, column): # Get FPS stuck durations
    count = 0
    counts = []
    for i in range(len(df)):
        if df.loc[i, column] <= STUCK_THRESHOLD:
            count += 1
        else:
            if count > 0:
                counts.extend([None] * (count - 1) + [count] + [None])
            else:
                counts.extend([None])
            count = 0
    if count > 0:
        counts.extend([None] * (count - 1) + [count])
    df['Stuck_Duration'] = counts
    return df

def append_accum_grant_size(df, column_grant_size, column_include, column_tech): # Get accumulated grant size where Include = Yes
    accum_grant_size = 0
    df[GRANT_SIZE_ACCUM] = 'NA'
    for i in range(len(df)):
        if df.loc[i, column_tech] != 4:
            accum_grant_size = 0
        elif df.loc[i, column_include] == 'Yes':
            df.loc[i, GRANT_SIZE_ACCUM] = accum_grant_size
            accum_grant_size = 0
        elif df.loc[i, column_include] == 'No':
            accum_grant_size += df.loc[i, column_grant_size]
    return df

df_serving_cell = pd.DataFrame(dict_serving_cell_info)
df_serving_cell = df_serving_cell.astype({'Timestamp': 'str'})

df_grant_size = pd.DataFrame(dict_grant_size)
df_grant_size = df_grant_size.astype({'Timestamp': 'str'})

df_fps_data = pd.read_excel(os.path.join(serving_cell_info.workingDir, 'FPS_data.xlsx'), sheet_name='Sheet1')
df_fps_data = df_fps_data.astype({'Timestamp': 'str'})
df_fps_data = append_stuck_duration(df_fps_data, 'FPS')

df_merged = df_serving_cell.merge(df_fps_data, on='Timestamp', how='outer')
df_merged = df_merged.sort_values(by='Timestamp')
df_merged = df_merged.merge(df_grant_size, on='Timestamp', how='outer')
df_merged = df_merged.sort_values(by='Timestamp')

df_merged[TECH] = df_merged[TECH].ffill()
df_merged[FREQUENCY] = df_merged[FREQUENCY].ffill()
df_merged[PCI] = df_merged[PCI].ffill()
df_merged[RSRP] = df_merged[RSRP].ffill()
df_merged[RSRQ] = df_merged[RSRQ].ffill()
df_merged[SNR] = df_merged[SNR].ffill()
df_merged[LOG_NAME] = df_merged[LOG_NAME].ffill()

df_merged['Include'] = 'Yes' # Include timestamps only from FPS data
df_merged['Include'] = df_merged['Include'].where(df_merged['FPS'] >= 0, 'No')
df_merged['FPS'] = df_merged['FPS'].ffill()

df_merged[GRANT_SIZE] = df_merged[GRANT_SIZE].fillna(0)
df_merged = df_merged.reset_index(drop=True)
df_merged = append_accum_grant_size(df_merged, GRANT_SIZE, 'Include', TECH)

df_merged = df_merged[[TIMESTAMP, TECH, FREQUENCY, PCI, RSRP, RSRQ, SNR, 'FPS', 'Stuck_Duration', GRANT_SIZE, GRANT_SIZE_ACCUM, 'Include', LOG_NAME]]

dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'FPS_vs_Serving_Cell_Info_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(serving_cell_info.workingDir, saveFileName)
df_merged.to_excel(savePath, sheet_name = 'sheet1', index = False)