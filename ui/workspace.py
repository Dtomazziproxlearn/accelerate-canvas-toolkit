import streamlit as st

from canvas import CanvasAPI

from tools.authorization import verify_accelerate_course

from ui.quiz_workspace import render_quiz_workspace
from ui.assignment_workspace import render_assignment_workspace
from ui.course_workspace import render_course_workspace


# ============================================================
# ACCELERATE CANVAS ADMINISTRATION SUITE
# Workspace Controller
#
# Routes dashboard modules to their dedicated workspace files.
#
# SINGLE-COURSE AUTHORIZATION:
# Before Course, Assignment, or Quiz Management controls are
# displayed for a Single Course target, the selected course
# must pass Accelerate Education course verification.
#
# Changing the Course ID clears the previous verification and
# any stored Preview or execution data tied to the old target.
# ============================================================


# ============================================================
# AUTHORIZATION SESSION STATE
# ============================================================


def initialize_authorization_state():
    """
    Initialize shared course-verification session state.
    """

    defaults = {
        "authorization_target_id": None,
        "authorization_verified_course_id": None,
        "authorization_passed": False,
        "authorization_result": None,
    }

    for key, default_value in defaults.items():

        if key not in st.session_state:

            st.session_state[
                key
            ] = default_value


# ============================================================
# CLEAR TARGET-SPECIFIC WORKSPACE STATE
# ============================================================


def clear_target_workspace_state():
    """
    Clear Preview, confirmation, and execution data that may
    belong to a previously selected Course ID.

    Configuration selections are intentionally preserved where
    possible, but no Preview or execution result is allowed to
    carry over to a different course.
    """

    explicit_keys = [
        # Course Management
        "course_preview",
        "course_preview_signature",
        "course_execution_results",
        "course_confirm_apply",

        # Assignment Management
        "assignment_preview",
        "assignment_preview_signature",
        "assignment_execution_results",
        "assignment_confirm_apply",

        # Quiz & Exam Management
        "quiz_preview",
        "quiz_preview_signature",
        "quiz_execution_results",
        "quiz_confirm_apply",
    ]

    for key in explicit_keys:

        if key in st.session_state:

            if key.endswith(
                "confirm_apply"
            ):

                st.session_state[
                    key
                ] = False

            else:

                st.session_state[
                    key
                ] = None


    # --------------------------------------------------------
    # DEFENSIVE CLEANUP
    #
    # This catches future Preview/result keys that follow the
    # established naming pattern without removing settings.
    # --------------------------------------------------------

    protected_fragments = (
        "preview",
        "execution_result",
        "confirm_apply",
    )

    for key in list(
        st.session_state.keys()
    ):

        if not key.startswith(
            (
                "course_",
                "assignment_",
                "quiz_",
            )
        ):

            continue

        if not any(
            fragment in key
            for fragment in protected_fragments
        ):

            continue

        if "confirm_apply" in key:

            st.session_state[
                key
            ] = False

        else:

            st.session_state[
                key
            ] = None


# ============================================================
# RESET AUTHORIZATION
# ============================================================


def reset_course_authorization():
    """
    Reset verification for the currently selected target.
    """

    st.session_state.authorization_verified_course_id = None
    st.session_state.authorization_passed = False
    st.session_state.authorization_result = None


# ============================================================
# DETECT COURSE-ID CHANGES
# ============================================================


def sync_authorization_target(
    target_id
):
    """
    Detect when the Course ID changes.

    A verification result is valid only for the exact Course ID
    that was inspected. Changing the ID resets verification,
    Preview data, confirmations, and execution results.
    """

    normalized_target_id = str(
        target_id
        or ""
    ).strip()

    previous_target_id = (
        st.session_state.get(
            "authorization_target_id"
        )
    )

    if (
        previous_target_id
        != normalized_target_id
    ):

        st.session_state.authorization_target_id = (
            normalized_target_id
        )

        reset_course_authorization()

        clear_target_workspace_state()

    return normalized_target_id


