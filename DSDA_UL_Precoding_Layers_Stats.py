from PostProcessingUtils import PostProcessingUtils, LogPacket
from FilterMask import *
from openpyxl import Workbook
from datetime import datetime
import sys
import os
import re

filter_mask[LOG_FILTER] = [0xB885]
filter_mask[EVENT_FILTER] = []
filter_mask[F3S_NON_REGEX] = []
filter_mask[QTRACE_NON_REGEX] = ['nr5g_macctrl_update_on_dsda_entry', 'nr5g_macctrl_update_on_dsda_exit']

# MIN_ONE_LAYER_GRANTS_OF_CONVERGENCE = 50
MIN_ONE_LAYER_GRANTS_OF_CONVERGENCE = 15

First_Row = ['KPI Field']
Total_DSDA_Entry = ['Total DSDA Entry']
DSDA_Timestamps = ['DSDA Timestamps']
Total_Mismatch_Occasions = ['Total 2-Layer Grant Occasions (Layer Mismatch)']
Mismatch_Timestamps_Rows = {}

class LogPacket_Precoding_Layer(LogPacket):

    ### Constructor ###
    def __init__(self, logPacket):
        
        self.numOfOneLayerGrant = 0
        self.numOfTwoLayerGrant = 0
        self.totalNumOfGrant = 0
        self.isTwoLayerGrantReceived = False
        self.inDSDAState = False
        self.DSDA_Entry = False
        self.DSDA_Exit = False

        re_PrecodingLayer = re.compile(r'.*UL_0_[01]\|[A-Z_|\d\s]{133}\|[\s]{7,8}([\d]{1,2})\|.*')
        
        DSDA_ENTRY = 'nr5g_macctrl_update_on_dsda_entry'
        DSDA_EXIT = 'nr5g_macctrl_update_on_dsda_exit'
        
        if len(logPacket.getHeadline()) == 0:
            sys.exit('(LogPacket_Precoding_Layer/__init__) ' + 'No log packets found!!!')
        else:
            self.packetCode = logPacket.getPacketCode()
            self.subID = logPacket.getSubID()
            self.timestamp = logPacket.getTimestamp()
            self.title = logPacket.getTitle()
            self.headline = logPacket.getHeadline()
            self.content = logPacket.getContent()
            self.absTime = logPacket.getAbsTime()
            if logPacket.getPacketCode() == '0xB885':            
                for line in logPacket.getContent():
                    if re_PrecodingLayer.match(line):
                        # precodingLayer = int(re_PrecodingLayer.match(line).groups()[0])
                        precodingLayer = re_PrecodingLayer.match(line).groups()[0]
                        precodingLayer = precodingLayer.strip()
                        if precodingLayer == '2': # SMDL
                            self.numOfTwoLayerGrant += 1
                            if not self.isTwoLayerGrantReceived:
                                self.isTwoLayerGrantReceived = True
                        else: # SMSL/SISO
                            self.numOfOneLayerGrant += 1
                    else:
                        continue
            elif logPacket.getPacketCode() == '0x1FE8':
                if logPacket.containsIE(DSDA_ENTRY):
                    self.DSDA_Entry = True
                    self.inDSDAState = True
                elif logPacket.containsIE(DSDA_EXIT):
                    self.DSDA_Exit = True
        
    ### Getters ###
    def getnumOfOneLayerGrant(self):
        return self.numOfOneLayerGrant
    
    def getnumOfTwoLayerGrant(self):
        return self.numOfTwoLayerGrant
    
    def getTotalNumOfGrant(self):
        return self.totalNumOfGrant

    def isTwoLayerGrantsPresent(self):
        return self.isTwoLayerGrantReceived
    
    def isDSDAEntry(self):
        return self.DSDA_Entry
    
    def isDSDAExit(self):
        return self.DSDA_Exit
    
    def isInDSDAState(self):
        return self.inDSDAState
    
    ### Setters ###
    def setAsInDSDAState(self):
        self.inDSDAState = True
    
    @staticmethod
    def getMismatchAndDSDAPeriod(logPktList_All):
        if logPktList_All == []:
            print(datetime.now().strftime("%H:%M:%S"), '(DSDA_UL_Precoding_Layers_Stats/LogPacket_Precoding_Layer/getMismatchAndDSDAPeriod) ' + 'No logs found!')
            return [], 0, [], 0
        logPktList = logPktList_All
        DSDA_state_entry_found = False
        DSDAPeriod_All = []
        DSDAPair = ['N/A', 'N/A']
        NumOfDSDAEntry = 0
        MismatchPeriod_All = []
        MismatchFound = False
        MismatchPair = ['N/A', 'N/A', 'N/A', 'N/A'] # Add num of 1 layer grant
        NumOfMismatchOccasions = 0
        CurrentTwoLayerGrants = 0
        OneLayerGrantDuringToggling = 0
        OneLayerPair = ['N/A', 'N/A', 'N/A']
        CurrentOneLayerGrants = 0
        OneLayerGrantCounter = 0
        StartOfConvergence = 'N/A'
        # Find all DSDA period and mark all pkts within the period as inDSDAState
        for n in range(0, len(logPktList)):
            if logPktList[n].isDSDAEntry(): # Looking for DSDA entry
                if DSDA_state_entry_found: # Skip if duplicated
                    logPktList[n].setAsInDSDAState()
                    continue
                else: # Found DSDA entry
                    DSDA_state_entry_found = True
                    DSDAPair = ['N/A', 'N/A']
                    DSDAPair[0] = logPktList[n]
                    logPktList[n].setAsInDSDAState()
            elif logPktList[n].isDSDAExit():
                if not DSDA_state_entry_found: # Skip if DSDA entry is missing
                    continue
                else: # Found DSDA exit
                    DSDA_state_entry_found = False
                    if DSDAPair[0] != 'N/A' and DSDAPair[1] == 'N/A':
                        DSDAPair[1] = logPktList[n]
                        DSDAPeriod_All.append(DSDAPair[0].getTimestamp() + ' --- ' + DSDAPair[1].getTimestamp() + ' -> ' + str(LogPacket.getDelay(DSDAPair[1], DSDAPair[0])) + 'ms' + '\n')
                    else:
                        continue
            elif n == len(logPktList) - 1 and DSDA_state_entry_found: # If no DSDA exit till end of log (DSDA entry found), take the timestamp of last pkt as exit
                    DSDA_state_entry_found = False
                    if DSDAPair[0] != 'N/A' and DSDAPair[1] == 'N/A':
                        DSDAPair[1] = logPktList[n]
                        DSDAPeriod_All.append(DSDAPair[0].getTimestamp() + ' --- ' + DSDAPair[1].getTimestamp() + ' -> ' + str(LogPacket.getDelay(DSDAPair[1], DSDAPair[0])) + 'ms' + '\n')
                        logPktList[n].setAsInDSDAState()
                    else:
                        continue
            else:
                if DSDA_state_entry_found: # For other pkts, mark as inDSDAState if entry found and add to result list
                    logPktList[n].setAsInDSDAState()
                else:
                    continue
        
        NumOfDSDAEntry = len(DSDAPeriod_All)
        
        # Find all mismatch occasions based on pkt marked as inDSDAState
        for m in range(0, len(logPktList)):
            if not logPktList[m].isInDSDAState() and not MismatchFound: # If not in DSDA state and mismatch start point not found, use the last pkt as end of 1 layer period
                if StartOfConvergence != 'N/A':
                    OneLayerPair[0] = StartOfConvergence
                    OneLayerPair[1] = logPktList[m]
                    OneLayerPair[2] = CurrentOneLayerGrants
                    if OneLayerPair[0] != 'N/A' and OneLayerPair[1] != 'N/A' and OneLayerPair[2] != 'N/A':
                        MismatchPeriod_All.append('1L - ' + OneLayerPair[0].getTimestamp() + ' --- ' + OneLayerPair[1].getTimestamp() + ' -> ' + str(LogPacket.getDelay(OneLayerPair[1], OneLayerPair[0])) + 'ms (' + str(OneLayerPair[2]) + ')')
                    StartOfConvergence = 'N/A'
                    OneLayerGrantDuringToggling = 0
            elif not logPktList[m].isInDSDAState() and MismatchFound: # Upon DSDA exit, mark StartOfConvergence as the end of mismatch if start point found (Convergence threshold not meet yet)
                MismatchFound =False
                if MismatchPair[0] != 'N/A' and MismatchPair[1] == 'N/A' and MismatchPair[2] == 'N/A':
                    if StartOfConvergence != 'N/A' and OneLayerGrantCounter != 0: # If convergence started but not completed, mark the last pkt as end of 1 layer period
                        MismatchPair[1] = StartOfConvergence
                        OneLayerPair[0] = StartOfConvergence
                        OneLayerPair[1] = logPktList[m]
                        CurrentOneLayerGrants += logPktList[m].getnumOfOneLayerGrant()
                        OneLayerPair[2] = CurrentOneLayerGrants
                    else:
                        MismatchPair[1] = logPktList[m]
                    MismatchPair[2] = CurrentTwoLayerGrants
                    MismatchPair[3] = OneLayerGrantDuringToggling
                    MismatchPeriod_All.append('2L - ' + MismatchPair[0].getTimestamp() + ' --- ' + MismatchPair[1].getTimestamp() + ' -> ' + str(LogPacket.getDelay(MismatchPair[1], MismatchPair[0])) + 'ms (' + str(MismatchPair[2]) + ',' + str(MismatchPair[3]) + ')')
                    NumOfMismatchOccasions += 1
                    if OneLayerPair[0] != 'N/A' and OneLayerPair[1] != 'N/A' and OneLayerPair[2] != 'N/A':
                        MismatchPeriod_All.append('1L - ' + OneLayerPair[0].getTimestamp() + ' --- ' + OneLayerPair[1].getTimestamp() + ' -> ' + str(LogPacket.getDelay(OneLayerPair[1], OneLayerPair[0])) + 'ms (' + str(OneLayerPair[2]) + ')')
                StartOfConvergence = 'N/A'
                OneLayerGrantDuringToggling = 0
            else: # In DSDA state
                if logPktList[m].isTwoLayerGrantsPresent(): # If two layer grant exist
                    if MismatchFound:  # Already found the start of current mismatch, just count the num of 2 layer grants
                        CurrentTwoLayerGrants += logPktList[m].getnumOfTwoLayerGrant()
                        OneLayerGrantDuringToggling += OneLayerGrantCounter
                        OneLayerGrantDuringToggling += logPktList[m].getnumOfOneLayerGrant() # Sometimes single 0xB885 carriers both 1 layer and 2 layer grants
                        OneLayerGrantCounter = 0 # Reset all one layer counter and marker
                        CurrentOneLayerGrants = 0
                        StartOfConvergence = 'N/A'
                    else: # Not yet found the start of current mismatch, use current pkt as start of mismatch and end of 1 layer period, and count the num of 2 layer grants
                        MismatchFound = True
                        OneLayerPair[0] = StartOfConvergence
                        OneLayerPair[1] = logPktList[m]
                        OneLayerPair[2] = CurrentOneLayerGrants
                        if OneLayerPair[0] != 'N/A' and OneLayerPair[1] != 'N/A' and OneLayerPair[2] != 'N/A':
                            MismatchPeriod_All.append('1L - ' + OneLayerPair[0].getTimestamp() + ' --- ' + OneLayerPair[1].getTimestamp() + ' -> ' + str(LogPacket.getDelay(OneLayerPair[1], OneLayerPair[0])) + 'ms (' + str(OneLayerPair[2]) + ')')
                        OneLayerPair = ['N/A', 'N/A', 'N/A']
                        MismatchPair = ['N/A', 'N/A', 'N/A', 'N/A']
                        OneLayerGrantCounter = 0
                        OneLayerGrantDuringToggling = 0
                        CurrentOneLayerGrants = 0
                        StartOfConvergence = 'N/A'
                        CurrentTwoLayerGrants = 0
                        CurrentTwoLayerGrants += logPktList[m].getnumOfTwoLayerGrant()
                        MismatchPair[0] = logPktList[m]
                elif m == len(logPktList) - 1: # At the end of log, mark StartOfConvergence as the end of mismatch and start of 1 layer period if start point found (Convergence threshold not meet yet)
                    if MismatchFound:
                        MismatchFound =False
                        if MismatchPair[0] != 'N/A' and MismatchPair[1] == 'N/A' and MismatchPair[2] == 'N/A': 
                            if StartOfConvergence != 'N/A' and OneLayerGrantCounter != 0: # If convergence started but not completed, mark the last pkt as end of 1 layer period
                                MismatchPair[1] = StartOfConvergence
                                OneLayerPair[0] = StartOfConvergence
                                OneLayerPair[1] = logPktList[m]
                                CurrentOneLayerGrants += logPktList[m].getnumOfOneLayerGrant()
                                OneLayerPair[2] = CurrentOneLayerGrants
                            else:
                                MismatchPair[1] = logPktList[m]
                            CurrentTwoLayerGrants += logPktList[m].getnumOfTwoLayerGrant()
                            MismatchPair[2] = CurrentTwoLayerGrants
                            MismatchPair[3] = OneLayerGrantDuringToggling
                            OneLayerGrantDuringToggling = 0
                            MismatchPeriod_All.append('2L - ' + MismatchPair[0].getTimestamp() + ' --- ' + MismatchPair[1].getTimestamp() + ' -> ' + str(LogPacket.getDelay(MismatchPair[1], MismatchPair[0])) + 'ms (' + str(MismatchPair[2]) + ',' + str(MismatchPair[3]) + ')')
                            NumOfMismatchOccasions += 1
                            if OneLayerPair[0] != 'N/A' and OneLayerPair[1] != 'N/A' and OneLayerPair[2] != 'N/A':
                                MismatchPeriod_All.append('1L - ' + OneLayerPair[0].getTimestamp() + ' --- ' + OneLayerPair[1].getTimestamp() + ' -> ' + str(LogPacket.getDelay(OneLayerPair[1], OneLayerPair[0])) + 'ms (' + str(OneLayerPair[2]) + ')')
                    else:
                        OneLayerPair[0] = StartOfConvergence
                        OneLayerPair[1] = logPktList[m]
                        CurrentOneLayerGrants += logPktList[m].getnumOfOneLayerGrant()
                        OneLayerPair[2] = CurrentOneLayerGrants
                        if OneLayerPair[0] != 'N/A' and OneLayerPair[1] != 'N/A' and OneLayerPair[2] != 'N/A':
                            MismatchPeriod_All.append('1L - ' + OneLayerPair[0].getTimestamp() + ' --- ' + OneLayerPair[1].getTimestamp() + ' -> ' + str(LogPacket.getDelay(OneLayerPair[1], OneLayerPair[0])) + 'ms (' + str(OneLayerPair[2]) + ')')
                elif not logPktList[m].isTwoLayerGrantsPresent() and logPktList[m].getnumOfOneLayerGrant() >= 1: # If no two layer grant exist
                    if MismatchFound: # if 2 layer grants start point found (During toggling)
                        if StartOfConvergence == 'N/A': # Mark first 1 layer grant as start of convergence
                            StartOfConvergence = logPktList[m]
                        OneLayerGrantCounter += logPktList[m].getnumOfOneLayerGrant()
                        CurrentOneLayerGrants += logPktList[m].getnumOfOneLayerGrant()
                        if OneLayerGrantCounter >= MIN_ONE_LAYER_GRANTS_OF_CONVERGENCE: # 1 layer grant above threshold, convergence completed, mark StartOfConvergence as end point of mismatch
                            MismatchFound =False
                            if MismatchPair[0] != 'N/A' and MismatchPair[1] == 'N/A' and MismatchPair[2] == 'N/A':
                                MismatchPair[1] = StartOfConvergence
                                MismatchPair[2] = CurrentTwoLayerGrants
                                MismatchPair[3] = OneLayerGrantDuringToggling
                                OneLayerGrantDuringToggling = 0
                                MismatchPeriod_All.append('2L - ' + MismatchPair[0].getTimestamp() + ' --- ' + MismatchPair[1].getTimestamp() + ' -> ' + str(LogPacket.getDelay(MismatchPair[1], MismatchPair[0])) + 'ms (' + str(MismatchPair[2]) + ',' + str(MismatchPair[3]) + ')')
                                NumOfMismatchOccasions += 1
                            # OneLayerGrantCounter = 0
                            # StartOfConvergence = 'N/A'
                        else: # 1 layer grant below threshold, continue
                            continue
                    else: # Mismatch start point not found, counting 1 layer grant and continue
                        CurrentOneLayerGrants += logPktList[m].getnumOfOneLayerGrant()
                        if StartOfConvergence == 'N/A':
                            StartOfConvergence = logPktList[m]
        
        return DSDAPeriod_All, NumOfDSDAEntry, MismatchPeriod_All, NumOfMismatchOccasions          
                    

    ### Destructor ###
    def __del__(self):
        LogPacket.__del__(self)
        self.numOfOneLayerGrant = 0
        self.numOfTwoLayerGrant = 0
        self.totalNumOfGrant = 0
        self.isTwoLayerGrantReceived = False
        self.inDSDAState = False
        self.DSDA_Entry = False
        self.DSDA_Exit = False
        
