import streamlit as st
import json
import pandas as pd
from streamlit_extras.stylable_container import stylable_container
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# json_data_path = "example_data/test.json"
# json_data_path = "example_data/machine_status_000010_000020_EXAMPLE.json"
json_data_path = "example_data/machine_status_example.json"

# st.session_state['time'] = '00:00:00-00:00:10'
st.session_state['machine'] = 'Milling'
st.session_state['pallet_id'] = 'A_2663577'
st.session_state['data'] = ''

if 'box_value' not in st.session_state:
    st.session_state['box_value'] = 0
if 'time' not in st.session_state:
    st.session_state['time'] = "00:00:00-00:00:10"
      


# st.session_state['time'] = "00:00:40-00:00:50"


with open(json_data_path, "r") as f:
    x = json.load(f)
temp_data = []
for pal_time in x:
    for machine in x[pal_time]:
        for pallet_id, pallet_data in x[st.session_state['time']][machine]['pallets'].items():
            temp_data.append({
                "MachineName": machine,
                "StationNumber": x[st.session_state['time']][machine]['StationNumber'],
                "Time": pal_time,
                **pallet_data
            })
df = pd.DataFrame(temp_data)
# print(df)
# processing_pallets = df[df['status'] == 'processing']['pallet_id']
# incoming_pallets = df[df['status'] == 'incoming']['pallet_id']
processing_pallets = df[df['status'] == 'processing']
incoming_pallets = df[df['status'] == 'incoming']

st.session_state['processing_pallets'] = processing_pallets
st.session_state['incoming_pallets'] = incoming_pallets

# print("processing_pallets ", processing_pallets)
# print("incoming_pallets ", incoming_pallets)


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
    .button {
        align-content: center;
    }
            

    div.stButton > button:first-child {
    font-size:20px;
    height:1em;
    width:6em;
    border-radius:10px 10px 10px 10px;
    }
    yellow {
    background-color: yellow;
    color:black;
    }
    red {
    background-color: red;
    color:black;
    }
</style>
""", unsafe_allow_html=True)



def save_data(data):
    with open(json_data_path, "w") as f:
        json.dump(data, f)

def load_data():
    st.session_state['data'] = json.load(open(json_data_path))
    return json.load(open(json_data_path))

def kanban_board(data):
    columns = st.columns(len(data[st.session_state['time']]))
    html = ""
    for idx, machineName in enumerate(data[st.session_state['time']]):
        with columns[idx]:

            st.session_state['machine'] = machineName

            time = st.session_state['time']

            print(machineName, ": ", data[time][st.session_state['machine']]["num_errors"])
            print(st.session_state['time'])
            print(data[time][st.session_state['machine']])
            if data[time][st.session_state['machine']]["num_errors"] != 0:
                with stylable_container(
                                "red", 
                                css_styles="""
                                button {
                                    background-color: red;
                                    color: black;
                                }""",
                            ):
                                station_button = st.button(machineName, key=machineName)
            else:
                if data[time][st.session_state['machine']]["num_warnings"] != 0:
                    with stylable_container(
                                    "yellow",
                                    css_styles="""
                                    button {
                                        background-color: yellow;
                                        color: black;
                                    }""",
                                ):
                                    station_button = st.button(machineName, key=machineName)
                else:
                    with stylable_container(
                                    "green",
                                    css_styles="""
                                    button {
                                        background-color: green;
                                        color: black;
                                    }""",
                                ):
                                    station_button = st.button(machineName, key=machineName)
                            
            if station_button:
                # pallet_board(st.session_state['time'], pal["MachineName"], current_id)
                st.switch_page("pages/2Station_Management.py")
            


def pallet_board(time, machine, pallet_id): 
    # print("input_data: ", time, machine, pallet_id)
    data = load_data()

    st.write("## Pallet ID: ", pallet_id)
    st.write(st.session_state['time'])
    st.write(machine)
    # st.write()
    # print("test !!! ", data[time][machine])
    for item in data[time][machine]["pallets"][pallet_id]:
        st.write(item, ": ", data[time][machine]["pallets"][pallet_id][item])
    
    going_back = st.button("Go Back")
    if going_back:
        kanban_board(data)

def main():
    st.title("Dashboard")

    data = load_data()

    time_array = []
    for spot in data:
          time_array.append(spot)

    time_box = st.sidebar.selectbox('Select', time_array, st.session_state['box_value'])
    if time_box:
        st.session_state['box_value'] = time_array.index(time_box)
        st.session_state['time'] = time_box
    st.write("Current Time: " + st.session_state['time'])
    print(st.session_state['time'])

    # minhour = st.sidebar.time_input('Time', step=60)
    # interval = st.sidebar.slider('Time Range', min_value=0, max_value=50, step=10)

    # submit_time = st.sidebar.button("Select Time")
    # if submit_time:
    #     time_change = datetime.timedelta(seconds=10) 
        
    #     starttime_object = datetime.strptime(minhour, '%H:%M:%S')
    #     starttime_object = starttime_object + time_change
    #     endtime_object = starttime_object + time_change
    #     # start_time = minhour + datetime.timedelta(seconds=interval)
    #     # start_time = start_time + time_change
    #     # end_time = start_time + time_change
    #     # time = f"{minhour + interval}:{interval}-{minhour}:{interval+10}"
    #     # new_time
    #     print(starttime_object, " ", endtime_object)

    # print(interval)

    kanban_board(data)
    

if __name__ == "__main__":
    main()