# ============================================================
# CANVAS CONNECTION
# ============================================================


def get_authorization_canvas_connection():
    """
    Build a CanvasAPI instance from the connection information
    collected by the shared sidebar.

    Returns:
        tuple:
            canvas
            error_message
    """

    connected = st.session_state.get(
        "canvas_connected",
        False
    )

    canvas_url = str(
        st.session_state.get(
            "canvas_url_input",
            ""
        )
        or ""
    ).strip()

    api_token = str(
        st.session_state.get(
            "canvas_api_token_input",
            ""
        )
        or ""
    ).strip()

    connected_canvas_url = (
        st.session_state.get(
            "connected_canvas_url"
        )
    )

    if not connected:

        return (
            None,
            (
                "Connect to Canvas using the sidebar before "
                "verifying the selected course."
            )
        )

    if not canvas_url:

        return (
            None,
            (
                "The Canvas URL is missing. Enter it in the "
                "sidebar and test the connection again."
            )
        )

    if not api_token:

        return (
            None,
            (
                "The Canvas API token is missing. Enter it in "
                "the sidebar and test the connection again."
            )
        )

    normalized_canvas_url = (
        canvas_url.rstrip("/")
    )

    if (
        connected_canvas_url
        and normalized_canvas_url
        != connected_canvas_url
    ):

        return (
            None,
            (
                "The Canvas URL has changed since the last "
                "successful connection test. Test the "
                "connection again before continuing."
            )
        )

    return (
        CanvasAPI(
            canvas_url=normalized_canvas_url,
            api_token=api_token
        ),
        None
    )


# ============================================================
# COURSE VERIFICATION UI
# ============================================================


def render_course_verification_gate(
    target_id
):
    """
    Render the shared Single Course verification gate.

    Returns:
        True when the currently entered Course ID has passed
        verification.

        False when controls must remain locked.
    """

    st.markdown(
        "### Course Verification"
    )

    st.caption(
        "The selected course must be verified before "
        "administration tools can be used."
    )

    if not target_id:

        st.info(
            "Enter a Course ID in the sidebar to continue."
        )

        return False

    verified_course_id = str(
        st.session_state.get(
            "authorization_verified_course_id"
        )
        or ""
    ).strip()

    verification_is_current = (
        st.session_state.get(
            "authorization_passed",
            False
        )
        and verified_course_id == target_id
    )


    # ========================================================
    # CURRENT VERIFIED STATE
    # ========================================================

    if verification_is_current:

        result = (
            st.session_state.get(
                "authorization_result"
            )
            or {}
        )

        course = (
            result.get("course")
            or {}
        )

        course_name = (
            course.get("name")
            or f"Course {target_id}"
        )

        st.success(
            "Accelerate Education course verified."
        )

        st.caption(
            f"Verified course: {course_name} "
            f"(Canvas Course ID: {target_id})"
        )

        return True


    # ========================================================
    # VERIFY BUTTON
    # ========================================================

    verify_button = st.button(
        "Verify Course",
        type="primary",
        use_container_width=True,
        key="verify_accelerate_course"
    )

    if verify_button:

        reset_course_authorization()

        clear_target_workspace_state()

        canvas, connection_error = (
            get_authorization_canvas_connection()
        )

        if connection_error:

            st.error(
                connection_error
            )

            return False

        with st.spinner(
            "Verifying course eligibility..."
        ):

            result = verify_accelerate_course(
                canvas=canvas,
                course_id=target_id
            )

        st.session_state.authorization_result = (
            result
        )

        if (
            result.get("success")
            and result.get("verified")
        ):

            st.session_state.authorization_passed = True

            st.session_state.authorization_verified_course_id = (
                target_id
            )

            st.rerun()

        reset_course_authorization()

        # Preserve the failure result after reset so it can be
        # displayed during this run and subsequent reruns.
        st.session_state.authorization_result = (
            result
        )


    # ========================================================
    # DISPLAY FAILED / ERROR RESULT
    # ========================================================

    result = (
        st.session_state.get(
            "authorization_result"
        )
    )

    if result:

        st.error(
            result.get(
                "message",
                (
                    "The selected course could not be "
                    "verified. Please enter another Course ID "
                    "or contact Accelerate Education Support."
                )
            )
        )

    else:

        st.info(
            "Verify the selected course to unlock the "
            "administration controls."
        )

    return False


