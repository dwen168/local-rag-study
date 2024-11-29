import streamlit as st
import time
import hashlib
import yaml
import os

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Create user_state
if 'user_state' not in st.session_state:
    st.session_state.user_state = {
        'user_id': '',
        'password': '',
        'logged_in': False
    }

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load users from the YAML file
def load_users():
    file_path = 'config/user.yaml'
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'r') as file:
            users = yaml.safe_load(file)
            return {user: hash_password(password) for user, password in users.items()}
    except FileNotFoundError:
        print("can't connect to authorisation service, please try later")
        return {}

def login():
    if not st.session_state.user_state['logged_in']:
        st.write('Please login')
        user_id = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submit = st.button('Login')

        # Load users from the YAML file
        users = load_users()

        # Check if user is logged in
        if submit and st.session_state.user_state['logged_in'] == False:
            if user_id in users:
                hashed_stored_password = users[user_id]
                hashed_password = hash_password(password)
                if hashed_password == hashed_stored_password:
                    st.session_state.user_state['user_id'] = user_id
                    st.session_state.user_state['password'] = password
                    st.session_state.user_state['logged_in'] = True
                    st.write('You are logged in')
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.write("Invalid username or password")

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.write("You have logged out")
        time.sleep(1.5)
        st.rerun()

        
login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

#https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation
#https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded
chatspace = st.Page(
    "workingspace/chat_space.py", title="Let's Talk", icon=":material/chat:", default=True
)

uploadfile = st.Page(
    "workingspace/document_upload.py", title="Manage Knowledge", icon=":material/upload_file:", default=False
)

historychat = st.Page(
    "workingspace/chat_history.py", title="Chat History", icon=":material/history:", default=False
)

if st.session_state.logged_in:
    pg = st.navigation(
            {
                "Account": [logout_page],
                "My Workspace": [chatspace, uploadfile, historychat],
            }
        )
else:
    pg = st.navigation([login_page])

pg.run()
