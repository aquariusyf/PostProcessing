from PostProcessingUtils import PostProcessingUtils
from FilterMask import *
import sys

# RRC Setup/RACH delay/HO Delay breakdown
'''filter_mask[LOG_FILTER] = [0xB821]
filter_mask[EVENT_FILTER] = [3188, 3190, 3393]
filter_mask[QTRACE_NON_REGEX] = ['rach_setup_msg1_tx', 'Got DL_RAR_RESULT_INDI', 'rach_rar_state_handler', 'send MAC_RACH_ACTIVITY_IND rach_status',
                                 'Meas_Eval: VMR Cell Entering', 'Meas rpt proc', 'Doing CHO eval after 0', 'Meas_Eval: Meas eval type',
                                 'Meas_Eval: Meas eval type', '5GSRCH_DTLD_CON: Meas_Eval: Meas id being evaluated is %d and corresponding  MO is %d[0:Inter, 1:Intra] BM ML Enable: %d Meas eval type - %d (0:Intra 1:Non-Intra 2:CHO), rpt_cfg is CHO - %dReporting config type - %d and Eval trig event- nr5g %d, EUTRAN %d']
filter_mask[KEYWORDS_FILTER] = ['rach_setup_msg1_tx', 'Got DL_RAR_RESULT_INDI', 'rach_rar_state_handler', 'send MAC_RACH_ACTIVITY_IND rach_status',
                                'RRC Setup Req', 'RRC Setup', 'RRCSetup Complete', 'RRC_RECONFIG', 'DL_DCCH / RRCReconfiguration', 'RRCConfiguration Complete',
                                'Meas_Eval: VMR Cell Entering', 'Meas rpt proc', 'Doing CHO eval after 0', 'Meas_Eval: Meas eval type - 2', 'Meas eval type -',
                                'Event  --  EVENT_NR5G_RRC_RADIO_LINK_FAILURE_STAT_V8', 'Event  --  EVENT_NR5G_RRC_HO_STARTED_V2',
                                'Event  --  EVENT_NR5G_RRC_HO_SUCCESS']'''
# Prescheduling FR                           
'''filter_mask[LOG_FILTER] = [0xB821]
filter_mask[EVENT_FILTER] = []
filter_mask[QTRACE_NON_REGEX] = ['presched']
filter_mask[KEYWORDS_FILTER] = ['init_state_int', 'presched_det_state_int', 'sr_sup_state_int', 'tmp_sr_trg_int', 'last_presched_slot update']'''

