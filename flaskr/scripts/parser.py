# flaskr/parser.py
import re
import math
from flaskr.scripts.metrics import LOGS_PROCESSED,DPP_BASIC_LOGS_PROCESSED,ULCA_PHR_PWR_AL_LOGS_PROCESSED,UMRC_DP_LOGS_PROCESSED,URAC_RA_LOGS_PROCESSED,TOTAL_CRC_FAILS,SCELL_STATE_ULCA_LOGS_PROCESSED,PCELL_STATE_CHANGE_LOGS_PROCESSED,PCELL_STATE_ULCA_LOGS_PROCESSED,PCELL_STATE_ACT_LOGS_PROCESSED

def process_label(v):
    if v is None:
        return "unknown"
    s = str(v)
    return s.replace('"', '\\"').replace("\n", " ")

DPP_BASIC_4G_LINE_RE = re.compile(
    r"""
    ^\s*
    (?P<date>\d{6})\|(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+
    @(?P<slot>\d{1,3})\|(?P<id1>[0-9A-Fa-f]+)\|(?P<id2>\d+)\s+
    [^\>]*>\s*DPP_BASIC,
    (?P<csv_payload>.*?)
    (?:\s+\(|$)
    """,
    re.VERBOSE,
)

PB_BASIC_4G_LINE_RE = re.compile(
    r"""
    ^\s*
    (?P<date>\d{6})\|(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+
    @(?P<slot>\d{1,3})\|(?P<id1>[0-9A-Fa-f]+)\|(?P<id2>\d+)\s+
    [^\>]*>\s*PB_BASIC,
    (?P<csv_payload>.*?)
    (?:\s+\(|$)
    """,
    re.VERBOSE,
)

def safe_int(s):
    if s is None:
        return None
    s = str(s).strip()
    if s == "":
        return None
    try:
        return int(s)
    except Exception:
        try:
            return int(float(s))
        except Exception:
            return None

def safe_log10(value):
    if value is None:
        return None
    try:
        val = float(value)
        if val <= 0:
            return None
        return 10 * math.log10(val)
    except (ValueError, TypeError):
        return None

def parse_timestamp_str(date_str, time_str):
    return f"{date_str}|{time_str}"

def parse_4G_log_line(username, filename, raw_line, line_index, metadata_dict):
    LOGS_PROCESSED.labels(user = username, filename= filename).inc()
    dpp_basic = DPP_BASIC_4G_LINE_RE.match(raw_line)
    if dpp_basic:
        return process_dpp_basic_log(username, filename, dpp_basic, line_index , 0, metadata_dict)
    pb_basic = PB_BASIC_4G_LINE_RE.match(raw_line)
    if pb_basic:
        return process_pb_basic_log(username, filename, pb_basic, line_index , 1, metadata_dict)
    return None


URAC_RA_5G_LINE_RE = re.compile(
    r"""
    ^\s*
    (?P<date>\d{6})\|(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+
    @(?P<slot>\d{1,3})\|(?P<id1>[0-9A-Fa-f]+)\|(?P<id2>\d+)\s+
    [^\>]*>\s*URAC_RA,
    (?P<csv_payload>.*?)
    (?:\s+\(|$)
    """,
    re.VERBOSE,
)

UMRC_DP_5G_LINE_RE = re.compile(
    r"""
    ^\s*
    (?P<date>\d{6})\|(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+
    @(?P<slot>\d{1,3})\|(?P<id1>[0-9A-Fa-f]+)\|(?P<id2>\d+)\s+
    [^\>]*>\s*UMRC_DP,
    (?P<csv_payload>.*?)
    (?:\s+\(|$)
    """,
    re.VERBOSE,
)

ULCA_PHR_PWR_AL_5G_LINE_RE = re.compile(
    r"""
    ^\s*
    (?P<date>\d{6})\|(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+
    @(?P<slot>\d{1,3})\|(?P<id1>[0-9A-Fa-f]+)\|(?P<id2>\d+)\s+
    [^\>]*>\s*ULCA_PHR_PWR_AL,
    (?P<csv_payload>.*?)
    (?:\s+\(|$)
    """,
    re.VERBOSE,
)

