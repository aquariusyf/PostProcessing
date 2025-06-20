# 3190 HO success event flatterned

from PostProcessingUtils import LogPacket
from FilterMask import *
import re

# REs
RE_EVENT = re.compile(r'.*(HO_SUCCESS).*')
RE_SOURCE_PCI = re.compile(r'.*Source Phy Cell Id = ([\d]+]),.*')
RE_SOURCE_ARFCN = re.compile(r'.*Source ARFCN = ([\d]+).*')

class LogPacket_3190(LogPacket):
    
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
        self.valid = False
        
        if logPacket.getPacketCode() == '0x1FFB' and logPacket.getTitle() == 'Event  --  EVENT_NR5G_RRC_HO_SUCCESS':
            self.valid = True
            for line in logPacket.getContent():
                if RE_EVENT.match(line):
                    self.event = RE_EVENT.match(line).groups()[0]
                elif RE_SOURCE_PCI.match(line):
                    self.source_pci = int(RE_SOURCE_PCI.match(line).groups()[0])
                elif RE_SOURCE_ARFCN.match(line):
                    self.source_arfcn = int(RE_SOURCE_ARFCN.match(line).groups()[0])
                else:
                    continue
    
    ### Getters ###
    def getEvent(self):
        return self.event
    
    def getSourcePCI(self):
        return self.source_pci
    
    def getSourceARFCN(self):
        return self.source_arfcn
    
    def isValidPkt(self):
        return self.valid
    
    ### Destructor ###
    def __del__(self):
        LogPacket.__del__(self)
        self.event = 'NA'
        self.source_pci = 'NA'
        self.source_arfcn = 'NA'
        self.valid = False