import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re

# ------------------------------------------------------------------
# CONFIGURATION – Reads from Streamlit secrets
# ------------------------------------------------------------------
ADMIN_EMAIL = st.secrets["smtp"]["username"]          # your Gmail address
ADMIN_PASSWORD = st.secrets["smtp"]["password"]       # app password
SMTP_SERVER = st.secrets["smtp"]["server"]
SMTP_PORT = st.secrets["smtp"]["port"]

# Admin app login password (change or read from secrets)
ADMIN_LOGIN_PASSWORD = st.secrets.get("admin_password", "admin123")

# In-memory stores (replace with SQLite/Google Sheets for production)
PENDING_USERS = {}
APPROVED_USERS = {}

# ------------------------------------------------------------------
# INDIAN PHONE NUMBER VALIDATION
# ------------------------------------------------------------------
def verify_indian_phone(phone):
    cleaned = re.sub(r'[\s\-\(\)]+', '', phone.strip())
    if cleaned.startswith('+91'):
        number = cleaned[3:]
    elif cleaned.startswith('91'):
        number = cleaned[2:]
    elif cleaned.startswith('0'):
        number = cleaned[1:]
    else:
        number = cleaned
    return bool(re.match(r'^[6-9]\d{9}$', number))

def normalize_indian_phone(phone):
    cleaned = re.sub(r'[\s\-\(\)]+', '', phone.strip())
    digits = re.sub(r'\D', '', cleaned)
    if digits.startswith('91') and len(digits) == 12:
        return f"+{digits}"
    elif digits.startswith('0') and len(digits) == 11:
        return f"+91{digits[1:]}"
    elif len(digits) == 10:
        return f"+91{digits}"
    return cleaned

# ------------------------------------------------------------------
# EMAIL NOTIFICATION (uses secrets)
# ------------------------------------------------------------------
def send_new_user_email(phone_normalized):
    subject = f"🔔 New Dashboard Access Request: {phone_normalized}"
    body = f"""
    ➡️ New access request for Zen Estate Dashboard!
    
    📱 Phone: {phone_normalized}
    ⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    ✅ Approve or ❌ Reject in the app's admin panel.
    
    Dashboard URL: https://zen-estate-financial-dashboard.streamlit.app/
    """
    
    msg = MIMEMultipart()
    msg['From'] = st.secrets["smtp"]["from_email"]
    msg['To'] = ADMIN_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ Email failed: {e}")
        return False

# ------------------------------------------------------------------
# ADMIN APPROVAL PANEL
# ------------------------------------------------------------------
def admin_panel():
    st.sidebar.markdown("---")
    st.sidebar.subheader("✅ Admin Approval Panel")
    
    if not PENDING_USERS:
        st.sidebar.info("No pending requests")
        return
    
    for phone, req_time in list(PENDING_USERS.items()):
        col1, col2, col3 = st.sidebar.columns([2, 1, 1])
        with col1:
            st.code(phone)
            st.caption(f"Requested {req_time.strftime('%H:%M')}")
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
    if 'user_phone' not in st.session_state:
        st.session_state.user_phone = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    
    if st.session_state.user_phone and st.session_state.user_phone in APPROVED_USERS:
        return True
    
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
            PENDING_USERS[normalized] = datetime.now()
            if send_new_user_email(normalized):
                st.success("✅ Request sent! Admin will be notified. Please wait for approval.")
            else:
                st.warning("Request submitted but email notification failed.")
    
    # Admin login section
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
