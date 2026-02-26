import streamlit as st
import authenticateUser

import loginPage
import statementPdfUploadPage
import customerDashboardPage
import managementDashboardPage
import customersListPage

from streamlit_js_eval import streamlit_js_eval

st.set_page_config(
    page_title="Axis Bank | Statement Analysis",
    page_icon="C:/MAMP/htdocs/axisBankTransactionAnalytics/clientenv/Scripts/fav_icon.png",
    layout="wide"
) 


# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

    @font-face {
        font-family: 'BankFont';
        src: url('https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Me5Q.ttf');
    }

    * {
        font-family: 'BankFont', sans-serif !important;
    }

    .st-key-user_role_token_check {
        display: none !important;    
    }
    
    .st-key-user_id_token_check {
        display: none !important;
    }
    
    .st-key-user_name_token_check {
        display: none !important;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2.8rem !important;
        padding-bottom: 5rem !important;
        max-width: 95% !important;
    }
    
    [data-testid="column"]:nth-of-type(1)::after {
        border-left: 1px solid #e3e3e3;
        padding: 40px;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 2rem !important;
    }

    [data-testid="stImage"] img {
        max-height: 400px; /* Limits the vertical growth */
        object-fit: contain;
        border-radius: 12px;
    }

    /* Main split container */
    .login-container {
        display: flex;
        height: 80vh;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0,0,0,0.1);
    }

    /* LEFT PANEL */
    .left-panel {
        flex: 1;
        background-color: #ffffff;
        padding: 40px;
    }

    .left-panel h2 {
        margin-bottom: 20px;
        font-weight: 600;
    }

    /* RIGHT PANEL */
    .right-panel {
        flex: 1;
        background: linear-gradient(135deg,#f5f7fa,#e4e8ef);
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 40px;
    }

    /* Login button */
    .stButton > button {
        background-color: #A0003E;
        color: white;
        border-radius: 8px;
        height: 45px;
        width: 100%;
        font-size: 16px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #820032;
        color: white;
    }

    /* Input box styling */
    input {
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

## To set logged in session ##
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Upload'

###### Main Flow  - Start #####
if st.session_state['logged_in'] == True:
    user_role = streamlit_js_eval(js_expressions="localStorage.getItem('user_role_token')", key='user_role_token_check')
    if user_role!='null' and user_role!='undefined' and user_role!=None:
        user_id = streamlit_js_eval(js_expressions="localStorage.getItem('user_id_token')", key='user_id_token_check')
        user_page_select = streamlit_js_eval(js_expressions="localStorage.getItem('user_page_select_token')", key='user_page_select_check')
        user_name = streamlit_js_eval(js_expressions="localStorage.getItem('user_name_token')", key='user_name_token_check')
        if st.session_state['current_page'] == "customers_list":
            customersListPage.customersListPage(st, user_name)
        elif st.session_state['current_page'] == "customer_dashboard":
            customerDashboardPage.customer_dashboard(st, st.session_state['selected_user_id'], user_name)
        else:
            if user_page_select == 'Upload':
                statementPdfUploadPage.statement_pdf_upload(st, user_id, user_name)
            elif user_page_select == 'Dashboard':
                if user_role == 'Customer':
                    customerDashboardPage.customer_dashboard(st, user_id, user_name)
                elif user_role == 'Management':
                    managementDashboardPage.management_dashboard(st, user_id, user_name)
            
        st.markdown('<div class="logout-button"></div>', unsafe_allow_html=True)
        if st.button("Log Out", key="sidebar_logout"):
            # Clear persistent token
            streamlit_js_eval(js_expressions="localStorage.removeItem('user_name_token');", key='user_name_token_clear')
            streamlit_js_eval(js_expressions="localStorage.removeItem('user_role_token');", key='user_role_token_clear')
            streamlit_js_eval(js_expressions="localStorage.removeItem('user_id_token');", key='user_id_token_clear')
            streamlit_js_eval(js_expressions="localStorage.removeItem('user_page_select_token');", key='user_page_select_token_clear')
            st.session_state['logged_in'] = False
            st.session_state['current_page'] = 'Upload'
            
            import time
            time.sleep(1) 
            st.rerun()
    else:
        loginPage.login_form(st, authenticateUser, streamlit_js_eval)
else:
    loginPage.login_form(st, authenticateUser, streamlit_js_eval)


# st.markdown("""
#         <style>
#             /* Target ONLY the button with the key 'sidebar_logout' */
#             div[data-testid="stElementContainer"]:has(button[key="sidebar_logout"]) {
#                 position: fixed;
#                 bottom: 20px;
#                 left: 20px;
#                 z-index: 999999;
#                 width: auto;
#             }
 
#             /* Target the specific button container */
#             div.stButton > button:first-child {
#                 position: fixed;
#                 bottom: 20px;
#                 width: auto !important;
#                 padding: 4px 20px !important;
#                 font-size: 14px !important;
#                 height: auto !important;
#                 min-height: unset !important;
#                 background-color: #861f41;
#                 color: white;
#                 border-radius: 4px;
#                 border: 1px solid #861f41;
#                 z-index: 999999;
#             }

#             div.stButton > button:first-child:hover {
#                 background-color: #a21c44;
#                 border-color: #a21c44;
#                 color: white;
#             }
#         </style>
#         """, unsafe_allow_html=True)

## To check session already logged in or not ##
if not st.session_state['logged_in']:
    stored_token = streamlit_js_eval(js_expressions="localStorage.getItem('user_name_token')", key='user_name_token_check')
    if stored_token and stored_token != 'null' and stored_token != 'undefined' and stored_token !=None:
        st.session_state['logged_in'] = True
        import time
        time.sleep(1)
        st.rerun() 