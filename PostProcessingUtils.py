#---------------------------------------------------------------------------------------------------------------------------------------------------
# Class PostProcessingUtils Functions
#  * getArgv ----- Get inputs from command line (ARGV[1] = log path, ARGV[1 + n] = log packet code or qtrace indicator or sub ID or skip filter flag)
#  * scanWorkingDir ----- Scan the path for files (or given type, .hdf by default) and dirs
#  * getFilesPath ----- Getter of files path in the working directory with given extension
#  * skipFitlerLogs ----- Get skip filter flag, will skip filtering logs if True
#  * initLogPacketList ----- Initializing the packet list extracted from text files
#  * getLogPacketList ----- Getter of log packet list
#  * getLogPktCodeList ----- Getter of log packet code list
#  * convertToText ----- Convert .hdf logs to text files with given log or qtrace filter
#  * findKeywords ----- Find keywords from log text file (Keywords defined in FilterMask)
#  * exportAnalyzer ----- Extract the given (or default) analyzer/grid from logs
#  * mergeLogs ----- Merge multiple logs (and convert .qdss/qmdl2 or .bin files to .hdf)
#  * checkConditionIn_X_secs_from_Y ----- Check log packets within x secs of anchor y, take actions (pre-defined) if condition (pre-defined) is met
#---------------------------------------------------------------------------------------------------------------------------------------------------
# Class LogPacket Functions
#  * Setters
#  * Getters
#  * timestampConverter ----- Convert log timestamp from string to int (in secs)
#  * absTimeToTimestamp ----- Convert abs time to timestamp str ###
#  * getDelayBySlot ----- Caculate delay by SFN and slot (A - B) ###
#  * getDelay ----- Calculate the delay between two log packets
#  * containsIE ----- Check if log pkt contains given IE
#---------------------------------------------------------------------------------------------------------------------------------------------------
# Class LogPacket_Talkspurt Functions (Inheritance of LogPacket)
#  * isInTalkspurt ----- Return true if pkt is within talk spurt
#  * setTalkspurt ----- Set talk spurt indicator to True
#  * setSilence ----- Set talk spurt indicator to False
#  * findTalkspurt ----- Check downlink RTP packet payload and mark talk spurt accordingly for any packet within
#--------------------------------------------------------------------------------------------------------------------------------------------------- 
# Class LogPacket_RTP Functions (Inheritance of LogPacket_Talkspurt, add RTP pkt propertyies from 0x1568 and 0x1569)
#  * getPacketBurst ----- Get number of DL rtp pkt in burst, mark pkt as inBurst, return burst start timestamp and number of pkt in burst
#  * setInBurst ----- Set inBurst to true if detect pkt is within rtp burst
#---------------------------------------------------------------------------------------------------------------------------------------------------
# class LogPacket_PHY_BLER Functions (Inheritance of LogPacket, get PHY layer pass/fail/newTx/ReTx in 0xB887 and 0xB883)
#---------------------------------------------------------------------------------------------------------------------------------------------------
# class LogPacket_CDRX Functions (Inheritance of LogPacket, get CDRX info in 0xB890)
#  * getCDRXEvent ----- Get CDRX event dict (timestamp: event)
#---------------------------------------------------------------------------------------------------------------------------------------------------
# class LogPacket_RSRP_SNR Functions (Inheritance of LogPacket, get RSRP/SNR info from 0xB8DD)
#  * getRSTYPE ----- Get reference signal type
#  * getRSRP ----- Get RSRP dict (Rx: [rsrp])
#  * getRSRP ----- Get SNR dict (Rx: [snr])
#---------------------------------------------------------------------------------------------------------------------------------------------------
# class LogPacket_HO Functions (Inheritance of LogPacket, get serving and target cell info from HO event)
#  * getSourceCellInfo ----- Get source cell arfcn and pci
#  * getTargetCellInfo ----- Get target cell arfcn and pci
#---------------------------------------------------------------------------------------------------------------------------------------------------

import os
import sys
import re
import signal
import pandas as pd
from datetime import datetime
from sys import platform
from typing import List
from FilterMask import *
if platform == "linux" or platform == "linux2":
    sys.path.append('/opt/qcom/APEX7/Support/Python')	
elif platform == "win32":
    sys.path.append('C:\Program Files (x86)\Qualcomm\APEX7\Support\Python')
import ApexClient

