import streamlit as st
import json
import pandas as pd
from streamlit_extras.stylable_container import stylable_container
import datetime

st.set_page_config(layout="wide")

# json_data_path = "example_data/test.json"
# json_data_path = "example_data/machine_status_000010_000020_EXAMPLE.json"
json_data_path = "example_data/machine_status_example.json"

st.session_state['time'] = '00:00:00-00:00:10'
st.session_state['machine'] = 'Milling'
st.session_state['pallet_id'] = 'A_2663577'
st.session_state['data'] = ''


with open(json_data_path, "r") as f:
    x = json.load(f)
temp_data = []
for time in x:
    for machine in x[time]:
        for pallet_id, pallet_data in x[time][machine]['pallets'].items():
            temp_data.append({
                "MachineName": machine,
                "StationNumber": x[time][machine]['StationNumber'],
                "Time": time,
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

st.session_state['time'] = "00:00:40-00:00:50"


def save_data(data):
    with open(json_data_path, "w") as f:
        json.dump(data, f)

def load_data():
    st.session_state['data'] = json.load(open(json_data_path))
    # print(st.session_state['data'])
    return json.load(open(json_data_path))

def kanban_board(data):
    columns = st.columns(len(data[st.session_state['time']]))
    # print(data)
    # html = f"<div class='wrapper'>"
    html = ""
    for idx, machineName in enumerate(data[st.session_state['time']]):
        # print("station", station)

        # html += f"<div class='header wrapper'>"
        # html += f"<div id='c{idx+1}'>"
        with columns[idx]:

            # print(idx)
            # for index, pal in incoming_pallets.iterrows():
            #     st.write("### ", pal["MachineName"])
            # print(data[time][station]["pallets"])
            # machineName = station
            st.session_state['machine'] = machineName
            # st.markdown(f"<div class='header'>", unsafe_allow_html = True)
            # html = f"{html}<h2 style='text-align: center'>{machineName}</h2>"
            # st.markdown(f"<h2 style='text-align: center'>{machineName}</h2>", unsafe_allow_html = True)
            # st.write("## ", machineName)

            # station_button = st.button(machineName, key=machineName)
            # for mach in data[time]:
            #     print(machineName)
            # print(machineName, ": ", data[time][st.session_state['machine']]["num_errors"])
            # print(time)
            # print(data[time][st.session_state['machine']])
            if data[time][st.session_state['machine']]["num_errors"] != 0:
                with stylable_container(
                                "red", 
                                css_styles="""
                                button {
                                    background-color: white;
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
                                        background-color: white;
                                        color: black;
                                    }""",
                                ):
                                    station_button = st.button(machineName, key=machineName)
                else:
                    with stylable_container(
                                    "green",
                                    css_styles="""
                                    button {
                                        background-color: white;
                                        color: black;
                                    }""",
                                ):
                                    station_button = st.button(machineName, key=machineName)
                            

                # for item in data[time][machineName]["pallets"][pallet_id]:
                #     # print("TEST: ", data[time][machine]["pallets"][pallet_id][item])
                #     if type(data[time][machineName]["pallets"][pallet_id][item]) == bool:
                #         if item == "too_long_in_station" or item == "too_short_in_station":
                #             if data[time][machineName]["pallets"][pallet_id][item] == True:
                #                 with stylable_container(
                #                     "yellow",
                #                     css_styles="""
                #                     button {
                #                         background-color: yellow;
                #                         color: black;
                #                     }""",
                #                 ):
                #                     station_button = st.button(st.session_state['machine'], key=st.session_state['machine'])
                #             else:
                #                 with stylable_container(
                #                     "green",
                #                     css_styles="""
                #                     button {
                #                         background-color: green;
                #                         color: black;
                #                     }""",
                #                 ):
                #                     station_button = st.button(st.session_state['machine'], key=st.session_state['machine'])
                #         else:
                #             if data[time][machine]["pallets"][pallet_id][item] == True:
                #                 with stylable_container(
                #                     "red",
                #                     css_styles="""
                #                     button {
                #                         background-color: red;
                #                         color: black;
                #                     }""",
                #                 ):
                #                     station_button = st.button(st.session_state['machine'], key=st.session_state['machine'])
                #             else:
                #                 with stylable_container(
                #                     "green",
                #                     css_styles="""
                #                     button {
                #                         background-color: green;
                #                         color: black;
                #                     }""",
                #                 ):
                #                     station_button = st.button(st.session_state['machine'], key=st.session_state['machine'])
                #     else:
                #         with stylable_container(
                #             "green",
                #             css_styles="""
                #             button {
                #                 background-color: green;
                #                 color: black;
                #             }""",
                #         ):
                #             station_button = st.button(st.session_state['machine'], key=st.session_state['machine'])

            # with stylable_container(
            #     "green",
            #     css_styles="""
            #     button {
            #         background-color: #00FF00;
            #         color: black;
            #     }""",
            # ):
            #     station_button = st.button(machineName, key=machineName)
            # with stylable_container(
            #     "red",
            #     css_styles="""
            #     button {
            #         background-color: #FF0000;

            #     }""",
            # ):
            #     station_button2 = st.button("Button 2", key="button2")
            # station_button = st.button(machineName, machineName, style="yellow")
            if station_button:
                # pallet_board(st.session_state['time'], pal["MachineName"], current_id)
                st.switch_page("pages/2Station_Management.py")
            

            # st.write(f"## ", station["MachineName"])
            # statuses = st.columns(2)
            # # html += f"<div class=wrapper_status>"
            # for i in range(2):
            #     if i == 0:
            #         current_state = "incoming"
            #         current_pallets = incoming_pallets
            #     else:
            #         current_state = "processing"
            #         current_pallets = processing_pallets
            #     with statuses[i]:
            #         # html += f"<div id='cd{i}'>"
            #         # html = f"{html}<h3 class='{current_state}-column' style='text-align: center'>{current_state}</h3>"
            #         # st.markdown(f"<h3 class='{current_state}-column' style='text-align: center'>{current_state}</h3>", unsafe_allow_html = True)
            #         st.write(f"### ", current_state)
            #         for index, pal in current_pallets.iterrows():
            #             # print("machineName", machineName)

            #             if(pal["MachineName"] == machineName and pal["Time"] == st.session_state['time']):
            #                 current_id = pal["pallet_id"]
            #                 st.session_state['pallet_id'] = current_id
            #                 # html = f"{html}<h4 class='{current_state}-data' style='text-align: center'>{current_id}</h4>"
            #                 # st.markdown(f"<h4 class='{current_state}-data' style='text-align: center'>{current_id}</h4>", unsafe_allow_html = True)
            #                 # st.write("#### ", current_id)
            #                 id_button = st.button(current_id, current_id)
            #                 if id_button:
            #                     # pallet_board(st.session_state['time'], pal["MachineName"], current_id)
            #                     st.switch_page("pages/pallet.py")
                    # html += f"</div>"
            # html += f"</div>"

            # html = f"{html}</div>"
            # st.markdown(f"</div>", unsafe_allow_html = True)
    
    # html = f"{html}</div>"
    # print(html)
    # st.markdown(html, unsafe_allow_html = True)

def pallet_board(time, machine, pallet_id): 
    # print("input_data: ", time, machine, pallet_id)
    data = load_data()

    st.write("## Pallet ID: ", pallet_id)
    st.write(time)
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
    # st.sidebar.header("Options")
    # option = st.sidebar.selectbox("Select Option", ["View Board", "Add Task"])
    
    # time_input = st.time_input('Time entry', step=5)
    # minhour = st.sidebar.time_input('Time', step=60)
    # interval = st.sidebar.slider('Time Range', min_value=0, max_value=50, step=10)

    # submit_time = st.sidebar.button("Select Time")
    # if submit_time:
    #     start_time = minhour + datetime.timedelta(seconds=interval)
    #     time_change = datetime.timedelta(seconds=10) 
    #     starttime += time_change
    #     end_time = start_time + time_change
    #     # time = f"{minhour + interval}:{interval}-{minhour}:{interval+10}"
    #     # new_time
    #     print(start_time, " ", end_time)

    # print(interval)

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
