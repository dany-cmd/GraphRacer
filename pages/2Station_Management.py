import streamlit as st
from streamlit_extras.stylable_container import stylable_container


time = st.session_state['time']
machine = st.session_state['machine']
pallet_id = st.session_state['pallet_id']


processing_pallets = st.session_state['processing_pallets']
incoming_pallets =  st.session_state['incoming_pallets']


st.title("Station Management")
st.write("## ", machine)

statuses = st.columns(2)
for i in range(2):
    if i == 0:
        current_state = "incoming"
        current_pallets = incoming_pallets
    else:
        current_state = "processing"
        current_pallets = processing_pallets
    with statuses[i]:
        st.write(f"### ", current_state)
        for index, pal in current_pallets.iterrows():

            if(pal["MachineName"] == machine and pal["Time"] == st.session_state['time']):
                current_id = pal["pallet_id"]
                st.session_state['pallet_id'] = current_id
    
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
                            
                if id_button:
                    st.switch_page("pages/3Pallet.py")
        
going_back = st.button("Go to Dashboard")
if going_back:
    st.switch_page("Dashboard.py")