UL_MIMO_Stats_DSDA = PostProcessingUtils()
ARGV = sys.argv
ARGV.append('qtrace')
ARGV.append('sub1')
UL_MIMO_Stats_DSDA.getArgv(ARGV)
UL_MIMO_Stats_DSDA.scanWorkingDir()
if not UL_MIMO_Stats_DSDA.skipFitlerLogs():
    UL_MIMO_Stats_DSDA.convertToText('UL_MIMO_Stats_DSDA')
UL_MIMO_Stats_DSDA.scanWorkingDir('_flt_text.txt', 'UL_MIMO_Stats_DSDA')
# UL_MIMO_Stats_DSDA.scanWorkingDir('_flt_text.txt', 'FindKW')
UL_MIMO_Stats_DSDA.initLogPacketList()
LogPkt_All = UL_MIMO_Stats_DSDA.getLogPacketList()

B885_DSDA_LogPkt_List_All = {}
isFirstLog = True
logCounter = 0
for key in LogPkt_All.keys():
    B885_DSDA_LogPkt_List_All[key] = []
    for pkt in LogPkt_All[key]:
        if pkt.getPacketCode() == '0xB885' or pkt.getPacketCode() == '0x1FE8':
            # print(pkt.getTimestamp())
            B885_DSDA_LogPkt_List_All[key].append(LogPacket_Precoding_Layer(pkt))
            
