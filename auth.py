import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import phonenumbers

# ------------------------------------------------------------------
# CONFIGURATION – Replace with your own details
# ------------------------------------------------------------------
ADMIN_EMAIL = "your-email@gmail.com"          # Your Gmail address
ADMIN_PASSWORD = "abcd efgh ijkl mnop"        # Gmail app password (16 chars)
ADMIN_LOGIN_PASSWORD = "admin123"             # Password to login as admin in the app

# In-memory stores (replace with SQLite/Google Sheets for persistence)
PENDING_USERS = {}   # {phone: request_time}
APPROVED_USERS = {}  # {phone: approved_time}

# ------------------------------------------------------------------
# EMAIL SENDING FUNCTION
# ------------------------------------------------------------------
def send_new_user_email(phone_number):
    """Send email to admin when a new user requests access."""
    subject = f"🔔 New Dashboard Access Request from {phone_number}"
    body = f"""
    A new user has requested access to the Zen Estate Financial Dashboard.
    
    📱 Phone: {phone_number}
    🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Action: Log in to the app as admin to approve or reject this request.
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
# PHONE NUMBER VALIDATION
# ------------------------------------------------------------------
def verify_phone(phone):
    try:
        parsed = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed)
    except:
        return False

# ------------------------------------------------------------------
# APPROVAL PANEL (shown only to admin)
# ------------------------------------------------------------------
def admin_panel():
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Admin Panel")
    if PENDING_USERS:
        st.sidebar.write("**Pending Requests:**")
        for phone, req_time in list(PENDING_USERS.items()):
            col1, col2, col3 = st.sidebar.columns([2, 1, 1])
            with col1:
                st.write(f"📱 {phone}")
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
    else:
        st.sidebar.info("No pending requests")

# ------------------------------------------------------------------
# AUTHENTICATION UI
# ------------------------------------------------------------------
def authentication_ui():
    """Show login/request form. Returns True if user is approved."""
    
    # Initialize session state
    if 'user_phone' not in st.session_state:
        st.session_state.user_phone = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    
    # If already approved, return True
    if st.session_state.user_phone:
        return True
    
    # Not logged in – show request form
    st.title("🔐 Access Required")
    st.write("Enter your mobile number to request access to the dashboard.")
    
    phone = st.text_input("Mobile Number (e.g., +1234567890)", placeholder="+1 (555) 123-4567")
    
    if st.button("Request Access"):
        if not phone:
            st.error("Please enter a phone number")
        elif not verify_phone(phone):
            st.error("Invalid phone number format (include country code)")
        elif phone in APPROVED_USERS:
            st.success("You already have access! Redirecting...")
            st.session_state.user_phone = phone
            st.rerun()
        elif phone in PENDING_USERS:
            st.info("Your request is pending admin approval. Check back later.")
        else:
            # Add to pending list and send email
            PENDING_USERS[phone] = datetime.now()
            email_sent = send_new_user_email(phone)
            if email_sent:
                st.success("✅ Access request submitted! An email notification has been sent to the admin. Please wait for approval.")
            else:
                st.warning("Request submitted but email notification failed. Admin may not see it immediately.")
    
    # Admin login (hidden in sidebar)
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔑 Admin Login")
        pwd = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if pwd == ADMIN_LOGIN_PASSWORD:
                st.session_state.is_admin = True
                st.success("Logged in as admin")
                st.rerun()
            else:
                st.error("Wrong password")
        
        if st.session_state.is_admin:
            admin_panel()
            if st.button("Logout Admin"):
                st.session_state.is_admin = False
                st.rerun()
    
    return False
