from PostProcessingUtils import PostProcessingUtils
from FilterMask import *
from datetime import datetime
import sys
import pandas as pd
import os

extract_data_stall_db = PostProcessingUtils()
extract_data_stall_db.getArgv(sys.argv)
extract_data_stall_db.scanWorkingDir()
extract_data_stall_db.exportAnalyzer('_Data_Stall_db.xlsm')
extract_data_stall_db.scanWorkingDir('.xlsm', '_Data_Stall_db')
all_grid = extract_data_stall_db.getFilesPath()

df_data_stall_db_lte = pd.DataFrame({'Time': [], 'UL_ARFCN': [], 'UL_PCI': [], 'UL_Band': [], 'UL_PS Penalty': [], 'UL_PS Penalty time left (s)': [], 
                                     'DL_ARFCN': [], 'DL_PCI': [], 'DL_Band': [], 'DL_PS Penalty': [], 'DL_PS Penalty time left (s)': [],
                                     'Log Name': []})

df_data_stall_db_nr = pd.DataFrame({'Time': [], 'UL_ARFCN': [], 'UL_PCI': [], 'UL_Band': [], 'UL_PS Penalty': [], 'UL_PS Penalty time left (ms)': [],
                                     'DL_ARFCN': [], 'DL_PCI': [], 'DL_Band': [], 'DL_PS Penalty': [], 'DL_PS Penalty time left (ms)': [],
                                     'Log Name': []})

for file in all_grid:
    try:
        df_data_stall_lte = pd.read_excel(file, sheet_name='0xB367_LTE_Data_Stall_db', header=4, index_col=0, engine='openpyxl').reset_index(drop=True)
        df_data_stall_lte['Log Name'] = (os.path.split(file)[1]).replace('.xlsm', '')
        df_data_stall_db_lte = pd.concat([df_data_stall_db_lte, df_data_stall_lte])
        df_data_stall_db_lte = df_data_stall_db_lte.sort_values(by='Time')
    except:
        pass

    try:
        df_data_stall_nr = pd.read_excel(file, sheet_name='0xB9AC_NR_Data_Stall_db', header=4, index_col=0, engine='openpyxl').reset_index(drop=True)
        df_data_stall_nr['Log Name'] = (os.path.split(file)[1]).replace('.xlsm', '')
        df_data_stall_db_nr = pd.concat([df_data_stall_db_nr, df_data_stall_nr])
        df_data_stall_db_nr = df_data_stall_db_nr.sort_values(by='Time')
    except:
        pass
    
dt_string = datetime.now().strftime('%Y%m%d_%H%M%S')
saveFileName = 'Data_Stall_db_All_Logs_' + dt_string + '.xlsx'
savePath = os.path.join(extract_data_stall_db.workingDir, saveFileName)
with pd.ExcelWriter(savePath, engine='xlsxwriter') as writer:
    df_data_stall_db_nr.to_excel(writer, sheet_name = 'NR_Data_Stall_db', index = False)
    df_data_stall_db_lte.to_excel(writer, sheet_name = 'LTE_Data_Stall_db', index = False)