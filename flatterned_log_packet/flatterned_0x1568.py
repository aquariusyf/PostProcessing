# 0x1568 log packet flatterned

from PostProcessingUtils import LogPacket
from FilterMask import *
import re

# REs
RE_DIRECTION = re.compile(r'.*Direction = (.*)')
RE_RAT_TYPE = re.compile(r'.*Rat Type = (.*)')
RE_SEQUENCE = re.compile(r'.*Sequence = (.*)')
RE_SSRC = re.compile(r'.*Ssrc = (.*)')
RE_RTP_TS = re.compile(r'.*Rtp Time stamp = (.*)')
RE_CODEC_TYPE = re.compile(r'.*CodecType = (.*)')
RE_MEDIA_TYPE = re.compile(r'.*mediaType = (.*)')
RE_PAYLOAD_SIZE = re.compile(r'.*PayLoad Size = (.*)')
RE_RTP_RED_INDICATOR = re.compile(r'.*Rtp Redundant Indicator = (.*)')

class LogPacket_0x1568(LogPacket):
    
    ### Constructor ###
    def __init__(self, logPacket):
        self.packetCode = logPacket.getPacketCode()
        self.subID = logPacket.getSubID()
        self.timestamp = logPacket.getTimestamp()
        self.title = logPacket.getTitle()
        self.headline = logPacket.getHeadline()
        self.content = logPacket.getContent()
        self.absTime = logPacket.getAbsTime()
        self.direction = 'NA'
        self.rat_type = 'NA'
        self.sequence = 'NA'
        self.ssrc = 'NA'
        self.rtp_ts = 'NA'
        self.codec_type = 'NA'
        self.media_type = 'NA'
        self.payload_size = 'NA'
        self.rtp_red_indicator = 'NA'
        self.valid = False
        
        if logPacket.getPacketCode() == '0x1568':
            self.valid = True
            for line in logPacket.getContent():
                if RE_DIRECTION.match(line):
                    self.direction = RE_DIRECTION.match(line).groups()[0]
                elif RE_RAT_TYPE.match(line):
                    self.rat_type = RE_RAT_TYPE.match(line).groups()[0]
                elif RE_SEQUENCE.match(line):
                    self.sequence = int(RE_SEQUENCE.match(line).groups()[0])
                elif RE_SSRC.match(line):
                    self.ssrc = int(RE_SSRC.match(line).groups()[0])
                elif RE_RTP_TS.match(line):
                    self.rtp_ts = int(RE_RTP_TS.match(line).groups()[0])
                elif RE_CODEC_TYPE.match(line):
                    self.codec_type = RE_CODEC_TYPE.match(line).groups()[0]
                elif RE_MEDIA_TYPE.match(line):
                    self.media_type = RE_MEDIA_TYPE.match(line).groups()[0]
                elif RE_PAYLOAD_SIZE.match(line):
                    self.payload_size = int(RE_PAYLOAD_SIZE.match(line).groups()[0])
                elif RE_RTP_RED_INDICATOR.match(line):
                    self.rtp_red_indicator = RE_RTP_RED_INDICATOR.match(line).groups()[0]
                else:
                    continue
            
    ### Getters ###
    def getDirection(self):
        return self.direction
    
    def getRatType(self):
        return self.rat_type
    
    def getSequence(self):
        return self.sequence
    
    def getSSRC(self):
        return self.ssrc
    
    def getRTP_TS(self):
        return self.rtp_ts
    
    def getCodecType(self):
        return self.codec_type
    
    def getMediaType(self):
        return self.media_type
    
    def getPayloadSize(self):
        return self.payload_size
    
    def getRTPRedIndicator(self):
        return self.rtp_red_indicator
    
    def isValidPkt(self):
        return self.valid
    
    ### Destructor ###
    def __del__(self):
        LogPacket.__del__(self)
        self.direction = 'NA'
        self.rat_type = 'NA'
        self.sequence = 'NA'
        self.ssrc = 'NA'
        self.rtp_ts = 'NA'
        self.codec_type = 'NA'
        self.media_type = 'NA'
        self.payload_size = 'NA'
        self.rtp_red_indicator = 'NA'
        self.valid = False