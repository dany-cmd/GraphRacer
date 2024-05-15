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
            print(self.current_start_time.strftime(self.TIME_FORMAT), " ", self.current_time_step_end.strftime(self.TIME_FORMAT))
            self.add_pallets_to_status(self.current_time_step_end, time_stamp)
            
            self.prev_start_time = self.current_start_time
            self.prev_end_time = self.current_time_step_end
            self.current_start_time = self.current_time_step_end
    
    def add_pallets_to_status(self, current_time_step_end, time_stamp):
        current_active_pallets = self.get_filtered_tracking_status(self.current_start_time, current_time_step_end)
        for i, pallet in current_active_pallets.iterrows():
            steps = self.get_steps_for_order(pallet["order_id"])
            print(pallet["order_id"])
            self.status[time_stamp][self.station_number_name_mapping[pallet["station"]]]["pallets"][pallet["order_id"]] = {"pallet_id": pallet["order_id"],
                                                                                                                           "expecting_in_station": 0,
                                                                                                                           "in_station_since": str(pallet["StartTime"]),
                                                                                                                           "needed_stations": steps,
                                                                                                                           "status": "processing",
                                                                                                                           "cumulative_throughput_time": 0,
                                                                                                                           "too_long_in_station": False,
                                                                                                                           "station_skipped": False,
                                                                                                                           "throughput_time_too_low": False}
                
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
            print(self.current_start_time.strftime(self.TIME_FORMAT), " ", self.current_time_step_end.strftime(self.TIME_FORMAT))
            
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
            print(self.current_start_time.strftime(self.TIME_FORMAT), " ", self.current_time_step_end.strftime(self.TIME_FORMAT))
            
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
                print(current_station_name)
                print(pallet_id)
                print(self.status[time_stamp][current_station_name]["pallets"].keys())
                if pallet_id in self.status[time_stamp][current_station_name]["pallets"].keys():
                    print("skip " + pallet_id)
                    continue
                next_station_number = pallet_prev_station[pallet_id] + 1
                if next_station_number not in self.station_number_name_mapping:
                    continue
                next_station_name = self.station_number_name_mapping[next_station_number]
                if pallet_id in self.status[time_stamp][next_station_name]["pallets"].keys():
                    pallet_prev_station[pallet_id] = next_station_number
                else:
                    #add expecting pallet
                    print("expecting pallet")
                    steps = self.get_steps_for_order(pallet_id)
                    self.status[time_stamp][next_station_name]["pallets"][pallet_id] = {"pallet_id": pallet_id,
                                                                                                                           "expecting_in_station": str(time_stamp),
                                                                                                                           "in_station_since": 0,
                                                                                                                           "needed_stations": steps,
                                                                                                                           "status": "incoming",
                                                                                                                           "cumulative_throughput_time": 0,
                                                                                                                           "too_long_in_station": False,
                                                                                                                           "station_skipped": False,
                                                                                                                           "throughput_time_too_low": False}
                
            self.prev_start_time = self.current_start_time
            self.prev_end_time = self.current_time_step_end
            self.current_start_time = self.current_time_step_end
    
    def write_status_to_file(self):
        with open(self.OUTPUT_DATA_PATH, 'w') as f:
                json.dump(self.status, f)

    def get_filtered_tracking_status(self, start, end):
        mask = ((start < self.TRACKING_DATA["StartTime"]) & (self.TRACKING_DATA["StartTime"] <= end)) | ((start < self.TRACKING_DATA["EndTime"]) & (self.TRACKING_DATA["EndTime"] <= end))
        return self.TRACKING_DATA.loc[mask]
    
    def check_all_pallets_unique_in_all_stations(self):
        return True

generator = MachineStatusGenerator()
generator.generate_machine_status_per_time_step()
generator.add_expecting_pallets()
generator.detect_skipped_stations()
generator.write_status_to_file()