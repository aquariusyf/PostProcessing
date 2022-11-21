from PostProcessingUtils import PostProcessingUtils
import sys

searchKeywords = PostProcessingUtils()
searchKeywords.getArgv(sys.argv)
searchKeywords.scanWorkingDir()
searchKeywords.convertToText()
searchKeywords.scanWorkingDir('_flt_text.txt')
searchKeywords.initLogPacketList()
searchKeywords.findKeywords()