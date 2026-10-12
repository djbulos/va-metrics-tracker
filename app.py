import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

# Configure the page
st.set_page_config(page_title="VA Performance Tracker", layout="wide")

# Initialize a session state to hold our data temporarily 
# (In production, we will connect this to a Google Sheet or database)
if 'metrics_data' not in st.session_state:
    st.session_state.metrics_data = pd.DataFrame(columns=[
        'Date', 'VA Name', 'Report Type', 'Dials', 'Contacts', 'Appointments', 'Transfers', 'Weekly Bookings'
    ])

st.title("📊 VA Performance Tracker")

# Create tabs for the interface
tab1, tab2 = st.tabs(["📝 Data Entry (VAs)", "📈 Boss's Dashboard"])

# --- TAB 1: DATA ENTRY FOR VAs ---
with tab1:
    st.header("Daily & Weekly Shift Report")
    st.write("Please submit your numbers before the end of your shift.")
    
    with st.form("data_entry_form"):
        date_input = st.date_input("Date", datetime.date.today())
        va_name = st.selectbox("VA Name", ["", "Harley", "Cindy", "Beth", "Other"])
        
        report_type = st.radio("Is this a daily report or the end-of-week Friday report?", 
                               ["Daily Shift (End of Shift)", "Weekly Summary (Friday)"])
        
        st.markdown("### Daily Metrics")
        col1, col2 = st.columns(2)
        with col1:
            dials = st.number_input("Total Dials", min_value=0, step=1)
            contacts = st.number_input("Total Contacts", min_value=0, step=1)
        with col2:
            appointments = st.number_input("Appointments Booked", min_value=0, step=1)
            transfers = st.number_input("Total Transfers", min_value=0, step=1)
            
        st.markdown("### Weekly Metrics")
        weekly_bookings = st.number_input("Total Bookings Across All Boards (Fridays Only)", 
                                          min_value=0, step=1, 
                                          help="Only fill this out on your Friday end-of-shift report.")
        
        submitted = st.form_submit_button("Submit Report")
        
        if submitted:
            if va_name == "":
                st.error("Please select your name before submitting.")
            else:
                # Save the data
                new_data = pd.DataFrame({
                    'Date': [date_input],
                    'VA Name': [va_name],
                    'Report Type': [report_type],
                    'Dials': [dials],
                    'Contacts': [contacts],
                    'Appointments': [appointments],
                    'Transfers': [transfers],
                    'Weekly Bookings': [weekly_bookings if "Weekly" in report_type else 0]
                })
                st.session_state.metrics_data = pd.concat([st.session_state.metrics_data, new_data], ignore_index=True)
                st.success(f"✅ Report successfully submitted for {va_name}!")

# --- TAB 2: DASHBOARD & EXPORT ---
with tab2:
    st.header("Executive Dashboard")
    st.write("Overview of all VA metrics.")
    
    if not st.session_state.metrics_data.empty:
        # Display summary metrics at the top
        st.subheader("Global Totals (All Time)")
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        metric_col1.metric("Total Dials", st.session_state.metrics_data['Dials'].sum())
        metric_col2.metric("Total Contacts", st.session_state.metrics_data['Contacts'].sum())
        metric_col3.metric("Total Appointments", st.session_state.metrics_data['Appointments'].sum())
        metric_col4.metric("Total Transfers", st.session_state.metrics_data['Transfers'].sum())
        
        st.markdown("---")
        st.subheader("Raw Data Table")
        st.dataframe(st.session_state.metrics_data, use_container_width=True)
        
        # --- EXCEL EXPORT FEATURE ---
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Metrics')
            processed_data = output.getvalue()
            return processed_data
            
        excel_data = to_excel(st.session_state.metrics_data)
        
        st.download_button(
            label="📥 Export Dashboard to Excel",
            data=excel_data,
            file_name=f"VA_Metrics_Report_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No data submitted yet. Once the VAs submit their shift reports, the dashboard will populate here.")