def parse_5G_log_line(username, filename, raw_line, line_index, metadata_dict):
    LOGS_PROCESSED.labels(user = username, filename= filename).inc()
    urac_ac = URAC_RA_5G_LINE_RE.match(raw_line)
    if urac_ac:
        return process_urac_log(username, filename, urac_ac, line_index, 0, metadata_dict)
    umrc_dp = UMRC_DP_5G_LINE_RE.match(raw_line)
    if umrc_dp:
        return process_umrc_dp_log(username, filename, umrc_dp, line_index, 1, metadata_dict)
    ulca_dp = ULCA_PHR_PWR_AL_5G_LINE_RE.match(raw_line)
    if ulca_dp:
        return process_ulca_phr_pwr_al_log(username , filename , ulca_dp, line_index, 2, metadata_dict)
    return None

SCELL_STATE_ULCA_RE = re.compile(
    r"""
    ^\s*
    (?P<date>\d{6})\|(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+
    @(?P<slot>\d{1,3})\|(?P<id1>[0-9A-Fa-f]+)\|(?P<id2>\d+)\s+
    [^\>]*>\s*SCELL_STATE_ULCA,
    (?P<csv_payload>.*?)
    (?:\s+\(|$)
    """,
    re.VERBOSE,
)

PCELL_STATE_ULCA_RE = re.compile(
    r"""
    ^\s*
    (?P<date>\d{6})\|(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+
    @(?P<slot>\d{1,3})\|(?P<id1>[0-9A-Fa-f]+)\|(?P<id2>\d+)\s+
    [^\>]*>\s*PCELL_STATE_ULCA,
    (?P<csv_payload>.*?)
    (?:\s+\(|$)
    """,
    re.VERBOSE,
)

PCELL_STATE_ACT_RE = re.compile(
    r"""
    ^\s*
    (?P<date>\d{6})\|(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+
    @(?P<slot>\d{1,3})\|(?P<id1>[0-9A-Fa-f]+)\|(?P<id2>\d+)\s+
    [^\>]*>\s*PCELL_STATE_ACT,
    (?P<csv_payload>.*?)
    (?:\s+\(|$)
    """,
    re.VERBOSE,
)

PCELL_STATE_CHANGE_RE = re.compile(
    r"""
    ^\s*
    (?P<date>\d{6})\|(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+
    @(?P<slot>\d{1,3})\|(?P<id1>[0-9A-Fa-f]+)\|(?P<id2>\d+)\s+
    [^\>]*>\s*PCELL_STATE_CHANGE,
    (?P<csv_payload>.*?)
    (?:\s+\(|$)
    """,
    re.VERBOSE,
)

def parse_4G_state_log_line(username, filename, raw_line, line_index, metadata_dict):
    LOGS_PROCESSED.labels(user = username, filename= filename).inc()
    scell_state = SCELL_STATE_ULCA_RE.match(raw_line)
    if scell_state:
        return process_scell_state_log(username, filename, scell_state, line_index, 0, metadata_dict)
    pcell_ulca_state = PCELL_STATE_ULCA_RE.match(raw_line)
    if pcell_ulca_state:
        return process_pcell_state_ulca_log(username, filename, pcell_ulca_state, line_index, 1, metadata_dict)
    pcell_change_state = PCELL_STATE_CHANGE_RE.match(raw_line)
    if pcell_change_state:
        return process_pcell_state_change_log(username, filename, pcell_change_state, line_index, 1, metadata_dict)
    pcell_act_state = PCELL_STATE_ACT_RE.match(raw_line)
    if pcell_act_state:
        return process_pcell_state_act_log(username, filename, pcell_act_state, line_index, 1, metadata_dict)
    return None
    
