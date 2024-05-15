import streamlit as st
from streamlit_extras.stylable_container import stylable_container


time = st.session_state['time']
machine = st.session_state['machine']
pallet_id = st.session_state['pallet_id']


processing_pallets = st.session_state['processing_pallets']
incoming_pallets =  st.session_state['incoming_pallets']


st.title("State Management")

# st.write(f"## ", station["MachineName"])
statuses = st.columns(2)
# html += f"<div class=wrapper_status>"
for i in range(2):
    if i == 0:
        current_state = "incoming"
        current_pallets = incoming_pallets
    else:
        current_state = "processing"
        current_pallets = processing_pallets
    with statuses[i]:
        # html += f"<div id='cd{i}'>"
        # html = f"{html}<h3 class='{current_state}-column' style='text-align: center'>{current_state}</h3>"
        # st.markdown(f"<h3 class='{current_state}-column' style='text-align: center'>{current_state}</h3>", unsafe_allow_html = True)
        st.write(f"### ", current_state)
        for index, pal in current_pallets.iterrows():
            # print("machineName", machineName)

            if(pal["MachineName"] == machine and pal["Time"] == st.session_state['time']):
                current_id = pal["pallet_id"]
                st.session_state['pallet_id'] = current_id
                # html = f"{html}<h4 class='{current_state}-data' style='text-align: center'>{current_id}</h4>"
                # st.markdown(f"<h4 class='{current_state}-data' style='text-align: center'>{current_id}</h4>", unsafe_allow_html = True)
                # st.write("#### ", current_id)

                # print(pal)

                # for item in pal:
                if pal["skipped_station"] == True or pal["wrong_station"] == True or pal["missing_qr_code"] == True:
                    with stylable_container(
                                    "red",
                                    css_styles="""
                                    button {
                                        background-color: red;
                                        color: black;
                                    }""",
                                ):
                                    id_button = st.button(current_id, key=current_id)
                else:
                    if pal["too_long_in_station"] == True or pal["too_short_in_station"] == True:
                        with stylable_container(
                                        "yellow",
                                        css_styles="""
                                        button {
                                            background-color: yellow;
                                            color: black;
                                        }""",
                                    ):
                                        id_button = st.button(current_id, key=current_id)
                    else:
                        with stylable_container(
                            "white",
                            css_styles="""
                            button {
                                background-color: white;
                                color: black;
                            }""",
                        ):
                          id_button = st.button(current_id, key=current_id)
                            
                # print("item", item)
                # if type(pal[item]) == bool and pal[item] == True:
                #     if item == "too_long_in_station" or item == "too_short_in_station":
                #     else:
                # else:
                #     id_button = st.button(current_id, key=current_id)
                          


                # id_button = st.button(current_id, current_id)
                if id_button:
                    # pallet_board(st.session_state['time'], pal["MachineName"], current_id)
                    st.switch_page("pages/3Pallet.py")
        
            # if data[time][st.session_state['machine']]["num_errors"] != 0:
            #     with stylable_container(
            #                     "red", 
            #                     css_styles="""
            #                     button {
            #                         background-color: red;
            #                         color: black;
            #                     }""",
            #                 ):
            #                     id_button = st.button(machineName, key=machineName)
            # else:
            #     if data[time][st.session_state['machine']]["num_warnings"] != 0:
            #         with stylable_container(
            #                         "yellow",
            #                         css_styles="""
            #                         button {
            #                             background-color: yellow;
            #                             color: black;
            #                         }""",
            #                     ):
            #                         id_button = st.button(machineName, key=machineName)
            #     else:
            #         with stylable_container(
            #                         "green",
            #                         css_styles="""
            #                         button {
            #                             background-color: green;
            #                             color: black;
            #                         }""",
            #                     ):
            #                         id_button = st.button(machineName, key=machineName)


going_back = st.button("Go to Dashboard")
if going_back:
    st.switch_page("Dashboard.py")