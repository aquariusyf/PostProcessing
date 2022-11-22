from PostProcessingUtils import PostProcessingUtils
from FilterMask import *
import sys

'''filter_mask[ANALYZER_FILTER] = [';NR5G;Summary;PDSCH;NR5G PDSCH Statistics', 
                ';NR5G;Summary;UCI;CSF;NR5G CQI Summary', 
                ';NR5G;Summary;NR5G Doppler and Delay Spread Bin Summary', 
                ';NR5G;Summary;MEAS;NR5G Cell Meas Summary V2', 
                ';NR5G;Summary;SNR;NR5G Sub6 SNR Summary',
                ';Common Displays;GPS Info;GPS Source and Speed vs. Pos Data', 
                ';NR5G;Time Grid;SRS;NR5G SRS Sched Grid']'''

'''filter_mask[ANALYZER_FILTER] = [';Common Displays;GPS Info;GPS Source and Speed vs. Pos Data',
                ';NR5G;Summary;NR5G Doppler and Delay Spread Bin Summary',
                ';NR5G;Time Grid;SRS;NR5G SRS Sched Grid']'''

filter_mask[ANALYZER_FILTER] = [';Common Displays;VoIP Analysis;VONR MO Call Setup Summary',
                                ';Common Displays;VoIP Analysis;VONR MT Call Setup Summary']

exportAnalyzer = PostProcessingUtils()
exportAnalyzer.getArgv(sys.argv)
exportAnalyzer.scanWorkingDir()
exportAnalyzer.exportAnalyzer()