def process_dpp_basic_log(username, filename, dpp_basic, line_index, dpp_column_index, metadata_dict):
    date = dpp_basic.group("date")
    time = dpp_basic.group("time")
    timestamp_str = parse_timestamp_str(date, time)
    csv_payload = dpp_basic.group("csv_payload").strip()
    csv_fields = [f.strip() for f in csv_payload.split(",")]

    def cf(i):
        return csv_fields[i - 1] if len(csv_fields) >= i else None
    
    parsed = {
        "tag" : "DPP_BASIC",
        "secondary_tag" : "UNMATCHED",
        "index" : line_index[dpp_column_index],
        "pb_matching_index" : -1,
        "timestamp_str": timestamp_str,
        "macgps_time": safe_int(cf(1)),
        "sector_id": safe_int(cf(2)),
        "ue_id": safe_int(cf(3)),
        "call_id": safe_int(cf(4)),
        "crc":safe_int(cf(5)),
        "retx_cnt": safe_int(cf(6)),
        "process_id": safe_int(cf(7)),
        "rnti" : safe_int(cf(8)),
        "mcs_level": safe_int(cf(9)),
        "service_type": safe_int(cf(10)),
        "u_size": safe_int(cf(11)),
        "n_power_ratio": safe_int(cf(12)),
        "cqiRequest*1000+ReportHeadroom" : safe_int(cf(13)),
        "SIR_before_SIC_0" : safe_int(cf(14)),
        "nInstDmrsSinrdB" : safe_int(cf(15)),
        "uPuschIndex*100000+uPuschOffsetAntNum*100+mimo_en" : safe_int(cf(16)),
        "rb_cnt": safe_int(cf(17)),
        "pdecode_n_timeoffset": safe_int(cf(18)),
        "n_time_offset_0": safe_int(cf(19)),
        "n_time_offset_1": safe_int(cf(20)),
        "snr_0+snr_1": safe_int(cf(21)),
        "snr_2+snr_3": safe_int(cf(22)),
        "a_air_time": safe_int(cf(23)),
        "pdecode_packet": safe_int(cf(24)),
        "bSpsEnable*1000+isUlCompnOn*10+bBundlingPDU": safe_int(cf(25)),
        "push_dtx_threshold": safe_int(cf(26)),
        "PreRlfStayCount+isPreRlfFlagOn": safe_int(cf(27)),
        "uCompJRAntNumFromModem*1000+uCompSearchIndex*100+uLlrCombStat*10+bHarqEnable": safe_int(cf(28)),
        "handover_reconfig_status": safe_int(cf(29)),
        "ul_tx_skip_qci_flags": safe_int(cf(30)),
        "dlca_isPCellCaUeOn*1000+dlca_isSCellCaUeOn*100+ulca_isPCellCaUeOn*10+ulca_isSCellCaUeOn": safe_int(cf(31)),
    }
    DPP_BASIC_LOGS_PROCESSED.labels(user = username, filename= filename, sector_id=process_label(parsed.get("sector_id"))).inc()
    metadata_key = (parsed["tag"] , parsed["sector_id"], parsed["ue_id"])
    metadata_dict[metadata_key] = True if parsed.get("crc") == 1 else False
    if parsed.get("crc") == 1:
        TOTAL_CRC_FAILS.labels(user = username, filename= filename, sector_id=process_label(parsed.get("sector_id"))).inc()
    line_index[dpp_column_index] += 1
    return parsed

def process_pb_basic_log(username, filename, pb_basic, line_index, pb_column_index, metadata_dict) :
    date = pb_basic.group("date")
    time = pb_basic.group("time")
    timestamp_str = parse_timestamp_str(date, time)
    csv_payload = pb_basic.group("csv_payload").strip()
    csv_fields = [f.strip() for f in csv_payload.split(",")]

    def cf(i):
        return csv_fields[i - 1] if len(csv_fields) >= i else None
    
    parsed = {
        "tag" : "PB_BASIC",
        "index" : line_index[pb_column_index],  
        "timestamp_str": timestamp_str,
        "macgps_time": safe_int(cf(1)),
        "sector_id": safe_int(cf(2)),
        "ue_id": safe_int(cf(3)),
        "call_id": safe_int(cf(4)),
        "handoverStartInd*100+isReconfigDisable*10+ReconfigStatus":safe_int(cf(5)),
        "isUplink256QamEnable*10000u+isBundlingEnable*1000u+NoResourceRestrictionForTTIBundling*100u+isEharqPatternFddOn*10u+isQciOneEnable": safe_int(cf(6)),
        "isPCellCaUeOn<<3+isSCellCaUeOn<<2+isPCellCaUeOn<<1+isSCellCaUeOn": safe_int(cf(7)),
        "u_service_type" : safe_int(cf(8)),
        "u_mcs_level": safe_int(cf(9)),
        "bPduBuildFail*1000u+bRetxPdu": safe_int(cf(10)),
        "u_retx_cnt": safe_int(cf(11)),
        "u_size": safe_int(cf(12)),
        "process_id" : safe_int(cf(13)),
        "u_prb_offset" : safe_int(cf(14)),
        "u_rb_cnt" : safe_int(cf(15)),
        "u_rnti" : safe_int(cf(16)),
        "u_tpc_cmd": safe_int(cf(17)),
        "uAggregateLevel*10000000+uDciGain": safe_int(cf(18)),
        "uLid*10000u+uRid*100+uMirroringEnable*10+bHoppingEnable": safe_int(cf(19)),
        "u_cqi_request_cnt": safe_int(cf(20)),
        "u_cqi_request[0]": safe_int(cf(21)),
        "u_cqi_request[1]": safe_int(cf(22)),
        "bPrachRbInSf*100+bDummyGrantFlag": safe_int(cf(23)),
        "bAdaptiveRetxReq*100u+bNonAdaptiveRetx*10u+bAdaptiveRetx": safe_int(cf(24)),
        "u_link_index": safe_int(cf(25)),
        "b_multi_cluster_pusch_support": safe_int(cf(26)),
        "u_vrb_offset_cL1": safe_int(cf(27)),
        "=uRbCntCL0<<8+uRbCntCL1" : safe_int(cf(28)),
        "DownlinkChannelRcd.Cqi": safe_int(cf(29)),
        "UlPowerControlUePm.ReportHeadroom": safe_int(cf(30)),
        "uplink_drx_prepare_active_period_check": safe_int(cf(31)),
        "uCompSearchIndex*100u+uInterTtiRsCType*10u+bPuschDmrsCombining": safe_int(cf(32)),
        "isHpaUe*10000u+bUplink256QamEnable*1000u+Ul256QamReconfigState": safe_int(cf(33)),
    }
    DPP_BASIC_LOGS_PROCESSED.labels(user = username, filename= filename, sector_id=process_label(parsed.get("sector_id"))).inc()
    metadata_key = (parsed["tag"] , parsed["sector_id"], parsed["ue_id"])
    metadata_dict[metadata_key] = False
    line_index[pb_column_index] +=1
    return parsed
    

