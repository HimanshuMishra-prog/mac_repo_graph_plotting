from prometheus_client import Counter, Gauge , Histogram

LOGS_PROCESSED = Counter('dpp_logs_processed_total' , 'Total_logs_processed' , ['user', 'filename'])
DPP_BASIC_LOGS_PROCESSED = Counter('dpp_basic_logs_processed_total' , 'Total_dpp_basic_logs_processed', ['user', 'filename', 'sector_id'])
PB_BASIC_LOGS_PROCESSED = Counter('pb_basic_logs_processed_total' , 'Total_pb_basic_logs_processed' , ['user', 'filename','sector_id'])
URAC_RA_LOGS_PROCESSED = Counter('urac_ra_logs_processed_total' , 'Total_urac_logs_processed', ['user', 'filename', 'sector_id'])
UMRC_DP_LOGS_PROCESSED = Counter('umrc_dp_logs_processed_total' , 'Total_umrc_dp_logs_processed', ['user', 'filename', 'sector_id'])
ULCA_PHR_PWR_AL_LOGS_PROCESSED = Counter('ulca_phr_pwr_al_logs_processed_total' , 'Total_ulca_phr_pwr_al_logs_processed', ['user', 'filename', 'sector_id'])
SCELL_STATE_ULCA_LOGS_PROCESSED = Counter('scell_state_ulca_logs_processed_total' , 'Total_scell_state_ulca_logs_processed', ['user', 'filename', 'sector_id'])
PCELL_STATE_ULCA_LOGS_PROCESSED = Counter('pcell_state_ulca_logs_processed_total' , 'Total_pcell_state_ulca_logs_processed', ['user', 'filename', 'sector_id'])
PCELL_STATE_ACT_LOGS_PROCESSED = Counter('pcell_state_act_logs_processed_total' , 'Total_pcell_state_act_logs_processed', ['user', 'filename', 'sector_id'])
PCELL_STATE_CHANGE_LOGS_PROCESSED = Counter('pcell_state_change_logs_processed_total' , 'Total_pcell_state_change_logs_processed', ['user', 'filename', 'sector_id'])

TOTAL_CRC_FAILS = Counter('total_crc_fails', 'Total_crc_fails' , ['user', 'filename', 'sector_id'])

#FOR DPP BASIC
# CRC_GAUGE = Gauge('dpp_crc_value', 'crc value' , ['user', 'filename', 'sector_id' , 'ue_id'])
# MCS_GAUGE = Gauge('dpp_mcs_value', 'mcs value' , ['user', 'filename', 'sector_id' , 'ue_id'])
# PWR_GAUGE = Gauge('dpp_pwr_value', 'pwr value' , ['user', 'filename', 'sector_id' , 'ue_id'])
# ULCA_GAUGE = Gauge('dpp_ulca_value', 'ulca value' , ['user', 'filename', 'sector_id' , 'ue_id'])
# DTX_GAUGE = Gauge('dpp_dtx_value', 'dtx value' , ['user', 'filename', 'sector_id' , 'ue_id'])
# U_SIZE = Gauge('dpp_u_size_value', 'usize value' , ['user', 'filename', 'sector_id' , 'ue_id'])
# RB_COUNT = Gauge('dpp_rb_count' , 'rb_count' , ['user', 'filename', 'sector_id' , 'ue_id'])
# PCELL_CA_UE = Gauge('dpp_pcell_ca_ue' , 'status of pcell ca ue' , ['user', 'filename', 'sector_id' , 'ue_id'])
# CRC_HISTOGRAM = Histogram('dpp_crc_histogram' , 'CRC_distribution' , ['user', 'filename', 'sector_id'])


#FOR PB_BASIC
# P_CELL_STATE = Gauge('pb_cell_state', 'cell state' , ['user', 'filename', 'sector_id' , 'ue_id'])
# P_CELL_HISTOGRAM = Histogram('pcell_state_histogram' , 'Pcell_state_distribution' , ['user', 'filename', 'sector_id'])