# General signallings
'''filter_mask[LOG_FILTER] = [0x156E, 0xB821, 0xB80B, 0xB80A, 0xB80B, 0xB800, 0xB801, 0x1830, 0x1831]
filter_mask[EVENT_FILTER] = []
filter_mask[KEYWORDS_FILTER] = ['NR5G NAS MM5G Plain OTA Outgoing Msg  --  Registration request', 'NR5G NAS MM5G Plain OTA Incoming Msg  --  Authentication req', '5gs_reg_type',
                                'NR5G NAS MM5G Plain OTA Outgoing Msg  --  Authentication resp', 'NR5G NAS MM5G Plain OTA Incoming Msg  --  Security mode command',
                                'NR5G NAS MM5G Plain OTA Outgoing Msg  --  Security mode complete', 'NR5G NAS MM5G Plain OTA Incoming Msg  --  Registration accept', 'emf =', 'emc =',
                                'NR5G NAS MM5G Plain OTA Outgoing Msg  --  Registration complete', 'NR5G NAS SM5G Plain OTA Outgoing Msg  --  PDU session establishment req',
                                'dnn_val', 'NR5G NAS SM5G Plain OTA Incoming Msg  --  PDU session establishment accept', 'freqBandIndicatorNR', 'subcarrierSpacing', 'carrierBandwidth',
                                'inOneGroup', 'dl-UL-TransmissionPeriodicity', 'nrofDownlinkSlots', 'nrofDownlinkSymbols', 'nrofUplinkSlots', 'nrofUplinkSymbols', 'trs-Info',
                                'IMS_SIP_REGISTER/INFORMAL_RESPONSE', 'IMS_SIP_REGISTER/UNAUTHORIZED', 'IMS_SIP_REGISTER/OK', 'IMS_SIP_INVITE/INFORMAL_RESPONSE',
                                'NR5G NAS MM5G Plain OTA Outgoing Msg  --  Service request', 'establishmentCause', 'BCCH_BCH / Mib', 'BCCH_DL_SCH / SystemInformationBlockType1', 'sib2', 'sib3', 'sib4', 'sib5',
                                'UL_CCCH / RRC Setup Req', 'DL_CCCH / RRC Setup', 'srb-Identity 1', 'UL_DCCH / RRCSetup Complete', 'DL_DCCH / securityModeCommand', 
                                'UL_DCCH / SecurityMode Complete', 'DL_DCCH / UeCapabilityEnquiry', 'UL_DCCH / UeCapabilityInformation', 'DL_DCCH / RRCReconfiguration',
                                'srb-Identity 2', 'rlc-Config am', 'UL_DCCH / RRCConfiguration Complete', 'NR5G NAS MM5G Plain OTA Incoming Msg  --  Service accept',
                                'measIdToAddModList', 'UL_DCCH / MeasurementReport', 'drx-Config release', 'Physical Cell ID =', 'Freq =', 'eventId', 'defaultPagingCycle',
                                'IMS_SIP_INVITE/TRYING', 'drb-ToAddModList', 'rlc-Config um', 'drx-onDurationTimer', 'drx-InactivityTimer', 'drx-LongCycleStartOffset',
                                'headerCompression rohc', 'gapOffset', 'mgl ms', 'mgrp ms', 'mgta ms', 'gapUE release', 'drb-Identity',
                                'NR5G NAS SM5G Plain OTA Incoming Msg  --  PDU session modification command', 'Create new QoS rule', 'NR5G RRC OTA Packet  --  PCCH / Paging',
                                'NR5G NAS SM5G Plain OTA Outgoing Msg  --  PDU session modification complete', 'Modifying existing EPS bearer',
                                'IMS_SIP_INVITE/SESSION_PROGRESS', 'IMS_SIP_PRACK/INFORMAL_RESPONSE', 'IMS_SIP_PRACK/OK', 'IMS_SIP_UPDATE/INFORMAL_RESPONSE',
                                'IMS_SIP_UPDATE/OK', 'P-Early-Media', 'IMS_SIP_INVITE/RINGING', 'IMS_SIP_INVITE/OK', 'IMS_SIP_ACK/INFORMAL_RESPONSE', 
                                'IMS_SIP_BYE/INFORMAL_RESPONSE', 'IMS_SIP_BYE/OK', 'drb-ToReleaseList', 'Delete existing QoS rule', 'DL_DCCH / RRC Release',
                                'NR5G NAS SM5G Plain OTA Outgoing Msg  --  PDU session release req', 'NR5G NAS SM5G Plain OTA Incoming Msg  --  PDU session release command',
                                'NR5G NAS SM5G Plain OTA Outgoing Msg  --  PDU session release complete', 'NR5G NAS MM5G Plain OTA Outgoing Msg  --  Deregistration request']'''

# Skip uplink FR
'''filter_mask[LOG_FILTER] = [0xB883, 0xB885, 0xB8AE]
filter_mask[EVENT_FILTER] = []
filter_mask[KEYWORDS_FILTER] = ['UL_0_1', 'UL_SKIP_FEATURE', '|                      ACK_NACK_RPT| TRUE|']'''

# SCC act/deact delay
'''filter_mask[LOG_FILTER] = [0xB885, 0xB886, 0xB887]
filter_mask[EVENT_FILTER] = []
filter_mask[F3S_NON_REGEX] = ['DIAG MARK CMD']
# filter_mask[KEYWORDS_FILTER] = ['Start HTTP_START', 'ACT SCELL', 'SCELL DEACT', '|      1|        C_RNTI|        DL_1_1|', 'Finish HTTP_START']
filter_mask[KEYWORDS_FILTER] = ['Start HTTP_START', 'Finish HTTP_START', 'ACT SCELL', 'SCELL DEACT']'''

