# 0x1E9C log packet flatterned

from PostProcessingUtils import LogPacket
from FilterMask import *
import re

# REs
RE_EVENT = re.compile(r'.*event = (.*)')
RE_DIRECTION = re.compile(r'.*direction = (.*)')
RE_HO_ADAPTED = re.compile(r'.*ho_adapted = (.*)')
RE_INET_TECH = re.compile(r'.*inet_tech = (.*)')
RE_LINK_STATE = re.compile(r'.*link_state = (.*)')
RE_LINK_SETUP_TIME = re.compile(r'.*link_setup_duration = ([\d]+)')
RE_EXP_PLAYOUT_CNT = re.compile(r'.*exp_playout_cnt = (.*)')
RE_RECEIVED_RED_FRAME_CNT = re.compile(r'.*received_red_rx_frames_cnt = (.*)')
RE_PLAYED_FRAMES_CNT_PRIM = re.compile(r'.*played_frames_cnt_prim = (.*)')
RE_PLAYED_FRAMES_CNT_RED = re.compile(r'.*played_frames_cnt_red = (.*)')
RE_DISCARD_RED_FRAMES_CNT = re.compile(r'.*discard_frames_cnt_red = (.*)')
RE_UNDERFLOW_FRAMES_CNT_RED = re.compile(r'.*uflow_frames_cnt_red = (.*)')
RE_TOT_DEQ_ATTEMPTS_WITHIN_INTERVAL = re.compile(r'.*tot_deq_attempts_cnt_witin_intvl =(.*)')
RE_DEQ_AGGR_FAIL_CNT = re.compile(r'.*deq_aggr_fail_cnt = (.*)')
RE_DEQ_PRIM_FAIL_CNT = re.compile(r'.*deq_prim_fail_cnt = (.*)')
RE_RED_USEFULNESS = re.compile(r'.*red_usefulness = (.*)')
RE_PRIM_PKT_LOSS_IN_LONG_WIN = re.compile(r'.*prim_pkt_loss_in_long_win = (.*)')
RE_TX_RTP_CNT_PRIM = re.compile(r'.*tx_rtp_cnt_prim = (.*)')
RE_TX_RTP_CNT_RED = re.compile(r'.*tx_rtp_cnt_red = (.*)')