for key in B885_DSDA_LogPkt_List_All:
    First_Row.append(key)
    logCounter += 1
    result = LogPacket_Precoding_Layer.getMismatchAndDSDAPeriod(B885_DSDA_LogPkt_List_All[key])
    Total_DSDA_Entry.append(result[1])
    result_0 = ''
    for line in result[0]:
        result_0 += line
    DSDA_Timestamps.append(result_0)
    Total_Mismatch_Occasions.append(result[3])
    
    # Mismatch_Timestamps_Rows
    for n in range(0, len(result[2])):
        if isFirstLog:
            if not 0 in Mismatch_Timestamps_Rows:
                Mismatch_Timestamps_Rows.update({0: []})
            Mismatch_Timestamps_Rows[0].append('Precoding Layer Timestamps and Num')
            isFirstLog = False
        elif not n in Mismatch_Timestamps_Rows:
            Mismatch_Timestamps_Rows.update({n: []})
            Mismatch_Timestamps_Rows[n].append(' ')
        while len(Mismatch_Timestamps_Rows[n]) < logCounter:
            Mismatch_Timestamps_Rows[n].append(' ')
        Mismatch_Timestamps_Rows[n].append(result[2][n])

wb = Workbook()
ws = wb.active
ws.title = 'UL_Layers_Mismatch_Stats'
ws.append(First_Row)
ws.append(Total_DSDA_Entry)
ws.append(DSDA_Timestamps)
ws.append(Total_Mismatch_Occasions)
for key in Mismatch_Timestamps_Rows:
    ws.append(Mismatch_Timestamps_Rows[key])

# Save KPI table to excel
dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'DSDA_Precoding_Layers_Stats_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(UL_MIMO_Stats_DSDA.workingDir, saveFileName)
print(datetime.now().strftime("%H:%M:%S"), '(DSDA_UL_Precoding_Layers_Stats) ' + 'KPI Summary extracted: ' + savePath)
wb.save(savePath)