# SNS Speedup dedug 
'''filter_mask[LOG_FILTER] = [0xB821, 0xB0C0, 0xB0EC, 0xB0ED, 0xB80B, 0xB80A]
filter_mask[EVENT_FILTER] = [3269, 3389, 3251, 3294, 1890, 1612, 2201, 3250]
filter_mask[F3S_NON_REGEX] = []
filter_mask[QTRACE_NON_REGEX] = ['trigger speedup opt, rsrp %d, jumping timestamp %d current time %d',
                                 'detected rsrp jumping, trigger speedup opt in conn',
                                 'detected rsrp jumping, trigger speedup opt in idle',
                                 'MM_CM_BEARER_CTXT_TRANSFER_IND, source rat %d, current rat %d',
                                 'overall call status %d, nas registration status %d emergency mode %d, in elevator status %d, nr rat deprio %d n2l force resel %d, hst mode %d, dsda %d,MPLMN is ongoing %d, suspend opt %d',
                                 'received NR5G_RRC_SERVING_CELL_INFO_IND, status %d, current time 0x%x%0x',
                                 'send LTE_CPHY_FAST_TO_NR_OPT_START_IND',
                                 'L2NR garage opti timer started for %d, opti status(1-elevator mode, 2-l2nr selection opti, 3-garage mode) %d, op mode %d',
                                 'ignore opt start. efs enabled %d protection %d, garage mode %d, force n2l resel %d HST %d call %d emc %d NR coverage %d',
                                 'set nr rat deprio %d',
                                 'skip this layer %d due to nr layer deprio in garage mode',
                                 'Send cafi mode reg req, ret %d, mode %d',
                                 'Send cafi mode de-reg req, ret %d, mode %d',
                                 'UTILS_CAFI_MODE_REG_CNF received, status %d',
                                 'UTILS_CAFI_MODE_IND received, action %d next state %d',
                                 'finish garage activity, next state %d',
                                 'L2NR srch opti timer expired',
                                 'l2nr_resel_to_higher_rsrp freq %d scs %d band %d pci %d',
                                 'l2nr_resel_to_higher_rsrp, serv rsrp %d, nbr(Freq%d,PCI%d) rsrp %d  thresh rsrp %d, bias %d, check pass %d, counter %d',
                                 'IRAT_NR5G - mode 0x%x, hst_mode %d, freq %d, srch_per %d, meas_per %d, num_layers %d, num_hst_layers %d',
                                 'Freq : %d, num cells detected : %d, db cells %d',
                                 'Resel Eval Freq %d Prio %d.%d Thresh_X %d MOB %d NW configured Tresel %d Ignore Tresel %d elevator mode %d num cells %d',
                                 'Cell id %d resel metric %d Srxlev %d Squal %d Tresel %d apply_level2(%d -> %d)',
                                 'drx_cycle %d arfcn %d srch_poss %d last_srch %d meas_poss %d last_meas %d SMTC2 Cells Config %d',
                                 'curr_tresel_timer_value %d resel configured %d',
                                 'Meas Results PCI %d RSRP [Q7] %d RSRQ [Q7] %d SINR [Q16] %d, db_index %d l2nr_te_offset %d frame_offset %d half_frame_index %d ssbs_span %d gap_start %d gap_end %d cell status %d',
                                 'Triggering ML1 CELL RESEL, rat %d freq %d id %d']
filter_mask[KEYWORDS_FILTER] = ['trigger speedup opt', 'detected rsrp jumping', 'MM_CM_BEARER_CTXT_TRANSFER_IND', 'received NR5G_RRC_SERVING_CELL_INFO_IND',
                                'L2NR garage opti timer started', 'ignore opt start. efs enabled', 'set nr rat deprio', 'skip this layer',
                                'Send cafi mode reg req', 'Send cafi mode de-reg req', 'UTILS_CAFI_MODE_REG_CNF received', 'UTILS_CAFI_MODE_IND received',
                                'finish garage activity', 'L2NR srch opti timer expired', 'l2nr_resel_to_higher_rsrp', 'overall call status',
                                'srch_per', 'L2NR: Freq : ', 'IRAT_NR5G: Resel Eval Freq', 'IRAT_NR5G: Cell id', 'IRAT_NR5G: drx_cycle',
                                'curr_tresel_timer_value', 'L2NR : Meas Results PCI', 'Triggering ML1 CELL RESEL',
                                'EVENT_NR5G_RRC_CELL_RESEL_STARTED', 'EVENT_ENHANCED_LTE_RRC_NEW_CELL_IND', 'EVENT_LTE_RRC_CELL_RESEL_FAILURE',
                                'EVENT_NR5G_RRC_IRAT_RESEL_FROM_NR_START', 'EVENT_NR5G_RRC_IRAT_RESEL_FROM_NR_END_V3',
                                'EVENT_NR5G_RRC_NEW_CELL_IND_V3', 
                                'EVENT_LTE_RRC_IRAT_RESEL_FROM_EUTRAN_START_EXT_EARFCN', 'EVENT_LTE_RRC_IRAT_RESEL_FROM_EUTRAN_END',
                                'Physical Cell Id =', 'Physical Cell ID =', 'Freq =',
                                'LTE RRC OTA Packet  --  UL_CCCH / RRCConnectionRequest',
                                'LTE RRC OTA Packet  --  DL_CCCH / RRCConnectionSetup',
                                'LTE RRC OTA Packet  --  UL_DCCH / RRCConnectionSetupComplete',
                                'LTE RRC OTA Packet  --  DL_DCCH / RRCConnectionRelease',
                                'LTE NAS EMM Plain OTA Outgoing Message  --  Tracking area update request Msg',
                                'LTE NAS EMM Plain OTA Incoming Message  --  Tracking area update accept Msg',
                                'LTE NAS EMM Plain OTA Outgoing Message  --  Tracking area update complete Msg',
                                'NR5G RRC OTA Packet  --  UL_CCCH / RRC Setup Req',
                                'NR5G RRC OTA Packet  --  DL_CCCH / RRC Setup',
                                'NR5G RRC OTA Packet  --  UL_DCCH / RRCSetup Complete',
                                'NR5G NAS MM5G Plain OTA Outgoing Msg  --  Registration request',
                                'NR5G NAS MM5G Plain OTA Incoming Msg  --  Registration accept',
                                'NR5G NAS MM5G Plain OTA Outgoing Msg  --  Registration complete',
                                'NR5G RRC OTA Packet  --  DL_DCCH / RRC Release']'''

