import streamlit as st
from datetime import datetime, timedelta

# Import admin functions
from admin import admin_login_page, admin_summary_page, admin_menu_page, admin_data_page
from admin_settings import admin_settings_page

# Import event info page
from event_info import event_info_page

# Import shared utilities
from utils import (
    save_rsvp, get_deadline_datetime, is_past_deadline,
    is_within_grace_period, is_within_warning_period, get_time_until_deadline,
    format_time_remaining
)

# Configure the page
st.set_page_config(
    page_title=st.secrets["wedding"]["page_title"],
    page_icon=st.secrets["wedding"]["page_icon"],
    initial_sidebar_state="collapsed",
    layout="wide"
)

# Constants
MAX_GUESTS_FOR_CLEANUP = 20  # Maximum number of guests to clear from session state
COLUMN_RATIO_HEADER = [2.5, 1]  # Column ratio for header layout
COLUMN_RATIO_CONTACT = [3, 4, 2]  # Column ratio for contact information
COLUMN_RATIO_GUEST = [3, 1]  # Column ratio for guest details
COLUMN_RATIO_MENU = [1.2, 1.8, 1.1]  # Column ratio for menu selections

# Menu options
STARTERS = st.secrets["menu"]["starters"]
MAINS = st.secrets["menu"]["mains"]
DESSERTS = st.secrets["menu"]["desserts"]

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'guests': [{}],
        'form_submitted': False,
        'submission_in_progress': False,
        'authenticated': False,
        'form_data': {}
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def add_guest():
    """Add a new guest to the session state"""
    if not st.session_state.submission_in_progress:
        st.session_state.guests.append({})

def remove_guest(index):
    """Remove a guest from the session state"""
    if len(st.session_state.guests) > 1 and not st.session_state.submission_in_progress:
        st.session_state.guests.pop(index)

def reset_form():
    """Reset the form after submission"""
    # Reset main form state
    form_state_reset = {
        'guests': [{}],
        'form_submitted': False,
        'submission_in_progress': False,
        'form_data': {}
    }

    for key, value in form_state_reset.items():
        st.session_state[key] = value

    # Clear form fields
    form_keys = ["attending", "contact_name", "contact_email", "contact_phone", "comments"]

    # Add guest-specific fields
    for i in range(MAX_GUESTS_FOR_CLEANUP):
        form_keys.extend([
            f"guest_first_name_{i}", f"guest_last_name_{i}",
            f"starter_{i}", f"main_{i}", f"dessert_{i}", f"dietary_{i}"
        ])

    # Remove the keys from session state
    for key in form_keys:
        st.session_state.pop(key, None)