def process_urac_log(username , filename , urac_log, line_index , urac_column_index, metadata_dict):
    date = urac_log.group("date")
    time = urac_log.group("time")
    timestamp_str = parse_timestamp_str(date, time)
    csv_payload = urac_log.group("csv_payload").strip()
    csv_fields = [f.strip() for f in csv_payload.split(",")]

    def cf(i):
        return csv_fields[i - 1] if len(csv_fields) >= i else None

    parsed = {
        "tag": "URAC_RA",
        "index": line_index[urac_column_index],
        "timestamp_str": timestamp_str,
        "macgps_time": safe_int(cf(1)),
        "sector_id": safe_int(cf(2)),
        "U_id": safe_int(cf(3)),
        "rnti": safe_int(cf(4)),                   
        "service_type": safe_int(cf(5)),          
        "vo_nr_info": safe_int(cf(6)),                  
        "bUl_mu_candidate*10000+u_mimo_mode*100+u_layer_cnt": safe_int(cf(7)),
        "dci_format_indicator": safe_int(cf(8)),      
        "cce_offset": safe_int(cf(9)),                 
        "coreset_id": safe_int(cf(10)),                
        "aggregate_level": safe_int(cf(11)),            
        "bForcedMrcOffFlag*100+bMrcOnOff*10+ulBfMode-or-0": safe_int(cf(12)),
        "mcs_level": safe_int(cf(13)),                  
        "dci_mcs_level": safe_int(cf(14)),             
        "size": safe_int(cf(15)),                      
        "qam_info": safe_int(cf(16)),                   
        "start_symbol": safe_int(cf(17)),               
        "length_symbol": safe_int(cf(18)),              
        "k2": safe_int(cf(19)),                         
        "ul_waveform_dmrs_fdm_info": safe_int(cf(20)),
        "process_id": safe_int(cf(21)),                
        "retx_cnt": safe_int(cf(22)),                  
        "dtx_cnt": safe_int(cf(23)),                    
        "crb_offset": safe_int(cf(24)),              
        "rb_cnt": safe_int(cf(25)),                     
        "rbg_bitmap": safe_int(cf(26)),                
        "uci_mux_type": safe_int(cf(27)),               
        "rda_info": safe_int(cf(28)),                  
        "bwp_info": safe_int(cf(29)),                  
        "ul_ca_act_info": safe_int(cf(30)),            
        "allocation_list_pdu_cnt": safe_int(cf(31)),   
        "allocation_list_pdcch_airtime": safe_int(cf(32)), 
        "allocation_list_pusch_airtime": safe_int(cf(33)), 
    }
    metadata_key = (parsed["tag"] , parsed["sector_id"], parsed["U_id"])
    metadata_dict[metadata_key] = False
    line_index[urac_column_index] +=1
    URAC_RA_LOGS_PROCESSED.labels(user = username, filename= filename, sector_id=process_label(parsed.get("sector_id"))).inc()
    return parsed


