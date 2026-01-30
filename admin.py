import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import toml
import os

# Import shared utilities
from utils import (
    load_rsvps, save_rsvps, get_deadline_datetime, is_past_deadline,
    get_time_until_deadline, format_time_remaining
)

# Admin password (configured in secrets.toml)
ADMIN_PASSWORD = st.secrets["admin"]["password"]

def show_login_success():
    """Display a simple login success acknowledgment"""
    st.success(":material/check_circle: Welcome to Admin Dashboard!")
    st.info("You now have access to all RSVP management features.")
    time.sleep(1)

def admin_welcome_header():
    """Display a welcome header for authenticated admin users"""
    st.info(":material/admin_panel_settings: **Welcome, Admin!** You are logged in to the Wedding RSVP Management System")

def admin_login_page():
    """Admin login page"""
    st.title(":material/lock: Admin Login")
    st.write("Please enter the password to access the RSVP admin dashboard.")

    # Use a form to enable Enter key submission
    with st.form("admin_login_form"):
        password = st.text_input("Password:", type="password", key="admin_password_input")
        submit_button = st.form_submit_button("Login", type="primary")

    if submit_button:
        if password == ADMIN_PASSWORD:
            # Set authentication state
            st.session_state.authenticated = True
            st.session_state.just_logged_in = True

            # Show login success
            show_login_success()
            st.rerun()
        else:
            st.error(":material/cancel: Incorrect password. Please try again.")

    st.markdown("---")
    st.info(":material/lightbulb: If you're a guest looking to submit your RSVP, please use the RSVP form instead.")

def admin_summary_page():
    """Admin summary page"""
    if not st.session_state.authenticated:
        st.error(":material/lock: Please log in to access this page.")
        st.stop()
    
    # Show welcome header for authenticated users
    admin_welcome_header()
    
    # Check if user just logged in to show additional acknowledgment
    if st.session_state.get('just_logged_in', False):
        st.success(":material/target: Successfully accessed RSVP Summary Dashboard!")
        st.session_state.just_logged_in = False  # Reset the flag
    
    st.title(f":material/bar_chart: RSVP Summary: (Time Zone: ({st.secrets['deadline'].get('timezone', 'UTC')})")

    # Display deadline status
    deadline = get_deadline_datetime()
    if deadline:
        col1, col2 = st.columns(2)

        with col1:
            if is_past_deadline():
                st.error(f":material/schedule: **Deadline has passed**")
                st.write(f"Deadline was: {deadline.strftime('%B %d, %Y at %I:%M %p %Z')}")

                # Check if still in grace period
                grace_hours = st.secrets["deadline"].get("grace_period_hours", 24)
                grace_end = deadline + timedelta(hours=grace_hours)
                now = datetime.now(deadline.tzinfo)

                if now <= grace_end:
                    st.warning(f":material/timer: Still in grace period until: {grace_end.strftime('%B %d, %Y at %I:%M %p %Z')}")
                else:
                    st.info(":material/block: Grace period has also ended")
            else:
                time_remaining = get_time_until_deadline()
                formatted_time = format_time_remaining(time_remaining)
                st.success(f":material/schedule: **Deadline is active**")
                st.error(f"Deadline: {deadline.strftime('%B %d, %Y at %I:%M %p %Z')}")
                st.info(f"Time remaining: {formatted_time}")

        with col2:
            # Deadline configuration display
            st.info(":material/settings: **Deadline Configuration**")
            warning_days = st.secrets["deadline"].get("warning_days", 7)
            grace_hours = st.secrets["deadline"].get("grace_period_hours", 24)

            st.warning(f"Warning period: {warning_days} days before deadline")
            st.warning(f"Grace period: {grace_hours} hours after deadline")

        st.markdown("---")

    # Load data
    df = load_rsvps()
    
    if not df.empty:
        # Summary statistics
        st.write("**RSVP Overview**")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_contacts = df['contact_name'].nunique()
        attending_contacts = df[df['attending'] == 'Yes']['contact_name'].nunique()
        not_attending_contacts = df[df['attending'] == 'No']['contact_name'].nunique()
        total_guests = len(df[df['attending'] == 'Yes'])
        
        with col1:
            st.metric("Total Responses", total_contacts)
        with col2:
            st.metric("Attending", attending_contacts)
        with col3:
            st.metric("Not Attending", not_attending_contacts)
        with col4:
            st.metric("Total Guests", total_guests)
        
        # Attendance breakdown
        # if total_contacts > 0:
        #     st.subheader("Response Breakdown")
        #     attendance_data = {
        #         'Response': ['Attending', 'Not Attending'],
        #         'Count': [attending_contacts, not_attending_contacts]
        #     }
        #     st.bar_chart(pd.DataFrame(attendance_data).set_index('Response'))
        
        # Recent RSVPs
        #st.subheader("Recent RSVPs")
        recent_df = df.sort_values('timestamp', ascending=False).head(10)
        st.divider()
        for _, row in recent_df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{row['contact_name']}**")
                    if row['attending'] == 'Yes' and (row.get('guest_first_name') or row.get('guest_last_name')):
                        guest_name = f"{row.get('guest_first_name', '')} {row.get('guest_last_name', '')}".strip()
                        st.write(f":material/person: {guest_name}")
                with col2:
                    status_color = ":material/check_circle:" if row['attending'] == 'Yes' else ":material/cancel:"
                    st.write(f"{status_color} {row['attending']}")
                    
                    # Fixed comments handling
                    if pd.notna(row['comments']) and str(row['comments']).strip():
                        st.write(f":material/chat_bubble: _{row['comments']}_")
                    else:
                        st.write(":material/chat_bubble_outline: No comments")
                        
                with col3:
                    st.write(f":material/date_range: *{row['timestamp'].split()[0]}*")  # Just the date

                st.markdown("---")
    else:
        st.info(":material/inbox: No RSVPs have been submitted yet.")

