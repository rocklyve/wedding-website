import streamlit as st
from utils import load_gift_registry, mark_gift_as_purchased, unmark_gift_as_purchased, can_undo_purchase, get_browser_id

def event_info_page():
    # Initialize browser ID for persistent gift tracking
    _ = get_browser_id()
    
    left_spacer, main_col, right_spacer = st.columns([2, 5, 2])
    with main_col:
        st.title(f":material/celebration: Die Hochzeit von {st.secrets['wedding']['wedding_couple']}")
        # Link zur RSVP-Form oben einfügen
        st.markdown("[Zur Zu/Absage →](/rsvp_form_page)", unsafe_allow_html=True)
        st.write(st.secrets['event']['welcome_text'])

        st.markdown("---")

        # Create tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            ":material/event: Details",
            ":material/restaurant_menu: Menü",
            ":material/schedule: Ablauf",
            ":material/hotel: Unterkünfte",
            ":material/directions_car: Anreise",
            ":material/card_giftcard: Geschenke & Infos",
            ":material/contact_mail: Kontakt"
        ])

        # Tab 1: Event Details (Date, Time, Ceremony, Reception)
        with tab1:
            with st.container(border=True):
                st.header(":material/calendar_today: Datum & Uhrzeit")
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Hochzeitsdatum**")
                    st.write(st.secrets['event']['wedding_date'])

                with col2:
                    st.write("**Uhrzeit der Trauung**")
                    st.write(st.secrets['event']['ceremony_time'])

                st.markdown("---")

                # Ceremony Venue
                if st.secrets['event'].get('ceremony_venue_name'):
                    st.header(":material/church: Trauung")

                    ceremony_col1, ceremony_col2 = st.columns([2, 1])

                    with ceremony_col1:
                        st.write(f"**{st.secrets['event']['ceremony_venue_name']}**")
                        st.write(st.secrets['event']['ceremony_venue_address'])

                        if st.secrets['event'].get('ceremony_venue_description'):
                            st.write("")
                            st.write(st.secrets['event']['ceremony_venue_description'])

                        if st.secrets['event'].get('ceremony_venue_map_url'):
                            st.page_link(st.secrets['event']['ceremony_venue_map_url'], label='In Maps öffnen', icon=":material/map:")

                    with ceremony_col2:
                        if st.secrets['event'].get('ceremony_venue_image'):
                            st.image(st.secrets['event']['ceremony_venue_image'], width=425)

                    st.markdown("---")

                # Reception Venue
                st.header(":material/celebration: Feierlocation")

                venue_col1, venue_col2 = st.columns([2, 1])

                with venue_col1:
                    st.write(f"**{st.secrets['event']['venue_name']}**")
                    st.write(st.secrets['event']['venue_address'])

                    if st.secrets['event'].get('venue_description'):
                        st.write(st.secrets['event']['venue_description'])

                    if st.secrets['event'].get('venue_map_url'):
                        st.page_link(st.secrets['event']['venue_map_url'], label='In Maps öffnen', icon=":material/map:")

                with venue_col2:
                    if st.secrets['event'].get('venue_image'):
                        st.image(st.secrets['event']['venue_image'], width=425)

        # Tab 2: Menu
        with tab2:
            if st.secrets.get('menu'):
                with st.container(border=True):
                    menu_info = st.secrets['menu']

                    starters_detailed = menu_info.get('starters_detailed', [])
                    mains_detailed = menu_info.get('mains_detailed', [])
                    desserts_detailed = menu_info.get('desserts_detailed', [])

                    def has_valid_items(items):
                        if not items:
                            return False
                        for item in items:
                            if isinstance(item, dict):
                                if item.get('name', '').strip():
                                    return True
                            elif isinstance(item, str) and item.strip():
                                return True
                        return False

                    has_starters = has_valid_items(starters_detailed)
                    has_mains = has_valid_items(mains_detailed)
                    has_desserts = has_valid_items(desserts_detailed)

                    if has_starters or has_mains or has_desserts:
                        if menu_info.get('menu_description'):
                            st.write(menu_info['menu_description'])

                        menu_col1, menu_col2, menu_col3 = st.columns(3)

                        if has_starters:
                            with menu_col1:
                                st.subheader(":material/restaurant: Vorspeisen")
                                for item in starters_detailed:
                                    if isinstance(item, dict):
                                        if item.get('name', '').strip():
                                            st.markdown(f"**{item['name']}**")
                                            if item.get('description'):
                                                st.caption(item['description'])
                                            st.write("")
                                    elif isinstance(item, str) and item.strip():
                                        st.write(f"• {item}")

                        if has_mains:
                            with menu_col2:
                                st.subheader(":material/hand_meal: Hauptgerichte")
                                for item in mains_detailed:
                                    if isinstance(item, dict):
                                        if item.get('name', '').strip():
                                            st.markdown(f"**{item['name']}**")
                                            if item.get('description'):
                                                st.caption(item['description'])
                                            st.write("")
                                    elif isinstance(item, str) and item.strip():
                                        st.write(f"• {item}")

                        if has_desserts:
                            with menu_col3:
                                st.subheader(":material/cake: Desserts")
                                for item in desserts_detailed:
                                    if isinstance(item, dict):
                                        if item.get('name', '').strip():
                                            st.markdown(f"**{item['name']}**")
                                            if item.get('description'):
                                                st.caption(item['description'])
                                            st.write("")
                                    elif isinstance(item, str) and item.strip():
                                        st.write(f"• {item}")

                        if menu_info.get('menu_notes'):
                            st.info(f":material/info: {menu_info['menu_notes']}")
            else:
                st.info("Menüinformationen folgen in Kürze.")

        # Tab 3: Timeline
        with tab3:
            timeline_items = st.secrets.get('timeline', [])
            if timeline_items:
                with st.container(border=True):
                    for item in timeline_items:
                        with st.container():
                            time_col, event_col = st.columns([0.5, 3])
                            with time_col:
                                st.markdown(f"**{item['time']}**")
                            with event_col:
                                st.write(item['event'])
                                if item.get('description'):
                                    st.caption(item['description'])
            else:
                st.info("Ablaufinformationen folgen in Kürze.")

        # Tab 4: Accommodations
        with tab4:
            accommodations_items = st.secrets.get('accommodations', [])
            if accommodations_items:
                st.write(st.secrets['event'].get('accommodations_intro',
                        'Wir haben Zimmerkontingente in folgenden Hotels reserviert:'))

                accommodations = st.secrets['accommodations']

                for hotel in accommodations:
                    with st.expander(f":material/hotel: {hotel['name']}", expanded=True):
                        st.write(f"**Adresse:** {hotel['address']}")

                        if hotel.get('distance'):
                            st.write(f"**Entfernung zur Location:** {hotel['distance']}")

                        if hotel.get('phone'):
                            st.write(f"**Telefon:** {hotel['phone']}")

                        if hotel.get('booking_code'):
                            st.info(f":material/info: Buchungscode: **{hotel['booking_code']}** für Sonderkonditionen")

                        if hotel.get('website'):
                            st.markdown(f"[:material/link: Website besuchen]({hotel['website']})")

                        if hotel.get('notes'):
                            st.write(hotel['notes'])
            else:
                st.info("Unterkunftsinformationen folgen in Kürze.")

        # Tab 5: Transportation
        with tab5:
            if st.secrets['event'].get('transportation'):
                transport_info = st.secrets['event']['transportation']
                with st.container(border=True):
                    if transport_info.get('parking'):
                        st.subheader(":material/local_parking: Parken")
                        st.write(transport_info['parking'])
                        st.markdown("")

                    if transport_info.get('public_transport'):
                        st.subheader(":material/train: Öffentlicher Nahverkehr")
                        st.write(transport_info['public_transport'])
                        st.markdown("")

                    if transport_info.get('taxi_info'):
                        st.subheader(":material/local_taxi: Taxi")
                        st.write(transport_info['taxi_info'])
            else:
                st.info("Anreiseinformationen folgen in Kürze.")

        # Tab 6: Registry & Additional Info
        with tab6:
            with st.container(border=True):
                dress_code = st.secrets['event'].get('dress_code')
                if dress_code:
                    st.subheader(":material/checkroom: Dresscode")
                    st.write(dress_code)

                    dress_code_notes = st.secrets['event'].get('dress_code_notes')
                    if dress_code_notes:
                        st.info(dress_code_notes)

                    st.markdown("---")

                # Gift Registry from CSV
                st.subheader(":material/card_giftcard: Geschenkliste")
                st.write(st.secrets['event'].get('registry_message',
                        'Eure Anwesenheit ist das größte Geschenk, aber falls ihr etwas schenken möchtet:'))
                
                # Load gift registry
                gift_df = load_gift_registry()
                
                if not gift_df.empty:
                    # Get browser ID
                    browser_id = get_browser_id()
                    
                    # Debug info (can be removed later)
                    with st.expander("🔧 Debug Info (zum Testen)"):
                        st.write(f"**Deine Browser-ID:** `{browser_id}`")
                        st.write(f"**ID bestätigt:** {st.session_state.get('browser_id_confirmed', False)}")
                        st.write(f"**Session State Keys:** {list(st.session_state.keys())}")
                    
                    # Info message
                    if browser_id.startswith('temp_'):
                        st.warning("⚠️ Browser-ID wird geladen... Bitte warte kurz oder lade die Seite neu.")
                    else:
                        st.info("💡 Du kannst nur deine eigenen Markierungen rückgängig machen. Diese werden automatisch in deinem Browser gespeichert.")
                    
                    st.write("")
                    
                    # Display gifts as cards in a grid (3 columns)
                    num_cols = 3
                    rows = [gift_df.iloc[i:i+num_cols] for i in range(0, len(gift_df), num_cols)]
                    
                    for row_items in rows:
                        cols = st.columns(num_cols)
                        
                        for col_idx, (idx, item) in enumerate(row_items.iterrows()):
                            with cols[col_idx]:
                                # Create a card container
                                with st.container(border=True):
                                    # Display image
                                    if item.get('image_url') and item['image_url'].strip():
                                        st.image(item['image_url'], width='stretch')
                                    
                                    # Title
                                    st.markdown(f"### {item['name']}")
                                    
                                    # Description
                                    st.write(item['description'])
                                    
                                    st.write("")
                                    
                                    # Product link
                                    if item['url'] and item['url'].strip():
                                        st.markdown(f"[:material/link: Zum Produkt]({item['url']})")
                                    
                                    st.write("")
                                    
                                    # Status and action buttons
                                    if item['purchased']:
                                        st.success("✓ Bereits gekauft")
                                        
                                        # Debug info
                                        with st.expander("🔍 Debug: Kaufinfo"):
                                            st.write(f"**Gespeicherte ID:** `{item.get('session_id', 'keine')}`")
                                            st.write(f"**Deine ID:** `{get_browser_id()}`")
                                            st.write(f"**Kannst rückgängig machen:** {can_undo_purchase(idx)}")
                                        
                                        # Show undo option only if this session purchased it
                                        if can_undo_purchase(idx):
                                            undo_key = f'undo_{idx}'
                                            
                                            if not st.session_state.get(undo_key, False):
                                                if st.button("Rückgängig machen", key=f"undo_btn_{idx}", type="secondary", width='stretch'):
                                                    st.session_state[undo_key] = True
                                                    st.rerun()
                                            else:
                                                # Show undo confirmation
                                                st.warning("Möchtest du die Markierung wirklich rückgängig machen?")
                                                col_yes, col_no = st.columns(2)
                                                with col_yes:
                                                    if st.button("✓ Ja", key=f"undo_yes_{idx}", type="primary", width='stretch'):
                                                        if unmark_gift_as_purchased(idx):
                                                            st.success("Die Markierung wurde rückgängig gemacht.")
                                                            st.session_state[undo_key] = False
                                                            st.rerun()
                                                        else:
                                                            st.error("Fehler beim Rückgängigmachen.")
                                                with col_no:
                                                    if st.button("✗ Nein", key=f"undo_no_{idx}", width='stretch'):
                                                        st.session_state[undo_key] = False
                                                        st.rerun()
                                    else:
                                        # Check if we're in confirmation mode for this item
                                        confirm_key = f'confirm_{idx}'
                                        
                                        if not st.session_state.get(confirm_key, False):
                                            # Show initial button
                                            if st.button("Als gekauft markieren", key=f"purchase_btn_{idx}", type="primary", width='stretch'):
                                                st.session_state[confirm_key] = True
                                                st.rerun()
                                        else:
                                            # Show confirmation
                                            st.warning("Möchtest du diesen Artikel wirklich als gekauft markieren?")
                                            col_yes, col_no = st.columns(2)
                                            with col_yes:
                                                if st.button("✓ Ja", key=f"yes_{idx}", type="primary", width='stretch'):
                                                    if mark_gift_as_purchased(idx):
                                                        st.success("Vielen Dank! Der Artikel wurde als gekauft markiert.")
                                                        st.session_state[confirm_key] = False
                                                        st.rerun()
                                                    else:
                                                        st.error("Fehler beim Speichern. Bitte versuche es erneut.")
                                            with col_no:
                                                if st.button("✗ Nein", key=f"no_{idx}", width='stretch'):
                                                    st.session_state[confirm_key] = False
                                                    st.rerun()
                else:
                    st.info("Die Geschenkliste wird in Kürze verfügbar sein.")

                st.markdown("---")

                additional_info = st.secrets['event'].get('additional_info')
                if additional_info:
                    valid_info = [
                        item for item in additional_info
                        if item.get('title', '').strip() and item.get('content', '').strip()
                    ]

                    if valid_info:
                        st.subheader(":material/info: Weitere Informationen")

                        for info_item in valid_info:
                            with st.expander(info_item['title']):
                                st.write(info_item['content'])

        # Tab 7: Contact
        with tab7:
            if st.secrets.get('contact'):
                contact = st.secrets['contact']
                with st.container(border=True):
                    st.write("Bei Fragen meldet euch gerne bei uns:")

                    contact_col1, contact_col2 = st.columns(2)

                    if contact.get('bride'):
                        with contact_col1:
                            st.write(f"**{contact['bride']['name']}**")
                            if contact['bride'].get('phone'):
                                st.write(f":material/phone: {contact['bride']['phone']}")
                            if contact['bride'].get('email'):
                                st.write(f":material/email: {contact['bride']['email']}")

                    if contact.get('groom'):
                        with contact_col2:
                            st.write(f"**{contact['groom']['name']}**")
                            if contact['groom'].get('phone'):
                                st.write(f":material/phone: {contact['groom']['phone']}")
                            if contact['groom'].get('email'):
                                st.write(f":material/email: {contact['groom']['email']}")
            else:
                st.info("Kontaktinformationen folgen in Kürze.")