def process_umrc_dp_log(username, filename, umrc_dp_log, line_index, umrc_dp_column_index, metadata_dict):
    date = umrc_dp_log.group("date")
    time = umrc_dp_log.group("time")
    timestamp_str = parse_timestamp_str(date, time)
    csv_payload = umrc_dp_log.group("csv_payload").strip()
    csv_fields = [f.strip() for f in csv_payload.split(",")]

    def cf(i):
        return csv_fields[i - 1] if len(csv_fields) >= i else None

    parsed = {
        "tag" : "UMRC_DP",
        "index" : line_index[umrc_dp_column_index],
        "timestamp_str": timestamp_str,
        "macgps_time": safe_int(cf(1)),
        "sector_id": safe_int(cf(2)),
        "U_id": safe_int(cf(3)),
        "air_time": safe_int(cf(4)),
        "pdu_cnt": safe_int(cf(5)),
        "crc": safe_int(cf(6)),
        "rnti": safe_int(cf(7)),
        "mimo_mode*100+selected_rx_mode": safe_int(cf(8)),
        "retx_pdu": safe_int(cf(9)),
        "retx_cnt": safe_int(cf(10)),
        "process_id": safe_int(cf(11)),
        "mcs_level": safe_int(cf(12)),
        "rb_index": safe_int(cf(13)),
        "rb_cnt": safe_int(cf(14)),
        "rbg_bit_map": safe_int(cf(15)),
        "physical_ant_bit_map": safe_int(cf(16)),
        "size": safe_int(cf(17)),
        "packet_offset": safe_int(cf(18)),
        "time_offset": safe_int(cf(19)),
        "valid_time_info": safe_int(cf(20)),
        "new_tx_air_time": safe_int(cf(21)),
        "additional_harq_info": safe_int(cf(22)),
        "service_type": safe_int(cf(23)),
        "uci_mux_info": safe_int(cf(24)),
        "forced_mrcOff_flag*100+mrc_on_off*10+ulbfMode": safe_int(cf(25)),
        "harq_buffer_overflow": safe_int(cf(26)),
        "SINR[0]": safe_log10(safe_int(cf(27))),
        "SINR[1]": safe_log10(safe_int(cf(28))),
        "preSINR[0]": safe_log10(safe_int(cf(29))),
        "preSINR[1]": safe_log10(safe_int(cf(30))),
        "preamble_index": safe_int(cf(31)),
        "slot_agg_pdu_index": safe_int(cf(32)),
        "ul_ca_act_info": safe_int(cf(33)),
    }
    metadata_key = (parsed["tag"] , parsed["sector_id"], parsed["U_id"])
    line_index[umrc_dp_column_index] += 1
    UMRC_DP_LOGS_PROCESSED.labels(user = username, filename= filename, sector_id=process_label(parsed.get("sector_id"))).inc()
    if parsed.get("crc") == 0:
        TOTAL_CRC_FAILS.labels(user = username, filename= filename, sector_id=process_label(parsed.get("sector_id"))).inc()
        metadata_dict[metadata_key] = True
    else :
        metadata_dict[metadata_key] = False
    return parsed


def process_ulca_phr_pwr_al_log(username, filename, ulca_phr_pwr_al_log, line_index, ulca_phr_pwr_al_column_index, metadata_dict):
    date = ulca_phr_pwr_al_log.group("date")
    time = ulca_phr_pwr_al_log.group("time")
    timestamp_str = parse_timestamp_str(date, time)
    csv_payload = ulca_phr_pwr_al_log.group("csv_payload").strip()
    csv_fields = [f.strip() for f in csv_payload.split(",")]

    def cf(i):
        return csv_fields[i - 1] if len(csv_fields) >= i else None
    
    parsed = {
        "tag": "ULCA_PHR_PWR_AL",
        "index": line_index[ulca_phr_pwr_al_column_index],
        "timestamp_str": timestamp_str,
        "macgps_time": safe_int(cf(1)),   
        "sector_id": safe_int(cf(2)),   
        "U_id": safe_int(cf(3)),          
        "ca_cc_id": safe_int(cf(4)),      
        "equal_power_sharing_result": safe_int(cf(5)),   
        "ul_ca_power_split_mode": safe_int(cf(6)),     
        "pcmax_dbm": safe_int(cf(7)),     
        "pcmax_linear": safe_int(cf(8)),   
        "pcmaxc_dbm": safe_int(cf(9)),  
        "pcmaxc_linear": safe_int(cf(10)), 
        "sum_pcmaxc_linear": safe_int(cf(11)),          
        "req_tx_power_per_rb_dbm": safe_int(cf(12)),    
        "req_tx_power_full_rb_linear": safe_int(cf(13)),
        "scell_scheduling_disable_flag": safe_int(cf(14)),
        "ul_ca_allocated_power_linear": safe_int(cf(15)),
        "ul_ca_allocated_power_dbm": safe_int(cf(16)),   
        "ul_ca_power_alloc_flag": safe_int(cf(17)),     
    }
    metadata_key = (parsed["tag"] , parsed["sector_id"], parsed["U_id"])
    metadata_dict[metadata_key] = False
    line_index[ulca_phr_pwr_al_column_index] += 1
    ULCA_PHR_PWR_AL_LOGS_PROCESSED.labels(user = username, filename= filename, sector_id=process_label(parsed.get("sector_id"))).inc()
    return parsed
    
