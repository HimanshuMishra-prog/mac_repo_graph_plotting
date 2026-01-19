import threading
import time
import json
import requests
from flaskr.scripts.parser import parse_4G_log_line,parse_5G_log_line,parse_4G_state_log_line
import logging
from flaskr.db.database_functions import save_metadata_to_db

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, requests_per_second):
        self.requests_per_second = requests_per_second
        self.last_request_time = 0
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0

    def wait_if_needed(self):
        if self.requests_per_second <= 0:
            return
            
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        sleep_time = self.min_interval - time_since_last_request
        
        if sleep_time > 0:
            time.sleep(sleep_time)
            self.last_request_time = time.time()
        else:
            self.last_request_time = current_time
            
global_rate_limiter = None

def initialize_rate_limiter(requests_per_second):
    global global_rate_limiter
    global_rate_limiter = RateLimiter(requests_per_second)

def process_label(v):
    if v is None:
        return "unknown"
    s = str(v)
    return s.replace('"', '\\"').replace("\n", " ")

def push_to_loki(loki_url, stream_labels, values, tenant=None, timeout=10, max_retries=3):
    payload = {"streams": [{"stream": stream_labels, "values": values}]}
    headers = {"Content-Type": "application/json"}
    if tenant:
        headers["X-Scope-OrgID"] = str(tenant)
    
    if global_rate_limiter:
        global_rate_limiter.wait_if_needed()
    
    url = loki_url.rstrip("/") + "/loki/api/v1/push"
    
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code == 429:
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"429 Too Many Requests. Retrying in {wait_time}s (attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"429 Too Many Requests. Max retries exceeded.")
                    resp.raise_for_status()
            else:
                resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            # if hasattr(e , 'response') and e.response is not None:
            #     logger.error(f"Loki error text : {e.response.text}")
            if attempt < max_retries and "429" not in str(e):
                wait_time = 2 ** attempt
                logger.warning(f"Request failed. Retrying in {wait_time}s (attempt {attempt + 1}/{max_retries + 1}): {e}")
                time.sleep(wait_time)
                continue
            else:
                raise e

def initialize_line_index(scenario) :
    if scenario == "4G_BASIC" :
        return [0 , 0]
    elif scenario == "5G" :
        return [0 , 0 , 0]
    elif scenario == "4G_STATE_CHANGE" :
        return [0, 0]
    else :
        return [0]

def parse_scenario(username, filename, raw_line, line_index, scenario, metadata_dict) :
    if scenario == "4G_BASIC" :
        return parse_4G_log_line(username=username,filename=filename,raw_line=raw_line,line_index=line_index, metadata_dict = metadata_dict)
    elif scenario == "5G" :
        return parse_5G_log_line(username=username,filename=filename,raw_line=raw_line,line_index=line_index, metadata_dict = metadata_dict)
    elif scenario == "4G_STATE_CHANGE" :
        return parse_4G_state_log_line(username=username,filename=filename,raw_line=raw_line,line_index=line_index, metadata_dict = metadata_dict)
    else :
        return None

def add_to_queue(pending_queue, log_entry) :
    key = (log_entry["ue_id"] , log_entry["sector_id"] , log_entry["process_id"] , log_entry["macgps_time"])
    pending_queue[key] = log_entry
    
def check_and_process_timeout(pending_queue, curr_time, label_batches, line_index, start_ns, username, filename, run_id, tenant) :
    timed_out_keys = []
    stubb_dpp = []
    for key, log_entry in pending_queue.items() :
        time_diff = calculate_time_diff(log_entry["macgps_time"], curr_time)
        if time_diff > 8 : 
            timed_out_keys.append(key)
            stub_dpp = create_stubb_dpp(log_entry)
            stubb_dpp.append(stub_dpp)
            line_str = json.dumps(stub_dpp, ensure_ascii=False)
            stream_labels = {
                "run_id": process_label(run_id),
                "user": process_label(username),
                "filename": process_label(filename),
                "tag" : process_label(stub_dpp.get("tag")),
                "sector_id": process_label(stub_dpp.get("sector_id"))
            }
            curr_time_str = str(start_ns + sum(line_index) * 100000) 
            labels_key = tuple(sorted(stream_labels.items()))
            if labels_key not in label_batches:
                label_batches[labels_key] = {
                    "labels": stream_labels,
                    "values": []
                }   
            label_batches[labels_key]["values"].append([curr_time_str, line_str])
    
    for key in timed_out_keys :
        #print(f"Removing key {key} from queue")
        del pending_queue[key]

