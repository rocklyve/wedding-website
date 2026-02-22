import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import pytz
import uuid
import random
import string
import extra_streamlit_components as stx

# CSV file path
CSV_FILE = st.secrets["files"]["csv_file"]

# Cookie manager (singleton)
@st.cache_resource
def get_cookie_manager():
    return stx.CookieManager()

def get_browser_id():
    """Get or create a persistent browser ID using cookies"""
    
    cookie_manager = get_cookie_manager()
    
    # Try to get existing cookie
    try:
        browser_id = cookie_manager.get(cookie='wedding_user_id')
        
        if browser_id:
            st.session_state.browser_id = browser_id
            st.session_state.browser_id_confirmed = True
            return browser_id
    except:
        pass
    
    # If we have it in session state, return it
    if 'browser_id' in st.session_state and st.session_state.get('browser_id_confirmed', False):
        return st.session_state.browser_id
    
    # Generate new ID if we don't have one
    if 'browser_id' not in st.session_state or not st.session_state.browser_id or st.session_state.browser_id.startswith('temp_'):
        new_id = 'usr_' + str(uuid.uuid4())[:12]
        st.session_state.browser_id = new_id
        
        # Set cookie
        try:
            cookie_manager.set(
                cookie='wedding_user_id',
                val=new_id,
                max_age=365 * 24 * 60 * 60,  # 1 year in seconds
                key='set_wedding_user_id'
            )
            st.session_state.browser_id_confirmed = True
        except:
            pass
        
        return new_id
    
    return st.session_state.get('browser_id', 'temp_' + str(uuid.uuid4())[:8])

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
