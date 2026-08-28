import streamlit as st

from ui.sidebar import render_sidebar
from ui.dashboard import render_dashboard
from ui.workspace import render_workspace


# ============================================================
# ACCELERATE CANVAS ADMINISTRATION SUITE
# Version 0.2 Alpha
#
# Main application entry point.
# ============================================================


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Accelerate Canvas Administration Suite",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "active_module" not in st.session_state:
    st.session_state.active_module = None


# ============================================================
# GLOBAL BRAND STYLES
# ============================================================

st.markdown(
    """
<style>

/* ==========================================================
   MAIN APPLICATION
   ========================================================== */

.stApp {
    background-color: #F7F9FC;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}


/* ==========================================================
   MAIN PAGE HEADINGS
   ========================================================== */

section[data-testid="stMain"] h1,
section[data-testid="stMain"] h2,
section[data-testid="stMain"] h3 {
    color: #1F3768;
}


/* ==========================================================
   SIDEBAR BACKGROUND
   ========================================================== */

section[data-testid="stSidebar"] {
    background-color: #1F3768;
}


/* ==========================================================
   SIDEBAR HEADINGS
   ========================================================== */

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
}


/* ==========================================================
   SIDEBAR NORMAL TEXT
   ========================================================== */

section[data-testid="stSidebar"] p {
    color: #D8E8F7;
}


/* ==========================================================
   SIDEBAR CAPTIONS
   ========================================================== */

section[data-testid="stSidebar"]
[data-testid="stCaptionContainer"] {
    color: #D8E8F7 !important;
}

section[data-testid="stSidebar"]
[data-testid="stCaptionContainer"] p {
    color: #D8E8F7 !important;
}


/* ==========================================================
   SIDEBAR INPUT LABELS
   ========================================================== */

section[data-testid="stSidebar"] label {
    color: #FFFFFF !important;
    font-weight: 600;
}


/* ==========================================================
   SIDEBAR TEXT INPUTS
   ========================================================== */

section[data-testid="stSidebar"]
div[data-baseweb="input"] {

    background-color: #FFFFFF !important;
    border-radius: 8px !important;
    border: 1px solid #D8DEE8 !important;
}


/* Input focus */

section[data-testid="stSidebar"]
div[data-baseweb="input"]:focus-within {

    border: 2px solid #79B8D8 !important;

    box-shadow:
        0 0 0 2px
        rgba(121, 184, 216, 0.20) !important;
}


/* Actual input text */

section[data-testid="stSidebar"] input {

    color: #1F2937 !important;
    background-color: #FFFFFF !important;
}


/* Input placeholders */

section[data-testid="stSidebar"]
input::placeholder {

    color: #8A94A6 !important;
    opacity: 1 !important;
}


/* ==========================================================
   SIDEBAR RADIO BUTTONS
   ========================================================== */

section[data-testid="stSidebar"]
div[role="radiogroup"] label {

    color: #FFFFFF !important;
}

section[data-testid="stSidebar"]
div[role="radiogroup"] label p {

    color: #FFFFFF !important;
}


/* ==========================================================
   SIDEBAR BUTTON
   ========================================================== */

section[data-testid="stSidebar"]
div.stButton > button {

    background-color: #79B8D8 !important;

    color: #102A43 !important;

    border: 1px solid #79B8D8 !important;

    border-radius: 8px !important;

    font-weight: 700 !important;

    min-height: 42px !important;

    transition:
        background-color 0.15s ease,
        border-color 0.15s ease,
        transform 0.15s ease,
        box-shadow 0.15s ease !important;
}


/* Button text */

section[data-testid="stSidebar"]
div.stButton > button * {

    color: #102A43 !important;
}


/* Button hover */

section[data-testid="stSidebar"]
div.stButton > button:hover {

    background-color: #92C8E2 !important;

    border-color: #92C8E2 !important;

    box-shadow:
        0 3px 8px
        rgba(0, 0, 0, 0.18) !important;

    transform: translateY(-1px);
}


/* Button pressed */

section[data-testid="stSidebar"]
div.stButton > button:active {

    background-color: #69A8C8 !important;

    transform: translateY(0);

    box-shadow:
        0 1px 3px
        rgba(0, 0, 0, 0.15) !important;
}


/* Button keyboard focus */

section[data-testid="stSidebar"]
div.stButton > button:focus {

    outline: 2px solid #FFFFFF !important;
    outline-offset: 2px !important;
}


/* ==========================================================
   SIDEBAR DIVIDERS
   ========================================================== */

section[data-testid="stSidebar"] hr {

    border-color:
        rgba(255, 255, 255, 0.18) !important;
}


/* ==========================================================
   SIDEBAR STATUS BOXES
   ========================================================== */

section[data-testid="stSidebar"]
[data-testid="stAlert"] p {

    color: inherit !important;
}


/* ==========================================================
   APPLICATION HEADER
   ========================================================== */

.accelerate-header {

    background-color: #1F3768;

    padding: 28px 32px;

    border-radius: 14px;

    margin-bottom: 28px;
}


.accelerate-header-title {

    color: #FFFFFF;

    font-size: 34px;

    font-weight: 700;

    line-height: 1.2;

    margin: 0;

    padding: 0;
}


.accelerate-header-subtitle {

    color: #D8E8F7;

    font-size: 17px;

    margin-top: 8px;

    padding: 0;
}


/* ==========================================================
   FOOTER
   ========================================================== */

.accelerate-footer {

    margin-top: 2rem;

    padding-top: 1.25rem;

    border-top:
        1px solid #D8DEE8;

    color: #6B7280;

    font-size: 13px;

    line-height: 1.7;
}


.accelerate-footer strong {

    color: #1F3768;
}

</style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

connection_settings = render_sidebar()


# ============================================================
# APPLICATION HEADER
#
# IMPORTANT:
# Keep this HTML as compact concatenated strings.
# This prevents Streamlit Markdown from interpreting indented
# HTML as a code block.
# ============================================================

st.markdown(
    '<div class="accelerate-header">'
    '<div class="accelerate-header-title">'
    'Accelerate Canvas Administration Suite'
    '</div>'
    '<div class="accelerate-header-subtitle">'
    'Enterprise automation for Canvas LMS administration'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# APPLICATION ROUTING
# ============================================================

if st.session_state.active_module is None:

    render_dashboard()

else:

    render_workspace(
        st.session_state.active_module
    )


# ============================================================
# FOOTER
#
# Also kept as compact HTML to prevent the same raw HTML
# rendering issue from occurring in the footer.
# ============================================================

st.markdown(
    '<div class="accelerate-footer">'
    '<strong>'
    'Accelerate Canvas Administration Suite'
    '</strong>'
    '&nbsp;•&nbsp;'
    'Version 0.2 Alpha'
    '<br>'
    '© 2026 Accelerate Education. All rights reserved.'
    '</div>',
    unsafe_allow_html=True
)