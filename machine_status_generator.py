import datetime
import pandas as pd
import json
import copy

class MachineStatusGenerator:

    def __init__(self):
        self.DATA_FOLDER = "./data"
        self.MACHINE_DATA_PATH = self.DATA_FOLDER + "/machines.json"
        self.ORDERS_DATA_PATH = self.DATA_FOLDER + "/orders.json"
        self.TRACKING_DATA_PATH = self.DATA_FOLDER + "/trackingresults.json"
        self.OUTPUT_DATA_PATH = "./output_data/machine_status.json"
        self.TIME_FORMAT = "%H:%M:%S"

        self.MACHINE_DATA = pd.read_json(self.MACHINE_DATA_PATH)
        self.ORDERS_DATA = pd.read_json(self.ORDERS_DATA_PATH)
        self.TRACKING_DATA = pd.read_json(self.TRACKING_DATA_PATH)
        self.TRACKING_DATA["StartTime"] = pd.to_datetime(self.TRACKING_DATA["StartTime"], format=self.TIME_FORMAT)
        self.TRACKING_DATA["EndTime"] = pd.to_datetime(self.TRACKING_DATA["EndTime"], format=self.TIME_FORMAT)
        self.station_number_name_mapping = {1: "Milling", 2: "Polishing", 3: "Assembly", 4: "Conservation"}

        self.START_TIME = datetime.datetime.strptime("00:00:00", self.TIME_FORMAT)
        self.END_TIME = datetime.datetime.strptime("00:04:00", self.TIME_FORMAT)

        self.current_start_time = self.START_TIME
        self.current_end_time = None

        self.prev_start_time = None
        self.prev_end_time = None

        self.machines = self.build_init_machine_status()
        self.status = {}
        self.data_to_add = []
        self.test_status = {}
    
    def build_init_machine_status(self):
        machines = {}
        for index, machine in self.MACHINE_DATA.iterrows():
            machines[machine["MachineName"]] = {
                             "StationNumber": machine["StationNumber"],
                             "avg_throughput_time": machine["avg_throughput_time(hh:mm:ss)"],
                             "num_warnings": 0,
                             "num_errors": 0,
                             "num_pallets_with_warnings": 0,
                             "num_pallets_with_errors": 0,
                             "pallets": {}}
        return machines

    def generate_machine_status_per_time_step(self):
        while self.current_start_time < self.END_TIME:
            self.current_time_step_end = self.current_start_time + datetime.timedelta(seconds=10)
            time_stamp = self.current_start_time.strftime(self.TIME_FORMAT) + '-' + self.current_time_step_end.strftime(self.TIME_FORMAT)
            self.status[time_stamp] = copy.deepcopy(self.machines)
            self.add_pallets_to_status(self.current_time_step_end, time_stamp)
            
            self.prev_start_time = self.current_start_time
            self.prev_end_time = self.current_time_step_end
            self.current_start_time = self.current_time_step_end
    
    def add_pallets_to_status(self, current_time_step_end, time_stamp):
        current_active_pallets = self.get_filtered_tracking_status(self.current_start_time, current_time_step_end)
        for i, pallet in current_active_pallets.iterrows():
            steps = self.get_steps_for_order(pallet["order_id"])
            self.status[time_stamp][self.station_number_name_mapping[pallet["station"]]]["pallets"][pallet["order_id"]] = {"pallet_id": pallet["order_id"],
                                                                                                                           "expecting_in_station": 0,
                                                                                                                           "in_station_since": str(pallet["StartTime"]),
                                                                                                                           "needed_stations": steps,
                                                                                                                           "status": "processing",
                                                                                                                           "too_long_in_station": False,
                                                                                                                           "station_skipped": False,
                                                                                                                           "throughput_time_too_low": False,
                                                                                                                           "wrong_station": False}
                
    def get_steps_for_order(self, pallet_id):
        steps = []
        for i, order in self.ORDERS_DATA.iterrows():
            if order["order_id"] == pallet_id:
                steps = order["steps"]
        return steps
    
    def detect_skipped_stations(self):
        self.current_start_time = self.START_TIME
        self.current_end_time = None
        pallet_visited_stations = {}
        while self.current_start_time < self.END_TIME:
            self.current_time_step_end = self.current_start_time + datetime.timedelta(seconds=10)
            time_stamp = self.current_start_time.strftime(self.TIME_FORMAT) + '-' + self.current_time_step_end.strftime(self.TIME_FORMAT)

            for station_name in self.status[time_stamp].keys():
                station_number = self.status[time_stamp][station_name]["StationNumber"]
                for pallet_id in self.status[time_stamp][station_name]["pallets"].keys():
                    if self.status[time_stamp][station_name]["pallets"][pallet_id]["status"] != "processing":
                        continue
                    if pallet_id not in pallet_visited_stations.keys():
                        pallet_visited_stations[pallet_id] = []
                    if station_number not in pallet_visited_stations[pallet_id]:
                        pallet_visited_stations[pallet_id].append(station_number)
                        if not self.check_increasing_number(pallet_visited_stations[pallet_id]):
                            self.status[time_stamp][station_name]["pallets"][pallet_id]["station_skipped"] = True
            self.prev_start_time = self.current_start_time
            self.prev_end_time = self.current_time_step_end
            self.current_start_time = self.current_time_step_end
    
    def detect_wrong_station(self):
        self.current_start_time = self.START_TIME
        self.current_end_time = None
        pallet_visited_stations = {}
        while self.current_start_time < self.END_TIME:
            self.current_time_step_end = self.current_start_time + datetime.timedelta(seconds=10)
            time_stamp = self.current_start_time.strftime(self.TIME_FORMAT) + '-' + self.current_time_step_end.strftime(self.TIME_FORMAT)

            for station_name in self.status[time_stamp].keys():
                for pallet_id in self.status[time_stamp][station_name]["pallets"].keys():
                    if self.status[time_stamp][station_name]["pallets"][pallet_id]["status"] != "processing":
                        continue
                    if station_name not in self.status[time_stamp][station_name]["pallets"][pallet_id]["needed_stations"]:
                        self.status[time_stamp][station_name]["pallets"][pallet_id]["wrong_station"] = True
            self.prev_start_time = self.current_start_time
            self.prev_end_time = self.current_time_step_end
            self.current_start_time = self.current_time_step_end
    

    def check_increasing_number(self, arr):
        prev_num = None
        for num in arr:
            if prev_num:
                if num != prev_num + 1:
                    return False
            prev_num = num
        return arr
    
    def add_expecting_pallets(self):
        self.current_start_time = self.START_TIME
        self.current_end_time = None
        pallet_prev_station = {}
        for i, order in self.ORDERS_DATA.iterrows():
            pallet_prev_station[order["order_id"]] = None
        while self.current_start_time < self.END_TIME:
            self.current_time_step_end = self.current_start_time + datetime.timedelta(seconds=10)
            time_stamp = self.current_start_time.strftime(self.TIME_FORMAT) + '-' + self.current_time_step_end.strftime(self.TIME_FORMAT)

            #set initially seen station
            for station_name in self.status[time_stamp].keys():
                station_number = self.status[time_stamp][station_name]["StationNumber"]
                for pallet_id in self.status[time_stamp][station_name]["pallets"].keys():
                    if pallet_prev_station[pallet_id] == None:
                        pallet_prev_station[pallet_id] = int(station_number)
            

            for pallet_id in pallet_prev_station.keys():
                if pallet_prev_station[pallet_id] == None:
                    continue
                current_station_name = self.station_number_name_mapping[pallet_prev_station[pallet_id]]
                if pallet_id in self.status[time_stamp][current_station_name]["pallets"].keys():
                    continue
                next_station_number = pallet_prev_station[pallet_id] + 1
                if next_station_number not in self.station_number_name_mapping:
                    continue
                next_station_name = self.station_number_name_mapping[next_station_number]
                if pallet_id in self.status[time_stamp][next_station_name]["pallets"].keys():
                    pallet_prev_station[pallet_id] = next_station_number
                else:
                    #add expecting pallet
                    steps = self.get_steps_for_order(pallet_id)
                    self.status[time_stamp][next_station_name]["pallets"][pallet_id] = {"pallet_id": pallet_id,
                                                                                        "expecting_in_station": str(time_stamp),
                                                                                        "in_station_since": 0,
                                                                                        "needed_stations": steps,
                                                                                        "status": "incoming",
                                                                                        "too_long_in_station": False,
                                                                                        "station_skipped": False,
                                                                                        "throughput_time_too_low": False,
                                                                                        "wrong_station": False}
                
            self.prev_start_time = self.current_start_time
            self.prev_end_time = self.current_time_step_end
            self.current_start_time = self.current_time_step_end

    def update_time_status(self):
        self.current_start_time = self.START_TIME
        self.current_end_time = None
        pallet_visited_stations = {}
        while self.current_start_time < self.END_TIME:
            self.current_time_step_end = self.current_start_time + datetime.timedelta(seconds=10)
            time_stamp = self.current_start_time.strftime(self.TIME_FORMAT) + '-' + self.current_time_step_end.strftime(self.TIME_FORMAT)

            for station_name in self.status[time_stamp].keys():
                station_processing_time = self.get_machine_processing_time(station_name)

                for pallet_id in self.status[time_stamp][station_name]["pallets"].keys():
                    if self.status[time_stamp][station_name]["pallets"][pallet_id]["status"] != "processing":
                        continue
                    current_time = datetime.datetime.strptime(time_stamp.split("-")[0], self.TIME_FORMAT)
                    processing_since = datetime.datetime.strptime(self.status[time_stamp][station_name]["pallets"][pallet_id]["in_station_since"].split(" ")[1], self.TIME_FORMAT)
                    cum_processing_time = abs((current_time - processing_since).total_seconds())
                    over_avg_processing_time = int(cum_processing_time) > int(station_processing_time.split(":")[2])
                    under_avg_processing_time = int(cum_processing_time) + 10 < int(station_processing_time.split(":")[2])
                    self.status[time_stamp][station_name]["pallets"][pallet_id]["too_long_in_station"] = over_avg_processing_time
                    self.status[time_stamp][station_name]["pallets"][pallet_id]["throughput_time_too_low"] = under_avg_processing_time and self.current_start_time > processing_since
            self.prev_start_time = self.current_start_time
            self.prev_end_time = self.current_time_step_end
            self.current_start_time = self.current_time_step_end

    def ErrorWarningCounter(self):
        # "num_pallets_without_qr_code" is omitted
        for s in self.status.values():
            for station in s.values():
                # count the pallet attributes, and it's in dict type
                errCnt = 0
                errPalletCnt = 0
                # difference: per pallet count, total flags
                warningCnt = 0
                warningPalletCnt = 0
                for p in station["pallets"].values():
                    palletWarningFlag = False
                    if p["station_skipped"]:
                        errCnt = errCnt + 1
                        errPalletCnt = errPalletCnt + 1
                    if p["wrong_station"]:
                        errCnt = errCnt + 1
                        errPalletCnt = errPalletCnt + 1
                    if p["too_long_in_station"]:
                        warningCnt = warningCnt + 1
                        palletWarningFlag = True
                    if p["throughput_time_too_low"]:
                        warningCnt = warningCnt + 1
                        palletWarningFlag = True
                    if palletWarningFlag:  # count the pallet in the end
                        warningPalletCnt = warningPalletCnt + 1
                station["num_warnings"] = warningCnt
                station["num_errors"] = errCnt
                station["num_pallets_with_warnings"] = warningPalletCnt
                station["num_pallets_with_errors"] = errPalletCnt
    
    def get_machine_processing_time(self, name):
        for i, row in self.MACHINE_DATA.iterrows():
            if row["MachineName"] == name:
                return row["avg_throughput_time(hh:mm:ss)"]        
        return None
    
    def write_status_to_file(self):
        with open(self.OUTPUT_DATA_PATH, 'w') as f:
                json.dump(self.status, f)

    def get_filtered_tracking_status(self, start, end):
        mask = ((start < self.TRACKING_DATA["StartTime"]) & (self.TRACKING_DATA["StartTime"] <= end)) | ((start < self.TRACKING_DATA["EndTime"]) & (self.TRACKING_DATA["EndTime"] <= end)) | ((self.TRACKING_DATA["StartTime"] < start) & (self.TRACKING_DATA["EndTime"] > start))
        return self.TRACKING_DATA.loc[mask]
    
    def check_all_pallets_unique_in_all_stations(self):
        return True

generator = MachineStatusGenerator()
generator.generate_machine_status_per_time_step()
generator.add_expecting_pallets()
generator.detect_skipped_stations()
generator.update_time_status()
generator.ErrorWarningCounter()
generator.detect_wrong_station()
generator.write_status_to_file()