#---------------------------------------------------------------------------------------------------------------------------------------------------
# Extract N2N handover KPI from logs
#---------------------------------------------------------------------------------------------------------------------------------------------------

from PostProcessingUtils import LogPacket, PostProcessingUtils, LogPacket_HO
from FilterMask import *
from openpyxl import Workbook
from datetime import datetime
import sys
import os

filter_mask[LOG_FILTER] = [0xB821]
filter_mask[EVENT_FILTER] = [3188, 3190]
filter_mask[QTRACE_NON_REGEX] = ['rach_setup_msg1_tx', 'Got DL_RAR_RESULT_INDI', 'rach_rar_state_handler', 'send MAC_RACH_ACTIVITY_IND rach_status',
                                 'Meas_Eval: Meas eval type', '5GSRCH_DTLD_CON: Meas_Eval: Meas id being evaluated is %d and corresponding  MO is %d[0:Inter, 1:Intra] BM ML Enable: %d Meas eval type - %d (0:Intra 1:Non-Intra 2:CHO), rpt_cfg is CHO - %dReporting config type - %d and Eval trig event- nr5g %d, EUTRAN %d']

# Convert log to text file with default filter
HO_KPI = PostProcessingUtils()
ARGV = sys.argv
ARGV.append('qtrace')
HO_KPI.getArgv(ARGV)
HO_KPI.scanWorkingDir() # default is .hdf
if not HO_KPI.skipFitlerLogs():
    HO_KPI.convertToText('HO_KPI')
# Initialize log pkt list from filtered text files
HO_KPI.scanWorkingDir('_flt_text.txt', 'HO_KPI')
HO_KPI.initLogPacketList()
logPktList_All_Logs = HO_KPI.getLogPacketList()

ARFCN = 'arfcn'
PCI = 'pci'

CRITMET = 'critMet'
MR = 'measReport'
GEN_RRC_RECONFIG = 'GEN_RRC_RECONFIG'
HO_CMD = 'HO_START'
GEN_RRC_COMPLETE = 'GEN_RRC_COMPLETE'
MSG_1 = 'MSG1'
MSG_2 = 'MSG2'
SEND_RRC_COMPLETE = 'SEND_RRCCOMPLETE'

CRITMET_TO_MR = 'Meas Criteria Met --> Meas Report'
MR_TO_HOCMD = 'Meas Report --> HO Command'
HOCMD_TO_GENRRCCOMPLETE = 'HO Command --> Generate RRC Reconfig Complete'
GENRRCCOMPLETE_TO_MSG1 = 'Generate RRC Reconfig Complete --> RACH MSG1'
MSG1_TO_MSG2 = 'RACH MSG1 --> RACH MSG2'
MSG2_TO_SENDRRCCOMPLETE = 'RACH MSG2 --> RRC Reconfig Complete'

CRITMET_TO_GENRRCRECONFIG = 'Meas Criteria Met --> Generate RRC Reconfig'
GENRRCRECONFIG_TO_GENRRCCOMPLETE = 'Generate RRC Reconfig --> Generate RRC Reconfig Complete'

# KPI Table Rows
First_Row = ['KPI Field']
TotalNumHO = ['Total Num of Handover']
TotalNumRegHO = ['Total Num of Regular Handover']
TotalNumCHO = ['Total Num of Conditional Handover']
AVGRegHODelay = ['AVG Regular HO Delay']
HOEventCritMet_To_MR = ['Meas Criteria Met --> Meas Report']
MR_To_HOCommand = ['Meas Report --> HO Command']
HOCommand_To_GenRRCReconfigComplete = ['HO Command --> Generate RRC Reconfig Complete']
HO_GenRRCReconfigComplete_To_MSG1 = ['Generate RRC Reconfig Complete --> RACH MSG1']
HO_MSG1_To_MSG2 = ['RACH MSG1 --> RACH MSG2']
HO_MSG2_To_Send_RRCReconfigComplete = ['RACH MSG2 --> RRC Reconfig Complete']
AVGCHODelay = ['AVG Conditional HO Delay']
HOEventCritMet_To_GenRRCReconfig = ['Meas Criteria Met --> Generate RRC Reconfig']
GenRRCReconfig_To_GenRRCReconfigComplete = ['Generate RRC Reconfig --> Generate RRC Reconfig Complete']
CHO_GenRRCReconfigComplete_To_MSG1 = ['Generate RRC Reconfig Complete --> RACH MSG1']
CHO_MSG1_To_MSG2 = ['RACH MSG1 --> RACH MSG2']
CHO_MSG2_To_Send_RRCReconfigComplete = ['RACH MSG2 --> RRC Reconfig Complete']