def process_submission():
    """Process the RSVP submission"""
    form_data = st.session_state.form_data

    # Check deadline enforcement first
    if is_past_deadline() and not is_within_grace_period():
        st.error(":material/block: Die Anmeldefrist für die Zusage ist abgelaufen. Zusagen werden nicht mehr angenommen.")
        st.info("Bitte kontaktieren Sie das Hochzeitspaar direkt, wenn Sie Ihre Zusage noch ändern möchten.")
        st.session_state.submission_in_progress = False
        return False

    # Show warning if in grace period
    if is_within_grace_period():
        st.warning(":material/timer: Sie befinden sich in der Nachfrist – die Anmeldefrist ist abgelaufen, aber Zusagen werden noch angenommen.")

    # Show urgency warning if within warning period
    if is_within_warning_period():
        time_remaining = get_time_until_deadline()
        formatted_time = format_time_remaining(time_remaining)
        st.warning(f":material/schedule: Die Anmeldefrist endet bald – noch {formatted_time} übrig!")

    # Validation
    errors = []
    
    if not form_data.get('contact_name', '').strip():
        errors.append("Name der Hauptkontaktperson ist erforderlich")
    
    if form_data.get('attending') == "Ja, ich/wir nehme(n) teil":
        for i, _ in enumerate(st.session_state.guests):
            guest_first_name = form_data.get(f"guest_first_name_{i}", "")
            guest_last_name = form_data.get(f"guest_last_name_{i}", "")
            # No menu selection validation
            if not guest_first_name.strip():
                errors.append(f"Vorname von Gast {i + 1} ist erforderlich")
            if not guest_last_name.strip():
                errors.append(f"Nachname von Gast {i + 1} ist erforderlich")
    
    if errors:
        st.error("Bitte beheben Sie die folgenden Fehler:")
        for error in errors:
            st.error(f"• {error}")
        
        # Reset submission state on error
        st.session_state.submission_in_progress = False
        return False
    
    # Prepare data for saving
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        if form_data.get('attending') == "Ja, ich/wir nehme(n) teil":
            # Save each guest as a separate row
            for i, _ in enumerate(st.session_state.guests):
                rsvp_data = {
                    "timestamp": timestamp,
                    "contact_name": form_data.get('contact_name', '').strip(),
                    "contact_email": form_data.get('contact_email', '').strip(),
                    "contact_phone": form_data.get('contact_phone', '').strip(),
                    "attending": "Ja",
                    "guest_first_name": form_data.get(f"guest_first_name_{i}", "").strip(),
                    "guest_last_name": form_data.get(f"guest_last_name_{i}", "").strip(),
                    "essenspräferenz": form_data.get(f"preference_{i}", "Keine"),
                    "dietary_requirements": form_data.get(f"dietary_{i}", "").strip(),
                    "comments": form_data.get('comments', '').strip()
                }
                save_rsvp(rsvp_data)
        else:
            # Save single "not attending" entry
            rsvp_data = {
                "timestamp": timestamp,
                "contact_name": form_data.get('contact_name', '').strip(),
                "contact_email": form_data.get('contact_email', '').strip(),
                "contact_phone": form_data.get('contact_phone', '').strip(),
                "attending": "No",
                "guest_first_name": "",
                "guest_last_name": "",
                "starter_choice": "",
                "main_choice": "",
                "dessert_choice": "",
                "dietary_requirements": "",
                "comments": form_data.get('comments', '').strip()
            }
            save_rsvp(rsvp_data)
        
        # Mark as successfully submitted
        st.session_state.form_submitted = True
        st.session_state.submission_in_progress = False
        return True
        
    except Exception as e:
        st.error(f"Beim Speichern Ihrer Zusage ist ein Fehler aufgetreten: {str(e)}")
        st.session_state.submission_in_progress = False
        return False

def rsvp_form_page():
    """Main RSVP form page"""
    # Create 3-column layout with 2,5,2 ratio - left and right are spacers
    left_spacer, main_col, right_spacer = st.columns([1, 3, 1])

    with main_col:
        col1, col2 = st.columns(COLUMN_RATIO_HEADER)
        with col1:
            st.header(f"{st.secrets['wedding']['wedding_couple']} Hochzeit - Zusage")
            st.write(st.secrets["welcome"]["message"])
            st.write("Bitte geben Sie unten die Details für jeden teilnehmenden Gast an (das vollständige Menü finden Sie auf der Seite [**Veranstaltungsinformationen**](/event_info_page)).")
            # Check deadline status and display countdown/warning
            deadline = get_deadline_datetime()
            if deadline:
                if is_past_deadline():
                    if is_within_grace_period():
                        st.error(":material/schedule: Die Anmeldefrist ist abgelaufen, aber Zusagen werden noch für kurze Zeit angenommen.")
                        grace_end = deadline + timedelta(hours=st.secrets["deadline"].get("grace_period_hours", 24))
                        st.warning(f":material/timer: Nachfrist endet: {grace_end.strftime('%d. %B %Y um %H:%M %Z')}")
                    else:
                        st.error(":material/block: Die Anmeldefrist ist abgelaufen. Neue Zusagen werden nicht mehr angenommen.")
                        st.info("Bitte kontaktieren Sie das Hochzeitspaar direkt, wenn Sie Ihre Zusage noch ändern möchten.")
                        return  # Stop rendering the form
                elif is_within_warning_period():
                    time_remaining = get_time_until_deadline()
                    formatted_time = format_time_remaining(time_remaining)

                    st.warning(f":material/schedule: **Anmeldefrist endet bald!**")

                    # Create a prominent countdown display
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(90deg, #ff6b6b, #ee5a52);
                            padding: 15px;
                            border-radius: 8px;
                            text-align: center;
                            color: white;
                            margin: 10px 0;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                        ">
                            <h3>⏰ Verbleibende Zeit: {formatted_time}</h3>
                            <p>Frist: {deadline.strftime('%d. %B %Y um %H:%M %Z')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Show normal deadline info
                    time_remaining = get_time_until_deadline()
                    formatted_time = format_time_remaining(time_remaining)
                    # Deutsches Datumsformat und Zeit (24h)
                    import locale
                    try:
                        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
                    except locale.Error:
                        pass  # Fallback, falls nicht installiert

                    deadline_str = deadline.strftime('%d. %B %Y um %H:%M Uhr')

                    def format_time_de(time_delta):
                        days = time_delta.days
                        hours, remainder = divmod(time_delta.seconds, 3600)
                        minutes = remainder // 60
                        parts = []
                        if days > 0:
                            parts.append(f"{days} Tag{'e' if days != 1 else ''}")
                        if hours > 0:
                            parts.append(f"{hours} Stunde{'n' if hours != 1 else ''}")
                        if minutes > 0:
                            parts.append(f"{minutes} Minute{'n' if minutes != 1 else ''}")
                        return ", ".join(parts) if parts else "weniger als 1 Minute"

                    formatted_time_de = format_time_de(get_time_until_deadline())
                    st.info(f":material/schedule: **Anmeldefrist**:  {deadline_str} ({formatted_time_de} verbleibend)")

        with col2:
            if st.secrets['wedding'].get('banner_image'):
                st.image(st.secrets['wedding']['banner_image'])
        st.markdown("---")

        # Initialize session state
        initialize_session_state()

        # Check if form has been successfully submitted
        if st.session_state.form_submitted:
            st.success(":material/check_circle: Zusage erfolgreich übermittelt! Vielen Dank für Ihre Rückmeldung.")
            st.balloons()

            # if st.button("Weitere Antwort absenden", type="primary"):
            #     reset_form()
            #     st.rerun()

            # st.info(":material/lightbulb: Wenn Sie eine weitere Antwort absenden oder Änderungen vornehmen möchten, klicken Sie bitte oben auf die Schaltfläche.")
            return

        # Check if submission is in progress
        if st.session_state.submission_in_progress:
            st.info(":material/refresh: Ihre Antwort wird verarbeitet...")
            with st.spinner("Bitte warten..."):
                if process_submission():
                    st.rerun()
                else:
                    st.rerun()
            return

        # RSVP Response
        with st.container(border=True):
            st.markdown("**Werden Sie an unserer Hochzeit teilnehmen?**")
            attending = st.radio(
                "**Werden Sie an unserer Hochzeit teilnehmen?**",
                ["Ja, ich/wir nehme(n) teil", "Nein, ich/wir kann/können nicht teilnehmen"],
                key="attending", horizontal=True, label_visibility="collapsed"
            )

        # Contact Information
        with st.container(border=True):
            st.markdown("**Kontaktinformationen**")
            contact_col1, contact_col2, contact_col3 = st.columns(COLUMN_RATIO_CONTACT)
            with contact_col1:
                contact_name = st.text_input("Name der Hauptkontaktperson*", key="contact_name", width=300)
            with contact_col2:
                contact_email = st.text_input("E-Mail-Adresse", key="contact_email", width=350)
            with contact_col3:
                contact_phone = st.text_input("Telefonnummer", key="contact_phone", width=200)

        if attending == "Ja, ich/wir nehme(n) teil":
            st.markdown("**Gästedetails**")
            st.write("Bitte geben Sie die Details für jeden teilnehmenden Gast an:")

            # Display guests
            for i, _ in enumerate(st.session_state.guests):
                with st.container(border=True):
                    st.markdown(f"**Gast {i + 1}**")

                    # Create columns for guest details
                    guest_col1, guest_col2 = st.columns(COLUMN_RATIO_GUEST)

                    with guest_col1:
                        name_col1, name_col2 = st.columns(2)
                        with name_col1:
                            st.text_input(
                                f"Vorname*",
                                key=f"guest_first_name_{i}",
                                placeholder="Vorname"
                            )
                        with name_col2:
                            st.text_input(
                                f"Nachname*",
                                key=f"guest_last_name_{i}",
                                placeholder="Nachname"
                            )

                        # Essenspräferenz Dropdown
                        st.selectbox(
                            "Essenspräferenz",
                            ["Keine", "Vegetarisch", "Vegan"],
                            key=f"preference_{i}",
                            index=0
                        )

                    with guest_col2:
                        if i > 0:  # Don't show remove button for first guest
                            if st.button(f"Entfernen", key=f"remove_{i}"):
                                remove_guest(i)
                                st.rerun()

                    # Dietary requirements
                    st.text_area(
                        "Unverträglichkeiten/Allergien",
                        key=f"dietary_{i}",
                        placeholder="Bitte geben Sie Unverträglichkeiten oder Allergien an",
                        height=60
                    )


            # Add guest button
            if st.button("**Weiteren Gast hinzufügen**", icon=":material/add:"):
                add_guest()
                st.rerun()

        # Additional comments
        with st.container(border=True):
            st.markdown("**Weitere Kommentare**")
            comments = st.text_area(
                "Weitere Kommentare oder besondere Wünsche:",
                key="comments",
                height=100
            )

        # Submit button
        if st.button("Antwort absenden", type="primary", width="content"):
            # Store form data in session state before processing
            st.session_state.form_data = {
                'attending': attending,
                'contact_name': contact_name,
                'contact_email': contact_email,
                'contact_phone': contact_phone,
                'comments': comments
            }

            # Store guest data
            for i, _ in enumerate(st.session_state.guests):
                st.session_state.form_data[f"guest_first_name_{i}"] = st.session_state.get(f"guest_first_name_{i}", "")
                st.session_state.form_data[f"guest_last_name_{i}"] = st.session_state.get(f"guest_last_name_{i}", "")
                st.session_state.form_data[f"preference_{i}"] = st.session_state.get(f"preference_{i}", "Keine")
                st.session_state.form_data[f"dietary_{i}"] = st.session_state.get(f"dietary_{i}", "")

            # Set submission in progress
            st.session_state.submission_in_progress = True
            st.rerun()

def main():
    """Main application entry point"""
    initialize_session_state()

    if st.session_state.authenticated:
        # Admin is logged in - show only admin pages with sidebar navigation
        _run_admin_navigation()
    else:
        # Public user - show RSVP Form, Event Info, and Admin Login
        _run_public_navigation()

def _run_admin_navigation():
    st.set_page_config(
        page_title=st.secrets["wedding"]["page_title"],
        page_icon=st.secrets["wedding"]["page_icon"],
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Define admin pages
    admin_pages = [
        st.Page(admin_summary_page, title="Summary", icon=":material/bar_chart:", default=True),
        st.Page(admin_menu_page, title="Menu Planning", icon=":material/restaurant:"),
        st.Page(admin_data_page, title="Data Export", icon=":material/download:"),
        st.Page(admin_settings_page, title="Settings", icon=":material/settings:"),
    ]

    # Create navigation in sidebar
    pg = st.navigation(admin_pages, position="sidebar")

    # Add logout button to sidebar
    with st.sidebar:
        if st.button(":material/logout: Logout", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.just_logged_in = False
            st.success("Successfully logged out!")
            st.rerun()

    # Run the selected page
    pg.run()

def _run_public_navigation():
    """Public navigation - top navigation bar with RSVP, Event Info, and Admin Login"""
    pages = [
        st.Page(rsvp_form_page, title="RSVP Form", icon=":material/favorite:", default=True),
        st.Page(event_info_page, title="Event Information", icon=":material/celebration:"),
        st.Page(admin_login_page, title="Admin Login", icon=":material/lock:"),
    ]
    pg = st.navigation(pages, position="top")
    pg.run()

if __name__ == "__main__":
    main()