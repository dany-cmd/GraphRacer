import streamlit as st

time = st.session_state['time']
machine = st.session_state['machine']
pallet_id = st.session_state['pallet_id']

data = st.session_state['data']

st.write("## Pallet ID: ", pallet_id)
st.write(time)
st.write(machine)
for item in data[time][machine]["pallets"][pallet_id]:
    string = f"{item}: "
    string += str(data[time][machine]["pallets"][pallet_id][item])
    if type(data[time][machine]["pallets"][pallet_id][item]) == bool and data[time][machine]["pallets"][pallet_id][item] == True:
        if item == "too_long_in_station" or item == "too_short_in_station":
            st.markdown(f"<p style='color: yellow'>{string}</p>", unsafe_allow_html = True)
        else:
            st.markdown(f"<p style='color: red'>{string}</p>", unsafe_allow_html = True)
    else:
        st.write(item, ": ", data[time][machine]["pallets"][pallet_id][item])

going_back = st.button("Go to Pallet")
if going_back:
    st.switch_page("pages/2Station_Management.py")
