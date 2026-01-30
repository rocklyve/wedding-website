import streamlit as st

def event_info_page():
    left_spacer, main_col, right_spacer = st.columns([2, 5, 2])
    with main_col:
        st.title(f":material/celebration: The Wedding of {st.secrets['wedding']['wedding_couple']}")
        st.write(st.secrets['event']['welcome_text'])

        st.markdown("---")

        # Create tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            ":material/event: Event Details",
            ":material/restaurant_menu: Menu",
            ":material/schedule: Timeline",
            ":material/hotel: Accommodations",
            ":material/directions_car: Transportation",
            ":material/card_giftcard: Registry & Info",
            ":material/contact_mail: Contact"
        ])

        # Tab 1: Event Details (Date, Time, Ceremony, Reception)
        with tab1:
            with st.container(border=True):
            # Wedding Date and Time
                st.header(":material/calendar_today: Date & Time")
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Wedding Date**")
                    st.write(st.secrets['event']['wedding_date'])

                with col2:
                    st.write("**Ceremony Time**")
                    st.write(st.secrets['event']['ceremony_time'])

                st.markdown("---")

                # Ceremony Venue (Church)
                if st.secrets['event'].get('ceremony_venue_name'):
                    st.header(":material/church: Wedding Ceremony")

                    ceremony_col1, ceremony_col2 = st.columns([2, 1])

                    with ceremony_col1:
                        st.write(f"**{st.secrets['event']['ceremony_venue_name']}**")
                        st.write(st.secrets['event']['ceremony_venue_address'])

                        if st.secrets['event'].get('ceremony_venue_description'):
                            st.write("")
                            st.write(st.secrets['event']['ceremony_venue_description'])

                        # Add map if URL provided
                        if st.secrets['event'].get('ceremony_venue_map_url'):
                            st.page_link(st.secrets['event']['ceremony_venue_map_url'], label='Open in Maps', icon=":material/map:")

                    with ceremony_col2:
                        # Ceremony venue image if provided
                        if st.secrets['event'].get('ceremony_venue_image'):
                            st.image(st.secrets['event']['ceremony_venue_image'], width=425)

                    st.markdown("---")

                # Reception Venue
                st.header(":material/celebration: Reception Venue")

                venue_col1, venue_col2 = st.columns([2, 1])

                with venue_col1:
                    st.write(f"**{st.secrets['event']['venue_name']}**")
                    st.write(st.secrets['event']['venue_address'])

                    if st.secrets['event'].get('venue_description'):
                        st.write(st.secrets['event']['venue_description'])

                    # Add map if URL provided
                    if st.secrets['event'].get('venue_map_url'):
                        st.page_link(st.secrets['event']['venue_map_url'], label='Open in Maps', icon=":material/map:")

                with venue_col2:
                    # Venue image if provided
                    if st.secrets['event'].get('venue_image'):
                        st.image(st.secrets['event']['venue_image'], width=425)

        # Tab 2: Menu
        with tab2:
            if st.secrets.get('menu'):
                with st.container(border=True):
                    menu_info = st.secrets['menu']

                    # Check if there are any detailed menu items to display
                    starters_detailed = menu_info.get('starters_detailed', [])
                    mains_detailed = menu_info.get('mains_detailed', [])
                    desserts_detailed = menu_info.get('desserts_detailed', [])

                    # Helper function to check if items exist and are valid
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
                        # Optional menu description
                        if menu_info.get('menu_description'):
                            st.write(menu_info['menu_description'])

                        menu_col1, menu_col2, menu_col3 = st.columns(3)

                        if has_starters:
                            with menu_col1:
                                st.subheader(":material/restaurant: Starters")
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
                                st.subheader(":material/hand_meal: Main Courses")
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

                        # Optional menu notes
                        if menu_info.get('menu_notes'):
                            st.info(f":material/info: {menu_info['menu_notes']}")
            else:
                st.info("Menu information will be available soon.")

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
                st.info("Timeline information will be available soon.")

        # Tab 4: Accommodations
        with tab4:
            accommodations_items = st.secrets.get('accommodations', [])
            if accommodations_items:
                st.write(st.secrets['event'].get('accommodations_intro',
                        'We have reserved room blocks at the following hotels:'))

                accommodations = st.secrets['accommodations']

                for hotel in accommodations:
                    with st.expander(f":material/hotel: {hotel['name']}", expanded=True):
                        st.write(f"**Address:** {hotel['address']}")

                        if hotel.get('distance'):
                            st.write(f"**Distance from venue:** {hotel['distance']}")

                        if hotel.get('phone'):
                            st.write(f"**Phone:** {hotel['phone']}")

                        if hotel.get('booking_code'):
                            st.info(f":material/info: Use booking code: **{hotel['booking_code']}** for our group rate")

                        if hotel.get('website'):
                            st.markdown(f"[:material/link: Visit Website]({hotel['website']})")

                        if hotel.get('notes'):
                            st.write(hotel['notes'])
            else:
                st.info("Accommodation information will be available soon.")

        # Tab 5: Transportation
        with tab5:
            if st.secrets['event'].get('transportation'):
                transport_info = st.secrets['event']['transportation']
                with st.container(border=True):
                    if transport_info.get('parking'):
                        st.subheader(":material/local_parking: Parking")
                        st.write(transport_info['parking'])
                        st.markdown("")

                    if transport_info.get('public_transport'):
                        st.subheader(":material/train: Public Transportation")
                        st.write(transport_info['public_transport'])
                        st.markdown("")

                    if transport_info.get('taxi_info'):
                        st.subheader(":material/local_taxi: Taxi Services")
                        st.write(transport_info['taxi_info'])
            else:
                st.info("Transportation information will be available soon.")

        # Tab 6: Registry & Additional Info
        with tab6:
            with st.container(border=True):
            # Dress Code
                dress_code = st.secrets['event'].get('dress_code')
                if dress_code:
                    st.subheader(":material/checkroom: Dress Code")
                    st.write(dress_code)

                    dress_code_notes = st.secrets['event'].get('dress_code_notes')
                    if dress_code_notes:
                        st.info(dress_code_notes)

                    st.markdown("---")

                # Gift Registry
                registries = st.secrets['event'].get('registry')
                if registries:
                    # Filter out registries with empty name or URL
                    valid_registries = [
                        r for r in registries
                        if r.get('name', '').strip() and r.get('url', '').strip()
                    ]

                    if valid_registries:
                        st.subheader(":material/card_giftcard: Gift Registry")
                        st.write(st.secrets['event'].get('registry_message',
                                'Your presence is the greatest gift, but if you wish to give something, we are registered at:'))

                        reg_cols = st.columns(len(valid_registries))
                        for idx, registry in enumerate(valid_registries):
                            with reg_cols[idx]:
                                st.markdown(f"""
                                <div style='
                                    text-align: center;
                                    padding: 20px;
                                    border: 1px solid #ddd;
                                    border-radius: 10px;
                                    background-color: #f9f9f9;
                                '>
                                    <h3>{registry['name']}</h3>
                                    <a href='{registry['url']}' target='_blank' style='
                                        text-decoration: none;
                                        background-color: #4CAF50;
                                        color: white;
                                        padding: 10px 20px;
                                        border-radius: 5px;
                                        display: inline-block;
                                        margin-top: 10px;
                                    '>View Registry</a>
                                </div>
                                """, unsafe_allow_html=True)

                        st.markdown("---")

                # Additional Information
                additional_info = st.secrets['event'].get('additional_info')
                if additional_info:
                    # Filter out items with empty title or content
                    valid_info = [
                        item for item in additional_info
                        if item.get('title', '').strip() and item.get('content', '').strip()
                    ]

                    if valid_info:
                        st.subheader(":material/info: Additional Information")

                        for info_item in valid_info:
                            with st.expander(info_item['title']):
                                st.write(info_item['content'])

        # Tab 7: Contact
        with tab7:
            if st.secrets.get('contact'):
                contact = st.secrets['contact']
                with st.container(border=True):
                    st.write("If you have any questions, please don't hesitate to reach out:")

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
                st.info("Contact information will be available soon.")