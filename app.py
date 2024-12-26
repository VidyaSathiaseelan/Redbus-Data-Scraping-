import streamlit as st
import pandas as pd
import pymysql

with st.container():
    col1,col2 = st.columns([1,6])
    with col1:
        st.image("C:/Users/Sathiaseelan/Pictures/redbus logo.png",width=100)
    with col2:
        st.header(":red[Redbus]",divider = True)

#Database Connection
myconnection = pymysql.connect(host='127.0.0.1',user='root',passwd='Mainboot@1', database='Redbus')
mycursor = myconnection.cursor()

#State Selection
query = "Select distinct state from bus_routes_state"
mycursor.execute(query)
data = mycursor.fetchall()
for i in data:
    state_names = [i[0] for i in data] 
State_Selected = st.selectbox("Select Your Route",(state_names))

#Route Selection
query = f"Select distinct route_name from bus_routes_state where state = '{State_Selected}'"
mycursor.execute(query)
data = mycursor.fetchall()
for i in data:
    route_names = [i[0] for i in data] 
Route_Selected = st.selectbox("Select Your Route",(route_names))
query = f"Select Bus_Name,Bus_Type,Departing_Time,Duration,Reaching_Time,Star_Rating,Price,Seats_Availability from bus_routes where Route_Name ='{Route_Selected}'"
mycursor.execute(query)
df = pd.DataFrame(mycursor.fetchall(), columns=['Bus_Name', 'Bus_Type', 'Departing_Time', 'Duration', 'Reaching_Time','Star_Rating', 'Price', 'Seats_Availability'])
df['Reaching_Time'] = df['Reaching_Time'].apply(lambda x: str(x).split()[2])
df['Departing_Time'] = df['Departing_Time'].apply(lambda x: str(x).split()[2])

st.sidebar.write(":red[Filter your preferences here!]")

price_selected = st.sidebar.number_input("Enter your price range", min_value = 200, max_value = 10000, value = 500, step = 100)
filtered_df = df[(df['Price']<=price_selected)]

start, end = st.sidebar.select_slider(
    "Select the star rating preferred",
    options=[0,1,2,3,4,5],
    value=(0, 5),)
filtered_df = filtered_df[(filtered_df['Star_Rating'] >= start) & (filtered_df['Star_Rating'] <= end)]

st.sidebar.write("Tell us your bus type preferences")
# selected_bus_types = []
selected_bus_types1 = st.sidebar.radio("Tell us your preferred condition",("Non AC","AC"))
selected_bus_types2 = st.sidebar.radio("Tell us your preferred seat type",("Seater","Sleeper"))
if selected_bus_types1 == "AC":
    condition1 = ((filtered_df['Bus_Type'].str.contains(r"AC", case=False, na=False)) | (filtered_df['Bus_Type'].str.contains(r"A/C", case=False, na=False))
) & ~filtered_df['Bus_Type'].str.contains(r"Non", case=False, na=False)
elif selected_bus_types1 == "Non AC":
    condition1 = filtered_df['Bus_Type'].str.contains(r"Non AC", case=False, na=False)  # Exact match for 'Non AC'
# Check if selected_bus_types2 is "Seater" or "Sleeper"
if selected_bus_types2 == "Seater":
    condition2 = filtered_df['Bus_Type'].str.contains(r"Seater", case=False, na=False)  # Exact match for 'Seater'
elif selected_bus_types2 == "Sleeper":
    condition2 = filtered_df['Bus_Type'].str.contains(r"Sleeper", case=False, na=False)  # Exact match for 'Sleeper'

# Combine conditions to filter the DataFrame
filtered_df = filtered_df[condition1 & condition2]

time_p = st.sidebar.time_input("Tell us your timing preferred",value = pd.to_datetime("18:00:00").time())
time_p = str(time_p)
condition = filtered_df['Departing_Time'] >= time_p
filtered_df = filtered_df[condition]

# Pagination settings
items_per_page = 10
total_items = len(filtered_df)
total_pages = (total_items // items_per_page) + (1 if total_items % items_per_page != 0 else 0)

# Initialize the page state if it does not exist
if 'page' not in st.session_state:
    st.session_state.page = 0

# Show the current page's data
start_idx = st.session_state.page * items_per_page
end_idx = start_idx + items_per_page
current_page_data = filtered_df.iloc[start_idx:end_idx]

# Display the data for the current page
st.dataframe(current_page_data)

# Page navigation buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Previous", disabled=st.session_state.page == 0):
        st.session_state.page -= 1

with col2:
    if st.button("Next", disabled=st.session_state.page == total_pages-1):
        st.session_state.page += 1

# Display current page number
st.write(f"Page {st.session_state.page + 1} of {total_pages}")
    