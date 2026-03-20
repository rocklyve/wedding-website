import streamlit as st
import pandas as pd
from utils import load_gift_registry, save_gift_registry

def admin_wishlist_page():
    """Admin page for managing the gift registry/wishlist"""
    if not st.session_state.get('authenticated', False):
        st.error(":material/lock: Please log in to access this page.")
        st.stop()

    main_col1, main_col2, main_col3 = st.columns([1, 4, 1])
    with main_col2:
        st.title(":material/card_giftcard: Wunschliste verwalten")
        st.info(":material/info: Hier kannst du die Geschenke auf der Wunschliste verwalten.")

        # Load current gift registry
        df = load_gift_registry()

        # Initialize session state for editing
        if 'editing_gift' not in st.session_state:
            st.session_state.editing_gift = None
        if 'adding_new_gift' not in st.session_state:
            st.session_state.adding_new_gift = False

        # Add new gift button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(":material/add: Neues Geschenk hinzufügen", type="primary", width='stretch'):
                st.session_state.adding_new_gift = True
                st.session_state.editing_gift = None
                st.rerun()

        st.markdown("---")

        # Form for adding new gift
        if st.session_state.adding_new_gift:
            with st.container(border=True):
                st.subheader(":material/add: Neues Geschenk hinzufügen")

                with st.form("add_gift_form", clear_on_submit=False):
                    name = st.text_input("Name*", placeholder="z.B. Kaffeemaschine")
                    description = st.text_area("Beschreibung*", placeholder="Beschreibe das Geschenk", height=100)
                    url = st.text_input("Produkt-URL", placeholder="https://...")
                    image_url = st.text_input("Bild-URL", placeholder="https://...")
                    quantity_total = st.number_input("Anzahl verfügbar", min_value=1, value=1, step=1)

                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        submitted = st.form_submit_button(":material/save: Hinzufügen", type="primary", width='stretch')
                    with col_cancel:
                        cancelled = st.form_submit_button(":material/cancel: Abbrechen", width='stretch')

                    if submitted:
                        if name.strip() and description.strip():
                            # Create new gift entry
                            new_gift = pd.DataFrame([{
                                'name': name.strip(),
                                'description': description.strip(),
                                'url': url.strip(),
                                'image_url': image_url.strip(),
                                'purchased': False,
                                'session_id': '',
                                'quantity_total': quantity_total,
                                'quantity_purchased': 0,
                                'purchase_details': '[]'
                            }])

                            # Append to dataframe
                            df = pd.concat([df, new_gift], ignore_index=True)

                            if save_gift_registry(df):
                                st.success(":material/check_circle: Geschenk erfolgreich hinzugefügt!")
                                st.session_state.adding_new_gift = False
                                st.rerun()
                            else:
                                st.error(":material/error: Fehler beim Speichern des Geschenks.")
                        else:
                            st.error(":material/error: Name und Beschreibung sind erforderlich!")

                    if cancelled:
                        st.session_state.adding_new_gift = False
                        st.rerun()

        # Display existing gifts
        if not df.empty:
            st.subheader(":material/list: Vorhandene Geschenke")

            for idx, row in df.iterrows():
                with st.container(border=True):
                    # Check if this gift is being edited
                    is_editing = st.session_state.editing_gift == idx

                    if is_editing:
                        # Edit mode
                        st.markdown("### :material/edit: Geschenk bearbeiten")

                        with st.form(f"edit_gift_form_{idx}"):
                            new_name = st.text_input("Name*", value=row['name'])
                            new_description = st.text_area("Beschreibung*", value=row['description'], height=100)
                            new_url = st.text_input("Produkt-URL", value=row.get('url', ''))
                            new_image_url = st.text_input("Bild-URL", value=row.get('image_url', ''))
                            new_quantity_total = st.number_input(
                                "Anzahl verfügbar",
                                min_value=1,
                                value=int(row.get('quantity_total', 1)),
                                step=1
                            )

                            # Show current purchase status
                            quantity_purchased = int(row.get('quantity_purchased', 0))
                            if quantity_purchased > 0:
                                st.info(f"ℹ️ Bereits gekauft: {quantity_purchased} von {row['quantity_total']}")

                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                save_btn = st.form_submit_button(":material/save: Speichern", type="primary", width='stretch')
                            with col_cancel:
                                cancel_btn = st.form_submit_button(":material/cancel: Abbrechen", width='stretch')

                            if save_btn:
                                if new_name.strip() and new_description.strip():
                                    # Update the dataframe
                                    df.at[idx, 'name'] = new_name.strip()
                                    df.at[idx, 'description'] = new_description.strip()
                                    df.at[idx, 'url'] = new_url.strip()
                                    df.at[idx, 'image_url'] = new_image_url.strip()
                                    df.at[idx, 'quantity_total'] = new_quantity_total

                                    # Update purchased flag based on quantity
                                    df.at[idx, 'purchased'] = (quantity_purchased >= new_quantity_total)

                                    if save_gift_registry(df):
                                        st.success(":material/check_circle: Geschenk erfolgreich aktualisiert!")
                                        st.session_state.editing_gift = None
                                        st.rerun()
                                    else:
                                        st.error(":material/error: Fehler beim Speichern.")
                                else:
                                    st.error(":material/error: Name und Beschreibung sind erforderlich!")

                            if cancel_btn:
                                st.session_state.editing_gift = None
                                st.rerun()

                    else:
                        # Display mode
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.markdown(f"### {row['name']}")
                            st.write(row['description'])

                            # Show purchase status
                            quantity_total = int(row.get('quantity_total', 1))
                            quantity_purchased = int(row.get('quantity_purchased', 0))
                            quantity_remaining = quantity_total - quantity_purchased

                            if quantity_purchased > 0:
                                if quantity_remaining > 0:
                                    st.info(f"📊 {quantity_purchased} von {quantity_total} gekauft ({quantity_remaining} verfügbar)")
                                else:
                                    st.success(f"✓ Vollständig gekauft ({quantity_total} Stück)")
                            else:
                                if quantity_total > 1:
                                    st.caption(f"📦 {quantity_total} Stück verfügbar")

                            if row.get('url'):
                                st.caption(f"🔗 {row['url']}")
                            if row.get('image_url'):
                                st.caption(f"🖼️ {row['image_url']}")

                        with col2:
                            st.write("")
                            st.write("")
                            if st.button(":material/edit: Bearbeiten", key=f"edit_{idx}", width='stretch'):
                                st.session_state.editing_gift = idx
                                st.session_state.adding_new_gift = False
                                st.rerun()

                            if st.button(":material/delete: Löschen", key=f"delete_{idx}", type="secondary", width='stretch'):
                                st.session_state[f'confirm_delete_{idx}'] = True
                                st.rerun()

                        # Delete confirmation
                        if st.session_state.get(f'confirm_delete_{idx}', False):
                            st.warning("⚠️ Möchtest du dieses Geschenk wirklich löschen?")
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("✓ Ja, löschen", key=f"confirm_yes_{idx}", type="primary", width='stretch'):
                                    df = df.drop(idx).reset_index(drop=True)
                                    if save_gift_registry(df):
                                        st.success(":material/check_circle: Geschenk erfolgreich gelöscht!")
                                        st.session_state[f'confirm_delete_{idx}'] = False
                                        st.rerun()
                                    else:
                                        st.error(":material/error: Fehler beim Löschen.")
                            with col_no:
                                if st.button("✗ Abbrechen", key=f"confirm_no_{idx}", width='stretch'):
                                    st.session_state[f'confirm_delete_{idx}'] = False
                                    st.rerun()

        else:
            st.info(":material/info: Noch keine Geschenke in der Wunschliste. Füge das erste Geschenk hinzu!")

        st.markdown("---")

        # Statistics
        if not df.empty:
            st.subheader(":material/bar_chart: Statistik")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Gesamt Artikel", len(df))

            with col2:
                total_items = df['quantity_total'].sum()
                st.metric("Gesamt Stück", int(total_items))

            with col3:
                purchased_items = df['quantity_purchased'].sum()
                st.metric("Gekaufte Stück", int(purchased_items))

            with col4:
                if total_items > 0:
                    percentage = (purchased_items / total_items) * 100
                    st.metric("Gekauft %", f"{percentage:.1f}%")
                else:
                    st.metric("Gekauft %", "0%")
