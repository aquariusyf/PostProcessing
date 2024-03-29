from PostProcessingUtils import PostProcessingUtils
from FilterMask import *
import sys

filter_mask[LOG_FILTER] = [0xB9BE, 0xB986, 0xB97E, 0xB96A, 0xB956, 0xB952, 0xB8E2, 0xB8DE, 0xB8D2, 0xB8CE, 0xB8AE, 0xB8A6, 0xB896, 0xB88A, 0xB886, 0xB882, 0xB872, 0xB856,
                           0xB84E, 0xB862, 0xB842, 0xB82A, 0xB826, 0xB822, 0xB1EA, 0x1C9E, 0x1CA6, 0x1852, 0x1C6E, 0x1C72, 0x1CE2, 0x1C8E, 0x1476, 0xB066, 0xB082, 0xB092,
                           0xB0B2, 0xB126, 0xB132, 0xB14E, 0xB9B9, 0xB989, 0xB979, 0xB96D, 0xB969, 0xB965, 0xB959, 0xB955, 0xB8E5, 0xB8E1, 0xB8DD, 0xB8D1, 0xB8CD, 0xB89D,
                           0xB88D, 0xB889, 0xB885, 0xB881, 0xB875, 0xB871, 0xB869, 0xB84D, 0xB861, 0xB841, 0xB825, 0xB821, 0xB30D, 0xB195, 0xB16D, 0x1C9D, 0x156D, 0x1CA5,
                           0x1851, 0x1C71, 0x1951, 0x1391, 0x1849, 0xB081, 0xB091, 0xB0A5, 0xB139, 0xB14D, 0xB9C0, 0xB9A8, 0xB990, 0xB988, 0xB97C, 0xB974, 0xB96C, 0xB968,
                           0xB960, 0xB950, 0xB8C4, 0xB8C0, 0xB8A4, 0xB89C, 0xB890, 0xB88C, 0xB888, 0xB870, 0xB86C, 0xB868, 0xB864, 0xB860, 0xB844, 0xB840, 0xB824, 0xB1D8,
                           0xB198, 0x156C, 0x1CD0, 0x1CA4, 0x1980, 0x1850, 0x1854, 0x1C70, 0x19B8, 0xB060, 0xB064, 0xB0A4, 0xB0A8, 0xB0B0, 0xB0B4, 0xB0C0, 0xB134, 0xB13C,
                           0xB9BF, 0xB9A3, 0xB993, 0xB98F, 0xB987, 0xB977, 0xB96B, 0xB8E7, 0xB8D3, 0xB8A7, 0xB89B, 0xB897, 0xB88F, 0xB88B, 0xB887, 0xB883, 0xB873, 0xB857,
                           0xB84B, 0xB843, 0xB18F, 0xB173, 0xB14F, 0x1C9F, 0x1897, 0x156B, 0x1CA3, 0x1CA7, 0x1917, 0x1853, 0x1C6F, 0x1D0B, 0x19E3, 0x19EF, 0x1477, 0x1CD3,
                           0xB063, 0xB083, 0xB087, 0xB097, 0xB0B3, 0xB11B]

getLogPktCodeList = PostProcessingUtils()
getLogPktCodeList.getArgv(sys.argv)
getLogPktCodeList.scanWorkingDir()
if not getLogPktCodeList.skipFitlerLogs():
    getLogPktCodeList.convertToText('getLogPktCodeList')
getLogPktCodeList.scanWorkingDir('_flt_text.txt', 'getLogPktCodeList')
getLogPktCodeList.getLogPktCodeList()