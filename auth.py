import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re

# ------------------------------------------------------------------
# CONFIGURATION – Replace with your own details
# ------------------------------------------------------------------
ADMIN_EMAIL = "your-email@gmail.com"
ADMIN_PASSWORD = "abcd efgh ijkl mnop"  # Gmail app password
ADMIN_LOGIN_PASSWORD = "admin123"       # Dashboard admin password

# In-memory stores (replace with SQLite/Google Sheets for persistence)
PENDING_USERS = {}  # {phone: request_time}
APPROVED_USERS = {} # {phone: approved_time}

# ------------------------------------------------------------------
# INDIAN PHONE NUMBER VALIDATION
# ------------------------------------------------------------------
def verify_indian_phone(phone):
    """
    Validates Indian mobile numbers:
    - Must start with +91 or 0
    - Must be 10 digits after that
    - Must start with 6,7,8,9
    """
    # Remove spaces, dashes, brackets
    cleaned = re.sub(r'[\s\-\(\)]+', '', phone.strip())
    
    # Check for +91 or 91 or 0 prefix
    if cleaned.startswith('+91'):
        number = cleaned[3:]  # Remove +91
    elif cleaned.startswith('91'):
        number = cleaned[2:]  # Remove 91
    elif cleaned.startswith('0'):
        number = cleaned[1:]  # Remove leading 0 (landline style)
    else:
        number = cleaned  # Assume it's 10-digit mobile number
    
    # Indian mobile numbers: 10 digits, first digit is 6-9
    if re.match(r'^[6-9]\d{9}$', number):
        return True
    else:
        return False

def normalize_indian_phone(phone):
    """Return standardized Indian mobile number: +91XXXXXXXXXX"""
    cleaned = re.sub(r'[\s\-\(\)]+', '', phone.strip())
    # Extract digits only
    digits = re.sub(r'\D', '', cleaned)
    
    # Handle various prefixes
    if digits.startswith('91') and len(digits) == 12:
        return f"+{digits}"  # Already +91 format
    elif digits.startswith('0') and len(digits) == 11:
        return f"+91{digits[1:]}"  # Remove leading 0
    elif len(digits) == 10:
        return f"+91{digits}"  # Add country code
    else:
        return cleaned  # Fallback

# ------------------------------------------------------------------
# EMAIL NOTIFICATION
# ------------------------------------------------------------------
def send_new_user_email(phone_normalized):
    """Send email to admin when new user requests access."""
    subject = f"🔔 New Dashboard Access Request: {phone_normalized}"
    body = f"""
    ➡️ New access request for Zen Estate Dashboard!
    
    📱 Phone: {phone_normalized}
    ⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    ✅ Approve or ❌ Reject in the app's admin panel.
    
    Dashboard URL: https://zen-estate-financial-dashboard.streamlit.app/
    """
    
    msg = MIMEMultipart()
    msg['From'] = ADMIN_EMAIL
    msg['To'] = ADMIN_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

# ------------------------------------------------------------------
# ADMIN APPROVAL PANEL
# ------------------------------------------------------------------
def admin_panel():
    """Show pending requests with approve/reject buttons."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("✅ Admin Approval Panel")
    
    if not PENDING_USERS:
        st.sidebar.info("No pending requests")
        return
    
    for phone, req_time in list(PENDING_USERS.items()):
        col1, col2, col3 = st.sidebar.columns([2, 1, 1])
        with col1:
            st.code(phone)
            st.caption(f"Requested: {req_time.strftime('%H:%M')}")
        with col2:
            if st.button("✅ Approve", key=f"ap_{phone}"):
                APPROVED_USERS[phone] = datetime.now()
                del PENDING_USERS[phone]
                st.sidebar.success(f"Approved {phone}")
                st.rerun()
        with col3:
            if st.button("❌ Reject", key=f"rj_{phone}"):
                del PENDING_USERS[phone]
                st.sidebar.warning(f"Rejected {phone}")
                st.rerun()

# ------------------------------------------------------------------
# AUTHENTICATION UI GATE
# ------------------------------------------------------------------
def authentication_ui():
    """Returns True if user is approved, otherwise shows request form."""
    
    # Initialize session state
    if 'user_phone' not in st.session_state:
        st.session_state.user_phone = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    
    # Already approved
    if st.session_state.user_phone and st.session_state.user_phone in APPROVED_USERS:
        return True
    
    # Show request form
    st.title("🔐 Access Required")
    st.write("Zen Estate Financial Dashboard")
    st.info("Enter your **Indian mobile number** (+91) to request access.")
    
    phone = st.text_input("Mobile Number", 
                         placeholder="+91 9876543210 or 9876543210",
                         help="Indian mobile number (10 digits, starting with 6-9)")
    
    if st.button("Request Access"):
        if not phone:
            st.error("Please enter a phone number")
            return False
            
        if not verify_indian_phone(phone):
            st.error("Invalid Indian mobile number. It must be a 10-digit number starting with 6,7,8 or 9.")
            return False
        
        normalized = normalize_indian_phone(phone)
        
        if normalized in APPROVED_USERS:
            st.success("✅ You already have access! Loading dashboard...")
            st.session_state.user_phone = normalized
            st.rerun()
            return True
        elif normalized in PENDING_USERS:
            st.info("⏳ Your request is pending admin approval.")
        else:
            # Add to pending and notify admin
            PENDING_USERS[normalized] = datetime.now()
            if send_new_user_email(normalized):
                st.success("✅ Request sent! Admin will be notified. Please wait for approval.")
            else:
                st.warning("Request submitted but email notification failed. Admin may need to check manually.")
    
    # Admin login section (hidden in sidebar)
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔑 Admin Login")
        with st.form("admin_login"):
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if pwd == ADMIN_LOGIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.success("Admin logged in")
                    st.rerun()
                else:
                    st.error("Wrong password")
        
        if st.session_state.is_admin:
            admin_panel()
            if st.button("Logout Admin"):
                st.session_state.is_admin = False
                st.rerun()
    
    return False