def process_scell_state_log(username, filename, scell_state_log, line_index, scell_state_column_index, metadata_dict):
    date = scell_state_log.group("date")
    time = scell_state_log.group("time")
    timestamp_str = parse_timestamp_str(date, time)
    csv_payload = scell_state_log.group("csv_payload").strip()
    csv_fields = [f.strip() for f in csv_payload.split(",")]

    def cf(i):
        return csv_fields[i - 1] if len(csv_fields) >= i else None
    
    parsed = {
        "tag": "SCELL_STATE_ULCA",
        "index": line_index[scell_state_column_index],
        "timestamp_str": timestamp_str,
        "macgps_time": safe_int(cf(1)),   
        "sector_id": safe_int(cf(3)),   
        "ue_id": safe_int(cf(4)),          
        "pcell_Uid": safe_int(cf(5)),      
        "prev_state": safe_int(cf(6)),   
        "u_state": safe_int(cf(7)),     
        "pcell_index": safe_int(cf(8)),     
        "activation_bitmap": safe_int(cf(9)),   
        "uid_bitmap": safe_int(cf(10)),  
        "ul_activation_trigger": safe_int(cf(11)), 
        "pdcch_order_tx_cnt": safe_int(cf(12)),          
        "ul_repreparing_timer": safe_int(cf(13)),    
        "pdcch_order_ack_flag": safe_int(cf(14)),
        "push_rx_flag": safe_int(cf(15)),
        "ul_deactivation_times": safe_int(cf(16)),
        "link_state": safe_int(cf(17)),   
        "link_timer": safe_int(cf(18)),     
        "scell_ta_link_state": safe_int(cf(19)),
    }
    metadata_key = (parsed["tag"] , parsed["sector_id"], parsed["ue_id"])
    is_malperforming = False 
    if parsed["prev_state"]is not None and parsed["u_state"] is not None :
        is_malperforming = parsed["prev_state"] > parsed["u_state"] or parsed["u_state"] == 8
    if metadata_key in metadata_dict and is_malperforming :
        metadata_dict[metadata_key] = True 
    else :
        metadata_dict[metadata_key] = is_malperforming
    line_index[scell_state_column_index] += 1
    SCELL_STATE_ULCA_LOGS_PROCESSED.labels(user = username, filename= filename, sector_id=process_label(parsed.get("sector_id"))).inc()
    return parsed


