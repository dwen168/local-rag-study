import streamlit as st
import time

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Create user_state
if 'user_state' not in st.session_state:
    st.session_state.user_state = {
        'username': '',
        'password': '',
        'logged_in': False
    }


def login():
    if not st.session_state.user_state['logged_in']:
        st.write('Please login')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submit = st.button('Login')

        # Check if user is logged in
        if submit and st.session_state.user_state['logged_in'] == False:
            if username == 'admin' and password == '1234':
                st.session_state.user_state['username'] = username
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
        time.sleep(2.5)
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

#https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation
#https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded
chatspace = st.Page(
    "workingspace/chat_space.py", title="Let's Talk", icon=":material/chat:", default=True
)

uploadfile = st.Page(
    "workingspace/document_upload.py", title="Document Upload", icon=":material/upload_file:", default=False
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
