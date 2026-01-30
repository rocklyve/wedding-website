# Wedding RSVP Application

A Streamlit-based web application for managing wedding RSVPs with menu selections, deadline tracking, and administrative dashboard.

## Features

- **Guest RSVP Form** - Allow guests to RSVP with menu selections (starters, mains, desserts)
- **Multi-guest Support** - Submit RSVPs for multiple guests in one submission
- **Deadline Management** - Automatic deadline tracking with warning and grace periods
- **Detailed Menu Descriptions** - Display detailed menu item descriptions with formatting
- **Event Information Page** - Display venue details, timeline, accommodations, and transportation
- **Admin Dashboard** - Secure admin panel with:
  - RSVP summary statistics and charts
  - Menu planning with choice counts
  - Dietary requirements tracking
  - Data export to CSV
  - Search and filter functionality
- **Admin Settings Page** - Web-based configuration editor for:
  - Edit all configuration settings through the UI
  - Real-time changes to wedding details, menus, deadlines, and event information
  - Automatic backup creation before saving
  - No need to manually edit TOML files

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/rcastley/rsvp
   cd rsvp
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure secrets**

   Copy the example secrets file and customize it:

   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

   Then edit `.streamlit/secrets.toml` with your wedding details:

   - **Required settings:** wedding couple names, admin password, RSVP deadline
   - **Menu options:** Customize starters, mains, and desserts (with optional detailed descriptions)
   - **Event details:** Ceremony and reception venues, timeline, accommodations
   - **Optional:** Transportation, dress code, registry, contact information

   See `.streamlit/secrets.toml.example` for a complete configuration template with all available options.

   **Note:** After the initial setup, you can edit all settings (including secrets.toml) through the Admin Settings page in the web interface (see below).

## Running the Application

1. **Start the Streamlit app**

   ```bash
   streamlit run app.py
   ```

2. **Access the application**
   - Open your browser to `http://localhost:8501`
   - The RSVP form will be the default landing page

3. **Admin access**
   - Navigate to "Admin Login" from the sidebar
   - Enter the password configured in secrets.toml
   - Access admin features:
     - **Summary** - View RSVP statistics, attendance charts, and dietary requirements
     - **Menu Planning** - See menu choice counts and meal planning totals
     - **Data Export** - Search, filter, and export RSVP data to CSV
     - **Settings** - Edit all configuration settings through a web interface, including secrets.toml (no need to manually edit TOML files)

## Using the Admin Settings Page

The Admin Settings page allows you to modify your wedding configuration (secrets.toml) without editing files directly:

1. Log in to the admin dashboard
2. Navigate to "Settings" from the sidebar
3. Edit any configuration values:
   - Wedding details (couple names, page title, banner)
   - Admin password
   - Menu options (add/remove/edit menu items and descriptions)
   - RSVP deadline and grace periods
   - Event information (venues, timeline, accommodations)
   - Contact information and additional details
4. Click "Save All Changes" to apply
5. Restart the Streamlit app for changes to take effect

**Note:** The Settings page automatically creates a timestamped backup of secrets.toml before saving changes.
