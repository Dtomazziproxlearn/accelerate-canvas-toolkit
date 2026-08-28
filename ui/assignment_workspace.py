import streamlit as st

from canvas import CanvasAPI

from tools.assignments import (
    build_single_course_assignment_preview,
    execute_single_course_assignment_changes
)


# ============================================================
# ACCELERATE CANVAS ADMINISTRATION SUITE
# Assignment Management Workspace
#
# CURRENT VERSION:
# - Single Course mode
# - True Canvas assignments only
# - Assignment Attempt Limit
# - Read-only Preview
# - Explicit confirmation before execution
# - Controlled execution results
#
# Quizzes, exams, discussions, and unsupported assignment-like
# Canvas objects are intentionally invisible to this workspace.
#
# Sub-Account mode will be added after the course-level
# Assignment Management engine has been fully validated.
# ============================================================


# ============================================================
# SESSION STATE HELPERS
# ============================================================


def initialize_assignment_workspace_state():
    """
    Initialize Assignment Management session-state values.
    """

    if "assignment_preview" not in st.session_state:
        st.session_state.assignment_preview = None

    if "assignment_preview_signature" not in st.session_state:
        st.session_state.assignment_preview_signature = None

    if "assignment_execution_results" not in st.session_state:
        st.session_state.assignment_execution_results = None

    if "assignment_confirm_apply" not in st.session_state:
        st.session_state.assignment_confirm_apply = False


def clear_assignment_preview():
    """
    Clear previously generated Preview and execution data.

    This helper is only called before the confirmation checkbox
    is instantiated during the current Streamlit run.
    """

    st.session_state.assignment_preview = None
    st.session_state.assignment_preview_signature = None
    st.session_state.assignment_execution_results = None
    st.session_state.assignment_confirm_apply = False


# ============================================================
# CONNECTION HELPERS
# ============================================================


def get_assignment_canvas_connection():
    """
    Build a CanvasAPI instance from the connection information
    already collected by the application sidebar.

    Returns:
        tuple:
            canvas
            error_message
    """

    canvas_url = st.session_state.get(
        "canvas_url_input",
        ""
    )

    api_token = st.session_state.get(
        "canvas_api_token_input",
        ""
    )

    connected = st.session_state.get(
        "canvas_connected",
        False
    )

    connected_canvas_url = st.session_state.get(
        "connected_canvas_url"
    )

    # --------------------------------------------------------
    # REQUIRE SUCCESSFUL CONNECTION
    # --------------------------------------------------------

    if not connected:

        return (
            None,
            (
                "Connect to Canvas using the sidebar before "
                "generating a Preview."
            )
        )

    # --------------------------------------------------------
    # REQUIRE URL
    # --------------------------------------------------------

    if not canvas_url.strip():

        return (
            None,
            (
                "The Canvas URL is missing. "
                "Enter the Canvas URL in the sidebar."
            )
        )

    # --------------------------------------------------------
    # REQUIRE TOKEN
    # --------------------------------------------------------

    if not api_token.strip():

        return (
            None,
            (
                "The Canvas API token is missing. "
                "Enter the API token in the sidebar."
            )
        )

    # --------------------------------------------------------
    # VERIFY CURRENT URL MATCHES TESTED CONNECTION
    # --------------------------------------------------------

    normalized_canvas_url = (
        canvas_url.strip().rstrip("/")
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
                "successful connection test. "
                "Test the connection again before continuing."
            )
        )

    # --------------------------------------------------------
    # BUILD CANVAS API SERVICE
    # --------------------------------------------------------

    canvas = CanvasAPI(
        canvas_url=normalized_canvas_url,
        api_token=api_token.strip()
    )

    return (
        canvas,
        None
    )


# ============================================================
# PREVIEW SIGNATURE
# ============================================================


def build_assignment_preview_signature(
    scope,
    target_id,
    attempt_limit
):
    """
    Create a signature representing the settings used to
    generate the current Preview.

    If the administrator changes the target or requested
    setting after Preview generation, Apply is blocked until
    a new Preview is generated.
    """

    return (
        str(scope),
        str(target_id).strip(),
        str(attempt_limit)
    )


# ============================================================
# PREVIEW DISPLAY
# ============================================================


