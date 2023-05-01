from PostProcessingUtils import PostProcessingUtils
from FilterMask import *
import sys

'''filter_mask[LOG_FILTER] = [0xB821]
filter_mask[EVENT_FILTER] = []
filter_mask[QTRACE_NON_REGEX] = ['rach_setup_msg1_tx', 'Got DL_RAR_RESULT_INDI', 'rach_rar_state_handler', 'send MAC_RACH_ACTIVITY_IND rach_status']
filter_mask[KEYWORDS_FILTER] = ['rach_setup_msg1_tx', 'Got DL_RAR_RESULT_INDI', 'rach_rar_state_handler', 'send MAC_RACH_ACTIVITY_IND rach_status',
                                'RRC Setup Req', 'RRC Setup', 'RRCSetup Complete']'''
                                
'''filter_mask[LOG_FILTER] = [0xB821]
filter_mask[EVENT_FILTER] = []
filter_mask[QTRACE_NON_REGEX] = ['presched']
filter_mask[KEYWORDS_FILTER] = ['init_state_int', 'presched_det_state_int', 'sr_sup_state_int', 'tmp_sr_trg_int', 'last_presched_slot update']'''

filter_mask[LOG_FILTER] = [0x156E, 0xB821, 0xB80B, 0xB80A, 0xB80B, 0xB800, 0xB801, 0x1830, 0x1831]
filter_mask[EVENT_FILTER] = []
filter_mask[KEYWORDS_FILTER] = ['IMS_SIP_REGISTER/INFORMAL_RESPONSE', 'IMS_SIP_REGISTER/UNAUTHORIZED', 'IMS_SIP_REGISTER/OK', 'IMS_SIP_INVITE/INFORMAL_RESPONSE',
                                'NR5G NAS MM5G Plain OTA Outgoing Msg  --  Service request', 'establishmentCause', 'BCCH_BCH / Mib', 'BCCH_DL_SCH / SystemInformationBlockType1', 
                                'UL_CCCH / RRC Setup Req', 'DL_CCCH / RRC Setup', 'srb-Identity 1', 'UL_DCCH / RRCSetup Complete', 'DL_DCCH / securityModeCommand', 
                                'UL_DCCH / SecurityMode Complete', 'DL_DCCH / UeCapabilityEnquiry', 'UL_DCCH / UeCapabilityInformation', 'DL_DCCH / RRCReconfiguration',
                                'srb-Identity 2', 'rlc-Config am', 'UL_DCCH / RRCConfiguration Complete', 'NR5G NAS MM5G Plain OTA Incoming Msg  --  Service accept',
                                'measIdToAddModList', 'UL_DCCH / MeasurementReport', 'drx-Config release',
                                'IMS_SIP_INVITE/TRYING', 'drb-ToAddModList', 'rlc-Config um', 'drx-onDurationTimer', 'drx-InactivityTimer', 'drx-LongCycleStartOffset',
                                'headerCompression rohc', 'gapOffset', 'mgl ms', 'mgrp ms', 'mgta ms', 'gapUE release', 'drb-Identity',
                                'NR5G NAS SM5G Plain OTA Incoming Msg  --  PDU session modification command', 'Create new QoS rule',
                                'NR5G NAS SM5G Plain OTA Outgoing Msg  --  PDU session modification complete', 'Modifying existing EPS bearer',
                                'IMS_SIP_INVITE/SESSION_PROGRESS', 'IMS_SIP_PRACK/INFORMAL_RESPONSE', 'IMS_SIP_PRACK/OK', 'IMS_SIP_UPDATE/INFORMAL_RESPONSE',
                                'IMS_SIP_UPDATE/OK', 'P-Early-Media', 'IMS_SIP_INVITE/RINGING', 'IMS_SIP_INVITE/OK', 'IMS_SIP_ACK/INFORMAL_RESPONSE', 
                                'IMS_SIP_BYE/INFORMAL_RESPONSE', 'IMS_SIP_BYE/OK', 'drb-ToReleaseList', 'Delete existing QoS rule', 'DL_DCCH / RRC Release']

'''filter_mask[LOG_FILTER] = [0xB883, 0xB885, 0xB8AE]
filter_mask[EVENT_FILTER] = []
filter_mask[KEYWORDS_FILTER] = ['UL_0_1', 'UL_SKIP_FEATURE', '|                      ACK_NACK_RPT| TRUE|']'''

'''filter_mask[LOG_FILTER] = [0xB885, 0xB886, 0xB887]
filter_mask[EVENT_FILTER] = []
filter_mask[F3S_NON_REGEX] = ['DIAG MARK CMD']
filter_mask[KEYWORDS_FILTER] = ['Start HTTP_START', 'ACT SCELL', 'SCELL DEACT', '|      1|        C_RNTI|        DL_1_1|', 'Finish HTTP_START']'''

searchKeywords = PostProcessingUtils()
searchKeywords.getArgv(sys.argv)
searchKeywords.scanWorkingDir()
if not searchKeywords.skipFitlerLogs():
    searchKeywords.convertToText('FindKW')
searchKeywords.scanWorkingDir('_flt_text.txt', 'FindKW')
searchKeywords.initLogPacketList()
searchKeywords.findKeywords()