##### Get command line inputs (directory, files, log pkt filter), and run multiple post processing tasks #####
class PostProcessingUtils(object):
    
    ### Constructor ###
    def __init__(self, filterMask = filter_mask):
        self.skipFilterLog = False # Indicator of skip filtering logs (HDF to Text) from ARGV
        self.files = [] # All files of given type in current working dir
        self.fileExt = '.hdf' # File extension, default = .hdf
        self.dirs = [] # All sub dirs in current working dir
        self.workingDir = '' # Current working dir from ARGV
        self.sid = '0' # Sub ID indicator from ARGV
        self.pktFilter = [] # Log packet filter from ARGV
        self.pktCodeFormat = re.compile(r'[0][x][\dA-F]{4}$') # Packet code RE format
        self.defaultPacketFilter = filterMask[LOG_FILTER] # Default packet filter
        self.eventFilter = [] # Event filter from ARGV
        self.eventCodeFormat = re.compile(r'^[\d]{3,4}$') # Event code RE format
        self.defaultEventFilter = filterMask[EVENT_FILTER] # Default event filter
        self.keywords = filterMask[KEYWORDS_FILTER] # Keyword filter
        self.isQtrace = False # Qtrace indicator from ARGV (To enable Qtrace filter)
        self.qtraceFilterStringList = {} # Qtrace filter strings
        self.qtraceFilterStringListNonRegex = filterMask[QTRACE_NON_REGEX] # Non regex Qtrace strings
        self.qtraceFilterStringListRegex = filterMask[QTRACE_REGEX] # Regex Qtrace strings
        self.F3FilterStringList = {} # F3 filter strings
        self.F3FilterStringListNonRegex = filterMask[F3S_NON_REGEX] # Non regex F3
        self.F3FilterStringListRegex = filterMask[F3S_REGEX] # Regex F3
        self.analyzerGrid = [] # Grid to be extracted from working dir
        self.defaultAnalyzerList = filterMask[ANALYZER_FILTER] # Default analyzers to be extracted
        self.logPackets = {} # Log packets from logs in working dir
        self.logPacketFormat = {'headlineFormat':re.compile(r'^[\d]{4}[\s]{1}[A-Za-z]{3}[\s]{1,2}[\d]{1,2}[\s]{2}([\d]{2}:[\d]{2}:[\d]{2}\.[\d]{3}).*([0][x][\dA-F]{4})(.*)$'), 
                                'subIdFormat': re.compile(r'^Subscription ID =.*([\d]{1})')} # Log packet headline and sub id RE format


    ### Interpret command line, get working directory, initialize log filter ###
    def getArgv(self, sysArgv):
        
        # Get the command line arguments, initialize pkt filter
        if len(sysArgv) > 1:
            if (sysArgv[1].find('-?')) > -1 or (sysArgv[1].find('-h') > -1) or (sysArgv[1].find('-help') > -1):
                sys.exit('(PostProcessingUtils/getArgv) ' + 'Command syntax: python <py file name> <log directory> <log packet codes>')
            else:
                self.workingDir = sysArgv[1] # Get current working dir from Argv
                logPacketFitler = []
                logEventFitler = []
                for n in range(2, len(sysArgv)): # Get log code/qtrace indicator/sub ID
                    if self.pktCodeFormat.match(str(sysArgv[n])):
                        logId = int(str(sysArgv[n]), 16)
                        self.pktFilter.append(logId)
                        logPacketFitler.append(hex(logId))
                    elif self.eventCodeFormat.match(str(sysArgv[n])):
                        eventId = int(str(sysArgv[n]), 10)
                        self.eventFilter.append(eventId)
                        logEventFitler.append(eventId)
                    elif str(sysArgv[n]) == '-sf':
                        self.skipFilterLog = True
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getArgv) ' + '-sf flag received, will skip filtering logs!')
                    elif str(sysArgv[n]) == 'qtrace':
                        self.isQtrace = True
                    elif str(sysArgv[n]) == 'sub1':
                        self.sid = '1'
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getArgv) ' + 'sub1 indicator received!')
                    elif str(sysArgv[n]) == 'sub2':
                        self.sid = '2'
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getArgv) ' + 'sub2 indicator received!')
                    else:
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getArgv) ' + 'Invalid log code or sub ID format: ' + str(sysArgv[n]))
                        continue
                if len(self.pktFilter) == 0:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getArgv) ' + 'No packet filter specified!')
                else:
                    print(datetime.now().strftime("%H:%M:%S"),  '(PostProcessingUtils/getArgv) ' + 'Packet filter: ', logPacketFitler)
                if len(self.eventFilter) == 0:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getArgv) ' + 'No event filter specified!')
                else:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getArgv) ' + 'Event filter: ', logEventFitler)
                if self.isQtrace:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getArgv) ' + 'Qtrace indication received!')                   
        else:
            self.workingDir = input(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getArgv) ' + 'Please specify the log directory:\t')
            self.workingDir = self.workingDir.strip()
        
        # Check if path exists
        if os.path.exists(os.path.abspath(self.workingDir)):
            print(datetime.now().strftime("%H:%M:%S"),  '(PostProcessingUtils/getArgv) ' + 'Working directory: ' + self.workingDir)
        else:
            sys.exit('(PostProcessingUtils/getArgv) ' + 'Error: Directory does not exist --- ' + self.workingDir)

    ### Scan dirs and get files (including .awsi) to be processed with given extension, by defualt fileExt is set to .hdf ###
    def scanWorkingDir(self, fileExt = '.hdf', flt_file_marker = ''):

        self.fileExt = fileExt # override fileExt if needed
        self.files = [] # Clear old files before new scan
        self.analyzerGrid = [] # Clear old files before new scan

        # Check if getArgv is executed and path exists
        if os.path.exists(os.path.abspath(self.workingDir)):
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'Scanning files in path: ' + self.workingDir)
        else:
            sys.exit(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'Error: Directory does not exist --- ' + self.workingDir)

        # Get files and dirs from working directory, scan for .awsi grid files
        for path, dirs, files in os.walk(os.path.abspath(self.workingDir)):
            for file in files:
                if file.endswith(self.fileExt) and (flt_file_marker == '' or flt_file_marker in file):
                    self.files.append(os.path.join(path, file))
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + self.fileExt + ' file found: ' + str(file))
                elif file.endswith('.awsi') or file.endswith('.aws'):
                    self.analyzerGrid.append(os.path.join(path, file))                                 
            
            for dir in dirs:
                self.dirs.append(os.path.join(path, dir))
                #print('(PostProcessingUtils/scanDirs)' + 'Dir found: ' + os.path.join(path, dir))
        
        # Check if Qtrace is enabled and filter is found
        if self.isQtrace and len(self.qtraceFilterStringListNonRegex) == 0 and len(self.qtraceFilterStringListRegex) == 0 and len(self.F3FilterStringListNonRegex) == 0 and len(self.F3FilterStringListRegex) == 0:
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + "No Qtrace/F3 filter found, please specify qtrace/F3 keywords in FilterMask!")
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'No Qtrace/F3 filter will be applied!')
            self.isQtrace = False
        elif self.isQtrace and self.fileExt == '.hdf':
            for qt_NonRegex in self.qtraceFilterStringListNonRegex:
                if qt_NonRegex == '\n' or qt_NonRegex.isspace():
                    continue
                else:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'Qtrace keywords in filter: ' + qt_NonRegex)
            for qt_Regex in self.qtraceFilterStringListRegex:
                if qt_Regex == '\n' or qt_Regex.isspace():
                    continue
                else:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'Qtrace key words in filter: ' + qt_Regex)
            for f3_NonRegex in self.F3FilterStringListNonRegex:
                if f3_NonRegex == '\n' or f3_NonRegex.isspace():
                    continue
                else:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'F3 keywords in filter: ' + f3_NonRegex)
            for f3_Regex in self.F3FilterStringListRegex:
                if f3_Regex == '\n' or f3_Regex.isspace():
                    continue
                else:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'F3 keywords in filter: ' + f3_Regex)                      
        
    ### Getter of files in the working directory with given extension ###
    def getFilesPath(self):
        return self.files
    
    ### Get skip filter flag, will skip filtering logs if True ###
    def skipFitlerLogs(self):
        return self.skipFilterLog

    ### Initialize log packet list, get log info from text file ###
    def initLogPacketList(self):

        # Check if filtered text file is found
        if len(self.files) == 0:
            sys.exit('(PostProcessingUtils/initLogPacketList) ' + 'No fitlered text file found, please check path or fileExt')

        currentLogPkts = []
        formatFound = ''
        for file in self.files: # Open filtered text files with log pkt info
            logPkt = LogPacket()
            fileLines = []
            openedFile = open(file, 'r') 
            fileLines = openedFile.readlines()
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/initLogPacketList) ' + 'File opened: ' + file)
            openedFile.close()

            for index, line in enumerate(fileLines): # Check each line in current text file, init logPacket with log info
                if index == len(fileLines) - 1: # If reach the EOF, save current logPkt obj
                    currentLogPkts.append(logPkt)
                    logPkt = LogPacket()
                    break
                if line == '\n' or line.isspace(): # Skip empty lines
                    continue
                else:
                    line = line.strip()
                    if (len(line) == 1 and (line == '{' or line == '}')) or (len(line) == 2 and line == '},'): # Skip lines with no valid info
                        continue 
                    if self.logPacketFormat['headlineFormat'].match(line): # Find the headline of log packet
                        if len(logPkt.getHeadline()) != 0: # If logPkt already has headline (initialized), save current logPacket instance and init new instance
                            currentLogPkts.append(logPkt)
                            '''print('(PostProcessingUtils/initLogPacketList) ' + 'Headline: ' + logPkt.getHeadline())
                            print('(PostProcessingUtils/initLogPacketList) ' + 'Timestamp: ' + logPkt.getTimestamp())
                            print('(PostProcessingUtils/initLogPacketList) ' + 'PktCode: ' + logPkt.getPacketCode())
                            print('(PostProcessingUtils/initLogPacketList) ' + 'Title: ' + logPkt.getTitle())
                            print('(PostProcessingUtils/initLogPacketList) ' + 'Sub ID: ' + logPkt.getSubID())
                            print('(PostProcessingUtils/initLogPacketList) ' + 'Log Content...')
                            for content in logPkt.content:
                                print('(PostProcessingUtils/initLogPacketList) ' + content)'''
                            logPkt = LogPacket()
                        formatFound = self.logPacketFormat['headlineFormat'].match(line)
                        line = line.strip()
                        logPkt.setHeadline(line)
                        ts = formatFound.groups()[0].strip()
                        logPkt.setTimestamp(ts)
                        pc = formatFound.groups()[1].strip()
                        logPkt.setPacketCode(pc)
                        tt = formatFound.groups()[2].strip()
                        logPkt.setTitle(tt)
                    elif self.logPacketFormat['subIdFormat'].match(line):
                        sid = self.logPacketFormat['subIdFormat'].match(line).groups()[0].strip()
                        logPkt.setSubID(sid)
                    else:
                        line = line.strip()
                        logPkt.setContent(line)
            
            if len(currentLogPkts) > 0: # All pkts initialized for current file
                self.logPackets[os.path.split(file)[1]] = currentLogPkts
            currentLogPkts = []
        #print('(PostProcessingUtils/initLogPacketList) ' + 'KEYS: ',  self.logPackets.keys())

    
    ### Getter of PacketList ###
    def getLogPacketList(self):
        
        if len(self.logPackets) > 0:
            if self.sid == '0': # if sub Id not specified, return all pkts
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getLogPacketList) ' + 'SubId not specified, getting logPkts for both subs')
                return self.logPackets
            elif self.sid == '1': # if sub1 specified, return sub1 pkts only
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getLogPacketList) ' + 'Getting logPkts for sub1')
                logPackets_sub1 = {}
                for key in self.logPackets.keys():
                    logPackets_sub1[key] = []
                    for log in self.logPackets[key]:
                        if log.getSubID() == self.sid: # Check if subID == 1
                            logPackets_sub1[key].append(log)
                return logPackets_sub1
            elif self.sid == '2': # if sub2 specified, return sub2 pkts only
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getLogPacketList) ' + 'Getting logPkts for sub2')
                logPackets_sub2 = {}
                for key in self.logPackets.keys():
                    logPackets_sub2[key] = []
                    for log in self.logPackets[key]:
                        if log.getSubID() == self.sid: # Check if subID == 2
                            logPackets_sub2[key].append(log)
                return logPackets_sub2
            else:
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getLogPacketList) ' + 'Invalid sub ID: ' + self.sid)
                return {}
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getLogPacketList) ' + 'No log packets found!!!')
            return {}

    ### Getter of log packet code list ###
    def getLogPktCodeList(self):
        if len(self.files) == 0:
            sys.exit('(PostProcessingUtils/getLogPktCodeList) ' + 'No fitlered text file found, please check path or fileExt')
        headLineFound = ''
        for file in self.files: # Open filtered text files with log pkt info
            openedFile = open(file, 'r')
            line = openedFile.readline()
            logPktCodeList = set()
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getLogPktCodeList) ' + 'Fetching log packet code list from: ' + file)  
            while line:
                if self.logPacketFormat['headlineFormat'].match(line):
                    headLineFound = self.logPacketFormat['headlineFormat'].match(line)
                    logPktCodeList.add(headLineFound.groups()[1].strip())
                    line = openedFile.readline()
                else:
                    line = openedFile.readline()
            resultFile =file.replace('.txt', '_LogPktCodeList_Result.txt')
            openedFile.close()
            f = f = open(resultFile, 'w')
            f.write('##### Total ' + str(len(logPktCodeList)) + ' log packet code found #####\n')
            f.write('--------------------------------------------------------------------------------------------------------------------\n')
            for logPktCode in logPktCodeList:
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getLogPktCodeList) ' + 'Found log packet: ' + logPktCode)
                f.write(logPktCode + '\n')
            f.close()   
        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getLogPktCodeList) ' + 'Fetching log packet code list completed!')
                  
    ### Apply filters and convert QXDM logs to txt files ###
    def convertToText(self, flt_file_marker = ''):
        
        # Check if logs are found and filter is applied
        noPacketFitler = False
        noEventFitler = False
        firstTimeRun = True
        if self.fileExt != '.hdf' or len(self.files) == 0:
            sys.exit('(PostProcessingUtils/convertToText) ' + 'No .hdf logs found, please check path or fileExt')
        if len(self.pktFilter) == 0:
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'No packet filters specified!')
            noPacketFitler = True
        if len(self.eventFilter) == 0:
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'No event filters specified!')
            noEventFitler = True
        if self.isQtrace:
            self.qtraceFilterStringList = {0: self.qtraceFilterStringListNonRegex, 1: self.qtraceFilterStringListRegex}
            self.F3FilterStringList = {0: self.F3FilterStringListNonRegex, 1: self.F3FilterStringListRegex}
        # Open APEX and set log filter
        try:
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Setup APEX automation client ...\n') 
            apex_auto_client = ApexClient.ApexAutomationClient('apex7 automation-client')
            apex = apex_auto_client.getApexAutomationManager()    
            apex_pid = apex.GetProcessID()
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'APEX pid: ', apex_pid, '\n')
            apex.Visible = False
            apex.ShowHexDump = False
            apex.UsePCTime = True
        except:
            raise RuntimeError('Failed to open APEX')

        # Open logs, set log filter and convert to text
        for logFile in self.files:
            if logFile.endswith('.hdf'):
                dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
                saveFileTail = '_' + flt_file_marker + '_' + dt_string + '_flt_text.txt'
                outputTextFile = logFile.replace('.hdf', saveFileTail)
                      
                apex.SetAll('PacketFilter', 0)
                apex.SetAll('EventFitler', 0)
                # Set log filter
                if noPacketFitler == False:
                    if firstTimeRun:
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Set log filters...')
                    for filter in self.pktFilter:
                        if apex.Set('PacketFilter', filter, 1):
                            if firstTimeRun:
                                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Set packet ', hex(filter), ' TRUE')
                        else:
                            if firstTimeRun:
                                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Invalid packet code: ', hex(filter))
                else:                        
                    if firstTimeRun:
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Apply default packet filter!')
                    for filter in self.defaultPacketFilter:
                        apex.Set('PacketFilter', filter, 1)
                        if firstTimeRun:
                            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Set packet ', hex(filter), ' TRUE')
                apex.Commit('PacketFilter')

                # Set event filter
                if noEventFitler == False:
                    if firstTimeRun:
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Set event filters...')
                    for filter in self.eventFilter:
                        if apex.Set('EventFilter', filter, 1):
                            if firstTimeRun:
                                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Set event ', filter, ' TRUE')
                        else:
                            if firstTimeRun:
                                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Invalid event code: ', filter)
                else:
                    if firstTimeRun:
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Apply default event filter!')
                    for filter in self.defaultEventFilter:
                        apex.Set('EventFilter', filter, 1)
                        if firstTimeRun:
                            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Set event ', filter, ' TRUE')
                apex.Commit('EventFilter')      

                # Set Qtrace/F3 filter
                if self.isQtrace:
                    if firstTimeRun:
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Apply Qtrace/F3 filter!')
                    '''apex.Set('PacketFilter', 0x1FE7, 1) # Qtrace and F3 pkt 0x1FE7, 0x1FE8, 0x1FEB have to be enabled explicitly
                    apex.Set('PacketFilter', 0x1FE8, 1)
                    apex.Set('PacketFilter', 0x1FEB, 1)
                    apex.Commit('PacketFilter')'''
                    apex.SetQtraceFilterString(self.qtraceFilterStringList)
                    apex.SetF3FilterString(self.F3FilterStringList)
                    apex.SortByTime()
       
                firstTimeRun = False
            
                # Open log
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Opening log: ' + str(logFile))
                if apex.OpenLog([logFile]) != 1:     
                    #apex.Exit()
                    #sys.exit('(PostProcessingUtils/convertToText) ' + 'Open log failed: ' + str(logFile))
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Open log failed, skip current log: ' + str(logFile))
                    continue
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Log opened')
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Converting to text......')  
                    
                # Save as text
                if apex.SaveAsText(outputTextFile) != 1:         
                    os.kill(apex_pid, signal.SIGTERM)
                    sys.exit('(PostProcessingUtils/convertToText) ' + 'Save as text failed: ' + str(logFile))
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Converting Completed: ' + outputTextFile)

                # Close log
                if apex.CloseFile() != 1:         
                    apex.Exit()
                    sys.exit('(PostProcessingUtils/convertToText) ' + 'Failed to close file: ' + str(logFile))  
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Log file closed: ' + str(logFile))  

        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'All logs converted!')
        apex.Exit()

    ### Find keywords from log text file (Keywords defined in FilterMask) ###
    def findKeywords(self):
        if len(self.files) == 0:
            sys.exit('(PostProcessingUtils/findKeywords) ' + 'No log text file found!!!')
        if len(self.keywords) == 0:
            sys.exit('(PostProcessingUtils/findKeywords) ' + "No keywords found, please specify keywords in FilterMask!")
        
        resultFile = os.path.join(self.workingDir, 'keywords_search_result.txt')      
        f = open(resultFile, 'w')
        kw_summary = {}
        
        for key in self.logPackets.keys():
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/findKeywords) ' + 'Searching keywords in: ' + key)  
            f.write('########## ' + key + ' ##########\n') # Print log name before keyword search result
            for kw in self.keywords: # Initialize search result for each keyword
                kw_summary[kw] = 0
            for logPkt in self.logPackets[key]:
                for kw in self.keywords:
                    if kw in logPkt.getHeadline(): # Search keywords in log headline
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/findKeywords) ' + "Found keyword: '" + kw + "' in " + logPkt.getHeadline())
                        f.write(logPkt.getTimestamp() + ' ' + logPkt.getTitle() + '\n') # Print the line with keywords in search result
                        kw_summary[kw] += 1
                logContent = logPkt.getContent()
                for contentLine in logContent:
                    for kw in self.keywords: 
                        if kw in contentLine: # Search keywords in each content line
                            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/findKeywords) ' + "Found keyword: '" + kw + "' in " + logPkt.getHeadline())
                            f.write(logPkt.getTimestamp() + ' ' + contentLine + '\n') # Print the line with keywords in search result
                            kw_summary[kw] += 1
                            continue
            f.write('\n')
            for key in kw_summary.keys():
                f.write('-----Found ' + str(kw_summary[key]) + " '" + key + "' " + '\n') # Print final search result in current log
            f.write('\n')
        f.close()
        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/findKeywords) ' + 'Search keywords completed!')
        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/findKeywords) ' + 'Result in: ' + resultFile)            

    ### Export analyzer to Excel ###
    def exportAnalyzer(self, analyzer_marker = '_All_Grid.xlsm'):

        # Check if getArgv and scanWorkingDir is executed and analyzer grids are found, if not, use default analyzer list
        useDefaultAnalyzerList = False
        if len(self.analyzerGrid) == 0:
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'No analyzer grid found, will apply default analyzer list!')
            useDefaultAnalyzerList = True
        elif self.fileExt != '.hdf' or len(self.files) == 0:
            sys.exit('(PostProcessingUtils/exportAnalyzer) ' + 'No .hdf logs found, please run scanWorkingDir first or check path: ' + self.workingDir)
        else:
            for grid in self.analyzerGrid:
                gridName = os.path.split(grid)[1]
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Found analyzer grid: ' + gridName)

        # Open log and export to Excel
        for logFile in self.files:
            # Open APEX
            try:
                apex_auto_client = ApexClient.ApexAutomationClient('apex7 automation-client')
                apex = apex_auto_client.getApexAutomationManager()    
                apex_pid = apex.GetProcessID()
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'APEX pid: ', apex_pid)
                apex.Visible = False
                apex.ShowHexDump = False
                apex.UsePCTime = True
            except:
                raise RuntimeError('Failed to open APEX')

            # Open log
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Opening log: ' + str(logFile))
            if apex.OpenLog([logFile]) != 1:     
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Open log failed: ' + str(logFile))
    
                # Restart APEX
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Trying to restart APEX...')
                os.kill(apex_pid, signal.SIGTERM)
                try:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Setup APEX automation client ...\n') 
                    apex_auto_client = ApexClient.ApexAutomationClient('apex7 automation-client')
                    apex = apex_auto_client.getApexAutomationManager()    
                    apex_pid = apex.GetProcessID()
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'APEX pid: ', apex_pid, '\n')
                    apex.Visible = False
                    apex.ShowHexDump = False
                    apex.UsePCTime = True
                except:
                    raise RuntimeError('Failed to open APEX')
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Opening log: ' + str(logFile))
                if apex.OpenLog([logFile]) != 1:          
                    # Restart APEX and skip current log
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Open log failed again, restart APEX and skip:  ' + str(logFile))
                    os.kill(apex_pid, signal.SIGTERM)
                    continue
                # apex.Exit()
                # sys.exit('(PostProcessingUtils/exportAnalyzer) ' + 'Open log failed: ' + str(logFile))
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Log opened')           
            
            # Load grid, .aswi file name has to match the grid name
            if useDefaultAnalyzerList:
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Applying default analyzer list...')    
                apex.SelectOutput(";", 0) # deselect all
                for analyzer in self.defaultAnalyzerList:
                    apex.SelectOutput(analyzer, 1)
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + analyzer)    
            else:      
                apex.LoadWorkspace('')
                apex.SelectOutput(";", 0) # deselect all 
                for gridFile in self.analyzerGrid:
                    if not apex.LoadWorkspace(gridFile):
                        apex.exit()
                        sys.exit('(PostProcessingUtils/exportAnalyzer) ' + 'Failed to load: ' + gridFile)
                    else:                   
                        loadedGrid = os.path.split(gridFile)[1]
                        loadedGrid = loadedGrid.replace('.awsi', '')
                        apex.SelectOutput(loadedGrid, 1)
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Load grid ' + loadedGrid + ' complete')

            # Export to Excel
            exportPath = logFile.replace('.hdf', analyzer_marker)
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Exporting to Excel...')
            if not apex.ExportToExcel(exportPath, 0):
                apex.Exit()
                print('(PostProcessingUtils/exportAnalyzer) ' + 'Failed to export Excel: ' + str(logFile))
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Restarting APEX!')
            else:
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Exported to: ' + exportPath)
                                                 
            # Close log
            if apex.CloseFile() != 1:         
                apex.Exit()
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Failed to close file: ' + str(logFile))
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Restarting APEX!')
            else:
                apex.Exit()      
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'Log file closed: ' + str(logFile))
    
        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/exportAnalyzer) ' + 'All Done!')
                            

    ### Merge logs files (.hdf/.qdss/.bin) ###
    def mergeLogs(self):
        
        # Check if getArgv and scanWorkingDir is executed
        if os.path.exists(os.path.abspath(self.workingDir)):
            self.dirs.append(self.workingDir)
        else:
            sys.exit('(PostProcessingUtils/scanWorkingDir) ' + 'Error: Directory does not exist --- ' + self.workingDir)

        # Scan logs from each dir
        filesToBeMerged = []
        for dir in self.dirs:
            filesInDir = []
            if os.path.exists(os.path.abspath(dir)):
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Scanning ' + self.fileExt + ' files in: ' + dir)
                for file in os.listdir(dir):
                    if file.endswith(self.fileExt): # File type to be merged
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Found log file: ' + file)
                        filesInDir.append(os.path.join(dir, file))
                    elif self.fileExt == '.qdss' and file.endswith('.qmdl2'):
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Found log file: ' + file)
                        filesInDir.append(os.path.join(dir, file))
                    else:
                        continue
                if len(filesInDir) > 0:
                    filesToBeMerged.append(filesInDir)
             
            else:
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Path does not exist: ' + dir)
                continue
        if len(filesToBeMerged) == 0:
            sys.exit('(PostProcessingUtils/mergeLogs) ' + 'No logs found in: ' + self.workingDir)
            
        # Open APEX
        try:
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Setup APEX automation client ...\n') 
            apex_auto_client = ApexClient.ApexAutomationClient('apex7 automation-client')
            apex = apex_auto_client.getApexAutomationManager()    
            apex_pid = apex.GetProcessID()
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'APEX pid: ', apex_pid, '\n')
            apex.Visible = False
            apex.ShowHexDump = False
            apex.UsePCTime = True
        except:
            raise RuntimeError('Failed to open APEX')

        # Open logs and merge, restard APEX and try second time if it fails
        for logFiles in filesToBeMerged:
            if len(logFiles) == 0:
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'No logs to be merged')
                continue
            currentDir = os.path.split(logFiles[0])[0]
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Opening and merging logs in...' + currentDir)
            mergedFileName = os.path.split(currentDir)[1]
            mergedFileName = mergedFileName + '_merged.hdf'
            saveFilePath = os.path.join(currentDir, mergedFileName)
            if not apex.OpenLog(logFiles):
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Open log failed in: ' + currentDir)
    
                # Restart APEX
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Trying to restart APEX...')
                os.kill(apex_pid, signal.SIGTERM)
                try:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Setup APEX automation client ...\n') 
                    apex_auto_client = ApexClient.ApexAutomationClient('apex7 automation-client')
                    apex = apex_auto_client.getApexAutomationManager()    
                    apex_pid = apex.GetProcessID()
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'APEX pid: ', apex_pid, '\n')
                    apex.Visible = False
                    apex.ShowHexDump = False
                    apex.UsePCTime = True
                except:
                    raise RuntimeError('Failed to open APEX')
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Opening and merging logs in...' + currentDir)
                if not apex.OpenLog(logFiles):          
                    # Restart APEX and skip current folder
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Open log failed again, restart APEX and skip:  ' + currentDir)
                    os.kill(apex_pid, signal.SIGTERM)
                    try:
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Setup APEX automation client ...\n') 
                        apex_auto_client = ApexClient.ApexAutomationClient('apex7 automation-client')
                        apex = apex_auto_client.getApexAutomationManager()    
                        apex_pid = apex.GetProcessID()
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'APEX pid: ', apex_pid, '\n')
                        apex.Visible = False
                        apex.ShowHexDump = False
                        apex.UsePCTime = True
                    except:
                        raise RuntimeError('Failed to open APEX')
                    continue
            
            if not apex.SaveAsNewFile(saveFilePath):
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Merge log failed in ' + currentDir)
                continue
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Merged as: ' + saveFilePath)
            
            # Close log
            if apex.CloseFile() != 1:         
                apex.Exit()
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Failed to close file')
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Restarting APEX!')
                try:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Setup APEX automation client ...\n') 
                    apex_auto_client = ApexClient.ApexAutomationClient('apex7 automation-client')
                    apex = apex_auto_client.getApexAutomationManager()    
                    apex_pid = apex.GetProcessID()
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'APEX pid: ', apex_pid, '\n')
                    apex.Visible = False
                    apex.ShowHexDump = False
                    apex.UsePCTime = True
                except:
                    raise RuntimeError('Failed to open APEX')  
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'Log file closed')
        
        apex.Exit()
        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/mergeLogs) ' + 'All logs merged!')

    ### Check log packets within x secs of anchor y, take actions if condition is met ###
    @staticmethod
    def checkConditionIn_X_secs_from_Y(x, y, logPacketList, checkCondition, actionWhenConditionMeet):
        if not isinstance(x, (int)) | isinstance(y, (LogPacket_Talkspurt)) | isinstance(logPacketList, (List)):
            raise TypeError(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/checkConditionIn_X_secs_from_Y) ' + 'Wrong operand type!')

        if len(logPacketList) == 0 or len(y.getHeadline()) == 0:
            sys.exit('(PostProcessingUtils/checkConditionIn_X_secs_from_Y) ' + 'No log packets found or anchor packet is empty!!!')

        result = logPacketList
        passed24Hours = False
        direction = ''

        # Initialize achor and endpoint, wrap around if passing 24 hours
        anchor = y.getAbsTime()
        if x >= 0:
            direction = 'fwd'
            if anchor + x > 86400:
                endPoint = anchor + x - 86400
                passed24Hours = True
            else:
                endPoint = anchor + x
        else:
            direction = 'back'
            if anchor + x < 0:
                endPoint = anchor + 86400 - x
                passed24Hours = True
            else:
                endPoint = anchor + x

        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/checkConditionIn_X_secs_from_Y) ' + 'anchor: ', anchor)
        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/checkConditionIn_X_secs_from_Y) ' + 'endPoint: ', endPoint)
        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/checkConditionIn_X_secs_from_Y) ' + 'direction: ' + direction)
        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/checkConditionIn_X_secs_from_Y) ' + 'passed24Hours: ', passed24Hours)

        # Check each log packet against pre-defined condtions, take actions if condition is met
        for n in range(0, len(result)):
            if len(result[n].getHeadline()) == 0:
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/checkConditionIn_X_secs_from_Y) ' + 'current packet is empty, move to next...')
                continue           
            currentPktAbsTime = result[n].getAbsTime()
            # print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/checkConditionIn_X_secs_from_Y) ' + 'currentPktAbsTime: ', currentPktAbsTime)
            if direction == 'fwd' and not passed24Hours:
                if currentPktAbsTime >= anchor and currentPktAbsTime <= endPoint:
                    if checkCondition(result[n]):
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/checkConditionIn_X_secs_from_Y) ' + 'Condition met!!!')
                        actionWhenConditionMeet(result[n])
                    else:
                        continue
                else:
                    continue
            elif direction == 'fwd' and passed24Hours:
                if currentPktAbsTime >= anchor or (currentPktAbsTime >= 0 and currentPktAbsTime <= endPoint):
                    if checkCondition(result[n]):
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/checkConditionIn_X_secs_from_Y) ' + 'Condition met!!!')
                        actionWhenConditionMeet(result[n])
                    else:
                        continue
                else:
                    continue
            elif direction == 'back' and not passed24Hours:
                if currentPktAbsTime >= endPoint and currentPktAbsTime <= anchor:
                    if checkCondition(result[n]):
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/checkConditionIn_X_secs_from_Y) ' + 'Condition met!!!')
                        actionWhenConditionMeet(result[n])
                    else:
                        continue
                else:
                    continue
            elif direction == 'back' and passed24Hours:
                if currentPktAbsTime >= endPoint or (currentPktAbsTime >= 0 and currentPktAbsTime <= anchor):
                    if checkCondition(result[n]):
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/checkConditionIn_X_secs_from_Y) ' + 'Condition met!!!')
                        actionWhenConditionMeet(result[n])
                    else:
                        continue
                else:
                    continue
        
        return result            


    ### Destructor ###
    def __del__(self):
        self.skipFilterLog = False
        self.files = []
        self.fileExt = ''
        self.dirs = []
        self.workingDir = ''
        self.sid = ''
        self.pktFilter = []
        self.pktCodeFormat = ''
        self.defaultPacketFilter = []
        self.eventFilter = []
        self.eventCodeFormat = []
        self.defaultEventFilter = []
        self.keywords = []
        self.isQtrace = False
        self.qtraceFilterStringList = {}
        self.qtraceFilterStringListNonRegex = []
        self.qtraceFilterStringListRegex = []
        self.F3FilterStringList = {}
        self.F3FilterStringListNonRegex = []
        self.F3FilterStringListRegex = []
        self.analyzerGrid = []
        self.defaultAnalyzerList = []
        self.logPackets = {}
        self.logPacketFormat = {}