# Bad TAI/DSDA
'''filter_mask[LOG_FILTER] = [0x156E, 0xB821, 0xB80B, 0xB80A, 0xB80B, 0xB800, 0xB801, 0x1830, 0x1831, 0xB885]
filter_mask[EVENT_FILTER] = [3188, 3190, 3325, 3368, 3393]
filter_mask[F3S_NON_REGEX] = []
filter_mask[QTRACE_NON_REGEX] = ['MIMO Bad TAI list DB', 'RRCCAP_DSDA', 'NR5GMAC_QSH_EVENT_TAI_UPD_TYPE', 'nr5g_macctrl_update_on_dsda_entry', 'nr5g_macctrl_update_on_dsda_exit', 
                                 'METRIC_INT_CMD | ADD_REQ | C:%d M:%d', 'METRIC_INT_CMD | DEL_REQ | C:%d M:%d', 'HYBRID_DSDA: hybrid_dsda %d, dsda_allowance %d (sub mode %d, TX concur %d)',
                                 'HYBRID_DSDA: DSDA_ALLOWANCE: %d->%d, reason 0x%x -> 0x%x, severity %d -> %d', 'MIMO Rank mismatch detected- Add TAI entry to MIMO Bad FTAI list',
                                 'no rank mismatch found- TAI removed from MIMO Bad FTAI list', 'HYBRID_DSDA: Report DSDA<> DSDS fallback mask to PM, old 0x%x, new 0x%x',
                                 'MM:DS: SUB %d =MM5G= MIMO Bad TAI List DB  PLMN (%u - %u) TAC = (0x%x 0x%x 0x%x) rlf_counter = (%d) is_voted_bad_tai = (%d) timer_count = (%u)',
                                 'BAD_TAI_METRIC | EFS_GET | winLenMs:[short: %d; long: %d]; minGrant#: %d; mimoCriteria: %d',
                                 'BAD_TAI_METRIC | time_elapsed: %d | short_win_grants[ul: %d | smdl: %d] | long_win_grants[ul: %d | smdl: %d]',
                                 'BAD_TAI_METRIC | start idx[short: %d | long: %d] | num_ul_grants:[short: %d | long: %d] | num_smdl_grants:[short: %d | long: %d]',
                                 'Initiating RRC conn release, rel_reason is NR5G_RRC_CONN_REL_LOCAL.']
filter_mask[KEYWORDS_FILTER] = ['MIMO Bad TAI list DB', 'current_ul_mimo_dwg_status', 'NR5GMAC_QSH_EVENT_TAI_UPD_TYPE', 'adv_srs_as_fallback', 'ADD_REQ', 'DEL_REQ',
                                'nr5g_macctrl_update_on_dsda_entry', 'nr5g_macctrl_update_on_dsda_exit', 'UL MIMO disabled due to DSDA entry', 'Disabling UL MIMO for DSDA entry',
                                'Removing mimo limits on DSDA exit', 'UL MIMO already disabled', 'dsda_allowance 0', 'dsda_allowance 1', 'HYBRID_DSDA: DSDA_ALLOWANCE: 0->1',
                                'Report DSDA<> DSDS fallback mask to PM', 'time_elapsed', 'num_ul_grants', 'num_smdl_grants', 'EFS_GET | winLenMs', 'rlf_counter =',
                                'Initiating RRC conn release, rel_reason is NR5G_RRC_CONN_REL_LOCAL.',
                                'HYBRID_DSDA: DSDA_ALLOWANCE: 1->0', 'Add TAI entry to MIMO Bad FTAI list', 'TAI removed from MIMO Bad FTAI list',
                                'IMS_SIP_REGISTER/INFORMAL_RESPONSE', 'IMS_SIP_REGISTER/UNAUTHORIZED', 'IMS_SIP_REGISTER/OK',
                                'NR5G RRC OTA Packet  --  UL_CCCH / RRC Setup Req',
                                'NR5G RRC OTA Packet  --  DL_CCCH / RRC Setup',
                                'NR5G RRC OTA Packet  --  UL_DCCH / RRCSetup Complete',
                                'NR5G NAS MM5G Plain OTA Outgoing Msg  --  Registration request',
                                'NR5G NAS MM5G Plain OTA Incoming Msg  --  Registration accept',
                                'NR5G NAS MM5G Plain OTA Outgoing Msg  --  Registration complete',
                                'UL_DCCH / UeCapabilityInformation', 'DL_DCCH / UeCapabilityEnquiry',
                                'IMS_SIP_INVITE/INFORMAL_RESPONSE', 'IMS_SIP_INVITE/TRYING',
                                'NR5G NAS SM5G Plain OTA Incoming Msg  --  PDU session modification command', 'Create new QoS rule',
                                'NR5G NAS SM5G Plain OTA Outgoing Msg  --  PDU session modification complete', 'Modifying existing EPS bearer',
                                'IMS_SIP_INVITE/SESSION_PROGRESS', 'IMS_SIP_PRACK/INFORMAL_RESPONSE', 'IMS_SIP_PRACK/OK', 'IMS_SIP_UPDATE/INFORMAL_RESPONSE',
                                'IMS_SIP_UPDATE/OK', 'P-Early-Media', 'IMS_SIP_INVITE/RINGING', 'IMS_SIP_INVITE/OK', 'IMS_SIP_ACK/INFORMAL_RESPONSE',
                                'IMS_SIP_BYE/INFORMAL_RESPONSE', 'IMS_SIP_BYE/OK',
                                'NR5G NAS SM5G Plain OTA Outgoing Msg  --  PDU session release req', 'NR5G NAS SM5G Plain OTA Incoming Msg  --  PDU session release command',
                                'NR5G RRC OTA Packet  --  DL_DCCH / RRC Release',
                                'Event  --  EVENT_NR5G_RRC_RADIO_LINK_FAILURE_STAT_V7',
                                'Event  --  EVENT_NR5G_RRC_RADIO_LINK_FAILURE_STAT_V8']'''
