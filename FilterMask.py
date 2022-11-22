# Filter name strings
LOG_FILTER = 'LOG_FILTER'
EVENT_FILTER = 'EVENT_FILTER'
QTRACE_NON_REGEX = 'QTRACE_NON_REGEX'
QTRACE_REGEX = 'QTRACE_REGEX'
F3S_NON_REGEX = 'F3S_NON_REGEX'
F3S_REGEX = 'F3S_REGEX'
KEYWORDS_FILTER = 'KEYWORDS_FILTER'
ANALYZER_FILTER = 'ANALYZER_FILTER'

# Log filter mask
filter_mask = {
    LOG_FILTER: [0xB821, 0x1568, 0x1569, 0x156A, 0x156C, 0xB800, 0xB801, 0xB808, 
                 0xB809, 0xB80A, 0xB80B, 0xB814, 0x1CD0],
    EVENT_FILTER: [3188, 3190],
    QTRACE_NON_REGEX: ['presched'],
    QTRACE_REGEX: [],
    F3S_NON_REGEX: [],
    F3S_REGEX: [],
    KEYWORDS_FILTER: ['init_state_int',
                      'presched_det_state_int',
                      'presched_grant_cnt 1',
                      'presched_grant_cnt 2',
                      'presched_grant_cnt 3',
                      'presched_grant_cnt 4',
                      'presched_grant_cnt 5',
                      'presched_grant_cnt 6',
                      'presched_grant_cnt 7',
                      'presched_grant_cnt 8',
                      'presched_grant_cnt 9',
                      'presched_grant_interval',
                      'sr_sup_state_int',       
                      'tmp_sr_trg_int'],
    ANALYZER_FILTER: [';NR5G;Summary;PDSCH;NR5G PDSCH Statistics', 
                      ';NR5G;Summary;UCI;CSF;NR5G CQI Summary', 
                      ';NR5G;Summary;NR5G Doppler and Delay Spread Bin Summary', 
                      ';NR5G;Summary;MEAS;NR5G Cell Meas Summary V2', 
                      ';NR5G;Summary;SNR;NR5G Sub6 SNR Summary']
}