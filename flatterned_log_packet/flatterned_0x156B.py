# 0x156B log packet flatterned

from PostProcessingUtils import LogPacket
from FilterMask import *
import re

# REs
RE_SEQUENCE = re.compile(r'.*Seq Number = (.*)')
RE_RTP_TS = re.compile(r'.*Rtp Time Stamp = (.*)')
RE_FRAME_RECEIVE_TIME = re.compile(r'.*Frame receive time = (.*)')
RE_ENQ_RESULT = re.compile(r'.*Enqueue result = (.*)')
RE_SSRC = re.compile(r'.*SSRC = (.*)')
RE_RAT = re.compile(r'.*RAT = (.*)')
RE_IS_REDUNDANT = re.compile(r'.*is_redundant = (.*)')

class LogPacket_0x156B(LogPacket):
    
    ### Constructor ###
    def __init__(self, logPacket):
        self.packetCode = logPacket.getPacketCode()
        self.subID = logPacket.getSubID()
        self.timestamp = logPacket.getTimestamp()
        self.title = logPacket.getTitle()
        self.headline = logPacket.getHeadline()
        self.content = logPacket.getContent()
        self.absTime = logPacket.getAbsTime()
        self.sequence = 'NA'
        self.rtp_ts = 'NA'
        self.ssrc = 'NA'
        self.frame_receive_time = 'NA'
        self.enq_result = 'NA'
        self.rat = 'NA'
        self.is_redundant = 'NA'
        self.valid = False
        
        if logPacket.getPacketCode() == '0x156B':
            self.valid = True
            for line in logPacket.getContent():
                if RE_SEQUENCE.match(line):
                    self.sequence = int(RE_SEQUENCE.match(line).groups()[0])
                elif RE_RTP_TS.match(line):
                    self.rtp_ts = int(RE_RTP_TS.match(line).groups()[0])
                elif RE_SSRC.match(line):
                    self.ssrc = int(RE_SSRC.match(line).groups()[0])
                elif RE_FRAME_RECEIVE_TIME.match(line):
                    self.frame_receive_time = int(RE_FRAME_RECEIVE_TIME.match(line).groups()[0])
                elif RE_ENQ_RESULT.match(line):
                    self.enq_result = RE_ENQ_RESULT.match(line).groups()[0]
                elif RE_RAT.match(line):
                    self.rat = RE_RAT.match(line).groups()[0]
                elif RE_IS_REDUNDANT.match(line):
                    self.is_redundant = int(RE_IS_REDUNDANT.match(line).groups()[0])
                else:
                    continue
    
    ### Getters ###
    def getRTP_TS(self):
        return self.rtp_ts
    
    def getSequence(self):
        return self.sequence
    
    def getSSRC(self):
        return self.ssrc
    
    def getFrameReceiveTime(self):
        return self.frame_receive_time
    
    def getEnQResult(self):
        return self.enq_result
    
    def getRat(self):
        return self.rat
    
    def getIsRedundant(self):
        return self.is_redundant
    
    def isValidPkt(self):
        return self.valid
    
    ### Destructor ###
    def __del__(self):
        LogPacket.__del__(self)
        self.sequence = 'NA'
        self.rtp_ts = 'NA'
        self.ssrc = 'NA'
        self.frame_receive_time = 'NA'
        self.enq_result = 'NA'
        self.rat = 'NA'
        self.is_redundant = 'NA'
        self.valid = False