# Early RLF
filter_mask[LOG_FILTER] = [0xB821, 0x3310]
filter_mask[EVENT_FILTER] = [3188, 3190, 3325, 3368, 3393]
filter_mask[QTRACE_NON_REGEX] = ['RLM[%d]: sync_state %d, out_sync_count %d, n310 %d',
                                 'RLM[%d]: Start T310 Timer for %d ms',
                                 'RLM_EARLY_T310[%d]: REG CNF status %d, pred_enabled %d, mtg_enabled %d, rlm_id %d',
                                 'RLM_EARLY_T310[%d]: Feeding Sample: timer_status %d , snr %d, api processing time %d us',
                                 'RLM_EARLY_T310[%d]: Triggering inference',
                                 'RLM_EARLY_T310[%d]: Start feeding samples to ML SW',
                                 'RLM_EARLY_T310[%d]: Stop feeding samples to ML SW',
                                 'RLM_EARLY_T310[%d]: STAGE3 MTG cb received, restart MTG timer for %d ms',
                                 'Rcvd T310_TRIG_PRED: t310_rlm_id:%d',
                                 'sub_id:%d cell_id:%d ca_id:%d pred_res:%d[1:STOP, 2:EXPIRY] pred_value(*1000000):%d',
                                 't310_rlm_id:%d, pred_res:%d',
                                 'RLM_EARLY_T310[%d]: Prediction Result %d [1:STOP, 2:EXPIRE]',
                                 'RLM_EARLY_T310[%d]: Sending SRCH MTG_STAGE_IND for STAGE%d',
                                 'RLM[%d]: T310 Expired. Send (v)RLF Indication',
                                 '5GSRCH_BRIEF_GMS: T310 timer status %d (0: stop/expire, 1: start)',
                                 'qvp_rtp_add_rr num_lost = %d and tot_lost = %d',
                                 'Early_RLF: early rlf enabled, best intra cell exist %d, serv_cell_is_poor %d, best_intra_cell_result %d, best_intra_cell_snr %d, srv_cell_result_rsrp %d, srv_cell_result_snr %d, a3_early_rlf_timestamp %08x%08x',
                                 'Early_RLF: early rlf timer expired and best neighor intra cell is not barred, trigger early rlf',
                                 'Sending CPHY_RL_FAILURE_IND from 0x%x for reason %d',
                                 'Invalid reg req, ret_val:%d, subid:%d, cell_grp:%d, ca_id:%d, purpose:%d',
                                 'Rcvd STARTED for t310_rlm_id:%d pred_done:%d, sample_cnt:%d timer_status_actual:%d, Resetting...',
                                 'RLM[%d]: RRC RLM parameters, T310:%d, N310:%d, N311:%d, threshold %d, bwp_id:%d, bfd_max %d, bfd_timer %d, num_rx %d, enable_mask 0x%x']
