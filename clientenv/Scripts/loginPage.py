def login_form(st, authenticateUser, streamlit_js_eval):
    with st.container(border=True):
    # ---------- LAYOUT ----------
        col1, col2 = st.columns([2,3], gap="large")

        # ---------- LEFT : LOGIN FORM ----------
        with col1:
            
            # ---- AXIS LOGO ----
            st.image(
                "C:/MAMP/htdocs/axisBankStatementAnalysis/clientenv/Scripts/fav_icon.png",   # your downloaded logo file
                width=100
            )

            # ---- HEADING ----
            st.markdown("### Login using")
            
            user_id = st.text_input("User ID", placeholder="Enter User ID")
            password = st.text_input("Password", type="password", placeholder="Enter Password")

            pageLandingOn = st.selectbox(
                "Login directly to",
                ["Upload","Dashboard"]
            )

            login_btn = st.button("Login")

            if login_btn:
                if user_id == '':
                    st.error('Enter the User ID')
                elif password == '':
                    st.error('Enter the Password')
                else:
                    checkAuthUser = authenticateUser.authenticate_user(user_id, password)
                    
                    if checkAuthUser:
                        st.success("Login Successful ✅")
                        st.session_state['logged_in'] = True
                        js_code = f'localStorage.setItem("user_name_token", "{checkAuthUser[3]}");'
                        streamlit_js_eval(js_expressions=js_code, key='user_name_token_set')
                        
                        js_code = f'localStorage.setItem("user_role_token", "{checkAuthUser[2]}");'
                        streamlit_js_eval(js_expressions=js_code, key='user_role_token_set')
                        
                        js_code = f'localStorage.setItem("user_id_token", "{checkAuthUser[0]}");'
                        streamlit_js_eval(js_expressions=js_code, key='user_id_token_set')
                        
                        st.session_state['current_page'] = pageLandingOn
                        
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Please check your credentials")
        # ---------- RIGHT : BANNER ----------
        with col2:
            st.markdown(
                """
                <div style="text-align:left;">
                    <h4 style="color:#6E6E6E;">Welcome to Axis Bank</h4>
                    <h3>Account Statement Analysis</h3>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.image(
                "https://images.unsplash.com/photo-1587614382346-4ec70e388b28",
                width=525
            )