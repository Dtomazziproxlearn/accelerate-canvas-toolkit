from pathlib import Path

import streamlit as st

from canvas import CanvasAPI


# ============================================================
# ACCELERATE CANVAS ADMINISTRATION SUITE
# Canvas Connection Sidebar
#
# Collects Canvas connection information and target scope.
#
# Explicit widget keys allow other application modules to
# reliably access the current Canvas connection and target.
# ============================================================


# ============================================================
# ASSET PATHS
# ============================================================

LOGO_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "accelerate_education_logo.png"
)


def render_sidebar():
    """
    Render the Canvas connection and target-selection sidebar.

    Returns:
        dict containing:
            canvas_url
            api_token
            scope
            target_id
            connected
            connected_user
    """

    # ========================================================
    # SESSION STATE INITIALIZATION
    # ========================================================

    if "canvas_connected" not in st.session_state:
        st.session_state.canvas_connected = False

    if "canvas_connected_user" not in st.session_state:
        st.session_state.canvas_connected_user = None

    if "canvas_connected_user_id" not in st.session_state:
        st.session_state.canvas_connected_user_id = None

    if "connected_canvas_url" not in st.session_state:
        st.session_state.connected_canvas_url = None


    # ========================================================
    # SIDEBAR TOP SPACING
    #
    # Reduces Streamlit's default top padding so the company
    # logo sits closer to the top of the navy sidebar.
    # ========================================================

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            padding-top: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # COMPANY LOGO
    # ========================================================

    if LOGO_PATH.exists():

        st.sidebar.image(
            str(LOGO_PATH),
            use_container_width=True
        )

    else:

        st.sidebar.caption(
            "Accelerate Education"
        )


    # ========================================================
    # SIDEBAR HEADER
    # ========================================================

    st.sidebar.markdown(
        "## Canvas Connection"
    )

    st.sidebar.caption(
        "Connect securely to a Canvas instance."
    )

    st.sidebar.markdown("---")


    # ========================================================
    # CANVAS URL
    # ========================================================

    canvas_url = st.sidebar.text_input(
        "Canvas URL",
        placeholder="https://school.instructure.com",
        help=(
            "Enter the base URL for the Canvas instance. "
            "Do not include /api/v1."
        ),
        key="canvas_url_input"
    )


    # ========================================================
    # API ACCESS TOKEN
    # ========================================================

    api_token = st.sidebar.text_input(
        "API Access Token",
        type="password",
        placeholder="Enter API token",
        help=(
            "The Canvas API token used to authorize "
            "administrative operations."
        ),
        key="canvas_api_token_input"
    )


    # ========================================================
    # TEST CONNECTION BUTTON
    # ========================================================

    test_connection = st.sidebar.button(
        "Test Connection",
        use_container_width=True,
        key="canvas_test_connection"
    )


    # ========================================================
    # TEST CONNECTION LOGIC
    # ========================================================

    if test_connection:

        # Reset previous connection state before testing again.

        st.session_state.canvas_connected = False
        st.session_state.canvas_connected_user = None
        st.session_state.canvas_connected_user_id = None
        st.session_state.connected_canvas_url = None


        # ----------------------------------------------------
        # VALIDATE CANVAS URL
        # ----------------------------------------------------

        if not canvas_url.strip():

            st.sidebar.error(
                "Enter a Canvas URL before testing the connection."
            )


        # ----------------------------------------------------
        # VALIDATE API TOKEN
        # ----------------------------------------------------

        elif not api_token.strip():

            st.sidebar.error(
                "Enter an API access token before testing the connection."
            )


        # ----------------------------------------------------
        # ATTEMPT CANVAS CONNECTION
        # ----------------------------------------------------

        else:

            canvas = CanvasAPI(
                canvas_url=canvas_url,
                api_token=api_token
            )

            # A normal Streamlit spinner can be placed inside
            # the sidebar using a sidebar context.

            with st.sidebar:

                with st.spinner(
                    "Connecting to Canvas..."
                ):

                    result = canvas.test_connection()


            # ------------------------------------------------
            # CONNECTION SUCCESS
            # ------------------------------------------------

            if result["success"]:

                st.session_state.canvas_connected = True

                st.session_state.canvas_connected_user = (
                    result["user_name"]
                )

                st.session_state.canvas_connected_user_id = (
                    result["user_id"]
                )

                st.session_state.connected_canvas_url = (
                    canvas_url.strip().rstrip("/")
                )

                st.sidebar.success(
                    "Canvas connection successful."
                )


            # ------------------------------------------------
            # CONNECTION FAILURE
            # ------------------------------------------------

            else:

                st.sidebar.error(
                    result["message"]
                )


    # ========================================================
    # TARGET SECTION
    # ========================================================

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "### Target"
    )

    st.sidebar.caption(
        "Choose where the requested administration changes "
        "should be applied."
    )


    # ========================================================
    # TARGET SCOPE
    # ========================================================

    scope = st.sidebar.radio(
        "Apply changes to",
        options=[
            "Single Course",
            "Sub-Account"
        ],
        key="canvas_scope"
    )


    # ========================================================
    # TARGET ID
    #
    # Both target types use the same internal Streamlit key:
    #
    # canvas_target_id
    #
    # This allows downstream modules to retrieve the target
    # without guessing whether it is a Course ID or Account ID.
    # ========================================================

    if scope == "Single Course":

        target_id = st.sidebar.text_input(
            "Course ID",
            placeholder="Enter Course ID",
            help=(
                "Apply the selected operation "
                "to one Canvas course."
            ),
            key="canvas_target_id"
        )

    else:

        target_id = st.sidebar.text_input(
            "Sub-Account ID",
            placeholder="Enter Sub-Account ID",
            help=(
                "Apply the selected operation to courses "
                "within the specified Canvas sub-account."
            ),
            key="canvas_target_id"
        )


    # ========================================================
    # CONNECTION STATUS
    # ========================================================

    st.sidebar.markdown("---")

    st.sidebar.caption(
        "CONNECTION STATUS"
    )


    if st.session_state.canvas_connected:

        user_name = (
            st.session_state.canvas_connected_user
            or "Canvas User"
        )

        st.sidebar.success(
            f"Connected — {user_name}"
        )

    else:

        st.sidebar.info(
            "Not Connected"
        )


    # ========================================================
    # VERSION INFORMATION
    # ========================================================

    st.sidebar.markdown("---")

    st.sidebar.caption(
        "Accelerate Canvas Administration Suite\n\n"
        "Version 0.2 Alpha"
    )


    # ========================================================
    # RETURN CURRENT SIDEBAR SETTINGS
    #
    # app.py receives this dictionary.
    #
    # Other modules may also retrieve these values through
    # the explicit Streamlit session-state keys:
    #
    # canvas_url_input
    # canvas_api_token_input
    # canvas_scope
    # canvas_target_id
    # ========================================================

    return {
        "canvas_url": canvas_url.strip().rstrip("/"),
        "api_token": api_token.strip(),
        "scope": scope,
        "target_id": target_id.strip(),
        "connected": st.session_state.canvas_connected,
        "connected_user": (
            st.session_state.canvas_connected_user
        )
    }