def process_pcell_state_ulca_log(username, filename, pcell_state_log, line_index, pcell_state_column_index, metadata_dict):
    date = pcell_state_log.group("date")
    time = pcell_state_log.group("time")
    timestamp_str = parse_timestamp_str(date, time)
    csv_payload = pcell_state_log.group("csv_payload").strip()
    csv_fields = [f.strip() for f in csv_payload.split(",")]

    def cf(i):
        return csv_fields[i - 1] if len(csv_fields) >= i else None
    
    parsed = {
        "tag": "PCELL_STATE_TAG",
        "tag_raw" : "PCELL_STATE_ULCA", 
        "index": line_index[pcell_state_column_index],
        "timestamp_str": timestamp_str,
        "macgps_time": safe_int(cf(1)),   
        "sector_id": safe_int(cf(3)),   
        "ue_id": safe_int(cf(4)),          
        "uemng_p2su": None,      
        "prev_state": safe_int(cf(5)),   
        "u_state": safe_int(cf(6)),     
        "u_cell_num": None,
        "logical_cell_id" : None,         
        "pCaStat_bActMacCeExist": safe_int(cf(7)),   
        "sCell_act_bitmap": safe_int(cf(8)),  
        "deactivation_timer": safe_int(cf(10)), 
        "is_deact_infinite_on": safe_int(cf(111)),             
        "num_of_continuous_err": safe_int(cf(12)),
        "pdsh_harq_acked": safe_int(cf(13)),
        "deact_mac_ce_exist": safe_int(cf(14)),   
        "max_deactivation_timer": safe_int(cf(15)),     
        "act_mac_ce_ack_flag": safe_int(cf(16)),
        "act_mac_ce_retx_cnt": safe_int(cf(17)),
        "cqi_zero_count": safe_int(cf(18)),
        "common_ca_ud_pm_be_bitmap": safe_int(cf(19)),
        "dl_ca_ue_pm_scell_num": safe_int(cf(20)),
        "activation_req_bitmap": None,
        "scell_activation_bitmap" : None,
        "ul_activation_trigger": None,
        "ul_deactivation_timer": None,
        "is_inter_site_ca_config_on": None,
        "backhaul_outage": None,
        "uhead*1000_utail": None,
        "uid_cnt": None,
        "max_transit_enqueu_per_tti": None,
        "pre_commit": None,
        "is_ue_massive_mimo_enable": None,
        "is_scell_srs_support_on": None,
        "scell_index*1000_scell_element": None,
        "cell_load_high_for_scell": None,
    }
    metadata_key = (parsed["tag"] , parsed["sector_id"], parsed["ue_id"])
    is_malperforming = False 
    if parsed["prev_state"]is not None and parsed["u_state"] is not None :
        is_malperforming = parsed["prev_state"] > parsed["u_state"] or parsed["u_state"] == 8
    if metadata_key in metadata_dict and is_malperforming :
        metadata_dict[metadata_key] = True 
    else :
        metadata_dict[metadata_key] = is_malperforming
    line_index[pcell_state_column_index] += 1
    PCELL_STATE_ULCA_LOGS_PROCESSED.labels(user = username, filename= filename, sector_id=process_label(parsed.get("sector_id"))).inc()
    return parsed


def process_pcell_state_change_log(username, filename, pcell_state_log, line_index, pcell_state_column_index, metadata_dict):
    date = pcell_state_log.group("date")
    time = pcell_state_log.group("time")
    timestamp_str = parse_timestamp_str(date, time)
    csv_payload = pcell_state_log.group("csv_payload").strip()
    csv_fields = [f.strip() for f in csv_payload.split(",")]

    def cf(i):
        return csv_fields[i - 1] if len(csv_fields) >= i else None
    
    parsed = {
        "tag": "PCELL_STATE_TAG",
        "tag_raw" : "PCELL_STATE_CHANGE", 
        "index": line_index[pcell_state_column_index],
        "timestamp_str": timestamp_str,
        "macgps_time": safe_int(cf(1)),   
        "sector_id": safe_int(cf(3)),   
        "ue_id": safe_int(cf(4)),          
        "uemng_p2su": safe_int(cf(5)),      
        "prev_state": safe_int(cf(6)),   
        "u_state": safe_int(cf(7)),     
        "u_cell_num": safe_int(cf(8)),
        "logical_cell_id" : safe_int(cf(8)),         
        "pCaStat_bActMacCeExist": safe_int(cf(9)),   
        "sCell_act_bitmap": safe_int(cf(10)),  
        "deactivation_timer": safe_int(cf(11)), 
        "is_deact_infinite_on": safe_int(cf(12)),             
        "num_of_continuous_err": safe_int(cf(13)),
        "pdsh_harq_acked": safe_int(cf(14)),
        "deact_mac_ce_exist": safe_int(cf(15)),   
        "max_deactivation_timer": safe_int(cf(16)),     
        "act_mac_ce_ack_flag": safe_int(cf(17)),
        "act_mac_ce_retx_cnt": safe_int(cf(18)),
        "cqi_zero_count": safe_int(cf(19)),
        "common_ca_ud_pm_be_bitmap": safe_int(cf(20)),
        "dl_ca_ue_pm_scell_num": safe_int(cf(21)),
        "activation_req_bitmap": safe_int(cf(22)),
        "scell_activation_bitmap" : None,
        "ul_activation_trigger": safe_int(cf(23)),
        "ul_deactivation_timer": safe_int(cf(24)),
        "is_inter_site_ca_config_on": safe_int(cf(25))%1000 if safe_int(cf(25)) is not None else 0,
        "backhaul_outage": safe_int(cf(25))/1000 if safe_int(cf(25)) is not None else 0,
        "uhead*1000_utail": safe_int(cf(26)),
        "uid_cnt": safe_int(cf(27)),
        "max_transit_enqueu_per_tti": safe_int(cf(28)),
        "pre_commit": safe_int(cf(29)),
        "is_ue_massive_mimo_enable": safe_int(cf(30)),
        "is_scell_srs_support_on": safe_int(cf(31)),
        "scell_index*1000_scell_element": safe_int(cf(32)),
        "cell_load_high_for_scell": safe_int(cf(33)),
    }
    metadata_key = (parsed["tag"] , parsed["sector_id"], parsed["ue_id"])
    is_malperforming = False 
    if parsed["prev_state"]is not None and parsed["u_state"] is not None :
        is_malperforming = parsed["prev_state"] > parsed["u_state"] or parsed["u_state"] == 8
    if metadata_key in metadata_dict and is_malperforming :
        metadata_dict[metadata_key] = True 
    else :
        metadata_dict[metadata_key] = is_malperforming
    line_index[pcell_state_column_index] += 1
    PCELL_STATE_CHANGE_LOGS_PROCESSED.labels(user = username, filename= filename, sector_id=process_label(parsed.get("sector_id"))).inc()
    return parsed

