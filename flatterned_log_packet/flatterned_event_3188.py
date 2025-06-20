# 3188 HO start event flatterned

from PostProcessingUtils import LogPacket
from FilterMask import *
import re

# REs
RE_EVENT = re.compile(r'.*(HO_STARTED).*')
RE_SOURCE_PCI = re.compile(r'.*Source Phy Cell Id = ([\d]+).*')
RE_SOURCE_ARFCN = re.compile(r'.*Source ARFCN = ([\d]+).*')
RE_TARGET_PCI = re.compile(r'.*Target Phy Cell Id = ([\d]+).*')
RE_TARGET_ARFCN = re.compile(r'.*Target ARFCN = ([\d]+).*')

class LogPacket_3188(LogPacket):
    
    ### Constructor ###
    def __init__(self, logPacket):
        self.packetCode = logPacket.getPacketCode()
        self.subID = logPacket.getSubID()
        self.timestamp = logPacket.getTimestamp()
        self.title = logPacket.getTitle()
        self.headline = logPacket.getHeadline()
        self.content = logPacket.getContent()
        self.absTime = logPacket.getAbsTime()
        self.event = 'NA'
        self.source_pci = 'NA'
        self.source_arfcn = 'NA'
        self.target_pci = 'NA'
        self.target_arfcn = 'NA'
        self.valid = False
        
        if logPacket.getPacketCode() == '0x1FFB' and logPacket.getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_STARTED_V2':
            self.valid = True
            for line in logPacket.getContent():
                if RE_EVENT.match(line):
                    self.event = RE_EVENT.match(line).groups()[0]
                if RE_SOURCE_PCI.match(line):
                    self.source_pci = int(RE_SOURCE_PCI.match(line).groups()[0])
                if RE_SOURCE_ARFCN.match(line):
                    self.source_arfcn = int(RE_SOURCE_ARFCN.match(line).groups()[0])
                if RE_TARGET_PCI.match(line):
                    self.target_pci = int(RE_TARGET_PCI.match(line).groups()[0])
                if RE_TARGET_ARFCN.match(line):
                    self.target_arfcn = int(RE_TARGET_ARFCN.match(line).groups()[0])

    ### Getters ###
    def getEvent(self):
        return self.event
    
    def getSourcePCI(self):
        return self.source_pci
    
    def getSourceARFCN(self):
        return self.source_arfcn
    
    def getTargetPCI(self):
        return self.target_pci
    
    def getTargetARFCN(self):
        return self.target_arfcn
    
    def isValidPkt(self):
        return self.valid
    
    ### Destructor ###
    def __del__(self):
        LogPacket.__del__(self)
        self.event = 'NA'
        self.source_pci = 'NA'
        self.source_arfcn = 'NA'
        self.target_pci = 'NA'
        self.target_arfcn = 'NA'
        self.valid = False