for key in logPktList_All_Logs.keys():
    First_Row.append(key) # Init first row with log names

print(datetime.now().strftime("%H:%M:%S"), '(N2N_Handover_Delay) ' + 'Extracting KPI Summary...')

def getHOKPI(pktList):
    if len(pktList) == 0:
        return [0, 0, 0, 
                'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']    
    
    TotalHO = 0
    TotalRegHO = 0
    TotalCHO = 0
    
    HO_BreakDown = {CRITMET: [],
                    MR: [],
                    HO_CMD: [],
                    GEN_RRC_COMPLETE: [],
                    MSG_1: [],
                    MSG_2: [],
                    SEND_RRC_COMPLETE: []}
    
    HO_DelayBreakDown = {CRITMET_TO_MR: [],
                      MR_TO_HOCMD: [],
                      HOCMD_TO_GENRRCCOMPLETE: [],
                      GENRRCCOMPLETE_TO_MSG1: [],
                      MSG1_TO_MSG2: [],
                      MSG2_TO_SENDRRCCOMPLETE: []}
    
    REGHO_CRITMET_TO_MR_Delay = 'N/A'
    REGHO_MR_TO_HOCMD_Delay = 'N/A'
    REGHO_HOCMD_TO_GENRRCCOMPLETE_Delay = 'N/A'
    REGHO_GENRRCCOMPLETE_TO_MSG1_Delay = 'N/A'
    REGHO_MSG1_TO_MSG2_Delay = 'N/A'
    REGHO_MSG2_TO_SENDRRCCOMPLETE_Delay = 'N/A'
    AVG_REGHO_Delay = 'N/A'
    
    CHO_BreakDown = {CRITMET: [],
                     GEN_RRC_RECONFIG: [],
                     GEN_RRC_COMPLETE: [],
                     MSG_1: [],
                     MSG_2: [],
                     SEND_RRC_COMPLETE: []}
    
    CHO_DelayBreakDown = {CRITMET_TO_GENRRCRECONFIG: [],
                      GENRRCRECONFIG_TO_GENRRCCOMPLETE: [],
                      GENRRCCOMPLETE_TO_MSG1: [],
                      MSG1_TO_MSG2: [],
                      MSG2_TO_SENDRRCCOMPLETE: []}
    
    CHO_CRITMET_TO_GENRRCRECONFIG_Delay = 'N/A'
    CHO_GENRRCRECONFIG_TO_GENRRCCOMPLETE_Delay = 'N/A'
    CHO_GENRRCCOMPLETE_TO_MSG1_Delay = 'N/A'
    CHO_MSG1_TO_MSG2_Delay = 'N/A'
    CHO_MSG2_TO_SENDRRCCOMPLETE_Delay = 'N/A'
    AVG_CHO_Delay = 'N/A'
    
    # CRITMET - Meas_Eval: Meas eval type - 0
    # MR - NR5G RRC OTA Packet  --  UL_DCCH / MeasurementReport
    # HOCMD - Event  --  EVENT_NR5G_RRC_HO_STARTED_V2
    # GENRRCCOMPLETE - RRCConfiguration Complete
    # MSG1 - rach_setup_msg1_tx
    # MSG2 - Got DL_RAR_RESULT_INDI
    # SENDRRCCOMPLETE - Event  --  EVENT_NR5G_RRC_HO_SUCCESS

    # Find the RRC Reconfig with HO cmd
    n = 0
    while n < len(pktList): 
        isHOSucEventMissing = False
        isCHO = False
        if pktList[n].getPacketCode() == '0x1FFB' and pktList[n].getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_STARTED_V2': # Find start of HO
            HO_pkt = LogPacket_HO(pktList[n])
            SourceCellInfo = HO_pkt.getSourceCellInfo()
            TargetCellInfo = HO_pkt.getTargetCellInfo()
            if SourceCellInfo[ARFCN] == TargetCellInfo[ARFCN] and SourceCellInfo[PCI] == TargetCellInfo[PCI]:
                print(datetime.now().strftime("%H:%M:%S"), '(N2N_Handover_Delay) ' + 'Detect source cell same as target cell! ' + 'ARFCN: ' + str(TargetCellInfo[ARFCN]) + ' PCI: ' + str(TargetCellInfo[PCI]))
                print(datetime.now().strftime("%H:%M:%S"), '(N2N_Handover_Delay) ' + 'Skip current HO!')
                n += 1
                continue
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

            HO_start_index = n
            m = HO_start_index
            # print(pktList[HO_start_index].getHeadline())
            while m >= 0: # Check if it is regular HO or CHO, and find CRIT Met
                x = -1
                if pktList[m].getPacketCode() == '0xB821' and pktList[m].getTitle() == 'NR5G RRC OTA Packet  --  DL_DCCH / RRCReconfiguration':
                    # print(isCHO)
                    HO_start_index = m
                    x = m - 1
                elif pktList[m].getPacketCode() == '0xB821' and pktList[m].getTitle() == 'NR5G RRC OTA Packet  --  RRC_RECONFIG':
                    HO_start_index = m
                    x = m - 1
                    isCHO = True
                else:
                    # print('M = ' + str(m))
                    # print('start index = ' + str(HO_start_index))
                    m -= 1
                    continue        
                while x >= 0:
                    if isCHO:
                        if pktList[x].getPacketCode() == '0x1FE8' and pktList[x].containsIE('Meas eval type - 2'):
                            CHO_BreakDown[CRITMET].append(pktList[x])
                            HO_start_index = x
                            # print('Found CHO CRIT MET!!!')
                            # print(pktList[x].getTimestamp())
                            break
                        elif x == 0 or (pktList[x].getPacketCode() == '0x1FFB' and pktList[x].getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_SUCCESS'): # No Meas eval found
                            CHO_BreakDown[CRITMET].append('N/A')
                            break
                        else:
                            x -= 1
                            continue
                    else:
                        if pktList[x].getPacketCode() == '0xB821' and pktList[x].getTitle() == 'NR5G RRC OTA Packet  --  UL_DCCH / MeasurementReport':
                            crit_n = x - 1
                            HO_BreakDown[MR].append(pktList[x])
                            crit_checked = False
                            while crit_n >= 0:
                                if pktList[crit_n].getPacketCode() == '0x1FE8' and pktList[crit_n].containsIE('Meas eval type - 0'):
                                    HO_BreakDown[CRITMET].append(pktList[crit_n])
                                    HO_start_index = crit_n
                                    crit_checked = True
                                    # print('Found HO CRIT MET!!!')
                                    break
                                elif crit_n == 0 or (pktList[crit_n].getPacketCode() == '0x1FFB' and pktList[crit_n].getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_SUCCESS'): # No Meas eval found
                                    HO_BreakDown[CRITMET].append('N/A')
                                    crit_checked = True
                                    break
                                else:
                                    crit_n -= 1
                                    continue
                            if not crit_checked:
                                HO_BreakDown[CRITMET].append('N/A')
                            break
                        elif x == 0 or (pktList[x].getPacketCode() == '0x1FFB' and pktList[x].getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_SUCCESS'):
                            HO_BreakDown[MR].append('N/A')
                            HO_BreakDown[CRITMET].append('N/A')
                            break
                        else:
                            x -= 1
                            continue
                break  
            
            Found_RRC_RECONFIG = False
            Found_GEN_RRC_COMPLETE = False
            Found_MSG_1 = False
            Found_MSG_2 = False
            Found_SEND_RRC_COMPLETE = False
            
            HO_CMD_Index = n
            GEN_RRC_RECONFIG_Index = -1
            GEN_RRC_COMPLETE_Index = -1
            MSG_1_Index = -1
            MSG_2_Index = -1
            SEND_RRC_COMPLETE_Index = -1
            
            # Find subsequent signalings
            for i in range(HO_start_index, len(pktList)):
                # print(i)
                if pktList[i].getPacketCode() == '0xB821' and pktList[i].getTitle() == 'NR5G RRC OTA Packet  --  RRC_RECONFIG' and isCHO and not Found_RRC_RECONFIG: # Find RRC_RECONFIG for CHO
                    GEN_RRC_RECONFIG_Index = i
                    Found_RRC_RECONFIG = True
                elif pktList[i].getPacketCode() == '0xB821' and pktList[i].getTitle() == 'NR5G RRC OTA Packet  --  UL_DCCH / RRCConfiguration Complete' and not Found_GEN_RRC_COMPLETE and i > n: # Find RRCReconfigComplete
                    GEN_RRC_COMPLETE_Index = i
                    Found_GEN_RRC_COMPLETE = True
                elif pktList[i].getPacketCode() == '0x1FE8' and pktList[i].containsIE('rach_setup_msg1_tx') and not Found_MSG_1 and i > n: # Find MSG 1
                    MSG_1_Index = i
                    Found_MSG_1 = True
                elif pktList[i].getPacketCode() == '0x1FE8' and pktList[i].containsIE('Got DL_RAR_RESULT_INDI') and not Found_MSG_2 and i > n: # Find MSG 2
                    MSG_2_Index = i
                    Found_MSG_2 = True
                elif pktList[i].getPacketCode() == '0x1FFB' and pktList[i].getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_SUCCESS' and not Found_SEND_RRC_COMPLETE and i > n: # Find end of HO
                    SEND_RRC_COMPLETE_Index = i
                    Found_SEND_RRC_COMPLETE = True         
                    break
                else:
                    continue
            if isCHO and GEN_RRC_RECONFIG_Index >= 0:
                CHO_BreakDown[GEN_RRC_RECONFIG].append(pktList[GEN_RRC_RECONFIG_Index])
            elif isCHO and GEN_RRC_RECONFIG_Index < 0:
                CHO_BreakDown[GEN_RRC_RECONFIG].append('N/A')
            if HO_CMD_Index >= 0 and not isCHO:
                HO_BreakDown[HO_CMD].append(pktList[HO_CMD_Index])
            elif HO_CMD_Index < 0 and not isCHO:
                HO_BreakDown[HO_CMD].append('N/A')
            if GEN_RRC_COMPLETE_Index >= 0:
                if isCHO:
                    CHO_BreakDown[GEN_RRC_COMPLETE].append(pktList[GEN_RRC_COMPLETE_Index])
                else:
                    HO_BreakDown[GEN_RRC_COMPLETE].append(pktList[GEN_RRC_COMPLETE_Index])
            else:
                if isCHO:
                    CHO_BreakDown[GEN_RRC_COMPLETE].append('N/A')
                else:
                    HO_BreakDown[GEN_RRC_COMPLETE].append('N/A')
            if MSG_1_Index >= 0:
                if isCHO:
                    CHO_BreakDown[MSG_1].append(pktList[MSG_1_Index])
                else:
                    HO_BreakDown[MSG_1].append(pktList[MSG_1_Index])
            else:
                if isCHO:
                    CHO_BreakDown[MSG_1].append('N/A')
                else:
                    HO_BreakDown[MSG_1].append('N/A')
            if MSG_2_Index >= 0:
                if isCHO:
                    CHO_BreakDown[MSG_2].append(pktList[MSG_2_Index])
                else:
                    HO_BreakDown[MSG_2].append(pktList[MSG_2_Index])
            else:
                if isCHO:
                    CHO_BreakDown[MSG_2].append('N/A')
                else:
                    HO_BreakDown[MSG_2].append('N/A')
            if SEND_RRC_COMPLETE_Index >= 0:
                if isCHO:
                    CHO_BreakDown[SEND_RRC_COMPLETE].append(pktList[SEND_RRC_COMPLETE_Index])
                else:
                    HO_BreakDown[SEND_RRC_COMPLETE].append(pktList[SEND_RRC_COMPLETE_Index])
            else:
                if isCHO:
                    CHO_BreakDown[SEND_RRC_COMPLETE].append('N/A')
                else:
                    HO_BreakDown[SEND_RRC_COMPLETE].append('N/A')
            n += 1
        else:
            n += 1
    
    # if len(HO_BreakDown[CRITMET]) != 0 and \
    #    len(HO_BreakDown[CRITMET]) == len(HO_BreakDown[MR]) and \
    #    len(HO_BreakDown[MR]) == len(HO_BreakDown[HO_CMD]) and \
    #    len(HO_BreakDown[HO_CMD]) == len(HO_BreakDown[GEN_RRC_COMPLETE]) and \
    #    len(HO_BreakDown[GEN_RRC_COMPLETE]) == len(HO_BreakDown[MSG_1]) and \
    #    len(HO_BreakDown[MSG_1]) == len(HO_BreakDown[MSG_2]) and \
    #    len(HO_BreakDown[MSG_2]) == len(HO_BreakDown[SEND_RRC_COMPLETE]):
    TotalRegHO = len(HO_BreakDown[SEND_RRC_COMPLETE]) # Get total num of regular HO
    REGHO_Delay = []
    AVG_REGHO_Delay = 'N/A'
    for n in range(0, len(HO_BreakDown[CRITMET])): # Get signaling delays
        if HO_BreakDown[MR][n] != 'N/A' and HO_BreakDown[CRITMET][n] != 'N/A':
            HO_DelayBreakDown[CRITMET_TO_MR].append(LogPacket.getDelay(HO_BreakDown[MR][n], HO_BreakDown[CRITMET][n]))
        if HO_BreakDown[HO_CMD][n] != 'N/A' and HO_BreakDown[MR][n] != 'N/A':
            HO_DelayBreakDown[MR_TO_HOCMD].append(LogPacket.getDelay(HO_BreakDown[HO_CMD][n], HO_BreakDown[MR][n]))
        if HO_BreakDown[GEN_RRC_COMPLETE][n] != 'N/A' and HO_BreakDown[HO_CMD][n] != 'N/A':
            HO_DelayBreakDown[HOCMD_TO_GENRRCCOMPLETE].append(LogPacket.getDelay(HO_BreakDown[GEN_RRC_COMPLETE][n], HO_BreakDown[HO_CMD][n]))
            # print(HO_BreakDown[GEN_RRC_COMPLETE][n].getHeadline())
            # print(HO_BreakDown[HO_CMD][n].getHeadline())
            # print(LogPacket.getDelay(HO_BreakDown[GEN_RRC_COMPLETE][n], HO_BreakDown[HO_CMD][n]))
        if HO_BreakDown[MSG_1][n] != 'N/A' and HO_BreakDown[GEN_RRC_COMPLETE][n] != 'N/A':
            HO_DelayBreakDown[GENRRCCOMPLETE_TO_MSG1].append(LogPacket.getDelay(HO_BreakDown[MSG_1][n], HO_BreakDown[GEN_RRC_COMPLETE][n]))
        if HO_BreakDown[MSG_2][n] != 'N/A' and HO_BreakDown[MSG_1][n] != 'N/A':
            HO_DelayBreakDown[MSG1_TO_MSG2].append(LogPacket.getDelay(HO_BreakDown[MSG_2][n], HO_BreakDown[MSG_1][n]))
        if HO_BreakDown[SEND_RRC_COMPLETE][n] != 'N/A' and HO_BreakDown[MSG_2][n] != 'N/A':
            HO_DelayBreakDown[MSG2_TO_SENDRRCCOMPLETE].append(LogPacket.getDelay(HO_BreakDown[SEND_RRC_COMPLETE][n], HO_BreakDown[MSG_2][n]))
        if HO_BreakDown[SEND_RRC_COMPLETE][n] != 'N/A' and HO_BreakDown[CRITMET][n] != 'N/A':
            REGHO_Delay.append(LogPacket.getDelay(HO_BreakDown[SEND_RRC_COMPLETE][n], HO_BreakDown[CRITMET][n]))
    if HO_DelayBreakDown[CRITMET_TO_MR] != []:
        REGHO_CRITMET_TO_MR_Delay = sum(HO_DelayBreakDown[CRITMET_TO_MR])/len(HO_DelayBreakDown[CRITMET_TO_MR])
    if HO_DelayBreakDown[MR_TO_HOCMD] != []:
        REGHO_MR_TO_HOCMD_Delay = sum(HO_DelayBreakDown[MR_TO_HOCMD])/len(HO_DelayBreakDown[MR_TO_HOCMD])
    if HO_DelayBreakDown[HOCMD_TO_GENRRCCOMPLETE] != []:
        REGHO_HOCMD_TO_GENRRCCOMPLETE_Delay = sum(HO_DelayBreakDown[HOCMD_TO_GENRRCCOMPLETE])/len(HO_DelayBreakDown[HOCMD_TO_GENRRCCOMPLETE])
    if HO_DelayBreakDown[GENRRCCOMPLETE_TO_MSG1] != []:
        REGHO_GENRRCCOMPLETE_TO_MSG1_Delay = sum(HO_DelayBreakDown[GENRRCCOMPLETE_TO_MSG1])/len(HO_DelayBreakDown[GENRRCCOMPLETE_TO_MSG1])
    if HO_DelayBreakDown[MSG1_TO_MSG2] != []:  
        REGHO_MSG1_TO_MSG2_Delay = sum(HO_DelayBreakDown[MSG1_TO_MSG2])/len(HO_DelayBreakDown[MSG1_TO_MSG2])
    if HO_DelayBreakDown[MSG2_TO_SENDRRCCOMPLETE] != []:
        REGHO_MSG2_TO_SENDRRCCOMPLETE_Delay = sum(HO_DelayBreakDown[MSG2_TO_SENDRRCCOMPLETE])/len(HO_DelayBreakDown[MSG2_TO_SENDRRCCOMPLETE])
    if REGHO_Delay != []:
        AVG_REGHO_Delay = sum(REGHO_Delay)/len(REGHO_Delay) # Get AVG delay
            
    # if len(CHO_BreakDown[CRITMET]) != 0 and \
    #    len(CHO_BreakDown[CRITMET]) == len(CHO_BreakDown[GEN_RRC_RECONFIG]) and \
    #    len(CHO_BreakDown[GEN_RRC_RECONFIG]) == len(CHO_BreakDown[GEN_RRC_COMPLETE]) and \
    #    len(CHO_BreakDown[GEN_RRC_COMPLETE]) == len(CHO_BreakDown[MSG_1]) and \
    #    len(CHO_BreakDown[MSG_1]) == len(CHO_BreakDown[MSG_2]) and \
    #    len(CHO_BreakDown[MSG_2]) == len(CHO_BreakDown[SEND_RRC_COMPLETE]):
    TotalCHO = len(CHO_BreakDown[SEND_RRC_COMPLETE]) # Get total num of CHO
    CHO_Delay = []
    AVG_CHO_Delay = 'N/A'
    for n in range(0, len(CHO_BreakDown[CRITMET])): # Get signaling delays
        if CHO_BreakDown[GEN_RRC_RECONFIG][n] != 'N/A' and CHO_BreakDown[CRITMET][n] != 'N/A':
            CHO_DelayBreakDown[CRITMET_TO_GENRRCRECONFIG].append(LogPacket.getDelay(CHO_BreakDown[GEN_RRC_RECONFIG][n], CHO_BreakDown[CRITMET][n]))
        if CHO_BreakDown[GEN_RRC_COMPLETE][n] != 'N/A' and CHO_BreakDown[GEN_RRC_RECONFIG][n] != 'N/A':
            CHO_DelayBreakDown[GENRRCRECONFIG_TO_GENRRCCOMPLETE].append(LogPacket.getDelay(CHO_BreakDown[GEN_RRC_COMPLETE][n], CHO_BreakDown[GEN_RRC_RECONFIG][n]))
        if CHO_BreakDown[MSG_1][n] != 'N/A' and CHO_BreakDown[GEN_RRC_COMPLETE][n] != 'N/A':
            CHO_DelayBreakDown[GENRRCCOMPLETE_TO_MSG1].append(LogPacket.getDelay(CHO_BreakDown[MSG_1][n], CHO_BreakDown[GEN_RRC_COMPLETE][n]))
        if CHO_BreakDown[MSG_2][n] != 'N/A' and CHO_BreakDown[MSG_1][n] != 'N/A':
            CHO_DelayBreakDown[MSG1_TO_MSG2].append(LogPacket.getDelay(CHO_BreakDown[MSG_2][n], CHO_BreakDown[MSG_1][n]))
        if CHO_BreakDown[SEND_RRC_COMPLETE][n] != 'N/A' and CHO_BreakDown[MSG_2][n] != 'N/A':
            CHO_DelayBreakDown[MSG2_TO_SENDRRCCOMPLETE].append(LogPacket.getDelay(CHO_BreakDown[SEND_RRC_COMPLETE][n], CHO_BreakDown[MSG_2][n]))
        if CHO_BreakDown[SEND_RRC_COMPLETE][n] != 'N/A' and CHO_BreakDown[CRITMET][n] != 'N/A':
            CHO_Delay.append(LogPacket.getDelay(CHO_BreakDown[SEND_RRC_COMPLETE][n], CHO_BreakDown[CRITMET][n]))
    if CHO_DelayBreakDown[CRITMET_TO_GENRRCRECONFIG] != []:
        CHO_CRITMET_TO_GENRRCRECONFIG_Delay = sum(CHO_DelayBreakDown[CRITMET_TO_GENRRCRECONFIG])/len(CHO_DelayBreakDown[CRITMET_TO_GENRRCRECONFIG])
    if CHO_DelayBreakDown[GENRRCRECONFIG_TO_GENRRCCOMPLETE] != []:
        CHO_GENRRCRECONFIG_TO_GENRRCCOMPLETE_Delay = sum(CHO_DelayBreakDown[GENRRCRECONFIG_TO_GENRRCCOMPLETE])/len(CHO_DelayBreakDown[GENRRCRECONFIG_TO_GENRRCCOMPLETE])
    if CHO_DelayBreakDown[GENRRCCOMPLETE_TO_MSG1] != []:
        CHO_GENRRCCOMPLETE_TO_MSG1_Delay = sum(CHO_DelayBreakDown[GENRRCCOMPLETE_TO_MSG1])/len(CHO_DelayBreakDown[GENRRCCOMPLETE_TO_MSG1])
    if CHO_DelayBreakDown[MSG1_TO_MSG2] != []:
        CHO_MSG1_TO_MSG2_Delay = sum(CHO_DelayBreakDown[MSG1_TO_MSG2])/len(CHO_DelayBreakDown[MSG1_TO_MSG2])
    if CHO_DelayBreakDown[MSG2_TO_SENDRRCCOMPLETE] != []:
        CHO_MSG2_TO_SENDRRCCOMPLETE_Delay = sum(CHO_DelayBreakDown[MSG2_TO_SENDRRCCOMPLETE])/len(CHO_DelayBreakDown[MSG2_TO_SENDRRCCOMPLETE])
    if CHO_Delay != []:
        AVG_CHO_Delay = sum(CHO_Delay)/len(CHO_Delay) # Get AVG delay

    TotalHO = TotalRegHO + TotalCHO # Get total num of HO

    return [TotalHO, TotalRegHO, TotalCHO, 
            AVG_REGHO_Delay, REGHO_CRITMET_TO_MR_Delay, REGHO_MR_TO_HOCMD_Delay, REGHO_HOCMD_TO_GENRRCCOMPLETE_Delay, REGHO_GENRRCCOMPLETE_TO_MSG1_Delay, REGHO_MSG1_TO_MSG2_Delay, REGHO_MSG2_TO_SENDRRCCOMPLETE_Delay,
            AVG_CHO_Delay, CHO_CRITMET_TO_GENRRCRECONFIG_Delay, CHO_GENRRCRECONFIG_TO_GENRRCCOMPLETE_Delay, CHO_GENRRCCOMPLETE_TO_MSG1_Delay, CHO_MSG1_TO_MSG2_Delay, CHO_MSG2_TO_SENDRRCCOMPLETE_Delay]

for log in logPktList_All_Logs.values():
    HOKPI_Result = getHOKPI(log)
    TotalNumHO.append(HOKPI_Result[0])
    TotalNumRegHO.append(HOKPI_Result[1])
    TotalNumCHO.append(HOKPI_Result[2])
    AVGRegHODelay.append(HOKPI_Result[3])
    HOEventCritMet_To_MR.append(HOKPI_Result[4])
    MR_To_HOCommand.append(HOKPI_Result[5])
    HOCommand_To_GenRRCReconfigComplete.append(HOKPI_Result[6])
    HO_GenRRCReconfigComplete_To_MSG1.append(HOKPI_Result[7])
    HO_MSG1_To_MSG2.append(HOKPI_Result[8])
    HO_MSG2_To_Send_RRCReconfigComplete.append(HOKPI_Result[9])
    AVGCHODelay.append(HOKPI_Result[10])
    HOEventCritMet_To_GenRRCReconfig.append(HOKPI_Result[11])
    GenRRCReconfig_To_GenRRCReconfigComplete.append(HOKPI_Result[12])
    CHO_GenRRCReconfigComplete_To_MSG1.append(HOKPI_Result[13])
    CHO_MSG1_To_MSG2.append(HOKPI_Result[14])
    CHO_MSG2_To_Send_RRCReconfigComplete.append(HOKPI_Result[15])

# Init work book and fill rows with data
wb = Workbook()
ws = wb.active
ws.title = 'N2N_Handover_KPI'
ws.append(First_Row)
ws.append(TotalNumHO)
ws.append(TotalNumRegHO)
ws.append(TotalNumCHO)
ws.append(AVGRegHODelay)
ws.append(HOEventCritMet_To_MR)
ws.append(MR_To_HOCommand)
ws.append(HOCommand_To_GenRRCReconfigComplete)
ws.append(HO_GenRRCReconfigComplete_To_MSG1)
ws.append(HO_MSG1_To_MSG2)
ws.append(HO_MSG2_To_Send_RRCReconfigComplete)
ws.append(AVGCHODelay)
ws.append(HOEventCritMet_To_GenRRCReconfig)
ws.append(GenRRCReconfig_To_GenRRCReconfigComplete)
ws.append(CHO_GenRRCReconfigComplete_To_MSG1)
ws.append(CHO_MSG1_To_MSG2)
ws.append(CHO_MSG2_To_Send_RRCReconfigComplete)

# Save KPI table to excel
dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'N2N_Handover_KPI_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(HO_KPI.workingDir, saveFileName)
print(datetime.now().strftime("%H:%M:%S"), '(N2N_Handover_KPI) ' + 'KPI Summary extracted: ' + savePath)
wb.save(savePath)