##### Struct of log packet #####
class LogPacket(object):

    ### Constructor ###
    def __init__(self):
        
        self.packetCode = ''
        self.subID = ''
        self.timestamp = ''
        self.absTime = -1
        self.title = ''
        self.headline = ''
        self.content = [] 

    ### Getters ###
    def getPacketCode(self):
        if len(self.packetCode) > 0:
            return self.packetCode
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/Getters) ' + 'No packet code found!')
            return ''

    def getSubID(self):
        if len(self.subID) > 0:
            return self.subID
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/Getters) ' + 'No sub ID found!')
            return ''

    def getTimestamp(self):
        if len(self.timestamp) > 0:
            return self.timestamp
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/Getters) ' + 'No timestamp found!')
            return ''

    def getAbsTime(self):
        return self.absTime 

    def getTitle(self):
        if len(self.title) > 0:
            return self.title
        else:
            print(datetime.now().strftime("%H:%M:%S"),  '(LogPacket/Getters) ' + 'No title found!')
            return ''

    def getHeadline(self):
        if len(self.headline) > 0:
            return self.headline
        else:
            # print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/Getters) ' + 'No headline found!')
            return ''

    def getContent(self):
        if len(self.content) > 0:
            return self.content
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/Getters) ' + 'No content found!')
            return ''

    ### Setters ###
    def setPacketCode(self, packetCodeIn):
        if len(packetCodeIn) > 0:
            self.packetCode = packetCodeIn
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/Setters) ' + 'No packet code found from input!')

    def setSubID(self, subIDIn):
        if len(subIDIn) > 0:
            self.subID = subIDIn
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/Setters) ' + 'No sub ID found from input!')

    def setTimestamp(self, timestampIn):
        if len(timestampIn) > 0:
            self.timestamp = timestampIn
            self.absTime = self.timestampConverter()
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/Setters) ' + 'No timestamp found from input!')

    def setAbsTime(self, absTimeIn):
        if absTimeIn >= 0:
            self.absTime = absTimeIn
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/Setters) ' + 'No absTimeIn found from input!')

    def setTitle(self, titleIn):
        if len(titleIn) > 0:
            self.title = titleIn
        else:
            print('\n', datetime.now().strftime("%H:%M:%S"), '(LogPacket/Setters) ' + 'No title found from input!')

    def setHeadline(self, headlineIn):
        if len(headlineIn) > 0:
            self.headline = headlineIn
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/Setters) ' + 'No headline found from input!')

    def setContent(self, contentIn):
        if isinstance(contentIn, (list)):
            if len(contentIn) > 0:
                self.content = contentIn
        elif isinstance(contentIn, (str)):
            if len(contentIn) > 0:
                self.content.append(contentIn)
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/Setters) ' + 'No content found from input!')

    ### Convert timestamp from str to abs numbers in secs ###
    def timestampConverter(self):
        if len(self.headline) > 0 and len(self.timestamp) > 0:
            h, m, s = self.timestamp.split(':')
            '''print('\n(LogPacket/timestampConverter) ' + self.timestamp)
            print('\n(LogPacket/timestampConverter) ', h, ' = ', int(h)*3600)
            print('\n(LogPacket/timestampConverter) ', m, ' = ', int(m)*60)
            print('\n(LogPacket/timestampConverter) ', s, ' = ', float(s))
            print('\n(LogPacket/timestampConverter) ' + 'Total = ', int(h)*3600 + int(m)*60 + float(s))'''
            return int(h)*3600 + int(m)*60 + float(s)
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/timestampConverter) ' + 'No timestamp found!')
            return -1

    ### Convert abs time to timestamp str ###
    @staticmethod
    def absTimeToTimestamp(absTime):
        if absTime < 0:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/absTimeToTimestamp) ' + 'INVALID: absTime < 0')
            return ''
        # print(absTime)
        # print(pd.to_datetime(pd.to_datetime(absTime, unit = 's'), format = '%H:%M:%S'))
        date, time = str(pd.to_datetime(absTime, unit = 's')).split(' ')
        return time
    
    ### Caculate delay by SFN and slot (A - B) ###
    @staticmethod
    def getDelayBySlot(sfnA, slotNumA, sfnB, slotNumB, numSlotInSFN = 20):
        delay = -1
        if sfnA < 0 or slotNumA < 0 or sfnB < 0 or slotNumB < 0:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/getDelayBySlot) ' + 'INVALID: SFN or slot number < 0')
            return delay
        if numSlotInSFN <= 0:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/getDelayBySlot) ' + 'INVALID: numSlotInSFN <= 0')
            return delay
        TotalSlotA = (sfnA + 1)*numSlotInSFN + slotNumA + 1
        TotalSlotB = (sfnB + 1)*numSlotInSFN + slotNumB + 1
        delayInSlot = 0
        if TotalSlotA >= TotalSlotB:
            delayInSlot = TotalSlotA - TotalSlotB
        else:
            delayInSlot = TotalSlotA + 1024*numSlotInSFN - TotalSlotB
        delay = float('{:.3f}'.format(delayInSlot*(0.01/numSlotInSFN)))
        return delay
    
    ### Calculate delay of two packets (A - B) ###
    @staticmethod
    def getDelay(pktA, pktB):
        if len(pktA.timestamp) > 0 and len(pktB.timestamp) > 0:
            T_A = pktA.timestampConverter()
            T_B = pktB.timestampConverter()
            if T_A >= 0 and T_B >= 0 and T_A >= T_B:
                return int((T_A - T_B)*1000)
            elif T_A >= 0 and T_B >= 0 and T_A < T_B:
                return int((T_A + 86400 - T_B)*1000)
            else:
                return -1
        else:
            return -1

    ### Check if log pkt contains given IE ###
    def containsIE(self, itemToCheck = ''):
        if itemToCheck == '':
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/containsIE) ' + 'INVALID IE!')
            return False
        else:
            for line in self.getContent():
                if itemToCheck in line:
                    return True
        return False         

    ### Destructor ###
    def __del__(self):

        self.packetCode = ''
        self.subID = ''
        self.timestamp = ''
        self.absTime = -1
        self.title = ''
        self.headline = ''
        self.content = [] 


##### Inheritance of LogPacket, add talk spurt indicator #####
class LogPacket_Talkspurt(LogPacket):

    ### Constructor ###
    def __init__(self, logPacket):
        
        if len(logPacket.getHeadline()) > 0:
            self.packetCode = logPacket.getPacketCode()
            self.subID = logPacket.getSubID()
            self.timestamp = logPacket.getTimestamp()
            self.title = logPacket.getTitle()
            self.headline = logPacket.getHeadline()
            self.content = logPacket.getContent()
            self.absTime = logPacket.getAbsTime()
            self.inTalkspurt = False
        else:
            LogPacket.__init__(self)
            self.inTalkspurt = False

    ### Return true if pkt is within talk spurt ###
    def isInTalkspurt(self):
        return self.inTalkspurt    

    ### Set talk spurt indicator to True ###
    def setTalkspurt(self):
        self.inTalkspurt = True

    ### Set talk spurt indicator to False ###
    def setSilence(self):
        self.inTalkspurt = False        

    ### Check downlink RTP packet payload and mark talk spurt for any packet within ###
    @staticmethod
    def findTalkspurt(pktList):
        
        if len(pktList) == 0:
            sys.exit('(LogPacket_Talkspurt/findTalkspurt) ' + 'No log packets found!!!')
        isTalkspurt = False
        rtpPayloadSizeFormat = re.compile(r'^PayLoad Size.*([\d]{2})$')
        # Check RTP payload, greater than 50 = talk spurt, less than 50 = silence
        for pkt in pktList:
            if pkt.getTitle() == 'IMS RTP SN and Payload':
                RtpContent = pkt.getContent()
                for n in range(0, len(RtpContent)):
                    if RtpContent[n] == 'Direction                 = NETWORK_TO_UE':
                        for m in range(n, len(RtpContent)):
                            if rtpPayloadSizeFormat.match(RtpContent[m]):
                                payloadSize = rtpPayloadSizeFormat.match(RtpContent[m]).groups()[0]
                                payloadSize = int(payloadSize)
                                if(payloadSize > 30):
                                    pkt.setTalkspurt()
                                    isTalkspurt = True
                                    #print('(LogPacket_Talkspurt/findTalkspurt) ' + 'RTP payload size: ', payloadSize, ' is talk spurt: ', pkt.isInTalkspurt())
                                    break
                                else:
                                    pkt.setSilence()
                                    isTalkspurt = False
                                    #print('(LogPacket_Talkspurt/findTalkspurt) ' + 'RTP payload size: ', payloadSize, ' is talk spurt: ', pkt.isInTalkspurt())
                                    break
                        break
                    elif RtpContent[n] == 'Direction                 = UE_TO_NETWORK':
                        if isTalkspurt:
                            pkt.setTalkspurt()
                            break
                        else:
                            pkt.setSilence()
                            break
            else:
                if isTalkspurt:
                    pkt.setTalkspurt()
                else:
                    pkt.setSilence()       



    ### Destructor ###
    def __del__(self):
        
        LogPacket.__del__(self)
        self.inTalkspurt = None


##### Inheritance of LogPacket_Talkspurt, add RTP pkt propertyies from 0x1568 and 0x1569 #####
class LogPacket_RTP(LogPacket_Talkspurt):

    ### Constructor ###
    def __init__(self, logPacket):
        
        LogPacket_Talkspurt.__init__(self, logPacket)
        self.direction = ''
        self.ratType = ''
        self.sequence = 0
        self.ssrc = 0
        self.rtpTimeStamp = 0
        self.mediaType = ''
        self.codecType = ''
        self.payloadSize = 0
        self.numLoss = 0
        self.lossSeqNum = 0
        self.lossType = ''
        self.inBurst = False
        
        re_direction = re.compile(r'^Direction.* = (.*)$')
        re_ratType = re.compile(r'^Rat Type.* = (.*)$')
        re_sequence = re.compile(r'^Sequence.* = (.*)$')
        re_ssrc = re.compile(r'^Ssrc.* = (.*)$')
        re_rtpTimeStamp = re.compile(r'^Rtp Time stamp.* = (.*)$')
        re_mediaType = re.compile(r'^mediaType.* = (.*)$')
        re_codecType = re.compile(r'^CodecType.* = (.*)$')
        re_payloadSize = re.compile(r'^PayLoad Size.* = (.*)$')
        re_numLoss = re.compile(r'^Number Lost.* = (.*)$')
        re_lossSeqNum = re.compile(r'^Sequence Number.* = (.*)$')
        re_lossType = re.compile(r'^LossType.* = (.*)$')

        if len(logPacket.getHeadline()) > 0 and (logPacket.getPacketCode() == '0x1568' or logPacket.getPacketCode() == '0x1569'):          
            if self.packetCode == '0x1568':
                self.numLoss = 0
                self.lossSeqNum = 0
                self.lossType = ''
                for line in self.content:
                    if re_direction.match(line):
                        self.direction = re_direction.match(line).groups()[0]
                    elif re_ratType.match(line):
                        self.ratType = re_ratType.match(line).groups()[0]
                    elif re_sequence.match(line):
                        self.sequence = int(re_sequence.match(line).groups()[0])
                    elif re_ssrc.match(line):
                        self.ssrc = int(re_ssrc.match(line).groups()[0])  
                    elif re_rtpTimeStamp.match(line):
                        self.rtpTimeStamp = int(re_rtpTimeStamp.match(line).groups()[0])
                    elif re_mediaType.match(line):
                        self.mediaType = re_mediaType.match(line).groups()[0]
                    elif re_codecType.match(line):
                        self.codecType = re_codecType.match(line).groups()[0]
                    elif re_payloadSize.match(line):
                        self.payloadSize = int(re_payloadSize.match(line).groups()[0])
                    else:
                        continue
            elif self.packetCode == '0x1569':                
                for line in self.content:
                    if re_numLoss.match(line):
                        self.numLoss = int(re_numLoss.match(line).groups()[0])
                    elif re_lossSeqNum.match(line):
                        self.lossSeqNum = int(re_lossSeqNum.match(line).groups()[0])
                    elif re_lossType.match(line):
                        self.lossType = re_lossType.match(line).groups()[0]
                    else:
                        continue

    ### Getters ###
    def getDirection(self):
        return self.direction
    
    def getRatType(self):
        return self.ratType

    def getSequence(self):
        return self.sequence
    
    def getSsrc(self):
        return self.ssrc

    def getRtpTimeStamp(self):
        return self.rtpTimeStamp

    def getMediaType(self):
        return self.mediaType

    def getCodecType(self):
        return self.codecType

    def getPayloadSize(self):
        return self.payloadSize

    def getNumLoss(self):
        return self.numLoss

    def getLossSeqNum(self):
        return self.lossSeqNum

    def getLossType(self):
        return self.lossType

    def isInBurst(RTP_pkt):
        return RTP_pkt.inBurst

    ### Set inBurst to true (if detect pkt is within rtp burst) ###
    def setInBurst(self):
        self.inBurst = True

    ### Get number of DL voice rtp pkt in burst, mark pkt as inBurst, return burst start timestamp and number of pkt in burst ###
    @staticmethod
    def getPacketBurst(pktList):
        rtpBurst = {}  
        if len(pktList) == 0:
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket_RTP/getPacketBurst) ' + 'No RTP packets found!!!')  
            return rtpBurst
        burst_T = 0.01
        burst_TH = 4
        burstStart_T = -1
        burstTimestamp = ''
        burstStart_index = -1
        burst_counter = -1
        n = 0
        while n < len(pktList):
            '''print('n: ', n)
            print('PKT: ', pktList[n].getPacketCode())
            print('Direction: ', pktList[n].getDirection())
            print('AbsTime: ', pktList[n].getAbsTime())
            print('burstStart_T: ', burstStart_T)
            print('burstStart_index: ', burstStart_index)
            print('burst_counter: ', burst_counter)'''
            if pktList[n].getPacketCode() == '0x1568' and pktList[n].getDirection() == 'NETWORK_TO_UE' and pktList[n].getMediaType() == 'AUDIO':
                if burstStart_T == -1:
                    burstStart_T = pktList[n].getAbsTime()
                    burstTimestamp = pktList[n].getTimestamp()
                    burstStart_index = n
                    burst_counter = 1
                    n += 1
                    continue
                else:
                    if pktList[n].getAbsTime() - burstStart_T < burst_T:
                        burst_counter += 1
                        n += 1
                        continue
                    else:
                        if burst_counter >= burst_TH:
                            rtpBurst[burstTimestamp] = burst_counter
                            for x in range(burstStart_index, n):
                                if pktList[x].getDirection() == 'NETWORK_TO_UE' and pktList[x].getMediaType() == 'AUDIO':
                                    pktList[x].setInBurst()
                            n += 1
                            burstStart_T = -1
                            burstTimestamp = ''
                            burstStart_index = -1
                            burst_counter = -1                               
                            continue
                        else:
                            if burstStart_index != -1:
                                n = burstStart_index + 1
                            else:
                                n += 1
                            burstStart_T = -1
                            burstTimestamp = ''
                            burstStart_index = -1
                            burst_counter = -1                     
                            continue
            else:
                if burstStart_T == -1:
                    n += 1
                    continue
                else:
                    if pktList[n].getAbsTime() - burstStart_T < burst_T:
                        n += 1
                        continue
                    else:
                        if burst_counter >= burst_TH:
                            rtpBurst[burstTimestamp] = burst_counter
                            for x in range(burstStart_index, n):
                                if pktList[x].getDirection() == 'NETWORK_TO_UE' and pktList[x].getMediaType() == 'AUDIO':
                                    pktList[x].setInBurst()                                
                            n += 1
                            burstStart_T = -1
                            burstTimestamp = ''
                            burstStart_index = -1
                            burst_counter = -1                             
                            continue
                        else:
                            n = burstStart_index + 1
                            burstStart_T = -1
                            burstTimestamp = ''
                            burstStart_index = -1
                            burst_counter = -1                     
                            continue
        
        return rtpBurst

    ### Destructor ###
    def __del__(self):
        
        LogPacket_Talkspurt.__del__(self)
        self.direction = ''
        self.ratType = ''
        self.sequence = 0
        self.Ssrc = 0
        self.rtpTimeStamp = 0
        self.mediaType = ''
        self.codecType = ''
        self.payloadSize = 0
        self.inBurst = False
        self.numLoss = 0
        self.lossSeqNum = 0
        self.lossType = ''


##### Inheritance of LogPacket, get PHY layer pass/fail/newTx/ReTx in 0xB887 and 0xB883 #####
class LogPacket_PHY_BLER(LogPacket):

    ### Constructor ###
    def __init__(self, logPacket):
        
        self.numOfPass_PDSCH = 0
        self.numOfFail_PDSCH = 0
        self.numOfNewTx_PUSCH = 0
        self.numOfReTx_PUSCH = 0

        re_CRC_PASS = re.compile(r'.*PASS.*')
        re_CRC_FAIL = re.compile(r'.*FAIL.*')
        re_NEW_TX = re.compile(r'.*NEW_TX.*')
        re_RE_TX = re.compile(r'.*RE_TX.*')

        if len(logPacket.getHeadline()) == 0:
            sys.exit('(LogPacket_PHY_BLER/__init__) ' + 'No log packets found!!!')
        else:
            self.packetCode = logPacket.getPacketCode()
            self.subID = logPacket.getSubID()
            self.timestamp = logPacket.getTimestamp()
            self.title = logPacket.getTitle()
            self.headline = logPacket.getHeadline()
            self.content = logPacket.getContent()
            self.absTime = logPacket.getAbsTime()
            if logPacket.getPacketCode() == '0xB887':            
                for line in logPacket.getContent():
                    if re_CRC_PASS.match(line):
                        self.numOfPass_PDSCH += 1
                    elif re_CRC_FAIL.match(line):
                        self.numOfFail_PDSCH += 1
                    else:
                        continue
            elif logPacket.getPacketCode() == '0xB883':
                for line in logPacket.getContent():
                    if re_NEW_TX.match(line):
                        self.numOfNewTx_PUSCH += 1
                    elif re_RE_TX.match(line):
                        self.numOfReTx_PUSCH += 1
                    else:
                        continue            
        
    ### Getters ###
    def getnumOfPass_PDSCH(self):
        return self.numOfPass_PDSCH
    
    def getnumOfFail_PDSCH(self):
        return self.numOfFail_PDSCH

    def getnumOfNewTx_PUSCH(self):
        return self.numOfNewTx_PUSCH
    
    def getnumOfReTx_PUSCH(self):
        return self.numOfReTx_PUSCH
    
    ### Destructor ###
    def __del__(self):
        LogPacket.__del__(self)
        self.numOfPass_PDSCH = 0
        self.numOfFail_PDSCH = 0
        self.numOfNewTx_PUSCH = 0
        self.numOfReTx_PUSCH = 0

##### Inheritance of LogPacket, get CDRX info in 0xB890 #####
class LogPacket_CDRX(LogPacket):

    ### Constructor ###
    def __init__(self, logPacket):
        self.cdrxEvent = {}
        event = []
        sfn = []
        slot = []
        absTime = []
        timestamp = []
        lastSFN = -1
        lastSlot = -1
        re_CDRX_EVENT = re.compile(r'.*\|[0-9\sA-Za-z]{7}\|[\s]*([\d]{1,4})\|([0-9\s]{6})\|[\s]*[A-Z_]{1,18}\|([\s]*[A-Z_]{1,18}|[A-Z]{1,18})\|.*')
        if len(logPacket.getHeadline()) == 0:
            sys.exit('(LogPacket_CDRX/__init__) ' + 'No log packets found!!!')
        else:
            self.packetCode = logPacket.getPacketCode()
            self.subID = logPacket.getSubID()
            self.timestamp = logPacket.getTimestamp()
            self.title = logPacket.getTitle()
            self.headline = logPacket.getHeadline()
            self.content = logPacket.getContent()
            self.absTime = logPacket.getAbsTime()
            if logPacket.getPacketCode() == '0xB890':          
                for line in logPacket.getContent():
                    if re_CDRX_EVENT.match(line):
                        '''print(line)
                        print('g0 SFN: ' + re_CDRX_EVENT.match(line).groups()[0])
                        print('g1 SLOT: ' + re_CDRX_EVENT.match(line).groups()[1].strip())
                        print('g2 EVENT: ' + re_CDRX_EVENT.match(line).groups()[2].strip())'''
                        sfn.append(int(re_CDRX_EVENT.match(line).groups()[0]))
                        slot.append(int(re_CDRX_EVENT.match(line).groups()[1].strip()))
                        event.append(re_CDRX_EVENT.match(line).groups()[2].strip())
                event_sfn_size = len(event)
                if event_sfn_size != 0:
                    lastSFN = sfn[event_sfn_size - 1]
                    lastSlot = slot[event_sfn_size - 1]
                    
                    for n in range(0, event_sfn_size):
                        timeDifference = LogPacket.getDelayBySlot(lastSFN, lastSlot, sfn[n], slot[n])
                        absTime.append(float('{:.3f}'.format(self.absTime - timeDifference)))
                        '''print('TS: ' + self.getTimestamp())
                        print('absTime: ', absTime[len(absTime) - 1])
                        print('sfn: ', sfn[n])
                        print('slot: ', slot[n])
                        print('last sfn: ', lastSFN)
                        print('last slot: ', lastSlot)
                        print('TD: ', timeDifference)'''
                    
                    for absT in absTime:
                        timestamp.append(LogPacket.absTimeToTimestamp(absT))
                    
                    for n in range(0, event_sfn_size):
                        self.cdrxEvent[timestamp[n]] = event[n]             
    
    ### Getters ###
    def getCDRXEvent(self):
        return self.cdrxEvent
    
    ### Destructor ###
    def __del__(self):
        LogPacket.__del__(self)
        self.cdrxEvent = {}

##### Inheritance of LogPacket, get RSRP/SNR info from 0xB8DD #####
class LogPacket_RSRP_SNR(LogPacket):
    
    ### Constructor ###
    def __init__(self, logPacket):
        RX0 = 'Rx0'
        RX1 = 'Rx1'
        RX2 = 'Rx2'
        RX3 = 'Rx3'
        self.RS_TYPE = ''
        self.RSRP = {RX0: 'NA', RX1: 'NA', RX2: 'NA', RX3: 'NA'}
        self.SNR = {RX0: 'NA', RX1: 'NA', RX2: 'NA', RX3: 'NA'}
        re_RS_TYPE = re.compile(r'^SSB Or TRS.* = (.*)$')
        re_RSRP_SNR_Rx0 = re.compile(r'.*\|  0\|[\s]*[\d\.-]*\|[\s]*[\d\.-]*\|[\s]*[\d\.-]*\|[\s]*([\d\.-]*)\|[\s]*([\d\.-]*)\|$')
        re_RSRP_SNR_Rx1 = re.compile(r'.*\|  1\|[\s]*[\d\.-]*\|[\s]*[\d\.-]*\|[\s]*[\d\.-]*\|[\s]*([\d\.-]*)\|[\s]*([\d\.-]*)\|$')
        re_RSRP_SNR_Rx2 = re.compile(r'.*\|  2\|[\s]*[\d\.-]*\|[\s]*[\d\.-]*\|[\s]*[\d\.-]*\|[\s]*([\d\.-]*)\|[\s]*([\d\.-]*)\|$')
        re_RSRP_SNR_Rx3 = re.compile(r'.*\|  3\|[\s]*[\d\.-]*\|[\s]*[\d\.-]*\|[\s]*[\d\.-]*\|[\s]*([\d\.-]*)\|[\s]*([\d\.-]*)\|$')
        
        if len(logPacket.getHeadline()) == 0:
            sys.exit('(LogPacket_RSRP_SNR/__init__) ' + 'No log packets found!!!')
        else:
            self.packetCode = logPacket.getPacketCode()
            self.subID = logPacket.getSubID()
            self.timestamp = logPacket.getTimestamp()
            self.title = logPacket.getTitle()
            self.headline = logPacket.getHeadline()
            self.content = logPacket.getContent()
            self.absTime = logPacket.getAbsTime()
            if logPacket.getPacketCode() == '0xB8DD':          
                for line in logPacket.getContent():
                    if re_RS_TYPE.match(line):
                        self.RS_TYPE = re_RS_TYPE.match(line).groups()[0]
                    elif re_RSRP_SNR_Rx0.match(line):
                        self.SNR[RX0] = float(re_RSRP_SNR_Rx0.match(line).groups()[0])
                        self.RSRP[RX0] = float(re_RSRP_SNR_Rx0.match(line).groups()[1])
                    elif re_RSRP_SNR_Rx1.match(line):
                        self.SNR[RX1] = float(re_RSRP_SNR_Rx1.match(line).groups()[0])
                        self.RSRP[RX1] = float(re_RSRP_SNR_Rx1.match(line).groups()[1])
                    elif re_RSRP_SNR_Rx2.match(line):
                        self.SNR[RX2] = float(re_RSRP_SNR_Rx2.match(line).groups()[0])
                        self.RSRP[RX2] = float(re_RSRP_SNR_Rx2.match(line).groups()[1])
                    elif re_RSRP_SNR_Rx3.match(line):
                        self.SNR[RX3] = float(re_RSRP_SNR_Rx3.match(line).groups()[0])
                        self.RSRP[RX3] = float(re_RSRP_SNR_Rx3.match(line).groups()[1])
            
            '''print('SSB OR TRS: ' + self.RS_TYPE)
            for i, j in self.SNR.items():
                print('SNR ' + i, j)
            for i, j in self.RSRP.items():
                print('RSRP ' + i, j)'''     

    ### Getters ###
    def getRSTYPE(self):
        return self.RS_TYPE
    
    def getRSRP(self):
        return self.RSRP
    
    def getSNR(self):
        return self.SNR
            
    ### Destructor ###
    def __del__(self):
        LogPacket.__del__(self)
        self.RS_TYPE = ''
        self.RSRP = {}
        self.SNR = {}

##### Inheritance of LogPacket, get serving and target cell info from HO event #####
class LogPacket_HO(LogPacket):
    
    ### Constructor ###
    def __init__(self, logPacket):
        ARFCN = 'arfcn'
        PCI = 'pci'
        self.SourceCellInfo = {ARFCN: -1, PCI: -1}
        self.TargetCellInfo = {ARFCN: -1, PCI: -1}
        re_HOCellInfo = re.compile(r'^.*Source Phy Cell Id = ([\d]*),.*Source ARFCN = ([\d]*),.*Target Phy Cell Id = ([\d]*),.*Target ARFCN = ([\d]*).*$')

        # Payload String = Source Phy Cell Id = 9, Source ARFCN = 627264, Target Phy Cell Id = 10, Target ARFCN = 627264

        if len(logPacket.getHeadline()) == 0:
            sys.exit('(LogPacket_HO/__init__) ' + 'No log packets found!!!')
        else:
            self.packetCode = logPacket.getPacketCode()
            self.subID = logPacket.getSubID()
            self.timestamp = logPacket.getTimestamp()
            self.title = logPacket.getTitle()
            self.headline = logPacket.getHeadline()
            self.content = logPacket.getContent()
            self.absTime = logPacket.getAbsTime()
            if logPacket.getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_STARTED_V2':
                for line in logPacket.getContent():
                    if re_HOCellInfo.match(line):
                        self.SourceCellInfo[PCI] = int(re_HOCellInfo.match(line).groups()[0])
                        # print('Source PCI: ', self.SourceCellInfo[PCI])
                        self.SourceCellInfo[ARFCN] = int(re_HOCellInfo.match(line).groups()[1])
                        # print('Source ARFCN: ', self.SourceCellInfo[ARFCN])
                        self.TargetCellInfo[PCI] = int(re_HOCellInfo.match(line).groups()[2])
                        # print('Target PCI: ', self.TargetCellInfo[PCI])
                        self.TargetCellInfo[ARFCN] = int(re_HOCellInfo.match(line).groups()[3])
                        # print('Target ARFCN: ', self.TargetCellInfo[ARFCN])      

    ### Getters ###
    def getSourceCellInfo(self):
        return self.SourceCellInfo
    
    def getTargetCellInfo(self):
        return self.TargetCellInfo
    
    ### Destructor ###
    def __del__(self):
        LogPacket.__del__(self)
        self.SourceCellInfo = {}
        self.TargetCellInfo = {}

if __name__=='__main__': 
    # PostProcessingUtils test
    testDir = PostProcessingUtils()
    testDir.getArgv(sys.argv)
    testDir.scanWorkingDir()
    # testDir.convertToText()
    testDir.scanWorkingDir('.txt')
    testDir.initLogPacketList()
    for value in testDir.getLogPacketList().values():
        for log in value:
            if log.getPacketCode() == '0xB8DD':
                LogPacket_RSRP_SNR(log)
    # testDir.exportAnalyzer()
    # testDir.mergeLogs()
              