def match_dpp_with_pb(pending_queue, dpp_entry) :
    key = (dpp_entry["ue_id"], dpp_entry["sector_id"], dpp_entry["process_id"], dpp_entry["macgps_time"] - 6) if dpp_entry["macgps_time"] >= 6 else (dpp_entry["ue_id"], dpp_entry["sector_id"], dpp_entry["process_id"], 40960 - 6 + dpp_entry["macgps_time"])
    alternative_key = (dpp_entry["ue_id"], dpp_entry["sector_id"], dpp_entry["process_id"], dpp_entry["macgps_time"] - 8) if dpp_entry["macgps_time"] >= 8 else (dpp_entry["ue_id"], dpp_entry["sector_id"], dpp_entry["process_id"], 40960 - 8 + dpp_entry["macgps_time"])  
    matching_log = None 
    matching_key = None
    if key in pending_queue :
        matching_log = pending_queue[key]
        matching_key = key
    elif alternative_key in pending_queue :
        matching_log = pending_queue[alternative_key]
        matching_key = alternative_key      
    if matching_log:
        dpp_entry["pb_matching_index"] = matching_log["index"]
        dpp_entry["secondary_tag"] = "MATCHED"
        del pending_queue[matching_key]
        # if dpp_entry["sector_id"] == 1 and dpp_entry["ue_id"] == 21 :
        #     print(f"-------------------- index : matched {matching_log['index']} index for dpp_index {dpp_entry['index']} for time dpp : {dpp_entry['macgps_time']} and pb : {matching_log['macgps_time']}-------------------------------------")
        # return matching_log
    return None

def create_stubb_dpp(log_entry) :
    parsed = {
        "tag" : "DPP_BASIC",
        "secondary_tag" : "STUB",
        "index" : -1,
        "pb_matching_index" : log_entry["index"],
        "timestamp_str": "Error",
        "macgps_time": 0,
        "sector_id": -1,
        "ue_id": -1,
        "call_id": -1,
        "crc": 0,  
        "retx_cnt": 0,
        "process_id": log_entry["process_id"],
        "rnti" : log_entry["u_rnti"],
        "mcs_level": log_entry["u_mcs_level"],
        "service_type": log_entry["u_service_type"],
        "u_size": log_entry["u_size"],
        "n_power_ratio": 0,
        "cqiRequest*1000+ReportHeadroom" : 0,
        "SIR_before_SIC_0" : 0,
        "nInstDmrsSinrdB" : 0,
        "uPuschIndex*100000+uPuschOffsetAntNum*100+mimo_en" : 0,
        "rb_cnt": log_entry["u_rb_cnt"],
        "pdecode_n_timeoffset": 0,
        "n_time_offset_0": 0,
        "n_time_offset_1": 0,
        "snr_0+snr_1": 0,
        "snr_2+snr_3": 0,
        "a_air_time": 0,
        "pdecode_packet": 0,
        "bSpsEnable*1000+isUlCompnOn*10+bBundlingPDU": 0,
        "push_dtx_threshold": 0,
        "PreRlfStayCount+isPreRlfFlagOn": 0,
        "uCompJRAntNumFromModem*1000+uCompSearchIndex*100+uLlrCombStat*10+bHarqEnable": 0,
        "handover_reconfig_status": 0,
        "ul_tx_skip_qci_flags": 0,
        "dlca_isPCellCaUeOn*1000+dlca_isSCellCaUeOn*100+ulca_isPCellCaUeOn*10+ulca_isSCellCaUeOn": 0,
        "is_stub": True
    }
    return parsed

def calculate_time_diff(older_time, newer_time) :
    if newer_time >= older_time :
        return newer_time - older_time
    else :
        return 40960- older_time + newer_time  

