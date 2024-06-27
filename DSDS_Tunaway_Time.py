#---------------------------------------------------------------------------------------------------------------------------------------------------
# Extract tune away times from logs
#---------------------------------------------------------------------------------------------------------------------------------------------------

from PostProcessingUtils import PostProcessingUtils
from FilterMask import *
from openpyxl import Workbook
from datetime import datetime
import pandas as pd
import sys
import os
import re

filter_mask[LOG_FILTER] = []
filter_mask[EVENT_FILTER] = []
filter_mask[QTRACE_NON_REGEX] = ['NR5GML1_QSH_EVENT_MSIM_LTA', 'NR5GML1_QSH_EVENT_MSIM_DTA', 'NR5GML1_QSH_EVENT_MSIM_QDTA']

RE_LTA = re.compile(r'.*NR5GML1_QSH_EVENT_MSIM_(LTA).*')
RE_DTA = re.compile(r'.*NR5GML1_QSH_EVENT_MSIM_(DTA).*')
RE_QDTA = re.compile(r'.*NR5GML1_QSH_EVENT_MSIM_(QDTA).*')
RE_TA_TIME = re.compile(r'.*ta_time: ([\d]+) ms.*')

AVG_LTA_TIME = 'avg_lta_time'
AVG_DTA_TIME = 'avg_dta_time'
AVG_QDTA_TIME = 'avg_qdta_time'
KPI = 'kpi'
LOGNAME = 'logname'

ARGV = sys.argv
ARGV.append('-qtrace')

tuneawayTime = PostProcessingUtils()
tuneawayTime.getArgv(ARGV)
tuneawayTime.scanWorkingDir()
if not tuneawayTime.skipFitlerLogs():
    tuneawayTime.convertToText('Tunaway_Time')
tuneawayTime.scanWorkingDir('_flt_text.txt', 'Tunaway_Time')
tuneawayTime.initLogPacketList()


dict_ta_time = {KPI: [AVG_LTA_TIME, AVG_DTA_TIME, AVG_QDTA_TIME]}
all_log_pkt = tuneawayTime.getLogPacketList()
for logname, logs in all_log_pkt.items():
    dict_ta_time[logname] = []
    sum_lta = 0
    count_lta = 0
    sum_dta = 0
    count_dta = 0
    sum_qdta = 0
    count_qdta = 0
    for logpkt in logs:
        for line in logpkt.getContent():
            if RE_LTA.match(line):
                # print(RE_LTA.match(line).groups()[0] + ' ' + RE_TA_TIME.match(line).groups()[0] + ' ms')
                sum_lta += int(RE_TA_TIME.match(line).groups()[0])
                count_lta += 1
            elif RE_DTA.match(line):
                # print(RE_DTA.match(line).groups()[0] + ' ' + RE_TA_TIME.match(line).groups()[0] + ' ms')
                sum_dta += int(RE_TA_TIME.match(line).groups()[0])
                count_dta += 1
            elif RE_QDTA.match(line):
                # print(RE_QDTA.match(line).groups()[0] + ' ' + RE_TA_TIME.match(line).groups()[0] + ' ms')
                sum_qdta += int(RE_TA_TIME.match(line).groups()[0])
                count_qdta += 1
    if count_lta != 0:             
        dict_ta_time[logname].append(int(sum_lta/count_lta))
    else:
        dict_ta_time[logname].append('NA')
    if count_dta != 0:
        dict_ta_time[logname].append(int(sum_dta/count_dta))
    else:
        dict_ta_time[logname].append('NA')
    if count_qdta != 0:
        dict_ta_time[logname].append(int(sum_qdta/count_qdta))
    else:
        dict_ta_time[logname].append('NA')

df = pd.DataFrame(dict_ta_time)
dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'TA_Time_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(tuneawayTime.workingDir, saveFileName)
df.to_excel(savePath, sheet_name = 'sheet1', index = False)