filter_mask[KEYWORDS_FILTER] = ['pred_enabled 1', 'mtg_enabled 1',
                                'Event  --  EVENT_NR5G_RRC_RADIO_LINK_FAILURE_STAT_V8', 'Event  --  EVENT_NR5G_RRC_RADIO_LINK_FAILURE_STAT_V7',
                                'Cause =', 'Cause = RLF', 'Cause = EARLY_RLF', 'Cause = RACH_PROBLEM', 'Cause = HO_FAILURE', 'Cause = MAX_RETRX',
                                '5GSRCH_BRIEF_GMS: T310 timer status', 'Start T310 Timer for', 't310_rlm_id:', 'sync_state 1', 'Rcvd STARTED for t310_rlm_id', 'RRC RLM parameters',
                                'T310 Expired. Send (v)RLF Indication', 'Sending CPHY_RL_FAILURE_IND from', 'qvp_rtp_add_rr num_lost =', 'Rcvd T310_TRIG_PRED: t310_rlm_id:', 
                                'Sending SRCH MTG_STAGE_IND for STAGE',
                                'Start feeding samples to ML SW',
                                'Feeding Sample: timer_status', 
                                'Triggering inference', 
                                'Stop feeding samples to ML SW',
                                'pred_value(*1000000):', 
                                'Prediction Result',
                                'Predicted Timer Status =', 'Actual Timer Status =', 'Mitigation Type =', 'Sample collection time =', 'Model execution time =', 'Start to Mitigation duration =', 'Prediction to Mitigation duration =',
                                'Prediction threshold =', 'Prediction value =',
                                'restart MTG timer for',
                                'Event  --  EVENT_NR5G_RRC_HO_STARTED_V2', 'Event  --  EVENT_NR5G_RRC_HO_SUCCESS',
                                'Early_RLF: early rlf enabled, best intra cell exist', 
                                'early rlf timer expired', 'trigger early rlf',
                                'RRC Reestablishment Req', 'RRCReestablishment Complete', 'Freq =', 'Physical Cell ID =',
                                'DL_DCCH / RRCReconfiguration', 'UL_DCCH / RRCConfiguration Complete', 'DL_DCCH / RRC Release']

searchKeywords = PostProcessingUtils()
searchKeywords.getArgv(sys.argv)
searchKeywords.scanWorkingDir()
if not searchKeywords.skipFitlerLogs():
    searchKeywords.convertToText('FindKW')
searchKeywords.scanWorkingDir('_flt_text.txt', 'FindKW')
searchKeywords.initLogPacketList()
searchKeywords.findKeywords()