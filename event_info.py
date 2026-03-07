import streamlit as st
from utils import load_gift_registry, mark_gift_as_purchased, unmark_gift_as_purchased, can_undo_purchase, get_browser_id, get_remaining_quantity, get_user_purchased_quantity

def event_info_page():
    # Initialize browser ID for persistent gift tracking
    _ = get_browser_id()
    
    left_spacer, main_col, right_spacer = st.columns([2, 5, 2])
    with main_col:
        st.title(f":material/celebration: Hochzeit von {st.secrets['wedding']['wedding_couple']}")
        # Link zur RSVP-Form oben einfügen
        st.markdown("[Zur Zu/Absage →](/rsvp_form_page)", unsafe_allow_html=True)
        st.write(st.secrets['event']['welcome_text'])

        st.markdown("---")

        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            ":material/event: Details",
            ":material/hotel: Unterkünfte",
            ":material/card_giftcard: Wunschliste",
            ":material/contact_mail: Kontakt"
        ])

        # Tab 1: Event Details (Date, Time, Ceremony, Reception, Timeline)
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

                # Reception Venue
                st.header(":material/celebration: Trauung & Feierlocation")

                st.write(f"**{st.secrets['event']['venue_name']}**")
                st.write(st.secrets['event']['venue_address'])

                if st.secrets['event'].get('venue_map_url'):
                    st.page_link(st.secrets['event']['venue_map_url'], label='In Maps öffnen', icon=":material/map:")

                # st.write("**:material/local_parking: Parken**")
                st.write("(Kostenlose Parkplätze sind an der Location verfügbar)")

                st.markdown("---")

                # Timeline/Ablauf within Date section
                st.header(":material/schedule: Ablauf")
                timeline_items = st.secrets.get('timeline', [])
                if timeline_items:
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

                st.markdown("---")

                # Additional Info
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

        # Tab 2: Accommodations
        with tab2:
            accommodations_items = st.secrets.get('accommodations', [])
            if accommodations_items:

                accommodations = st.secrets['accommodations']

                for hotel in accommodations:
                    with st.expander(f":material/hotel: {hotel['name']}", expanded=True):
                        st.write(f"**Adresse:** {hotel['address']}")

                        if hotel.get('distance'):
                            st.write(f"**Entfernung zur Location:** {hotel['distance']}")

                        if hotel.get('website'):
                            st.markdown(f"[:material/link: Website besuchen]({hotel['website']})")

                        if hotel.get('notes'):
                            st.write(hotel['notes'])
            else:
                st.info("Unterkunftsinformationen folgen in Kürze.")

        # Tab 3: Registry
        with tab3:
            with st.container(border=True):
                # Gift Registry from CSV
                st.subheader(":material/card_giftcard: Wunschliste")
                st.write(st.secrets['event'].get('registry_message',
                        'Eure Anwesenheit ist das größte Geschenk. Wenn ihr uns dennoch eine Freude machen möchtet, findet ihr hier unsere Wunschliste.'))
                
                st.write("🌴 Alternativ könnt ihr uns auch mit einem Beitrag zu unserer Hochzeitsreise eine Freude machen!")
                
                # Load gift registry
                gift_df = load_gift_registry()
                
                if not gift_df.empty:
                    # Get browser ID
                    browser_id = get_browser_id()
                    
                    # Info message
                    st.info("💡 Du kannst nur deine eigenen Markierungen rückgängig machen. Diese werden über die URL gespeichert - kopiere die URL, um später darauf zuzugreifen!")
                    
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
                                    # Display image as square
                                    if item.get('image_url') and item['image_url'].strip():
                                        st.markdown(f"""
                                        <div style="width: 100%; padding-bottom: 100%; position: relative; overflow: hidden; border-radius: 8px;">
                                            <img src="{item['image_url']}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;">
                                        </div>
                                        """, unsafe_allow_html=True)
                                        st.write("")
                                    
                                    # Title
                                    st.markdown(f"### {item['name']}")
                                    
                                    # Description
                                    st.write(item['description'])
                                    
                                    st.write("")
                                    
                                    # Product link
                                    if item['url'] and item['url'].strip():
                                        st.markdown(f"[:material/link: Zum Produkt]({item['url']})")
                                    
                                    st.write("")
                                    
                                    # Quantity information
                                    quantity_total = int(item.get('quantity_total', 1))
                                    quantity_purchased = int(item.get('quantity_purchased', 0))
                                    quantity_remaining = quantity_total - quantity_purchased
                                    user_purchased_qty = get_user_purchased_quantity(idx)
                                    
                                    # Show quantity info if total > 1
                                    if quantity_total > 1:
                                        if quantity_purchased > 0:
                                            st.info(f"📊 {quantity_purchased} von {quantity_total} bereits gekauft")
                                        else:
                                            st.info(f"📊 {quantity_total} Stück verfügbar")
                                    
                                    st.write("")
                                    
                                    # Status and action buttons
                                    if quantity_remaining <= 0:
                                        st.success("✓ Vollständig gekauft")
                                        
                                        # Show undo option only if this session purchased it
                                        if can_undo_purchase(idx):
                                            if user_purchased_qty > 1:
                                                st.caption(f"Du hast {user_purchased_qty} Stück gekauft")
                                            
                                            undo_key = f'undo_{idx}'
                                            
                                            if not st.session_state.get(undo_key, False):
                                                if st.button("Rückgängig machen", key=f"undo_btn_{idx}", type="secondary", width='stretch'):
                                                    st.session_state[undo_key] = True
                                                    st.rerun()
                                            else:
                                                # Show undo confirmation
                                                if user_purchased_qty > 1:
                                                    st.warning(f"Möchtest du deine {user_purchased_qty} Stück wirklich rückgängig machen?")
                                                else:
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
                                        # Still available for purchase
                                        if quantity_purchased > 0 and can_undo_purchase(idx):
                                            # Show partial purchase with undo option
                                            if user_purchased_qty > 1:
                                                st.success(f"✓ Du hast {user_purchased_qty} Stück gekauft")
                                            else:
                                                st.success(f"✓ Du hast bereits gekauft")
                                            
                                            undo_key = f'undo_{idx}'
                                            if not st.session_state.get(undo_key, False):
                                                if st.button("Rückgängig machen", key=f"undo_btn_{idx}", type="secondary", width='stretch'):
                                                    st.session_state[undo_key] = True
                                                    st.rerun()
                                            else:
                                                # Show undo confirmation
                                                if user_purchased_qty > 1:
                                                    st.warning(f"Möchtest du deine {user_purchased_qty} Stück wirklich rückgängig machen?")
                                                else:
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
                                            
                                            st.write("")
                                        
                                        # Check if we're in confirmation mode for this item
                                        confirm_key = f'confirm_{idx}'
                                        
                                        if not st.session_state.get(confirm_key, False):
                                            # Show quantity selector if more than 1 available
                                            if quantity_total > 1:
                                                quantity_to_buy = st.number_input(
                                                    f"Anzahl:",
                                                    min_value=1,
                                                    max_value=quantity_remaining,
                                                    value=1,
                                                    step=1,
                                                    key=f"quantity_{idx}"
                                                )
                                                st.session_state[f"selected_quantity_{idx}"] = quantity_to_buy
                                            else:
                                                st.session_state[f"selected_quantity_{idx}"] = 1
                                            
                                            # Show initial button
                                            if st.button("Als gekauft markieren", key=f"purchase_btn_{idx}", type="primary", width='stretch'):
                                                st.session_state[confirm_key] = True
                                                st.rerun()
                                        else:
                                            # Show confirmation
                                            selected_qty = st.session_state.get(f"selected_quantity_{idx}", 1)
                                            if quantity_total > 1:
                                                st.warning(f"Möchtest du {selected_qty} Stück wirklich als gekauft markieren?")
                                            else:
                                                st.warning("Möchtest du diesen Artikel wirklich als gekauft markieren?")
                                            col_yes, col_no = st.columns(2)
                                            with col_yes:
                                                if st.button("✓ Ja", key=f"yes_{idx}", type="primary", width='stretch'):
                                                    if mark_gift_as_purchased(idx, selected_qty):
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
                    st.info("Die Wunschliste wird in Kürze verfügbar sein.")

        # Tab 4: Contact
        with tab4:
            if st.secrets.get('contact'):
                contact = st.secrets['contact']
                with st.container(border=True):
                    st.write("Bei Fragen meldet euch gerne bei uns:")

                    st.subheader(":material/favorite: Brautpaar")
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

                    st.markdown("---")

                    st.subheader(":material/groups: Trauzeugin & Trauzeugen")
                    trauzeugen_col1, trauzeugen_col2, trauzeugen_col3 = st.columns(3)

                    with trauzeugen_col1:
                        st.write("**Michaela Wurz**")
                        st.write(":material/phone: +49 176 85707832")
                        # st.write(":material/email: ...")

                    with trauzeugen_col2:
                        st.write("**Simon Laubenstein**")
                        st.write(":material/phone: +49 157 89153009")
                        # st.write(":material/email: ...")

                    with trauzeugen_col3:
                        st.write("**Paul Laubenstein**")
                        st.write(":material/phone: +49 157 83756750")
                        # st.write(":material/email: ...")
            else:
                st.info("Kontaktinformationen folgen in Kürze.")
