from PostProcessingUtils import PostProcessingUtils
import sys

mergeLog = PostProcessingUtils()
mergeLog.getArgv(sys.argv)
mergeLog.scanWorkingDir()
mergeLog.convertToText()