import datetime
import pandas as pd

class MachineStatusGenerator:

    def __init__(self):
        self.DATA_FOLDER = "./data"
        self.MACHINE_DATA_PATH = self.DATA_FOLDER + "/machines.json"
        self.ORDERS_DATA_PATH = self.DATA_FOLDER + "/orders.json"
        self.TRACKING_DATA_PATH = self.DATA_FOLDER + "/trackingresults.json"
        self.OUTPUT_DATA_PATH = "./output_data/machine_status"

        self.MACHINE_DATA = pd.read_json(self.MACHINE_DATA_PATH)
        self.ORDERS_DATA = pd.read_json(self.ORDERS_DATA_PATH)
        self.TRACKING_DATA = pd.read_json(self.TRACKING_DATA_PATH)
        self.TRACKING_DATA["StartTime"] = pd.to_datetime(self.TRACKING_DATA["StartTime"], format='%H:%M:%S')
        self.TRACKING_DATA["EndTime"] = pd.to_datetime(self.TRACKING_DATA["EndTime"], format='%H:%M:%S')

        self.START_TIME = datetime.datetime.strptime("00:00:00", '%H:%M:%S')
        self.END_TIME = datetime.datetime.strptime("00:04:00", '%H:%M:%S')

        self.status = self.build_init_status()
    
    def build_init_status(self):
        machines = []
        for index, machine in self.MACHINE_DATA.iterrows():
            machines.append({"MachineName": machine["MachineName"],
                             "StationNumber": machine["StationNumber"],
                             "avg_throughput_time": machine["avg_throughput_time(hh:mm:ss)"],
                             "num_warnings": 0,
                             "num_errors": 0,
                             "num_pallets_with_warnings": 0,
                             "num_pallets_with_errors": 0,
                             "num_pallets_without_qr_code": 0,
                             "pallets": {}})
        return machines

    def generate_machine_status_per_time_step(self):
        while self.START_TIME < self.END_TIME:
            current_time_step_end = self.START_TIME + datetime.timedelta(seconds=10)
            print(self.START_TIME.strftime("%H:%M:%S"), " ", current_time_step_end.strftime("%H:%M:%S"))
            current_active_pallets = self.get_filtered_tracking_status(self.START_TIME, current_time_step_end)
            for index, pallet in current_active_pallets.iterrows():
                for i in range(len(self.status)):
                    if self.status[i]["StationNumber"] == pallet["station"]:
                        self.status[i]["pallets"][pallet["order_id"]] =  {"pallet_id": pallet["order_id"]}
            print(self.status)
            self.START_TIME = current_time_step_end
        return

    def get_filtered_tracking_status(self, start, end):
        mask = (start < self.TRACKING_DATA["StartTime"]) & (self.TRACKING_DATA["StartTime"] <= end) & (self.TRACKING_DATA["EndTime"] >= end)
        return self.TRACKING_DATA.loc[mask]
    
    def check_all_pallets_unique_in_all_stations(self):
        return True

generator = MachineStatusGenerator()
generator.generate_machine_status_per_time_step()

