from PostProcessingUtils import PostProcessingUtils
from FilterMask import *
import sys

filter_mask[LOG_FILTER] = [0xB821, 0x1568, 0x1569, 0x156A, 0x156C, 0xB800, 0xB801, 0xB808, 
                           0xB809, 0xB80A, 0xB80B, 0xB814, 0x1CD0, 0xB886]

filter_mask[KEYWORDS_FILTER] = ['MCE Bitmask = REC_BR_MCE',
                                'direction =',
                                'bit_rate_index =']

searchKeywords = PostProcessingUtils()
searchKeywords.getArgv(sys.argv)
searchKeywords.scanWorkingDir()
searchKeywords.convertToText()
searchKeywords.scanWorkingDir('_flt_text.txt')
searchKeywords.initLogPacketList()
searchKeywords.findKeywords()