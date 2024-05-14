import streamlit as st
import json
import pandas as pd

st.set_page_config(layout="wide")

# json_data_path = "example_data/test.json"
json_data_path = "example_data/machine_status_000010_000020_EXAMPLE.json"

with open(json_data_path, "r") as f:
    x = json.load(f)
temp_data = []
for machine in x:
    print(machine["MachineName"])
    for pallet_id, pallet_data in machine['pallets'].items():
        temp_data.append({
            "MachineName": machine['MachineName'],
            "StationNumber": machine['StationNumber'],
            **pallet_data
        })
df = pd.DataFrame(temp_data)
# processing_pallets = df[df['status'] == 'processing']['pallet_id']
# incoming_pallets = df[df['status'] == 'incoming']['pallet_id']
processing_pallets = df[df['status'] == 'processing']
incoming_pallets = df[df['status'] == 'incoming']
print(processing_pallets)
print(incoming_pallets)


# Add CSS style to customize column appearance
st.markdown("""
<style>
    /* Style for column */
    * {
        box-sizing: border-box;
    }
    .wrapper {
        grid-template-columns: 1fr 1fr 1fr 1fr;
        grid-template-areas:
            "c1 c2 c3 c4";
        display: grid;
    }
    .wrapper_status {
        grid-template-columns: 1fr 1fr;
        grid-template-areas:
            "cd0 cd1";
        display: grid;
    }
    #c1 {grid-area: c1}
    #c2 {grid-area: c2}
    #cd0 {grid-area: cd0}
    #cd1 {grid-area: cd1}
    #c3 {grid-area: c3}
    #c4 {grid-area: c4}
    .custom-column {
        border: 2px solid blue; /* Border color */
        background-color: lightgray; /* Background color */
        padding: 10px; /* Padding */
        border-radius: 5px; /* Border radius */
    }
    .incoming-column {
        border-color: black;
        border-bottom: solid 2px;
        border-right: solid 2px;
    }
    .processing-column {
        border-color: black;
        border-bottom: solid 2px;
        border-left: solid 2px;
    }
    .incoming-data {
        border-color: black;
        border-right: solid 2px;
    }
    .processing-data {
        border-color: black;
        border-left: solid 2px;
    }
    .header {
        border-color: black;
        border-right: solid 2px;
        border-left: solid 2px;
    }
</style>
""", unsafe_allow_html=True)
#TODO: Double line after c1

def save_data(data):
    with open(json_data_path, "w") as f:
        json.dump(data, f)

def load_data():
    try:
        with open(json_data_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"Milling": {
                    "MachineName": "Milling",
                    "StationNumber": 1,
                    "avg_throughput_time": "00:00:15",
                    "num_warnings": 0,
                    "num_errors": 0,
                    "num_pallets_with_warnings": 0,
                    "num_pallets_with_errors": 0,
                    "num_pallets_without_qr_code": 0,
                    "pallets": {}
                    },
                "Polishing": {
                    "MachineName": "Polishing",
                    "StationNumber": 2,
                    "avg_throughput_time": "00:00:20",
                    "num_warnings": 0,
                    "num_errors": 0,
                    "num_pallets_with_warnings": 0,
                    "num_pallets_with_errors": 0,
                    "num_pallets_without_qr_code": 0,
                    "pallets": {}
                },
                "Assembly": {
                    "MachineName": "Assembly",
                    "StationNumber": 3,
                    "avg_throughput_time": "00:00:45",
                    "num_warnings": 0,
                    "num_errors": 0,
                    "num_pallets_with_warnings": 0,
                    "num_pallets_with_errors": 0,
                    "num_pallets_without_qr_code": 0,
                    "pallets": {}
                },
                "Conservation": {
                    "MachineName": "Conservation",
                    "StationNumber": 4,
                    "avg_throughput_time": "00:00:55",
                    "num_warnings": 0,
                    "num_errors": 0,
                    "num_pallets_with_warnings": 0,
                    "num_pallets_with_errors": 0,
                    "num_pallets_without_qr_code": 0,
                    "pallets": {}
                }
            }

                
        # return {"Stations": [{"station_name": "Station 1", "status": {"Incoming": [], "Processing": []}},
        #                     {"station_name": "Station 2", "status": {"Incoming": [], "Processing": []}},
        #                     {"station_name": "Station 3", "status": {"Incoming": [], "Processing": []}}]}

def kanban_board(data):
    columns = st.columns(len(data))
    # print(data)
    # html = f"<div class='wrapper'>"
    html = ""
    for idx, station in enumerate(data):
        html += f"<div class='header wrapper'>"
        html += f"<div id='c{idx+1}'>"
        with columns[idx]:

            # print(idx)
            # for index, pal in incoming_pallets.iterrows():
            #     st.write("### ", pal["MachineName"])
            machineName = station["MachineName"]
            # st.markdown(f"<div class='header'>", unsafe_allow_html = True)
            html = f"{html}<h2 style='text-align: center'>{machineName}</h2>"
            # st.markdown(f"<h2 style='text-align: center'>{machineName}</h2>", unsafe_allow_html = True)
            
            # st.write(f"## ", station["MachineName"])
            statuses = st.columns(2)
            html += f"<div class=wrapper_status>"
            for i in range(2):
                if i == 0:
                    current_state = "incoming"
                    current_pallets = incoming_pallets
                else:
                    current_state = "processing"
                    current_pallets = processing_pallets
                with statuses[i]:
                    html += f"<div id='cd{i}'>"
                    html = f"{html}<h3 class='{current_state}-column' style='text-align: center'>{current_state}</h3>"
                    # st.markdown(f"<h3 class='{current_state}-column' style='text-align: center'>{current_state}</h3>", unsafe_allow_html = True)
                    for index, pal in current_pallets.iterrows():
                        if(pal["MachineName"] == station["MachineName"]):
                            current_id = pal["pallet_id"]
                            html = f"{html}<h4 class='{current_state}-data' style='text-align: center'>{current_id}</h4>"
                            # st.markdown(f"<h4 class='{current_state}-data' style='text-align: center'>{current_id}</h4>", unsafe_allow_html = True)
                    html += f"</div>"
            html += f"</div>"

            html = f"{html}</div>"
            # st.markdown(f"</div>", unsafe_allow_html = True)
    
    html = f"{html}</div>"
    print(html)
    st.markdown(html, unsafe_allow_html = True)

def main():
    st.title("Dashboard")
    st.sidebar.header("Options")
    option = st.sidebar.selectbox("Select Option", ["View Board", "Add Task"])



    if option == "View Board":
        data = load_data()
        kanban_board(data)
    
    # elif option == "Add Task":
    #     station_station_names = [station["station_name"] for station in load_data()["Stations"]]
    #     station = st.sidebar.selectbox("Select Station", station_station_names)
    #     board = st.sidebar.selectbox("Select Status", ["Incoming", "Processing"])
    #     task = st.sidebar.text_input("Task")
    #     if st.sidebar.button("Add Task"):
    #         data = load_data()
    #         for s in data["Stations"]:
    #             if s["station_name"] == station:
    #                 s["status"][board].append(task)
    #                 break
    #         save_data(data)
    #         st.sidebar.success("Task added successfully!")

if __name__ == "__main__":
    main()