def process_pcell_state_act_log(username, filename, pcell_state_log, line_index, pcell_state_column_index, metadata_dict):
    date = pcell_state_log.group("date")
    time = pcell_state_log.group("time")
    timestamp_str = parse_timestamp_str(date, time)
    csv_payload = pcell_state_log.group("csv_payload").strip()
    csv_fields = [f.strip() for f in csv_payload.split(",")]

    def cf(i):
        return csv_fields[i - 1] if len(csv_fields) >= i else None
    
    parsed = {
        "tag": "PCELL_STATE_TAG",
        "tag_raw" : "PCELL_STATE_ACT", 
        "index": line_index[pcell_state_column_index],
        "timestamp_str": timestamp_str,
        "macgps_time": safe_int(cf(1)),   
        "sector_id": safe_int(cf(3)),   
        "ue_id": safe_int(cf(4)),          
        "uemng_p2su": safe_int(cf(5)),      
        "prev_state": safe_int(cf(6)),   
        "u_state": safe_int(cf(7)),     
        "u_cell_num": None, 
        "logical_cell_id" : safe_int(cf(8)),    
        "pCaStat_bActMacCeExist": safe_int(cf(9)),   
        "sCell_act_bitmap": safe_int(cf(10)),  
        "deactivation_timer": safe_int(cf(11)), 
        "is_deact_infinite_on": safe_int(cf(12)),             
        "num_of_continuous_err": safe_int(cf(13)),
        "pdsh_harq_acked": safe_int(cf(14)),
        "deact_mac_ce_exist": safe_int(cf(15)),   
        "max_deactivation_timer": safe_int(cf(16)),     
        "act_mac_ce_ack_flag": safe_int(cf(17)),
        "act_mac_ce_retx_cnt": safe_int(cf(18)),
        "cqi_zero_count": safe_int(cf(19)),
        "common_ca_ud_pm_be_bitmap": safe_int(cf(20)),
        "dl_ca_ue_pm_scell_num": safe_int(cf(21)),
        "activation_req_bitmap": None,
        "scell_activation_bitmap" : safe_int(cf(22)),
        "ul_activation_trigger": safe_int(cf(23)),
        "ul_deactivation_timer": None,
        "is_inter_site_ca_config_on": safe_int(cf(25)),
        "backhaul_outage": safe_int(cf(26)),
        "uhead*1000_utail": safe_int(cf(27)),
        "uid_cnt": safe_int(cf(28)),
        "max_transit_enqueu_per_tti": None,
        "pre_commit": None,
        "is_ue_massive_mimo_enable": None,
        "is_scell_srs_support_on": None,
        "scell_index*1000_scell_element": safe_int(cf(29)),
        "cell_load_high_for_scell": safe_int(cf(30)),
    }
    metadata_key = (parsed["tag"] , parsed["sector_id"], parsed["ue_id"])
    is_malperforming = False 
    if parsed["prev_state"]is not None and parsed["u_state"] is not None :
        is_malperforming = parsed["prev_state"] > parsed["u_state"] or parsed["u_state"] == 8
    if metadata_key in metadata_dict and is_malperforming :
        metadata_dict[metadata_key] = True 
    else :
        metadata_dict[metadata_key] = is_malperforming
    line_index[pcell_state_column_index] += 1
    PCELL_STATE_ACT_LOGS_PROCESSED.labels(user = username, filename= filename, sector_id=process_label(parsed.get("sector_id"))).inc()
    return parsed
