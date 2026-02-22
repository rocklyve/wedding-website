import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import pytz
import uuid
import random
import string
import streamlit.components.v1 as components

# CSV file path
CSV_FILE = st.secrets["files"]["csv_file"]

def get_browser_id():
    """Get or create a persistent browser ID using cookies"""
    
    # Check if we already have a stable ID in session state
    if 'browser_id' in st.session_state and st.session_state.get('browser_id_confirmed', False):
        return st.session_state.browser_id
    
    # JavaScript to manage cookies
    browser_id = components.html(
        """
        <script>
        function getCookie(name) {
            let value = "; " + document.cookie;
            let parts = value.split("; " + name + "=");
            if (parts.length === 2) return parts.pop().split(";").shift();
            return null;
        }
        
        function setCookie(name, value, days) {
            let date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            let expires = "expires=" + date.toUTCString();
            document.cookie = name + "=" + value + ";" + expires + ";path=/;SameSite=Lax";
        }
        
        // Get or create browser ID
        let browserId = getCookie('wedding_user_id');
        if (!browserId) {
            browserId = 'usr_' + Date.now().toString(36) + '_' + Math.random().toString(36).substr(2, 6);
            setCookie('wedding_user_id', browserId, 365);
        }
        
        // Return immediately - Streamlit will pick it up on next rerun
        const value = browserId;
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: value
        }, '*');
        
        // Also write to page for debugging
        document.write('<div style="display:none">ID:' + value + '</div>');
        </script>
        """,
        height=0,
    )
    
    # Convert to string if it's not None and not already a string
    if browser_id is not None:
        browser_id_str = str(browser_id) if not isinstance(browser_id, str) else browser_id
        
        # If we got a valid ID from the component, store and confirm it
        if browser_id_str and 'usr_' in browser_id_str:
            st.session_state.browser_id = browser_id_str
            st.session_state.browser_id_confirmed = True
            return browser_id_str
    
    # Return from session state if available
    if 'browser_id' in st.session_state:
        return st.session_state.browser_id
    
    # Generate temporary ID (will be replaced when component loads)
    temp_id = 'temp_' + str(uuid.uuid4())[:8]
    st.session_state.browser_id = temp_id
    return temp_id

def load_rsvps():
    """Load existing RSVP data from CSV file"""
    if os.path.exists(CSV_FILE):
        try:
            return pd.read_csv(CSV_FILE, dtype={'contact_phone': str})
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def save_rsvp(rsvp_data):
    """Save RSVP data to CSV file"""
    df = load_rsvps()
    new_df = pd.DataFrame([rsvp_data])
    df = pd.concat([df, new_df], ignore_index=True)
    # Ensure phone numbers are saved as strings
    if 'contact_phone' in df.columns:
        df['contact_phone'] = df['contact_phone'].astype(str)
    df.to_csv(CSV_FILE, index=False)

def save_rsvps(df):
    """Save entire RSVP dataframe to CSV file"""
    # Ensure phone numbers are saved as strings
    if 'contact_phone' in df.columns:
        df['contact_phone'] = df['contact_phone'].astype(str)
    df.to_csv(CSV_FILE, index=False)

# Deadline utility functions
def get_deadline_datetime():
    """Get the deadline datetime from secrets configuration"""
    try:
        deadline_str = st.secrets["deadline"]["deadline_datetime"]
        timezone_str = st.secrets["deadline"].get("timezone", "UTC")

        # Parse the deadline string
        deadline_naive = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")

        # Add timezone
        tz = pytz.timezone(timezone_str)
        deadline_tz = tz.localize(deadline_naive)

        return deadline_tz
    except Exception as e:
        st.error(f"Error parsing deadline configuration: {e}")
        return None

def is_past_deadline():
    """Check if the current time is past the RSVP deadline"""
    deadline = get_deadline_datetime()
    if deadline is None:
        return False

    now = datetime.now(deadline.tzinfo)
    return now > deadline