def display_assignment_preview(preview):
    """
    Display the read-only Assignment Management Preview.

    Only true Canvas assignments managed by this engine are
    displayed.

    Quizzes, exams, discussions, and unsupported Canvas
    objects are intentionally omitted.
    """

    if not preview:

        return

    # ========================================================
    # COURSE INFORMATION
    # ========================================================

    course = preview.get(
        "course"
    ) or {}

    counts = preview.get(
        "counts"
    ) or {}

    st.markdown("---")

    st.markdown(
        "### Preview Results"
    )

    course_name = (
        course.get("name")
        or "Unnamed Course"
    )

    course_id = course.get(
        "id"
    )

    course_code = course.get(
        "course_code"
    )

    st.markdown(
        f"## {course_name}"
    )

    st.caption(
        f"Canvas Course ID: {course_id}"
    )

    if course_code:

        st.caption(
            f"Course Code: {course_code}"
        )


    # ========================================================
    # PREVIEW SUMMARY
    #
    # "Assignments Found" means true assignments managed by
    # this engine. Raw Canvas API objects such as quizzes and
    # discussions are intentionally not represented.
    # ========================================================

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.metric(
            "Assignments Found",
            counts.get(
                "total_found",
                0
            )
        )

    with col2:

        st.metric(
            "Would Change",
            counts.get(
                "would_change",
                0
            )
        )

    with col3:

        st.metric(
            "Already Set",
            counts.get(
                "already_set",
                0
            )
        )


    # ========================================================
    # ASSIGNMENTS
    # ========================================================

    assignments = preview.get(
        "assignments"
    ) or []

    if not assignments:

        st.info(
            "No assignments managed by this tool were found "
            "in the selected course."
        )

        return


    # ========================================================
    # CHANGE SUMMARY
    # ========================================================

    would_change = counts.get(
        "would_change",
        0
    )

    already_set = counts.get(
        "already_set",
        0
    )

    if would_change > 0:

        st.info(
            f"{would_change} assignment(s) would be updated "
            "if these changes are applied."
        )

    elif already_set > 0:

        st.success(
            "All assignments already match the requested "
            "Attempt Limit."
        )


    # ========================================================
    # PROPOSED CHANGES
    # ========================================================

    st.markdown(
        "### Proposed Changes"
    )

    st.caption(
        "Each assignment below shows its current Canvas "
        "setting and the requested setting."
    )

    for assignment in assignments:

        assignment_name = (
            assignment.get("name")
            or "Untitled Assignment"
        )

        assignment_id = assignment.get(
            "id"
        )

        assignment_status = (
            assignment.get("status")
            or ""
        )

        if assignment_status == "Would Change":

            status_icon = "🟡"

        elif assignment_status == "Already Set":

            status_icon = "🟢"

        else:

            status_icon = "⚪"

        expander_label = (
            f"{status_icon} {assignment_name}"
        )

        with st.expander(
            expander_label,
            expanded=False
        ):

            st.caption(
                f"Canvas Assignment ID: {assignment_id}"
            )

            changes = assignment.get(
                "changes"
            ) or []

            if not changes:

                st.info(
                    "No assignment setting changes were requested."
                )

                continue

            table_rows = []

            for change in changes:

                table_rows.append(
                    {
                        "Setting":
                            change.get(
                                "setting",
                                ""
                            ),

                        "Current":
                            change.get(
                                "current",
                                ""
                            ),

                        "Requested":
                            change.get(
                                "requested",
                                ""
                            ),

                        "Status":
                            change.get(
                                "status",
                                ""
                            )
                    }
                )

            st.dataframe(
                table_rows,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# EXECUTION RESULTS DISPLAY
# ============================================================


def display_assignment_execution_results(
    execution_result
):
    """
    Display Assignment Management execution results.

    Only assignments actually managed by this engine are
    represented.
    """

    if not execution_result:

        return

    st.markdown("---")

    st.markdown(
        "### Execution Results"
    )

    counts = execution_result.get(
        "counts"
    ) or {}

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(
            "Targeted",
            counts.get(
                "eligible",
                0
            )
        )

    with col2:

        st.metric(
            "Updated",
            counts.get(
                "updated",
                0
            )
        )

    with col3:

        st.metric(
            "Skipped",
            counts.get(
                "skipped",
                0
            )
        )

    with col4:

        st.metric(
            "Failed",
            counts.get(
                "failed",
                0
            )
        )

    failed_count = counts.get(
        "failed",
        0
    )

    updated_count = counts.get(
        "updated",
        0
    )

    if failed_count == 0:

        if updated_count > 0:

            st.success(
                "Canvas processing completed successfully."
            )

        else:

            st.info(
                "Processing completed. No assignment updates "
                "were required."
            )

    else:

        st.warning(
            execution_result.get(
                "message",
                (
                    "Assignment processing completed with "
                    "one or more failures."
                )
            )
        )

    results = execution_result.get(
        "results"
    ) or []

    if not results:

        return


    # ========================================================
    # EXECUTION RESULTS TABLE
    # ========================================================

    table_rows = []

    for item in results:

        updated_fields = (
            item.get(
                "updated_fields"
            )
            or []
        )

        readable_fields = []

        for field in updated_fields:

            if field == "allowed_attempts":

                readable_fields.append(
                    "Attempt Limit"
                )

            else:

                readable_fields.append(
                    field
                )

        table_rows.append(
            {
                "Assignment":
                    (
                        item.get("name")
                        or "Untitled Assignment"
                    ),

                "Status":
                    item.get(
                        "status",
                        ""
                    ),

                "Updated Fields":
                    (
                        ", ".join(
                            readable_fields
                        )
                        if readable_fields
                        else "—"
                    ),

                "Message":
                    item.get(
                        "message",
                        ""
                    )
            }
        )

    st.dataframe(
        table_rows,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# MAIN ASSIGNMENT WORKSPACE
# ============================================================


def render_assignment_workspace():
    """
    Render the Assignment Management workspace.
    """

    initialize_assignment_workspace_state()


    # ========================================================
    # WORKSPACE HEADER
    # ========================================================

    st.markdown(
        "## 📝 Assignment Management"
    )

    st.write(
        "Configure assignment attempt limits across "
        "Canvas courses."
    )

    st.markdown("---")


    # ========================================================
    # CURRENT TARGET
    # ========================================================

    scope = st.session_state.get(
        "canvas_scope",
        "Single Course"
    )

    target_id = st.session_state.get(
        "canvas_target_id",
        ""
    )

    st.markdown(
        "### Current Target"
    )

    target_col1, target_col2 = (
        st.columns(2)
    )

    with target_col1:

        st.caption(
            "SCOPE"
        )

        st.write(
            scope
        )

    with target_col2:

        if scope == "Single Course":

            st.caption(
                "COURSE ID"
            )

        else:

            st.caption(
                "SUB-ACCOUNT ID"
            )

        st.write(
            target_id
            if target_id
            else "Not entered"
        )


    # ========================================================
    # SUB-ACCOUNT MODE
    # ========================================================

    if scope != "Single Course":

        st.info(
            "Sub-Account Assignment Management is not enabled "
            "yet. Select Single Course in the sidebar to use "
            "the current Assignment Management tools."
        )

        return


    # ========================================================
    # 1. ASSIGNMENT SETTINGS
    # ========================================================

    st.markdown("---")

    st.markdown(
        "### 1. Assignment Settings"
    )

    st.caption(
        "Choose the assignment setting you want to apply. "
        "No Canvas changes occur until Preview has been "
        "generated, reviewed, and explicitly confirmed."
    )

    attempt_limit_options = [
        "Don't Change",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "Unlimited"
    ]

    attempt_limit = st.selectbox(
        "Attempt Limit",
        options=attempt_limit_options,
        index=0,
        key="assignment_attempt_limit",
        help=(
            "Choose the maximum number of submission attempts "
            "allowed for assignments. Select Unlimited to "
            "remove a numeric attempt limit."
        )
    )


    # ========================================================
    # 2. PREVIEW CHANGES
    # ========================================================

    st.markdown("---")

    st.markdown(
        "### 2. Preview Changes"
    )

    st.write(
        "Preview the assignments that would be affected before "
        "anything is written to Canvas."
    )

    preview_button = st.button(
        "Generate Preview",
        type="primary",
        use_container_width=True,
        key="assignment_generate_preview"
    )


    # ========================================================
    # GENERATE PREVIEW
    # ========================================================

    if preview_button:

        # ----------------------------------------------------
        # SAFE RESET
        #
        # At this point in the Streamlit run, the confirmation
        # checkbox has NOT yet been instantiated, so its state
        # may safely be reset.
        # ----------------------------------------------------

        st.session_state.assignment_execution_results = None
        st.session_state.assignment_confirm_apply = False


        # ----------------------------------------------------
        # VALIDATE TARGET
        # ----------------------------------------------------

        if not str(
            target_id
        ).strip():

            clear_assignment_preview()

            st.error(
                "Enter a Course ID in the sidebar before "
                "generating a Preview."
            )


        # ----------------------------------------------------
        # REQUIRE REQUESTED CHANGE
        # ----------------------------------------------------

        elif attempt_limit == "Don't Change":

            clear_assignment_preview()

            st.warning(
                "Select an Attempt Limit before generating "
                "a Preview."
            )


        # ----------------------------------------------------
        # VALIDATE CONNECTION
        # ----------------------------------------------------

        else:

            canvas, connection_error = (
                get_assignment_canvas_connection()
            )

            if connection_error:

                clear_assignment_preview()

                st.error(
                    connection_error
                )

            else:

                settings = {
                    "attempt_limit":
                        attempt_limit
                }

                with st.spinner(
                    "Loading assignments and building Preview..."
                ):

                    preview = (
                        build_single_course_assignment_preview(
                            canvas=canvas,
                            course_id=str(
                                target_id
                            ).strip(),
                            settings=settings
                        )
                    )

                if not preview[
                    "success"
                ]:

                    clear_assignment_preview()

                    st.error(
                        preview[
                            "message"
                        ]
                    )

                else:

                    st.session_state.assignment_preview = (
                        preview
                    )

                    st.session_state.assignment_preview_signature = (
                        build_assignment_preview_signature(
                            scope=scope,
                            target_id=target_id,
                            attempt_limit=attempt_limit
                        )
                    )


    # ========================================================
    # DISPLAY STORED PREVIEW
    # ========================================================

    preview = st.session_state.get(
        "assignment_preview"
    )

    if preview:

        display_assignment_preview(
            preview
        )


        # ====================================================
        # PREVIEW SIGNATURE VALIDATION
        # ====================================================

        current_signature = (
            build_assignment_preview_signature(
                scope=scope,
                target_id=target_id,
                attempt_limit=attempt_limit
            )
        )

        preview_signature = (
            st.session_state.get(
                "assignment_preview_signature"
            )
        )

        preview_is_current = (
            current_signature
            == preview_signature
        )

        if not preview_is_current:

            st.warning(
                "The target or Attempt Limit has changed since "
                "this Preview was generated. Generate a new "
                "Preview before applying changes."
            )


        # ====================================================
        # 3. APPLY CHANGES
        # ====================================================

        counts = preview.get(
            "counts"
        ) or {}

        would_change_count = counts.get(
            "would_change",
            0
        )

        st.markdown("---")

        st.markdown(
            "### 3. Apply Changes"
        )

        if would_change_count == 0:

            st.info(
                "No assignment changes need to be applied."
            )

        else:

            st.warning(
                (
                    f"This operation will update "
                    f"{would_change_count} assignment(s) "
                    "in Canvas."
                )
            )

            confirm_apply = st.checkbox(
                (
                    "I have reviewed the Preview and confirm "
                    "that I want to apply these assignment "
                    "changes to Canvas."
                ),
                key="assignment_confirm_apply"
            )

            apply_disabled = (
                not confirm_apply
                or not preview_is_current
            )

            apply_button = st.button(
                "Apply Changes",
                type="primary",
                use_container_width=True,
                disabled=apply_disabled,
                key="assignment_apply_changes"
            )


            # ================================================
            # EXECUTE CHANGES
            # ================================================

            if apply_button:

                canvas, connection_error = (
                    get_assignment_canvas_connection()
                )

                if connection_error:

                    st.error(
                        connection_error
                    )

                else:

                    settings = {
                        "attempt_limit":
                            attempt_limit
                    }

                    with st.spinner(
                        "Applying assignment changes to Canvas..."
                    ):

                        execution_result = (
                            execute_single_course_assignment_changes(
                                canvas=canvas,
                                course_id=str(
                                    target_id
                                ).strip(),
                                settings=settings
                            )
                        )

                    # ----------------------------------------
                    # STORE EXECUTION RESULTS
                    # ----------------------------------------

                    st.session_state.assignment_execution_results = (
                        execution_result
                    )

                    # ----------------------------------------
                    # CLEAR STALE PREVIEW
                    #
                    # Canvas may now contain updated values.
                    #
                    # IMPORTANT:
                    # Do NOT modify assignment_confirm_apply
                    # here. Its checkbox widget has already
                    # been instantiated during this Streamlit
                    # run. Modifying that widget's session
                    # state here causes StreamlitAPIException.
                    #
                    # Clearing the Preview removes the entire
                    # confirmation/apply section on rerun.
                    # ----------------------------------------

                    st.session_state.assignment_preview = None

                    st.session_state.assignment_preview_signature = None

                    # ----------------------------------------
                    # RERUN
                    #
                    # On the next run, the stale Preview and
                    # Apply controls will no longer render.
                    # ----------------------------------------

                    st.rerun()


    # ========================================================
    # EXECUTION RESULTS
    # ========================================================

    execution_result = st.session_state.get(
        "assignment_execution_results"
    )

    if execution_result:

        display_assignment_execution_results(
            execution_result
        )

        st.info(
            "The previous Preview has been cleared because "
            "Canvas may now contain updated values. Generate "
            "a new Preview before applying another change."
        )