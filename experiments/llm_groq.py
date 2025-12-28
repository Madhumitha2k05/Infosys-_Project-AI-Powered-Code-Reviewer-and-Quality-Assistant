#from langchain_groq import ChatGroq
#from langchain_core.messages import HumanMessage

#llm = ChatGroq(
#    model="llama-3.1-8b-instant",
#    temperature=0.3,
#)

#response = llm.invoke([
##])


#print(response.content)







import streamlit as st
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Madhumitha - AI Powered Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ================= CUSTOM CSS =================
st.markdown(
    """
    <style>

    /* App background */
    .stApp {
        background: linear-gradient(135deg, #e3f2fd, #ede7f6);
        font-family: 'Segoe UI', sans-serif;
        color: #111827;
    }

    /* Main card */
    .block-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 18px;
        box-shadow: 0px 12px 35px rgba(0,0,0,0.1);
    }

    /* Headings */
    h1, h2, h3 {
        color: #1e3a8a;
        font-weight: 700;
    }

    /* Text input */
    textarea, input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 10px !important;
        border: 1.8px solid #c7d2fe !important;
        font-size: 15px !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72, #2a5298);
    }

    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
        font-weight: 500;
    }

    /* ===== SELECTBOX FIX (REMOVE VERTICAL LINE & VISIBILITY) ===== */

    /* The Main Box Container */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #2563eb !important;
        border-radius: 12px !important;
        padding-right: 0px !important; /* Reset padding to avoid gaps */
        box-shadow: none !important;
        display: flex;
        align-items: center;
    }

    /* Remove the internal vertical divider line completely */
    div[data-baseweb="select"] > div > div {
        border: none !important;
        background-color: transparent !important;
    }

    /* Hide the default Streamlit SVG arrow (this often causes the line issue) */
    div[data-baseweb="select"] svg {
        display: none !important;
    }

    /* Ensure the Selected Text is Black and Visible */
    div[data-baseweb="select"] span {
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    /* Create a Clean Custom Arrow */
    div[data-baseweb="select"] > div::after {
        content: "▼";
        position: absolute;
        right: 15px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 12px;
        color: #2563eb;
        pointer-events: none;
        font-family: sans-serif;
    }

    /* Dropdown menu options container */
    ul[data-baseweb="menu"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
    }

    /* Individual list items in the dropdown */
    li[data-baseweb="option"] {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #2563eb, #1e40af);
        color: white;
        border: none;
        padding: 0.65em 1.4em;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        transition: 0.25s ease;
    }

    .stButton>button:hover {
        transform: scale(1.04);
        background: linear-gradient(90deg, #1e40af, #2563eb);
    }

    /* Expander */
    details {
        background-color: #f9fafb;
        border-radius: 14px;
        border: 2px solid #22c55e;
        padding: 12px;
    }

    summary {
        font-weight: 700;
        font-size: 16px;
        color: #166534;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Load API key
api_key = os.getenv("GROQ_API_KEY")

# ================= SIDEBAR =================
with st.sidebar:
    st.header("⚙️ Settings")

    # Modified Selectbox
    model_name = st.selectbox(
        "Select Model",
        options=[
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-120b"
        ]
    )

    temperature = st.slider(
        "Response Creativity",
        0.0, 1.0, 0.3, 0.1
    )

    st.caption("🚀 Powered by Groq + LangChain")

# ================= MAIN UI =================
st.title("🤖 AI-Powered Chatbot")
st.caption("Get structured AI responses to your queries instantly.")

st.markdown(
    """
    Welcome to the **AI Powered Chatbot**.  
    Ask your question below and get a structured AI response instantly.
    """
)

st.subheader("📝 Enter your Prompt")

user_input = st.text_area(
    "Ask something to the AI:",
    value="What is a Data Scientist? Explain step by step.",
    height=120
)

run_btn = st.button("🚀 Run AI")

# ================= LLM LOGIC =================
if not api_key:
    st.error("❌ GROQ_API_KEY not found. Please add it to your .env file.")
else:
    llm = ChatGroq(
        model=model_name,
        temperature=temperature,
        api_key=api_key
    )

    if run_btn:
        if not user_input.strip():
            st.warning("⚠️ Please enter a prompt.")
        else:
            with st.spinner("🤖 AI is thinking..."):
                response = llm.invoke(user_input)

            st.markdown("---")
            st.subheader("📌 AI Response")

            with st.expander("🔍 View Answer", expanded=True):
                st.write(response.content)

            st.success("✅ Response generated successfully!")