import streamlit as st
import base64
import boto3
import topHeader
from streamlit_pdf_viewer import pdf_viewer
from streamlit_js_eval import streamlit_js_eval

# --- Define the Confirmation Dialog ---
@st.dialog("Confirm Upload")
def confirm_upload_dialog(uploaded_file, s3, BUCKET_NAME, AWS_REGION):
    st.write(f"Are you sure you want to upload **{uploaded_file.name}**?")
    st.warning("This action will process the statement for upload.")
    user_id = streamlit_js_eval(js_expressions="localStorage.getItem('user_id_token')", key='user_id_token_pdf')
    
    print(user_id)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Yes, Upload", type="primary", use_container_width=True):
            # --- Place your actual processing logic here ---
            st.session_state.uploader_key += 1
            callUploadtoS3(uploaded_file, s3, BUCKET_NAME, AWS_REGION, user_id)
    with c2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
            
def callUploadtoS3(uploaded_file, s3, BUCKET_NAME, AWS_REGION, user_id):
    print(user_id)
    try:
        s3.upload_fileobj(
            uploaded_file,
            BUCKET_NAME,
            f"input/{user_id}_{uploaded_file.name}",   # S3 folder path
            ExtraArgs={"ContentType": "application/pdf"}
        )

        st.session_state.uploader_key += 1
        st.toast("Upload complete!", icon="✅")
        # st.rerun()
        
        # File URL (if bucket public)
        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/input/{uploaded_file.name}"
        # st.write("🔗 File URL:", file_url)

    except Exception as e:
        st.error(f"❌ Upload Failed: {e}")

def statement_pdf_upload(st, user_id, user_name):
    # statment pdf upload page
    # ---- HEADING ----
    st.subheader("Statement Upload - PDF")
    
    
    st.markdown("""
    <div class="upload-box">
        <p class="upload-text">Drag & Drop PDF Here</p>
        <p style="font-weight: normal; color: gray;">or</p>
        <p style="text-decoration: underline; cursor: pointer;">Click Browse Files</p>
    </div>
    """, unsafe_allow_html=True)

    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0
    
    # ---------- AWS CONFIG ----------
    AWS_ACCESS_KEY = "AKIARPCCUOF6F5LE72LK"
    AWS_SECRET_KEY = "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"
    AWS_REGION = "ap-south-1"
    BUCKET_NAME = "axis-bank-pdf-bucket"

    # ---------- S3 Client ----------
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    uploaded_file = st.file_uploader(
        "📄 Drag & Drop or Click to Upload Axis Bank Statement",
        type=["pdf"],
        label_visibility="collapsed",
        key=f"pdf_uploader_{st.session_state.uploader_key}"
    )
    
    isPreviewLoaded = 0
    # ---------- Handle File ----------
    if uploaded_file is not None:
        
        if uploaded_file.type == "application/pdf":
            st.markdown("##### Statement PDF - Preview")
            pdf_viewer(uploaded_file.getvalue(), width=1000, height=800)
            isPreviewLoaded = 1
            st.write("---") 
        else:
            st.error("❌ Uploaded file is not a PDF")
            
        # File details
        # st.success("✅ PDF Uploaded Successfully")

        # file_details = {
        #     "File Name": uploaded_file.name,
        #     "File Type": uploaded_file.type,
        #     "File Size (KB)": round(uploaded_file.size / 1024, 2)
        # }

        # st.write(file_details)

        # Save file locally (optional)
        # with open(f"uploaded_{uploaded_file.name}", "wb") as f:
        #     f.write(uploaded_file.read())

        # st.info("📁 File saved locally")

    else:
        st.warning("⬆️ Drag & Drop or Click Browse to upload PDF")
    
    if isPreviewLoaded==1:
        col1, col2, col3  = st.columns([2, 3, 2])
        with col2:
            if st.button("Upload Statement", type="primary"):
                confirm_upload_dialog(uploaded_file, s3, BUCKET_NAME, AWS_REGION)
    
    st.markdown("""
        <style>
        .upload-text {
            color: #9E1B4F;
            font-size: 18px;
            font-weight: bold;
        }
        
        .upload-box {
            border: 2px dashed #861f41;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            color: #861f41;
            font-weight: bold;
            position: relative;
            background-color: #fff;
        }

        .stFileUploader {
            position: absolute;
            top: -208px;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            z-index: 10;
            cursor: pointer;
        }
        
        div[data-testid="stFileUploader"] > section {
            padding: 0;
            min-height: 200px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    topHeader.topHeader(st, user_name)