class LogPacket_0x1E9C(LogPacket):
    
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
        self.direction = 'NA'
        self.ho_adapt = 'NA'
        self.inet_tech = 'NA'
        self.link_state = 'NA'
        self.link_setup_time = 'NA'
        self.exp_playout_cnt = 'NA'
        self.received_red_frame_cnt = 'NA'
        self.played_frame_cnt_prim = 'NA'
        self.played_frame_cnt_red = 'NA'
        self.discard_red_frame_cnt = 'NA'
        self.underflow_red_frame_cnt = 'NA'
        self.total_deq_attempt_within_interval = 'NA'
        self.deq_aggr_fail_cnt = 'NA'
        self.deq_prim_fail_cnt = 'NA'
        self.red_usefulness = 'NA'
        self.prim_pkt_loss_in_long_win = 'NA'
        self.tx_rtp_cnt_prim = 'NA'
        self.tx_rtp_cnt_red = 'NA'
        self.valid = False
        
        if logPacket.getPacketCode() == '0x1E9C':
            self.valid = True
            for line in logPacket.getContent():
                if RE_EVENT.match(line):
                    self.event = RE_EVENT.match(line).groups()[0]
                elif RE_DIRECTION.match(line):
                    self.direction = RE_DIRECTION.match(line).groups()[0]
                elif RE_HO_ADAPTED.match(line):
                    self.ho_adapt = RE_HO_ADAPTED.match(line).groups()[0]
                elif RE_INET_TECH.match(line):
                    self.inet_tech = RE_INET_TECH.match(line).groups()[0]
                elif RE_LINK_STATE.match(line):
                    self.link_state = RE_LINK_STATE.match(line).groups()[0]
                elif RE_LINK_SETUP_TIME.match(line):
                    self.link_setup_time = int(RE_LINK_SETUP_TIME.match(line).groups()[0])
                elif RE_EXP_PLAYOUT_CNT.match(line):
                    self.exp_playout_cnt = int(RE_EXP_PLAYOUT_CNT.match(line).groups()[0])
                elif RE_RECEIVED_RED_FRAME_CNT.match(line):
                    self.received_red_frame_cnt = int(RE_RECEIVED_RED_FRAME_CNT.match(line).groups()[0])
                elif RE_PLAYED_FRAMES_CNT_PRIM.match(line):
                    self.played_frame_cnt_prim = int(RE_PLAYED_FRAMES_CNT_PRIM.match(line).groups()[0])    
                elif RE_PLAYED_FRAMES_CNT_RED.match(line):
                    self.played_frame_cnt_red = int(RE_PLAYED_FRAMES_CNT_RED.match(line).groups()[0])
                elif RE_DISCARD_RED_FRAMES_CNT.match(line):
                    self.discard_red_frame_cnt = int(RE_DISCARD_RED_FRAMES_CNT.match(line).groups()[0]) 
                elif RE_UNDERFLOW_FRAMES_CNT_RED.match(line):
                    self.underflow_red_frame_cnt = int(RE_UNDERFLOW_FRAMES_CNT_RED.match(line).groups()[0])    
                elif RE_TOT_DEQ_ATTEMPTS_WITHIN_INTERVAL.match(line):
                    self.total_deq_attempt_within_interval = int(RE_TOT_DEQ_ATTEMPTS_WITHIN_INTERVAL.match(line).groups()[0])
                elif RE_DEQ_AGGR_FAIL_CNT.match(line):
                    self.deq_aggr_fail_cnt = int(RE_DEQ_AGGR_FAIL_CNT.match(line).groups()[0])      
                elif RE_DEQ_PRIM_FAIL_CNT.match(line):
                    self.deq_prim_fail_cnt = int(RE_DEQ_PRIM_FAIL_CNT.match(line).groups()[0])   
                elif RE_RED_USEFULNESS.match(line):
                    self.red_usefulness = int(RE_RED_USEFULNESS.match(line).groups()[0])
                elif RE_PRIM_PKT_LOSS_IN_LONG_WIN.match(line):
                    self.prim_pkt_loss_in_long_win = int(RE_PRIM_PKT_LOSS_IN_LONG_WIN.match(line).groups()[0])       
                elif RE_TX_RTP_CNT_PRIM.match(line):
                    self.tx_rtp_cnt_prim = int(RE_TX_RTP_CNT_PRIM.match(line).groups()[0])     
                elif RE_TX_RTP_CNT_RED.match(line):
                    self.tx_rtp_cnt_red = int(RE_TX_RTP_CNT_RED.match(line).groups()[0])   
                else:
                    continue
    
    ### Getters ###
    def getEvent(self):
        return self.event
    
    def getDirection(self):
        return self.direction
    
    def getHOAdapt(self):
        return self.ho_adapt
    
    def getInetTech(self):
        return self.inet_tech
    
    def getLinkState(self):
        return self.link_state
    
    def getLinkSetupTime(self):
        return self.link_setup_time
    
    def getExpPlayoutCount(self):
        return self.exp_playout_cnt
    
    def getReceivedRedFrameCount(self):
        return self.received_red_frame_cnt
    
    def getPlayedFrameCountPrim(self):
        return self.played_frame_cnt_prim
    
    def getPlayedFrameCountRed(self):
        return self.played_frame_cnt_red
    
    def getDiscardRedFrameCount(self):
        return self.discard_red_frame_cnt
    
    def getUnderflowRedFrameCount(self):
        return self.underflow_red_frame_cnt
    
    def getTotalDeQAttempsWithinInterval(self):
        return self.total_deq_attempt_within_interval
    
    def getDeQAggrFailCount(self):
        return self.deq_aggr_fail_cnt
    
    def getDeQPrimFailCount(self):
        return self.deq_prim_fail_cnt
    
    def getRedUsefulness(self):
        return self.red_usefulness
    
    def getPrimPktLossInLongWin(self):
        return self.prim_pkt_loss_in_long_win
    
    def getTxRtpCountPrim(self):
        return self.tx_rtp_cnt_prim
    
    def getTxRtpCountRed(self):
        return self.tx_rtp_cnt_red

    def isValidPkt(self):
        return self.valid
    
    ### Destructor ###
    def __del__(self):
        LogPacket.__del__(self)
        self.event = 'NA'
        self.direction = 'NA'
        self.ho_adapt = 'NA'
        self.inet_tech = 'NA'
        self.link_state = 'NA'
        self.link_setup_time = 'NA'
        self.exp_playout_cnt = 'NA'
        self.received_red_frame_cnt = 'NA'
        self.played_frame_cnt_prim = 'NA'
        self.played_frame_cnt_red = 'NA'
        self.discard_red_frame_cnt = 'NA'
        self.underflow_red_frame_cnt = 'NA'
        self.total_deq_attempt_within_interval = 'NA'
        self.deq_aggr_fail_cnt = 'NA'
        self.deq_prim_fail_cnt = 'NA'
        self.red_usefulness = 'NA'
        self.prim_pkt_loss_in_long_win = 'NA'
        self.tx_rtp_cnt_prim = 'NA'
        self.tx_rtp_cnt_red = 'NA'
        self.valid = False