def admin_menu_page():
    """Admin menu planning page"""
    if not st.session_state.authenticated:
        st.error(":material/lock: Please log in to access this page.")
        st.stop()
    
    # Show welcome header for authenticated users
    admin_welcome_header()
    
    st.title(":material/restaurant: Menu Planning")

    # Load data
    df = load_rsvps()

    # Check if dataframe is empty or missing required columns
    if df.empty or 'attending' not in df.columns:
        st.info(":material/inbox: No attending guests yet to display menu planning data.")
        return

    total_guests = len(df[df['attending'] == 'Yes'])

    if total_guests > 0:
        attending_df = df[df['attending'] == 'Yes']
        
        # Menu summary in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader(":material/restaurant: Starters")
            starter_counts = attending_df['starter_choice'].value_counts()
            for starter, count in starter_counts.items():
                st.write(f"**{starter}:** {count} guests")
            
            # Chart
            if not starter_counts.empty:
                st.bar_chart(starter_counts)
        
        with col2:
            st.subheader(":material/dinner_dining: Main Courses")
            main_counts = attending_df['main_choice'].value_counts()
            for main, count in main_counts.items():
                st.write(f"**{main}:** {count} guests")
            
            # Chart
            if not main_counts.empty:
                st.bar_chart(main_counts)
        
        with col3:
            st.subheader(":material/cake: Desserts")
            dessert_counts = attending_df['dessert_choice'].value_counts()
            for dessert, count in dessert_counts.items():
                st.write(f"**{dessert}:** {count} guests")
            
            # Chart
            if not dessert_counts.empty:
                st.bar_chart(dessert_counts)
        
        # Dietary requirements
        st.subheader(":material/health_and_safety: Dietary Requirements & Allergies")
        dietary_df = attending_df[attending_df['dietary_requirements'].notna() & 
                                (attending_df['dietary_requirements'] != '')]
        
        if not dietary_df.empty:
            for _, row in dietary_df.iterrows():
                guest_name = f"{row.get('guest_first_name', '')} {row.get('guest_last_name', '')}".strip()
                st.write(f"**{guest_name}:** {row['dietary_requirements']}")
        else:
            st.write("No special dietary requirements reported.")
    else:
        st.info("No attending guests yet to display menu planning data.")

def admin_data_page():
    """Admin detailed data page"""
    if not st.session_state.authenticated:
        st.error(":material/lock: Please log in to access this page.")
        st.stop()
    
    # Show welcome header for authenticated users
    admin_welcome_header()
    
    st.title(":material/description: Detailed Data")
    
    # Load data
    df = load_rsvps()
    
    if not df.empty:
        # Export functionality
        st.write("**:material/download: Export Data**")
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label=":material/description: Download All Data (CSV)",
                data=csv,
                file_name=f"wedding_rsvps_all_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Export only attending guests
            attending_df = df[df['attending'] == 'Yes']
            if not attending_df.empty:
                attending_csv = attending_df.to_csv(index=False)
                st.download_button(
                    label=":material/check_circle: Download Attending Only (CSV)",
                    data=attending_csv,
                    file_name=f"wedding_rsvps_attending_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        # Search and filter
        st.write("**:material/search: Search & Filter**")
        search_term = st.text_input("Search by contact name or guest name:")
        
        filtered_df = df
        if search_term:
            filtered_df = df[
                df['contact_name'].str.contains(search_term, case=False, na=False) |
                df['guest_first_name'].str.contains(search_term, case=False, na=False) |
                df['guest_last_name'].str.contains(search_term, case=False, na=False)
            ]
        
        # Display data table
        st.write("**:material/table_view: Complete RSVP Data**")
        if not filtered_df.empty:
            edited_df = st.data_editor(
                filtered_df,
                width="content",
                column_config={
                    "timestamp": "Submitted",
                    "contact_name": "Contact",
                    "contact_email": "Email",
                    "contact_phone": "Phone",
                    "attending": "Status",
                    "guest_first_name": "First Name",
                    "guest_last_name": "Last Name",
                    "starter_choice": "Starter",
                    "main_choice": "Main",
                    "dessert_choice": "Dessert",
                    "dietary_requirements": "Dietary Notes",
                    "comments": "Comments"
                }
            )

            st.write(f"Showing {len(filtered_df)} of {len(df)} total responses")

            # Save button to persist changes
            if st.button(":material/save: Save Changes", type="primary"):
                # Update the original dataframe with edited values
                if search_term:
                    # If filtered, update only the filtered rows in the original df
                    df.update(edited_df)
                else:
                    # If not filtered, replace the entire dataframe
                    df = edited_df

                save_rsvps(df)
                st.success(":material/check_circle: Changes saved successfully!")
                st.rerun()
        else:
            st.write("No data matches your search criteria.")
    else:
        st.info(":material/inbox: No RSVPs have been submitted yet.")