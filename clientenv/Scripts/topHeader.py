from customFunction import get_base64_image

def topHeader(st, user_name):
    img_base64 = get_base64_image(r"C:\MAMP\htdocs\axisBankTransactionAnalytics\clientenv\Scripts\fav_icon.png")
    
     # ---------- Inject CSS + HTML ----------
    st.markdown(
        f"""
        <style>

        /* ===== Header background ===== */
        header[data-testid="stHeader"] {{
            background-color: #9E1B4F;
        }}

        /* ===== Insert logo in header ===== */
        header[data-testid="stHeader"]::before {{
            content: "";
            display: block;
            background-image: url("data:image/png;base64,{img_base64}");
            background-repeat: no-repeat;
            background-size: contain;
            height: 40px;
            width: 180px;
            position: absolute;
            left: 15px;
            top: 8px;
        }}
        
        header[data-testid="stHeader"]::after {{
            content: "{user_name} ";
            color: #FFFFFF;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 0.5px;
            margin-right: 25px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )