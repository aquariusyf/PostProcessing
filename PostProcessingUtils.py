#---------------------------------------------------------------------------------------------------------------------------------------------------
# Class PostProcessingUtils Functions
#  * getArgv ----- Get inputs from command line (ARGV[1] = log path, ARGV[1 + n] = log packet code or qtrace indicator)
#  * scanWorkingDir ----- Scan the path for files (or given type, .hdf by default) and dirs
#  * getFilesPath ----- Getter of files path in the working directory with given extension
#  * initLogPacketList ----- Initializing the packet list extracted from text files
#  * getLogPacketList ----- Getter of log packet list
#  * convertToText ----- Convert .hdf logs to text files with given log or qtrace filter
#  * findKeywords ----- Find keywords from log text file (Put keywords in keywords_filter.txt and copy to log path)
#  * setDefaultAnalyzerList ----- Set the default analyzer/grid list (APEX build in)
#  * exportAnalyzer ----- Extract the given (or default) analyzer/grid from logs
#  * mergeLogs ----- Merge multiple logs (and convert .qdss/qmdl2 or .bin files to .hdf)
#  * checkConditionIn_X_secs_from_Y ----- Check log packets within x secs of anchor y, take actions (pre-defined) if condition (pre-defined) is met
#---------------------------------------------------------------------------------------------------------------------------------------------------
# Class LogPacket Functions
#  * Setters
#  * Getters
#  * timestampConverter ----- Convert log timestamp from string to int (in secs)
#  * getDelay ----- Calculate the delay between two log packets
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
# class LogPacket_PDSCH Functions (Inheritance of LogPacket, get number of PDSCH CRC PASS/FAIL stats in 0xB887)
#---------------------------------------------------------------------------------------------------------------------------------------------------

import os
import sys
import re
import signal
from datetime import datetime
from sys import platform
from typing import List
if platform == "linux" or platform == "linux2":
    sys.path.append('/opt/qcom/APEX7/Support/Python')	
elif platform == "win32":
    sys.path.append('C:\Program Files (x86)\Qualcomm\APEX7\Support\Python')
import ApexClient

##### Get command line inputs (directory, files, log pkt filter), and run multiple post processing tasks #####
class PostProcessingUtils(object):
    
    ### Constructor ###
    def __init__(self):
        self.files = []
        self.fileExt = '.hdf' # default = .hdf
        self.dirs = []
        self.workingDir = ''
        self.pktFilter = []
        self.pktCodeFormat = re.compile(r'[0][x][\dA-F]{4}$')
        self.defaultPacketFilter = [0xB821, 0x1568, 0x1569, 0x156A, 0x156C, 
                                    0xB800, 0xB801, 0xB808, 0xB809, 0xB80A, 
                                    0xB80B, 0xB814, 0x1CD0]
        self.eventFilter = []
        self.eventCodeFormat = re.compile(r'^[\d]{3,4}$')
        self.defaultEventFilter = [3188, 3190]
        self.keywords = []
        self.isQtrace = False
        self.qtraceFilterStringList = {} # Save Qtrace key words (line by line) in text file qtrace_strings_filter.txt, place in log folder
        self.qtraceFilterStringListNonRegex = [] # if related .qsr4 / .qdb is not with test log(s), then may specify it via "QShrink Server" config param
        self.qtraceFilterStringListRegex = [] # result = apexApp.PutProperty("QShrink Server", "C:\\Temp\\QShrink")
        self.analyzerGrid = []
        self.defaultAnalyzerList = [';NR5G;Summary;PDSCH;NR5G PDSCH Statistics', 
                                    ';NR5G;Summary;UCI;CSF;NR5G CQI Summary', 
                                    ';NR5G;Summary;NR5G Doppler and Delay Spread Bin Summary', 
                                    ';NR5G;Summary;MEAS;NR5G Cell Meas Summary V2', 
                                    ';NR5G;Summary;SNR;NR5G Sub6 SNR Summary'] # Place holder of default analyzer list
        self.logPackets = {}
        self.logPacketFormat = {'headlineFormat':re.compile(r'^[\d]{4}[\s]{1}[A-Za-z]{3}[\s]{1,2}[\d]{1,2}[\s]{2}([\d]{2}:[\d]{2}:[\d]{2}\.[\d]{3}).*([0][x][\dA-F]{4})(.*)$'), 
                                'subIdFormat': re.compile(r'^Subscription ID =.*([\d]{1})')}


    ### Interpret command line, get working directory, initialize log filter ###
    def getArgv(self, sysArgv):
        
        # Get the command line arguments, initialize pkt filter
        if len(sysArgv) > 1:
            if (sysArgv[1].find('-?')) > -1 or (sysArgv[1].find('-h') > -1) or (sysArgv[1].find('-help') > -1):
                sys.exit('(PostProcessingUtils/getArgv) ' + 'Command syntax: python <py file name> <log directory> <log packet codes>')
            else:
                self.workingDir = sysArgv[1]
                logPacketFitler = []
                logEventFitler = []
                for n in range(2, len(sysArgv)):
                    if self.pktCodeFormat.match(str(sysArgv[n])):
                        logId = int(str(sysArgv[n]), 16)
                        self.pktFilter.append(logId)
                        logPacketFitler.append(hex(logId))
                    elif self.eventCodeFormat.match(str(sysArgv[n])):
                        eventId = int(str(sysArgv[n]), 10)
                        self.eventFilter.append(eventId)
                        logEventFitler.append(eventId)
                    elif str(sysArgv[n]) == 'qtrace':
                        self.isQtrace = True
                    else:
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getArgv) ' + 'Invalid log code format: ' + str(sysArgv[n]))
                        continue
                if len(self.pktFilter) == 0:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getArgv) ' + 'No packet filter found!')
                else:
                    print(datetime.now().strftime("%H:%M:%S"),  '(PostProcessingUtils/getArgv) ' + 'Packet filter: ', logPacketFitler)
                if len(self.eventFilter) == 0:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getArgv) ' + 'No event filter found!')
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

    ### Scan dirs and get files (including .awsi, Qtrace filter, keywords filter) to be processed with given extension, by defualt fileExt is set to .hdf ###
    def scanWorkingDir(self, fileExt = '.hdf'):

        self.fileExt = fileExt # override fileExt if needed
        self.files = [] # Clear old files before new scan
        self.analyzerGrid = [] # Clear old files before new scan
        isQtraceFilterFound = False
        qtraceFilterFile = ''
        isKeywordsFilterFound = False
        keywordsFile = ''

        # Check if getArgv is executed and path exists
        if os.path.exists(os.path.abspath(self.workingDir)):
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'Scanning files in path: ' + self.workingDir)
        else:
            sys.exit(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'Error: Directory does not exist --- ' + self.workingDir)

        # Get files and dirs from working directory, scan for .awsi grid files, Qtrace log filter and keywords filter
        for path, dirs, files in os.walk(os.path.abspath(self.workingDir)):
            for file in files:
                if file.endswith(self.fileExt):
                    self.files.append(os.path.join(path, file))
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + self.fileExt + ' file found: ' + str(file))
                elif file.endswith('.awsi') or file.endswith('.aws'):
                    self.analyzerGrid.append(os.path.join(path, file))            
                elif self.isQtrace and file == 'qtrace_strings_filter.txt':
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'Qtrace fitler found')
                    isQtraceFilterFound = True
                    qtraceFilterFile = os.path.join(path,file)
                elif file == 'keywords_filter.txt' and self.fileExt == '_flt_text.txt':
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'Keywords fitler found')
                    isKeywordsFilterFound = True
                    keywordsFile = os.path.join(path,file)                              
            
            for dir in dirs:
                self.dirs.append(os.path.join(path, dir))
                #print('(PostProcessingUtils/scanDirs)' + 'Dir found: ' + os.path.join(path, dir))
        
        # Check if Qtrace is enabled and filter is found
        if self.isQtrace and isQtraceFilterFound == False:
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + "No Qtrace filter found, please create filter in 'qtrace_strings_filter.txt' and place it into log folder!")
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'No Qtrace filter will be applied!')
            self.isQtrace = False
        elif self.isQtrace and isQtraceFilterFound:
            filterFile = open(qtraceFilterFile, 'r')
            filterLines = filterFile.readlines()
            filterFile.close()
            for line in filterLines:
                if line == '\n' or line.isspace():
                    continue
                else:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'Qtrace key words in filter: ' + line)
                    line = line.strip()
                    self.qtraceFilterStringListNonRegex.append(line)
                    # self.qtraceFilterStringListRegex.append(line)
            if len(self.qtraceFilterStringListNonRegex) == 0:
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'No Qtrace key words found in filter')
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'No Qtrace filter will be applied!')
                self.isQtrace = False

        # Check if keywords filter is found
        if isKeywordsFilterFound:
            keywordsFitlerFile = open(keywordsFile, 'r')
            keywordsFilterLines = keywordsFitlerFile.readlines()
            keywordsFitlerFile.close()
            for line in keywordsFilterLines:
                if line == '\n' or line.isspace():
                    continue
                else:
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'Keyword in filter: ' + line)
                    line = line.strip()
                    self.keywords.append(line)
            if len(self.keywords) == 0:
                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/scanWorkingDir) ' + 'No keywords found in filter!')                                
        
    ### Getter of files in the working directory with given extension ###
    def getFilesPath(self):
        return self.files

    ### Initialize log packet list, get log info from text file ###
    def initLogPacketList(self):

        # Check if filtered text file is found
        if len(self.files) == 0:
            sys.exit('(PostProcessingUtils/initLogPacketList) ' + 'No fitlered text file found, please check path or fileExt')

        currentLogPkts = []
        formatFound = ''
        for file in self.files:
            logPkt = LogPacket()
            fileLines = []
            openedFile = open(file, 'r')
            fileLines = openedFile.readlines()
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/initLogPacketList) ' + 'FILE = ' + file)
            openedFile.close()

            for index, line in enumerate(fileLines):
                if index == len(fileLines) - 1:
                    currentLogPkts.append(logPkt)
                    logPkt = LogPacket()
                    break
                if line == '\n' or line.isspace():
                    continue
                else:
                    line = line.strip()
                    if (len(line) == 1 and (line == '{' or line == '}')) or (len(line) == 2 and line == '},'):
                        continue 
                    if self.logPacketFormat['headlineFormat'].match(line):
                        if len(logPkt.getHeadline()) != 0:
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
            
            if len(currentLogPkts) > 0:
                self.logPackets[os.path.split(file)[1]] = currentLogPkts
            currentLogPkts = []
        #print('(PostProcessingUtils/initLogPacketList) ' + 'KEYS: ',  self.logPackets.keys())

    
    ### Getter of PacketList ###
    def getLogPacketList(self): 
        if len(self.logPackets) > 0:
            return self.logPackets
        else:
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/getLogPacketList) ' + 'No log packets found!!!')
            return {}


    ### Apply filters and convert QXDM logs to txt files ###
    def convertToText(self):
        
        # Check if logs are found and filter is applied
        noPacketFitler = False
        noEventFitler = False
        firstTimeRun = True
        if self.fileExt != '.hdf' or len(self.files) == 0:
            sys.exit('(PostProcessingUtils/convertToText) ' + 'No .hdf logs found, please check path or fileExt')
        if len(self.pktFilter) == 0:
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'No packet filters applied!')
            noPacketFitler = True
        if len(self.eventFilter) == 0:
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'No event filters applied!')
            noEventFitler = True
        if self.isQtrace:
            self.qtraceFilterStringList = {0: self.qtraceFilterStringListNonRegex, 1: self.qtraceFilterStringListRegex}
            # self.qtraceFilterStringList[0] = self.qtraceFilterStringListNonRegex
            # self.qtraceFilterStringList[1] = self.qtraceFilterStringListRegex

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
                    outputTextFile = logFile.replace('.hdf', '_flt_text.txt')
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
                    elif self.isQtrace:
                        if firstTimeRun:
                            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Qtrace enabled and no pacekets specified, default packet filter will NOT be applied!!!')
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
                    elif self.isQtrace:
                        if firstTimeRun:
                            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Qtrace enabled and no events specified, default event filter will NOT be applied!!!')
                    else:
                        if firstTimeRun:
                            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Apply default event filter!')
                        for filter in self.defaultEventFilter:
                            apex.Set('EventFilter', filter, 1)
                            if firstTimeRun:
                                print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Set event ', filter, ' TRUE')
                    apex.Commit('EventFilter')      

                    # Set Qtrace filter
                    if self.isQtrace:
                        if firstTimeRun:
                            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Apply Qtrace filter!')
                        apex.Set('PacketFilter', 0x1FE7, 1) # Qtrace and F3 pkt 0x1FE7, 0x1FE8, 0x1FEB have to be enabled explicitly
                        apex.Set('PacketFilter', 0x1FE8, 1)
                        apex.Set('PacketFilter', 0x1FEB, 1)
                        apex.Commit('PacketFilter')
                        result = apex.SetQtraceFilterString(self.qtraceFilterStringList)
                        apex.SortByTime()
                    
                    firstTimeRun = False

                    # Open log
                    print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/convertToText) ' + 'Opening log: ' + str(logFile))
                    if apex.OpenLog([logFile]) != 1:     
                        apex.Exit()
                        sys.exit('(PostProcessingUtils/convertToText) ' + 'Open log failed: ' + str(logFile))
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

    ### Find keywords from log text file (Put keywords in keywords_filter.txt and copy to log path) ###
    def findKeywords(self):
        if len(self.files) == 0:
            sys.exit('(PostProcessingUtils/findKeywords) ' + 'No log text file found!!!')
        if len(self.keywords) == 0:
            sys.exit('(PostProcessingUtils/findKeywords) ' + "No keywords found, please create filter in 'keywords_filter.txt' and place it into log folder!")
        
        resultFile = os.path.join(self.workingDir, 'keywords_search_result.txt')      
        f = open(resultFile, 'w')
        kw_summary = {}
        
        for key in self.logPackets.keys():
            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/findKeywords) ' + 'Searching keywords in: ' + key)  
            f.write('########## ' + key + ' ##########\n')
            for kw in self.keywords:
                kw_summary[kw] = 0
            for logPkt in self.logPackets[key]:
                for kw in self.keywords:
                    if kw in logPkt.getHeadline():
                        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/findKeywords) ' + "Found keyword: '" + kw + "' in " + logPkt.getHeadline())
                        f.write(logPkt.getTimestamp() + ' ' + logPkt.getTitle() + '\n')
                        kw_summary[kw] += 1
                logContent = logPkt.getContent()
                for contentLine in logContent:
                    for kw in self.keywords:
                        if kw in contentLine:
                            print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/findKeywords) ' + "Found keyword: '" + kw + "' in " + logPkt.getHeadline())
                            f.write(logPkt.getTimestamp() + ' ' + contentLine + '\n')
                            kw_summary[kw] += 1
                            continue
            f.write('\n')
            for key in kw_summary.keys():
                f.write('-----Found ' + str(kw_summary[key]) + " '" + key + "' " + '\n')
            f.write('\n')
        f.close()
        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/findKeywords) ' + 'Search keywords completed!')
        print(datetime.now().strftime("%H:%M:%S"), '(PostProcessingUtils/findKeywords) ' + 'Result in: ' + resultFile)            
    
    ### Set default analyzer list ###
    def setDefaultAnalyzerList(self, analyzerList):
        if len(analyzerList) != 0:
            self.defaultAnalyzerList = analyzerList 
        else:
            sys.exit('(PostProcessingUtils/setDefaultAnalyzerList) ' + 'Input analyzer list is empty!!!')

    ### Export analyzer to Excel ###
    def exportAnalyzer(self):

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
            exportPath = logFile.replace('.hdf', '_CSD_All_Grid.xlsm')
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
            sys.exit('(PostProcessingUtils/mergeLogs) ' + 'No logs found in: ', self.workingDir)
            
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
        self.files = []
        self.fileExt = ''
        self.dirs = []
        self.workingDir = ''
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
            print(datetime.now().strftime("%H:%M:%S"), '(LogPacket/Getters) ' + 'No headline found!')
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
        TS_Threshhold = 30
        self.inBurst = False         

        re_direction = re.compile(r'^Direction.* = (.*)$')
        re_ratType = re.compile(r'^Rat Type.* = (.*)$')
        re_sequence = re.compile(r'^Sequence.* = (.*)$')
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
                    elif re_rtpTimeStamp.match(line):
                        self.rtpTimeStamp = int(re_rtpTimeStamp.match(line).groups()[0])
                    elif re_mediaType.match(line):
                        self.mediaType = re_mediaType.match(line).groups()[0]
                    elif re_codecType.match(line):
                        self.codecType = re_codecType.match(line).groups()[0]
                    elif re_payloadSize.match(line):
                        self.payloadSize = int(re_payloadSize.match(line).groups()[0])
                        if self.payloadSize > TS_Threshhold:
                            self.setTalkspurt()
                        else:
                            self.setSilence()
                    else:
                        continue
            elif self.packetCode == '0x1569':
                self.direction = ''
                self.ratType = ''
                self.sequence = 0
                self.rtpTimeStamp = 0
                self.mediaType = ''
                self.codecType = ''
                self.payloadSize = 0                
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

    ### Get number of DL rtp pkt in burst, mark pkt as inBurst, return burst start timestamp and number of pkt in burst ###
    @staticmethod
    def getPacketBurst(pktList):
        rtpBurst = {}  
        if len(pktList) == 0:
            print('(LogPacket_RTP/getPacketBurst) ' + 'No log packets found!!!')  
            return rtpBurst
        burst_T = 0.01
        burst_TH = 4
        burstStart_T = -1
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
            if pktList[n].getPacketCode() == '0x1568' and pktList[n].getDirection() == 'NETWORK_TO_UE':
                if burstStart_T == -1:
                    burstStart_T = pktList[n].getAbsTime()
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
                            rtpBurst[burstStart_T] = burst_counter
                            for x in range(burstStart_index, burstStart_index + burst_counter):
                                if pktList[x].getDirection() != 'NETWORK_TO_UE':
                                    burst_counter += 1
                            for x in range(burstStart_index, burstStart_index + burst_counter):
                                if pktList[x].getDirection() == 'NETWORK_TO_UE':
                                    pktList[x].setInBurst()
                                else:
                                    burst_counter += 1
                            n += 1
                            burstStart_T = -1
                            burstStart_index = -1
                            burst_counter = -1                               
                            continue
                        else:
                            if burstStart_index != -1:
                                n = burstStart_index + 1
                            else:
                                n += 1
                            burstStart_T = -1
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
                            rtpBurst[burstStart_T] = burst_counter
                            for x in range(burstStart_index, burstStart_index + burst_counter):
                                if pktList[x].getDirection() != 'NETWORK_TO_UE':
                                    burst_counter += 1
                            for x in range(burstStart_index, burstStart_index + burst_counter):
                                if pktList[x].getDirection() == 'NETWORK_TO_UE':
                                    pktList[x].setInBurst()
                            n += 1
                            burstStart_T = -1
                            burstStart_index = -1
                            burst_counter = -1                             
                            continue
                        else:
                            n = burstStart_index + 1
                            burstStart_T = -1
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
        self.rtpTimeStamp = 0
        self.mediaType = ''
        self.codecType = ''
        self.payloadSize = 0
        self.inBurst = False
        self.numLoss = 0
        self.lossSeqNum = 0
        self.lossType = ''


##### Inheritance of LogPacket, get number of PDSCH CRC PASS/FAIL stats in 0xB887 #####
class LogPacket_PDSCH(LogPacket):

    ### Constructor ###
    def __init__(self, logPacket):
        
        self.numOfPass = 0
        self.numOfFail = 0

        re_CRC_PASS = re.compile(r'.* PASS.*')
        re_CRC_FAIL = re.compile(r'.* FAIL.*')

        if len(logPacket.getHeadline()) == 0:
            sys.exit('(LogPacket_PDSCH/__init__) ' + 'No log packets found!!!')
        else:
            if logPacket.getPacketCode() == '0xB887':
                self.packetCode = logPacket.getPacketCode()
                self.subID = logPacket.getSubID()
                self.timestamp = logPacket.getTimestamp()
                self.title = logPacket.getTitle()
                self.headline = logPacket.getHeadline()
                self.content = logPacket.getContent()
                self.absTime = logPacket.getAbsTime()
                for line in logPacket.getContent():
                    if re_CRC_PASS.match(line):
                        self.numOfPass += 1
                    elif re_CRC_FAIL.match(line):
                        self.numOfFail += 1
                    else:
                        continue
        
    ### Getters ###
    def getNumOfPass(self):
        return self.numOfPass
    
    def getNumOfFail(self):
        return self.numOfFail

    ### Destructor ###
    def __del__(self):
        LogPacket.__del__(self)
        self.numOfPass = 0
        self.numOfFail = 0


if __name__=='__main__': 
    # PostProcessingUtils test
    testDir = PostProcessingUtils()
    # testDir.getArgv(sys.argv)
    # testDir.scanWorkingDir('.txt')
    # testDir.initLogPacketList()
    '''for value in testDir.getLogPacketList().values():
        for n in range(1, len(value)):
            print(LogPacket.getDelay(value[n], value[n-1]))'''
    # testDir.convertToText()
    # testDir.exportAnalyzer()
    # testDir.mergeLogs()
              