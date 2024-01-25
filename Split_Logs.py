from PostProcessingUtils import PostProcessingUtils
import sys

splitLog = PostProcessingUtils()
splitLog.getArgv(sys.argv)
splitLog.scanWorkingDir() # Put file ext to merge, default is .hdf

# Due to timestamp of F3/Qtrace sometimes not aligned with log pkt and event pkt, better to remove F3/Qtrace before split to avoid error
splitLog.fitlerLog('fltLog', True)
splitLog.scanWorkingDir()
splitLog.splitLog(4)