def is_within_grace_period():
    """Check if we're within the admin grace period after deadline"""
    if not is_past_deadline():
        return False

    deadline = get_deadline_datetime()
    if deadline is None:
        return False

    grace_hours = st.secrets["deadline"].get("grace_period_hours", 24)
    grace_period = timedelta(hours=grace_hours)

    now = datetime.now(deadline.tzinfo)
    return now <= (deadline + grace_period)

def is_within_warning_period():
    """Check if we're within the warning period before deadline"""
    deadline = get_deadline_datetime()
    if deadline is None:
        return False

    warning_days = st.secrets["deadline"].get("warning_days", 7)
    warning_period = timedelta(days=warning_days)

    now = datetime.now(deadline.tzinfo)
    return (deadline - warning_period) <= now <= deadline

def get_time_until_deadline():
    """Get the time remaining until the deadline"""
    deadline = get_deadline_datetime()
    if deadline is None:
        return None

    now = datetime.now(deadline.tzinfo)
    if now > deadline:
        return timedelta(0)  # Past deadline

    return deadline - now

def format_time_remaining(time_delta):
    """Format time remaining in a human-readable format"""
    if time_delta is None:
        return "Unknown"

    if time_delta.total_seconds() <= 0:
        return "Deadline has passed"

    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        return f"{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"

# Gift Registry utility functions
GIFT_REGISTRY_FILE = "gift_registry.csv"

def load_gift_registry():
    """Load gift registry data from CSV file"""
    if os.path.exists(GIFT_REGISTRY_FILE):
        try:
            df = pd.read_csv(GIFT_REGISTRY_FILE)
            # Ensure purchased column is boolean
            df['purchased'] = df['purchased'].astype(bool)
            return df
        except Exception as e:
            st.error(f"Error loading gift registry: {e}")
            return pd.DataFrame(columns=['name', 'description', 'url', 'image_url', 'purchased', 'session_id'])
    return pd.DataFrame(columns=['name', 'description', 'url', 'image_url', 'purchased', 'session_id'])

def save_gift_registry(df):
    """Save gift registry dataframe to CSV file"""
    try:
        df.to_csv(GIFT_REGISTRY_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving gift registry: {e}")
        return False

def mark_gift_as_purchased(gift_index):
    """Mark a gift as purchased by the current browser"""
    df = load_gift_registry()
    browser_id = get_browser_id()
    
    # Debug logging
    print(f"[DEBUG] Marking gift {gift_index} as purchased by {browser_id}")
    
    if 0 <= gift_index < len(df):
        df.at[gift_index, 'purchased'] = True
        df.at[gift_index, 'session_id'] = browser_id
        result = save_gift_registry(df)
        print(f"[DEBUG] Save result: {result}")
        return result
    print(f"[DEBUG] Invalid gift index: {gift_index}")
    return False

def unmark_gift_as_purchased(gift_index):
    """Unmark a gift as purchased - only if the browser ID matches"""
    df = load_gift_registry()
    browser_id = get_browser_id()
    
    if 0 <= gift_index < len(df):
        # Check if the browser ID matches
        stored_browser = str(df.at[gift_index, 'session_id']).strip()
        current_browser = browser_id
        
        # Debug logging
        print(f"[DEBUG] Unmark attempt - Stored: {stored_browser}, Current: {current_browser}, Match: {stored_browser == current_browser}")
        
        if stored_browser == current_browser:
            df.at[gift_index, 'purchased'] = False
            df.at[gift_index, 'session_id'] = ''
            return save_gift_registry(df)
        else:
            return False  # Browser doesn't match
    return False

def can_undo_purchase(gift_index):
    """Check if the current browser can undo the purchase of this gift"""
    df = load_gift_registry()
    browser_id = get_browser_id()
    
    if 0 <= gift_index < len(df):
        stored_browser = str(df.at[gift_index, 'session_id']).strip()
        current_browser = browser_id
        can_undo = stored_browser == current_browser
        
        # Debug logging
        print(f"[DEBUG] Can undo check - Index: {gift_index}, Stored: {stored_browser}, Current: {current_browser}, Result: {can_undo}")
        
        return can_undo
    return False
