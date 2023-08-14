# PostProcessing
* 11/18/2022: Repo created!
* Usage: Field test logs post processing and utility scripts

# Introductions
* Command line: python [script_name] [log_location] [additional_command]
* Additional command (Can be multiple entries in any order separate by space):
  1. Log code (e.g. 0xB887) - specify any log code to overwrite default filter mask
  2. Event code (e.g. 3190) - specify any event code to overwrite default filter mask
  3. Qtrace - enable qtrace/F3 filtering
  4. Sub ID (e.g. sub2) - specify sub ID for post processing
  5. -sf - skip filtering logs (.hdf to text)

# Script Utility
* PostProcessingUtils.py - Master/Helper classes
* FilterMask.py - Filters of log packets, events, Qtrace, F3s, Keywords and APEX build-in analyzers
* Merge_Logs.py - Merge .hdf logs files in given path
* Merge_QDSS.py - Merge .qdss logs files in each folder/sub-folder of given path, and save as .hdf
* ExportDefaultAnalyzer.py - Export APEX build-in analyzers from logs in given path to excel
* Export_Grid.py - Export APEX custom grids from logs in given path (grid file need to be placed in same path) to excel
* Extract_CSD.py - Extract APEX build-in VONR call setup delay summary from logs in given path to excel
* IMS_Media_KPI.py - Extract IMS media and N2N PSHO KPIs from logs in given path to excel
* VONR_to_VOLTE_IRAT_KPI.py - Extract VONR to VOLTE IRAT KPIs from logs in given path to excel
* Visual_IMS_Media.py - Plot VONR talk spurt, pkt loss, HO and PHY layer NewTx/ReTx from MO and MT logs (2 logs in pair) in given path
* RF_Profile_Histograms.py - Plot RSRP and SNR in histograms and timeline, extract total number of HO and number of unique PCIs from logs in given path
* FindKeywordsFromLog.py - Find and extract stats of keywords specified in filter mask from logs in given path
* GetLogPktCodeList.py - Get a list of log packet code captured in given log (Need input of logmask)
* N2N_Handover_Delay.py - Extract the N2N handover delays and signaling breakdowns
* Extract_RedundantTx_Ping_SimResult.py - Extract redundant Tx simulation ping result from sub1 and sub2 for ping++ping DSDA test case
* DSDA_UL_Precoding_Layers_Stats.py - Extract the stats of DDS sub precoding layers during DSDA state
