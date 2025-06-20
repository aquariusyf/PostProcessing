# 0x156C log packet flatterned

from PostProcessingUtils import LogPacket
from FilterMask import *
import re

# REs
RE_SEQUENCE = re.compile(r'Sequence Number = (.*)')
RE_RTP_TS = re.compile(r'.*Rtp Timestamp = (.*)')
RE_FRAME_RECEIVE_TIME = re.compile(r'.*Frame receive time = (.*)')
RE_FRAME_DELAY = re.compile(r'.*Frame Delay = (.*)')
RE_Q_SIZE = re.compile(r'.*Q Size = (.*)')
RE_TW_FACTOR = re.compile(r'.*TW Factor = (.*)')
RE_DEQ_DELTA = re.compile(r'.*Dequeue Delta = (.*)')
RE_TARGET_DELAY = re.compile(r'.*Target delay = (.*)')
RE_DEQ_STATE = re.compile(r'.*Dequeue State = (.*)')
RE_SSRC = re.compile(r'.*SSRC = (.*)')
RE_RAT = re.compile(r'.*RAT = (.*)')
RE_IS_REDUNDANT = re.compile(r'.*is_redundant = (.*)')
RE_RED_ENQ_STATUS = re.compile(r'.*red_enq_status = (.*)')

class LogPacket_0x156C(LogPacket):
    
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
        self.frame_receive_time = 'NA'
        self.frame_delay = 'NA'
        self.Q_size = 'NA'
        self.TW_factor = 'NA'
        self.deq_delta = 'NA'
        self.target_delay = 'NA'
        self.deq_state = 'NA'
        self.ssrc = 'NA'
        self.rat = 'NA'
        self.is_redundant = 'NA'
        self.red_enq_status = 'NA'
        self.valid = False
        
        if logPacket.getPacketCode() == '0x156C':
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
                elif RE_FRAME_DELAY.match(line):
                    self.frame_delay = int(RE_FRAME_DELAY.match(line).groups()[0])
                elif RE_Q_SIZE.match(line):
                    self.Q_size = int(RE_Q_SIZE.match(line).groups()[0])
                elif RE_TW_FACTOR.match(line):
                    self.TW_factor = int(RE_TW_FACTOR.match(line).groups()[0])
                elif RE_DEQ_DELTA.match(line):
                    self.deq_delta = int(RE_DEQ_DELTA.match(line).groups()[0])
                elif RE_TARGET_DELAY.match(line):
                    self.target_delay = int(RE_TARGET_DELAY.match(line).groups()[0])
                elif RE_DEQ_STATE.match(line):
                    self.deq_state = RE_DEQ_STATE.match(line).groups()[0]
                elif RE_RED_ENQ_STATUS.match(line):
                    self.red_enq_status = RE_RED_ENQ_STATUS.match(line).groups()[0]           
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
    
    def getFrameDelay(self):
        return self.frame_delay
    
    def getQSize(self):
        return self.Q_size
    
    def getTWFactor(self):
        return self.TW_factor
    
    def getDeQDelta(self):
        return self.deq_delta
    
    def getTargetDelay(self):
        return self.target_delay
    
    def getDeQState(self):
        return self.deq_state
    
    def getRedEnQStatus(self):
        return self.red_enq_status
    
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
        self.frame_receive_time = 'NA'
        self.frame_delay = 'NA'
        self.Q_size = 'NA'
        self.TW_factor = 'NA'
        self.deq_delta = 'NA'
        self.target_delay = 'NA'
        self.deq_state = 'NA'
        self.ssrc = 'NA'
        self.rat = 'NA'
        self.is_redundant = 'NA'
        self.red_enq_status = 'NA'
        self.valid = False