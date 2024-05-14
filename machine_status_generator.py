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

        self.MACHINE_DATA = pd.read_json(self.MACHINE_DATA_PATH)
        self.ORDERS_DATA = pd.read_json(self.ORDERS_DATA_PATH)
        self.TRACKING_DATA = pd.read_json(self.TRACKING_DATA_PATH)
        self.TRACKING_DATA["StartTime"] = pd.to_datetime(self.TRACKING_DATA["StartTime"], format='%H:%M:%S')
        self.TRACKING_DATA["EndTime"] = pd.to_datetime(self.TRACKING_DATA["EndTime"], format='%H:%M:%S')
        self.station_number_name_mapping = {1: "Milling", 2: "Polishing", 3: "Assembly", 4: "Conservation"}

        self.START_TIME = datetime.datetime.strptime("00:00:00", '%H:%M:%S')
        self.END_TIME = datetime.datetime.strptime("00:04:00", '%H:%M:%S')

        self.current_start_time = self.START_TIME

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
                             "num_pallets_without_qr_code": 0,
                             "pallets": {}}
        return machines

    def generate_machine_status_per_time_step(self):
        while self.current_start_time < self.END_TIME:
            self.current_time_step_end = self.current_start_time + datetime.timedelta(seconds=10)
            time_stamp = self.current_start_time.strftime("%H:%M:%S") + '-' + self.current_time_step_end.strftime("%H:%M:%S")
            self.status[time_stamp] = copy.deepcopy(self.machines)
            print(self.current_start_time.strftime("%H:%M:%S"), " ", self.current_time_step_end.strftime("%H:%M:%S"))
            self.add_pallets_to_status(self.current_time_step_end, time_stamp)
            
            self.prev_start_time = self.current_start_time
            self.prev_end_time = self.current_time_step_end
            self.current_start_time = self.current_time_step_end
        self.write_status_to_file()
    
    def add_pallets_to_status(self, current_time_step_end, time_stamp):
        current_active_pallets = self.get_filtered_tracking_status(self.START_TIME, current_time_step_end)
        for i, pallet in current_active_pallets.iterrows():
            steps = []
            for i, order in self.ORDERS_DATA.iterrows():
                if order["order_id"] == pallet["order_id"]:
                    steps = order["steps"]
            self.status[time_stamp][self.station_number_name_mapping[pallet["station"]]]["pallets"][pallet["order_id"]] = {"pallet_id": pallet["order_id"],
                                                                                                                           "expecting_in_station": 0,
                                                                                                                           "in_station_since": str(pallet["StartTime"]),
                                                                                                                           "needed_stations": steps,
                                                                                                                           "visited_stations": [],
                                                                                                                           "status": "processing",
                                                                                                                           "cumulative_throughput_time": 0,
                                                                                                                           "expecting_too_long": False,
                                                                                                                           "too_long_in_station": False,
                                                                                                                           "station_skipped": False,
                                                                                                                           "throughput_time_too_low": False}
                
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

