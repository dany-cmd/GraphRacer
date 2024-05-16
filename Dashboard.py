import streamlit as st
import json
import pandas as pd
from streamlit_extras.stylable_container import stylable_container
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

json_data_path = "example_data/machine_status_example.json"

st.session_state['machine'] = 'Milling'
st.session_state['pallet_id'] = 'A_2663577'
st.session_state['data'] = ''

if 'box_value' not in st.session_state:
    st.session_state['box_value'] = 0
if 'time' not in st.session_state:
    st.session_state['time'] = "00:00:00-00:00:10"
      
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
processing_pallets = df[df['status'] == 'processing']
incoming_pallets = df[df['status'] == 'incoming']

st.session_state['processing_pallets'] = processing_pallets
st.session_state['incoming_pallets'] = incoming_pallets

# Add CSS style to customize column appearance
st.markdown("""
<style>
    /* Style for column */
    * {
        box-sizing: border-box;
    }
    div.stButton > button:first-child {
    font-size:20px;
    height:1em;
    width:6em;
    border-radius:10px 10px 10px 10px;
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
                st.switch_page("pages/2Station_Management.py")

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

    kanban_board(data)
    

if __name__ == "__main__":
    main()
