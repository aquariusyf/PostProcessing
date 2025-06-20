# 0x1569 log packet flatterned

from PostProcessingUtils import LogPacket
from FilterMask import *
import re

# REs
RE_NUM_LOST = re.compile(r'.*Number Lost = (.*)')
RE_SEQUENCE = re.compile(r'.*Sequence Number = (.*)')
RE_SSRC = re.compile(r'.*SSRC = (.*)')
RE_CODEC_TYPE = re.compile(r'.*codecType = (.*)')
RE_LOST_TYPE = re.compile(r'.*LossType = (.*)')
RE_TOTAL_LOST = re.compile(r'.*Total Lost = (.*)')
RE_TOTAL_PKT_COUNT = re.compile(r'.*Total Packets Count = (.*)')

class LogPacket_0x1569(LogPacket):
    
    ### Constructor ###
    def __init__(self, logPacket):
        self.packetCode = logPacket.getPacketCode()
        self.subID = logPacket.getSubID()
        self.timestamp = logPacket.getTimestamp()
        self.title = logPacket.getTitle()
        self.headline = logPacket.getHeadline()
        self.content = logPacket.getContent()
        self.absTime = logPacket.getAbsTime()
        self.num_lost = 'NA'
        self.sequence = 'NA'
        self.ssrc = 'NA'
        self.lost_type = 'NA'
        self.codec_type = 'NA'
        self.total_lost = 'NA'
        self.total_pkt_count = 'NA'
        self.valid = False
        
        if logPacket.getPacketCode() == '0x1569':
            self.valid = True
            for line in logPacket.getContent():
                if RE_NUM_LOST.match(line):
                    self.num_lost = int(RE_NUM_LOST.match(line).groups()[0])
                elif RE_SEQUENCE.match(line):
                    self.sequence = int(RE_SEQUENCE.match(line).groups()[0])
                elif RE_SSRC.match(line):
                    self.ssrc = int(RE_SSRC.match(line).groups()[0])
                elif RE_LOST_TYPE.match(line):
                    self.lost_type = RE_LOST_TYPE.match(line).groups()[0]
                elif RE_CODEC_TYPE.match(line):
                    self.codec_type = RE_CODEC_TYPE.match(line).groups()[0]
                elif RE_TOTAL_LOST.match(line):
                    self.total_lost = int(RE_TOTAL_LOST.match(line).groups()[0])
                elif RE_TOTAL_PKT_COUNT.match(line):
                    self.total_pkt_count = int(RE_TOTAL_PKT_COUNT.match(line).groups()[0])
                else:
                    continue
    
    ### Getters ###
    def getNumLost(self):
        return self.num_lost
    
    def getSequence(self):
        return self.sequence
    
    def getSSRC(self):
        return self.ssrc
    
    def getLostType(self):
        return self.lost_type
    
    def getCodecType(self):
        return self.codec_type
    
    def getTotalLost(self):
        return self.total_lost
    
    def getTotalPktCount(self):
        return self.total_pkt_count
    
    def isValidPkt(self):
        return self.valid
    
    ### Destructor ###
    def __del__(self):
        LogPacket.__del__(self)
        self.num_lost = 'NA'
        self.sequence = 'NA'
        self.ssrc = 'NA'
        self.lost_type = 'NA'
        self.codec_type = 'NA'
        self.total_lost = 'NA'
        self.total_pkt_count = 'NA'
        self.valid = False