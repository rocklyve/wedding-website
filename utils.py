import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import pytz
import uuid

# CSV file path
CSV_FILE = st.secrets["files"]["csv_file"]

def get_browser_id():
    """Get or create a persistent browser ID using query params"""
    
    # Initialize from query params if not in session state
    if 'browser_id' not in st.session_state:
        # Try to get from URL query params
        browser_id = st.query_params.get('uid', None)
        
        if browser_id:
            st.session_state.browser_id = browser_id
            print(f"[DEBUG] Loaded browser ID from query params: {browser_id}")
        else:
            # Generate new ID
            new_id = 'usr_' + str(uuid.uuid4())[:12]
            st.session_state.browser_id = new_id
            st.query_params['uid'] = new_id
            print(f"[DEBUG] Generated new browser ID: {new_id}")
    
    return st.session_state.browser_id

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
            df = pd.read_csv(GIFT_REGISTRY_FILE, sep=';')
            # Ensure purchased column is boolean
            df['purchased'] = df['purchased'].astype(bool)
            
            # Add quantity columns if they don't exist
            if 'quantity_total' not in df.columns:
                df['quantity_total'] = 1
            if 'quantity_purchased' not in df.columns:
                df['quantity_purchased'] = 0
            
            # Fill NaN values with defaults
            df['quantity_total'] = df['quantity_total'].fillna(1).astype(int)
            df['quantity_purchased'] = df['quantity_purchased'].fillna(0).astype(int)
            
            return df
        except Exception as e:
            st.error(f"Error loading gift registry: {e}")
            return pd.DataFrame(columns=['name', 'description', 'url', 'image_url', 'purchased', 'session_id', 'quantity_total', 'quantity_purchased'])
    return pd.DataFrame(columns=['name', 'description', 'url', 'image_url', 'purchased', 'session_id', 'quantity_total', 'quantity_purchased'])

def save_gift_registry(df):
    """Save gift registry dataframe to CSV file"""
    try:
        df.to_csv(GIFT_REGISTRY_FILE, index=False, sep=';')
        return True
    except Exception as e:
        st.error(f"Error saving gift registry: {e}")
        return False

def mark_gift_as_purchased(gift_index, quantity=1):
    """Mark a gift as purchased by the current browser with specified quantity"""
    df = load_gift_registry()
    browser_id = get_browser_id()
    
    # Debug logging
    print(f"[DEBUG] Marking gift {gift_index} as purchased by {browser_id}, quantity: {quantity}")
    
    if 0 <= gift_index < len(df):
        # Update quantity purchased
        current_purchased = int(df.at[gift_index, 'quantity_purchased'])
        total_available = int(df.at[gift_index, 'quantity_total'])
        
        # Don't allow purchasing more than available
        new_purchased = min(current_purchased + quantity, total_available)
        
        df.at[gift_index, 'quantity_purchased'] = new_purchased
        df.at[gift_index, 'session_id'] = browser_id
        
        # Mark as fully purchased if quantity reached
        if new_purchased >= total_available:
            df.at[gift_index, 'purchased'] = True
        
        result = save_gift_registry(df)
        print(f"[DEBUG] Save result: {result}, new quantity: {new_purchased}/{total_available}")
        return result
    print(f"[DEBUG] Invalid gift index: {gift_index}")
    return False

def unmark_gift_as_purchased(gift_index, quantity=None):
    """Unmark a gift as purchased - only if the browser ID matches
    If quantity is None, removes all purchases by this user
    If quantity is specified, removes that many items
    """
    df = load_gift_registry()
    browser_id = get_browser_id()
    
    if 0 <= gift_index < len(df):
        # Check if the browser ID matches (last purchaser)
        stored_browser = str(df.at[gift_index, 'session_id']).strip()
        current_browser = browser_id
        
        # Debug logging
        print(f"[DEBUG] Unmark attempt - Stored: {stored_browser}, Current: {current_browser}, Match: {stored_browser == current_browser}")
        
        if stored_browser == current_browser:
            current_purchased = int(df.at[gift_index, 'quantity_purchased'])
            
            if quantity is None:
                # Remove all
                df.at[gift_index, 'quantity_purchased'] = 0
                df.at[gift_index, 'purchased'] = False
                df.at[gift_index, 'session_id'] = ''
            else:
                # Remove specified quantity
                new_purchased = max(0, current_purchased - quantity)
                df.at[gift_index, 'quantity_purchased'] = new_purchased
                
                # Update purchased flag
                total_available = int(df.at[gift_index, 'quantity_total'])
                df.at[gift_index, 'purchased'] = (new_purchased >= total_available)
                
                # Clear session_id if fully unmarked
                if new_purchased == 0:
                    df.at[gift_index, 'session_id'] = ''
            
            return save_gift_registry(df)
        else:
            return False  # Browser doesn't match
    return False

def can_undo_purchase(gift_index):
    """Check if the current browser can undo the purchase of this gift
    Only the last purchaser can undo
    """
    df = load_gift_registry()
    browser_id = get_browser_id()
    
    if 0 <= gift_index < len(df):
        # Check if there are any purchases first
        quantity_purchased = int(df.at[gift_index, 'quantity_purchased'])
        if quantity_purchased == 0:
            return False
        
        stored_browser = str(df.at[gift_index, 'session_id']).strip()
        current_browser = browser_id
        can_undo = stored_browser == current_browser
        
        # Debug logging
        print(f"[DEBUG] Can undo check - Index: {gift_index}, Stored: {stored_browser}, Current: {current_browser}, Result: {can_undo}")
        
        return can_undo
    return False

def get_remaining_quantity(gift_index):
    """Get the remaining quantity available for a gift"""
    df = load_gift_registry()
    
    if 0 <= gift_index < len(df):
        total = int(df.at[gift_index, 'quantity_total'])
        purchased = int(df.at[gift_index, 'quantity_purchased'])
        return max(0, total - purchased)
    return 0
