from PostProcessingUtils import PostProcessingUtils
import sys

exportAnalyzer = PostProcessingUtils()
exportAnalyzer.getArgv(sys.argv)
exportAnalyzer.scanWorkingDir()
exportAnalyzer.exportAnalyzer()