# ============================================================
# REPORTS WORKSPACE
# ============================================================


def render_reports_workspace():
    """
    Render the current Reports placeholder.
    """

    st.markdown(
        "## 📊 Reports"
    )

    st.write(
        "Review administration activity and export "
        "change reports."
    )

    st.markdown("---")

    st.info(
        "Reports workspace is ready for configuration."
    )

    st.markdown(
        "### Planned Tools"
    )

    st.markdown(
        """
        - Preview reports
        - Completed operation summaries
        - Success and failure results
        - Downloadable CSV reports
        """
    )


# ============================================================
# SETTINGS WORKSPACE
# ============================================================


def render_settings_workspace():
    """
    Render the current Settings placeholder.
    """

    st.markdown(
        "## ⚙️ Settings"
    )

    st.write(
        "Manage application preferences and administrative "
        "configuration."
    )

    st.markdown("---")

    st.info(
        "Settings workspace is ready for configuration."
    )


# ============================================================
# WORKSPACE CONTROLLER
# ============================================================


def render_workspace(
    module_name
):
    """
    Display the workspace for the administration module
    selected from the main dashboard.
    """

    initialize_authorization_state()


    # ========================================================
    # BACK TO DASHBOARD
    # ========================================================

    if st.button(
        "← Back to Dashboard",
        key="back_to_dashboard"
    ):

        st.session_state.active_module = None

        st.rerun()

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    # ========================================================
    # REPORTS
    #
    # Reports does not target one Canvas course, so no course
    # verification gate is required.
    # ========================================================

    if module_name == "reports":

        render_reports_workspace()

        return


    # ========================================================
    # SETTINGS
    #
    # Settings does not target one Canvas course, so no course
    # verification gate is required.
    # ========================================================

    if module_name == "settings":

        render_settings_workspace()

        return


    # ========================================================
    # SUPPORTED MANAGEMENT WORKSPACES
    # ========================================================

    supported_management_modules = {
        "course",
        "assignments",
        "quizzes",
    }

    if (
        module_name
        not in supported_management_modules
    ):

        st.warning(
            "The selected administration module could not "
            "be loaded."
        )

        return


    # ========================================================
    # CURRENT SCOPE AND TARGET
    # ========================================================

    scope = st.session_state.get(
        "canvas_scope",
        "Single Course"
    )

    target_id = st.session_state.get(
        "canvas_target_id",
        ""
    )


    # ========================================================
    # SINGLE COURSE VERIFICATION
    # ========================================================

    if scope == "Single Course":

        normalized_target_id = (
            sync_authorization_target(
                target_id
            )
        )

        verified = (
            render_course_verification_gate(
                normalized_target_id
            )
        )

        if not verified:

            return


    # ========================================================
    # SUB-ACCOUNT SCOPE
    #
    # Course-by-course authorization for Sub-Account jobs will
    # be implemented with the planned background-job engine.
    # Existing Sub-Account functionality is left unchanged for
    # now.
    # ========================================================

    else:

        reset_course_authorization()


    # ========================================================
    # ROUTE VERIFIED / ALLOWED WORKSPACE
    # ========================================================

    if module_name == "course":

        render_course_workspace()

    elif module_name == "assignments":

        render_assignment_workspace()

    elif module_name == "quizzes":

        render_quiz_workspace()
