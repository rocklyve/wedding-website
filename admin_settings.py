import streamlit as st
import toml
import os
from datetime import datetime

def admin_settings_page():
    """Admin settings page for editing secrets.toml"""
    if not st.session_state.get('authenticated', False):
        st.error(":material/lock: Please log in to access this page.")
        st.stop()

    main_col1, main_col2, main_col3 = st.columns([1, 4, 1])
    with main_col2:
        st.title(":material/settings: Settings Configuration")
        st.info(":material/info: Edit your secrets.toml configuration below. Changes require app restart to take effect.")

        # Path to secrets file
        secrets_path = os.path.join(".streamlit", "secrets.toml")

        if not os.path.exists(secrets_path):
            st.error(f":material/error: secrets.toml file not found at {secrets_path}")
            return

        # Load current secrets
        with open(secrets_path, 'r') as f:
            secrets = toml.load(f)

        # Initialize session state for edited values
        if 'edited_secrets' not in st.session_state:
            st.session_state.edited_secrets = secrets.copy()

        def format_label(key):
            """Format a key by removing underscores and capitalizing words"""
            return key.replace('_', ' ').title()

        def render_value(key_path, value, parent_dict):
            """Recursively render form fields based on value type"""
            full_key = "_".join(key_path)
            display_label = format_label(key_path[-1])

            if isinstance(value, dict):
                # Render as expander for nested dicts
                with st.expander(f":material/key: {display_label}", expanded=True):
                    for k, v in value.items():
                        render_value(key_path + [k], v, value)

            elif isinstance(value, list):
                st.markdown(f"**{display_label}** (List)")

                # Display existing items
                for i, item in enumerate(value):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        if isinstance(item, dict):
                            # For list of dicts, render as nested structure
                            with st.container(border=True):
                                st.markdown(f"*Item {i+1}*")
                                for k, v in item.items():
                                    render_value(key_path + [str(i), k], v, item)
                        else:
                            # Simple list item
                            new_val = st.text_input(
                                f"{display_label} [{i+1}]",
                                value=str(item),
                                key=f"{full_key}_{i}",
                                label_visibility="collapsed"
                            )
                            if new_val != str(item):
                                value[i] = new_val
                    with col2:
                        if st.button(":material/delete:", key=f"delete_{full_key}_{i}"):
                            value.pop(i)
                            update_nested_dict(st.session_state.edited_secrets, key_path, value)
                            st.rerun()

                # Add new item button (only for simple lists, not list of dicts)
                if not value or not isinstance(value[0], dict):
                    new_item = st.text_input(
                        f"Add new {display_label}",
                        key=f"new_{full_key}",
                        placeholder=f"Enter new {display_label}"
                    )
                    if st.button(f":material/add: Add to {display_label}", key=f"add_{full_key}"):
                        if new_item.strip():
                            value.append(new_item)
                            update_nested_dict(st.session_state.edited_secrets, key_path, value)
                            st.rerun()

            elif isinstance(value, bool):
                new_val = st.checkbox(
                    display_label,
                    value=value,
                    key=full_key
                )
                if new_val != value:
                    parent_dict[key_path[-1]] = new_val

            elif isinstance(value, (int, float)):
                new_val = st.number_input(
                    display_label,
                    value=value,
                    key=full_key
                )
                if new_val != value:
                    parent_dict[key_path[-1]] = new_val

            else:
                # String value - use text_area for long strings, text_input for short
                str_value = str(value)
                if len(str_value) > 100 or '\n' in str_value:
                    new_val = st.text_area(
                        display_label,
                        value=str_value,
                        key=full_key,
                        height=100
                    )
                else:
                    new_val = st.text_input(
                        display_label,
                        value=str_value,
                        key=full_key
                    )

                if new_val != str_value:
                    parent_dict[key_path[-1]] = new_val

        def update_nested_dict(d, key_path, value):
            """Update a nested dictionary given a key path"""
            for key in key_path[:-1]:
                d = d[key]
            d[key_path[-1]] = value

        # Render all sections as tabs
        section_tabs = st.tabs([format_label(key) for key in secrets.keys()])

        for tab, (section_key, section_value) in zip(section_tabs, secrets.items()):
            with tab:
                render_value([section_key], section_value, secrets)

        # Save button
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button(":material/save: Save Changes", type="primary", use_container_width=True):
                try:
                    # Create backup
                    backup_path = secrets_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    with open(secrets_path, 'r') as f:
                        backup_content = f.read()
                    with open(backup_path, 'w') as f:
                        f.write(backup_content)

                    # Write updated secrets
                    with open(secrets_path, 'w') as f:
                        toml.dump(secrets, f)

                    st.success(f":material/check_circle: Settings saved! Backup created at {backup_path}")
                    st.info(":material/restart_alt: **Important:** Restart the Streamlit app for changes to take effect.")

                    # Clear the edited state
                    if 'edited_secrets' in st.session_state:
                        del st.session_state.edited_secrets

                except Exception as e:
                    st.error(f":material/error: Error saving settings: {str(e)}")

        with col2:
            if st.button(":material/refresh: Reload File", use_container_width=True):
                if 'edited_secrets' in st.session_state:
                    del st.session_state.edited_secrets
                st.rerun()
