from PostProcessingUtils import PostProcessingUtils
import sys

mergeLog = PostProcessingUtils()
mergeLog.getArgv(sys.argv)
mergeLog.scanWorkingDir('.qdss') # Put file ext to merge, default is .hdf
mergeLog.mergeLogs()