def replay_file_worker(app, log_sno, username, file_path, filename,
                       loki_url=None, batch_size=None, replay_delay=None, start_ns=None, scenario = None,run_id = None, tenant=None, requests_per_second=None):
    loki_url = loki_url or app.config.get("LOKI_PUSH_URL", "http://127.0.0.1:3100")
    batch_size = int(batch_size or app.config.get("REPLAY_BATCH_SIZE", 2000))
    replay_delay = float(replay_delay if replay_delay is not None else app.config.get("REPLAY_DELAY", 0))
    tenant = tenant or app.config.get("LOKI_TENANT")
    requests_per_second = requests_per_second or app.config.get("LOKI_REQUESTS_PER_SECOND", 10) 
    
    initialize_rate_limiter(requests_per_second)
    
    label_batches = {}
    metadata_dict = {}
    pb_pending_queue = {}
    total_sent = 0
    
    try:
        with open(file_path, "r", errors="replace") as fh:
            if start_ns is None :
                offset = 1200 * 1000000000  # 1200 seconds = 20 minutes = 1,200,000,000,000 nanoseconds
                start_ns = int(time.time() * 1_000_000_000) - offset
            line_index = initialize_line_index(scenario)
            for raw_line in fh:
                raw_line = raw_line.rstrip("\n")
                parsed = parse_scenario(username , filename , raw_line, line_index, scenario, metadata_dict)
                if parsed is None:
                    continue
                
                if parsed["tag"] == "PB_BASIC" :
                    add_to_queue(pb_pending_queue, parsed)
                    check_and_process_timeout(pb_pending_queue, parsed["macgps_time"], label_batches, line_index, start_ns, username, filename, run_id, tenant)
                
                if parsed["tag"] == "DPP_BASIC" :
                    check_and_process_timeout(pb_pending_queue, parsed["macgps_time"], label_batches, line_index, start_ns, username, filename, run_id, tenant)
                    
                    matched_pb = match_dpp_with_pb(pb_pending_queue, parsed)
                        
                line_str = json.dumps(parsed, ensure_ascii=False)
                stream_labels = {
                    "run_id": process_label(run_id),
                    "user": process_label(username),
                    "filename": process_label(filename),
                    "tag" : process_label(parsed.get("tag")),
                    "sector_id": process_label(parsed.get("sector_id"))
                }
                curr_time = str(start_ns + sum(line_index) * 100000)
                labels_key = tuple(sorted(stream_labels.items()))
            
                if labels_key not in label_batches:
                    label_batches[labels_key] = {
                        "labels": stream_labels,
                        "values": []
                    }
                label_batches[labels_key]["values"].append([curr_time, line_str])
                if len(label_batches[labels_key]["values"]) >= batch_size:
                    # first_time = label_batches[labels_key]["values"][0][0]
                    # last_time = label_batches[labels_key]["values"][-1][0]
                    # print(f"Sending bactch : start time {first_time} end time : {last_time} current sys time {time.time_ns()}")
                    push_to_loki(loki_url, stream_labels, label_batches[labels_key]["values"], tenant=tenant)
                    total_sent += len(label_batches[labels_key]["values"])
                    label_batches[labels_key]["values"] = []
                    
                if replay_delay and replay_delay > 0:
                    time.sleep(replay_delay)

        for batch_info in label_batches.values():
            if batch_info["values"]:
                push_to_loki(loki_url, batch_info["labels"], batch_info["values"], tenant=tenant)
                total_sent += len(batch_info["values"])   
        try:
            with app.app_context():
                save_result = save_metadata_to_db(username, filename, metadata_dict)
                if save_result:
                    app.logger.info(f"Replay finished for {username}/{filename} (lines sent={total_sent})")
                else:
                    app.logger.error(f"Failed to save metadata for {username}/{filename}")
        except Exception as e:
            app.logger.error(f"Error saving metadata for {username}/{filename}: {e}")

    except Exception as e:
        logger.error(f"Error while replaying {username}/{filename}: {e}")

def start_replay_thread(app, log_sno, username, file_path, filename,
                        loki_url=None, batch_size=None, replay_delay=None,start_ns=None, scenario=None,run_id= None, tenant=None, requests_per_second=None):
    t = threading.Thread(
        target=replay_file_worker,
        args=(app, log_sno, username, file_path, filename, loki_url, batch_size, replay_delay,start_ns,scenario,run_id, tenant, requests_per_second),
        daemon=True,
    )
    logger.info(f"Replay worker started by user {username} for file : {filename}")
    t.start()
    return t
