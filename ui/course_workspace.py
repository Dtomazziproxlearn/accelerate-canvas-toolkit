import streamlit as st

from canvas import CanvasAPI

from tools.courses import (
    build_single_course_module_gating_preview,
    execute_single_course_module_gating,
    build_single_course_soft_zero_preview,
    execute_single_course_soft_zero
)


# ============================================================
# ACCELERATE CANVAS ADMINISTRATION SUITE
# Course Management Workspace
#
# CURRENT VERSION:
# - Version 0.2 Alpha UI foundation
# - Single Course mode
# - Module Gating v2
# - Don't Change / Enable / Disable
# - Read-only Preview
# - Explicit confirmation before execution
# - Controlled execution results
#
# PLANNED COURSE MANAGEMENT TOOLS:
# - Soft Zero
# - Due Dates
# - Sub-Account processing
# ============================================================


# ============================================================
# SESSION STATE
# ============================================================


def initialize_course_workspace_state():
    """
    Initialize Course Management session-state values.
    """

    if "course_preview" not in st.session_state:
        st.session_state.course_preview = None

    if "course_preview_signature" not in st.session_state:
        st.session_state.course_preview_signature = None

    if "course_execution_results" not in st.session_state:
        st.session_state.course_execution_results = None

    if "course_confirm_apply" not in st.session_state:
        st.session_state.course_confirm_apply = False


def clear_course_preview():
    """
    Clear stored Course Management Preview and execution data.

    This helper should only be called before the confirmation
    checkbox has been instantiated during the current
    Streamlit run.
    """

    st.session_state.course_preview = None

    st.session_state.course_preview_signature = None

    st.session_state.course_execution_results = None

    st.session_state.course_confirm_apply = False


# ============================================================
# CANVAS CONNECTION
# ============================================================


def get_course_canvas_connection():
    """
    Build a CanvasAPI instance using the connection information
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
    # REQUIRE CANVAS URL
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
    # REQUIRE API TOKEN
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


def build_course_preview_signature(
    scope,
    target_id,
    module_gating,
    soft_zero,
    missing_grade
):
    """Create a signature for the complete Course Management Preview."""

    normalized_grade = (
        float(missing_grade)
        if soft_zero == "Enable"
        else None
    )

    return (
        str(scope),
        str(target_id).strip(),
        str(module_gating),
        str(soft_zero),
        normalized_grade
    )


# ============================================================
# PREVIEW DISPLAY
# ============================================================


def display_course_preview(
    preview
):
    """
    Display a compact read-only Module Gating Preview.

    The UI intentionally summarizes module-item changes rather
    than displaying every page, assignment, quiz, discussion,
    file, or external tool individually.
    """

    if not preview:

        return


    # ========================================================
    # COURSE INFORMATION
    # ========================================================

    course = (
        preview.get("course")
        or {}
    )

    counts = (
        preview.get("counts")
        or {}
    )

    modules = (
        preview.get("modules")
        or []
    )

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
    # SUMMARY METRICS
    # ========================================================

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.metric(
            "Modules Found",
            counts.get(
                "modules_found",
                0
            )
        )

    with col2:

        st.metric(
            "Modules to Configure",
            counts.get(
                "modules_would_change",
                0
            )
        )

    with col3:

        st.metric(
            "Module Items Found",
            counts.get(
                "module_items_found",
                0
            )
        )


    # ========================================================
    # CURRENT / REQUESTED CONFIGURATION
    # ========================================================

    st.markdown(
        "### Module Gating"
    )

    current_configuration = (
        preview.get(
            "current_configuration"
        )
        or "Unknown"
    )

    requested_setting = (
        preview.get(
            "setting"
        )
        or "Don't Change"
    )

    setting_col1, setting_col2 = (
        st.columns(2)
    )

    with setting_col1:

        st.caption(
            "CURRENT CONFIGURATION"
        )

        st.write(
            current_configuration
        )

    with setting_col2:

        st.caption(
            "REQUESTED"
        )

        st.write(
            requested_setting
        )


    # ========================================================
    # PROPOSED GATING BEHAVIOR
    # ========================================================

    if requested_setting == "Enable":

        st.info(
            "Enabling Module Gating will configure sequential "
            "module progress, chain modules using prerequisites, "
            "and apply completion requirements to supported "
            "module items."
        )

        st.markdown(
            """
            **What will be applied:**

            - Sequential progress enabled for each module
            - Modules chained in Canvas course order
            - Pages, files, external URLs, and external tools → Must View
            - Assignments and quizzes → Must Submit
            - Discussions → Must Contribute
            """
        )


    elif requested_setting == "Disable":

        st.warning(
            "Disabling Module Gating will remove all module "
            "prerequisites and all module-item completion "
            "requirements from the selected course."
        )

        st.markdown(
            """
            **What will be removed:**

            - Sequential module progress
            - Every module prerequisite
            - Every module-item completion requirement
            """
        )


    # ========================================================
    # MODULE ITEM SUMMARY
    # ========================================================

    supported_items = counts.get(
        "supported_module_items",
        0
    )

    unsupported_items = counts.get(
        "unsupported_module_items",
        0
    )

    item_changes = counts.get(
        "item_requirements_would_change",
        0
    )

    item_already_set = counts.get(
        "item_requirements_already_set",
        0
    )

    summary_col1, summary_col2 = (
        st.columns(2)
    )

    with summary_col1:

        st.caption(
            "SUPPORTED MODULE ITEMS"
        )

        st.write(
            supported_items
        )

        st.caption(
            f"{item_changes} would change • "
            f"{item_already_set} already configured"
        )

    with summary_col2:

        if requested_setting == "Disable":

            st.caption(
                "ITEMS ALREADY WITHOUT REQUIREMENTS"
            )

            st.write(
                item_already_set
            )

            st.caption(
                "These items do not require any change."
            )

        else:

            st.caption(
                "UNSUPPORTED / IGNORED ITEMS"
            )

            st.write(
                unsupported_items
            )

            st.caption(
                "These items are not modified when enabling "
                "Module Gating."
            )


    # ========================================================
    # MODULE ITEM LOAD WARNINGS
    # ========================================================

    load_failures = counts.get(
        "module_item_load_failures",
        0
    )

    if load_failures > 0:

        st.warning(
            f"Canvas module items could not be loaded for "
            f"{load_failures} module(s). Do not apply changes "
            "until these Preview errors are reviewed."
        )


    # ========================================================
    # MODULE CHAIN
    # ========================================================

    if modules:

        with st.expander(
            (
                "View Module Chain"
                if requested_setting == "Enable"
                else "View Modules and Current Prerequisites"
            ),
            expanded=False
        ):

            for index, module in enumerate(
                modules,
                start=1
            ):

                module_name = (
                    module.get("name")
                    or "Unnamed Module"
                )

                prerequisite_name = (
                    module.get(
                        "expected_prerequisite_name"
                    )
                )

                published = module.get(
                    "published"
                )

                if published is False:

                    publication_label = (
                        " — Unpublished"
                    )

                else:

                    publication_label = ""

                if requested_setting == "Disable":

                    current_prerequisites = (
                        module.get(
                            "current_prerequisite_ids"
                        )
                        or []
                    )

                    if current_prerequisites:

                        current_label = ", ".join(
                            str(prerequisite_id)
                            for prerequisite_id
                            in current_prerequisites
                        )

                    else:

                        current_label = "None"

                    st.write(
                        f"**{index}. {module_name}**"
                        f"{publication_label}  \n"
                        f"Current prerequisite IDs: "
                        f"{current_label}  \n"
                        "After change: None"
                    )

                elif prerequisite_name:

                    st.write(
                        f"**{index}. {module_name}**"
                        f"{publication_label}  \n"
                        f"Requires: {prerequisite_name}"
                    )

                else:

                    st.write(
                        f"**{index}. {module_name}**"
                        f"{publication_label}  \n"
                        "Requires: None"
                    )


    # ========================================================
    # PREVIEW STATUS
    # ========================================================

    modules_found = counts.get(
        "modules_found",
        0
    )

    modules_would_change = counts.get(
        "modules_would_change",
        0
    )

    if modules_found == 0:

        st.info(
            "No modules were found in the selected course."
        )

    elif (
        modules_would_change == 0
        and load_failures == 0
    ):

        if requested_setting == "Enable":

            st.success(
                "Module Gating is already fully enabled "
                "according to the requested settings."
            )

        else:

            st.success(
                "Module Gating is already fully disabled. "
                "No prerequisites or completion requirements "
                "remain."
            )

    elif load_failures == 0:

        if requested_setting == "Enable":

            st.info(
                f"{modules_would_change} module(s) require "
                "configuration to fully enable Module Gating."
            )

        else:

            st.warning(
                f"{modules_would_change} module(s) contain "
                "gating settings or requirements that will "
                "be removed."
            )


# ============================================================
# EXECUTION RESULTS DISPLAY
# ============================================================


def display_course_execution_results(
    execution_result
):
    """
    Display Module Gating execution results.

    Results remain compact while still exposing failures.
    """

    if not execution_result:

        return

    st.markdown("---")

    st.markdown(
        "### Execution Results"
    )

    counts = (
        execution_result.get(
            "counts"
        )
        or {}
    )


    # ========================================================
    # MODULE RESULTS
    # ========================================================

    st.markdown(
        "#### Modules"
    )

    module_col1, module_col2, module_col3 = (
        st.columns(3)
    )

    with module_col1:

        st.metric(
            "Modules Found",
            counts.get(
                "modules_found",
                0
            )
        )

    with module_col2:

        st.metric(
            "Modules Updated",
            counts.get(
                "modules_updated",
                0
            )
        )

    with module_col3:

        st.metric(
            "Module Failures",
            counts.get(
                "modules_failed",
                0
            )
        )


    # ========================================================
    # MODULE ITEM RESULTS
    # ========================================================

    st.markdown(
        "#### Module Items"
    )

    item_col1, item_col2, item_col3, item_col4 = (
        st.columns(4)
    )

    with item_col1:

        st.metric(
            "Items Found",
            counts.get(
                "items_found",
                0
            )
        )

    with item_col2:

        st.metric(
            "Items Updated",
            counts.get(
                "items_updated",
                0
            )
        )

    with item_col3:

        st.metric(
            "Items Skipped",
            counts.get(
                "items_skipped",
                0
            )
        )

    with item_col4:

        st.metric(
            "Item Failures",
            counts.get(
                "items_failed",
                0
            )
        )


    # ========================================================
    # OVERALL STATUS
    # ========================================================

    if execution_result.get(
        "success"
    ):

        st.success(
            execution_result.get(
                "message",
                "Module Gating completed successfully."
            )
        )

    else:

        st.warning(
            execution_result.get(
                "message",
                (
                    "Module Gating completed with "
                    "one or more failures."
                )
            )
        )


    # ========================================================
    # MODULE FAILURES
    # ========================================================

    module_results = (
        execution_result.get(
            "module_results"
        )
        or []
    )

    failed_modules = [
        result
        for result in module_results
        if result.get("status") == "Failed"
    ]

    if failed_modules:

        with st.expander(
            "View Module Failures",
            expanded=True
        ):

            module_failure_rows = []

            for result in failed_modules:

                module_failure_rows.append(
                    {
                        "Module":
                            result.get(
                                "name",
                                ""
                            ),

                        "Message":
                            result.get(
                                "message",
                                ""
                            )
                    }
                )

            st.dataframe(
                module_failure_rows,
                use_container_width=True,
                hide_index=True
            )


    # ========================================================
    # MODULE ITEM FAILURES
    # ========================================================

    item_results = (
        execution_result.get(
            "item_results"
        )
        or []
    )

    failed_items = [
        result
        for result in item_results
        if result.get("status") == "Failed"
    ]

    if failed_items:

        with st.expander(
            "View Module Item Failures",
            expanded=True
        ):

            item_failure_rows = []

            for result in failed_items:

                item_failure_rows.append(
                    {
                        "Module":
                            result.get(
                                "module_name",
                                ""
                            ),

                        "Item":
                            result.get(
                                "item_name",
                                ""
                            ),

                        "Type":
                            result.get(
                                "item_type",
                                ""
                            ),

                        "Message":
                            result.get(
                                "message",
                                ""
                            )
                    }
                )

            st.dataframe(
                item_failure_rows,
                use_container_width=True,
                hide_index=True
            )



# ============================================================
# COURSE MANAGEMENT UI HELPERS
# ============================================================


def render_course_feature_header(
    icon,
    number,
    title,
    description
):
    """
    Render a prominent Course Management feature heading.

    This helper creates a consistent visual structure for
    Course Gating, Soft Zero, Due Dates, Preview, and Apply.
    """

    st.markdown(
        f"""
        <div style="
            background-color: #0B2D4D;
            border-radius: 10px;
            padding: 16px 18px;
            margin-top: 22px;
            margin-bottom: 12px;
        ">
            <div style="
                color: white;
                font-size: 1.22rem;
                font-weight: 700;
                margin-bottom: 4px;
            ">
                {icon} {number}. {title}
            </div>
            <div style="
                color: #DDE8F2;
                font-size: 0.95rem;
                line-height: 1.45;
            ">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_current_course_target(
    scope,
    target_id
):
    """
    Display the currently selected Canvas scope and target.
    """

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


def render_course_choice_styles():
    """
    Style horizontal radio controls as large selectable action cards.

    The controls remain native Streamlit radio buttons for keyboard
    navigation and session-state behavior, while the visible radio
    circles are hidden so the entire card becomes the selection target.
    """

    st.markdown(
        """
        <style>
        /* Full-width, three-column action-card layout. */
        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            width: 100%;
            align-items: stretch;
        }

        /* Base card styling. */
        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label {
            position: relative;
            width: 100%;
            min-height: 104px;
            margin: 0;
            padding: 1.15rem 1.25rem;
            border: 1.5px solid #CAD3DE;
            border-radius: 12px;
            background: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            cursor: pointer;
            transition:
                border-color 0.16s ease,
                background-color 0.16s ease,
                box-shadow 0.16s ease,
                transform 0.16s ease;
        }

        /* Hide only the visual radio circle; the native input remains. */
        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label input {
            position: absolute;
            opacity: 0;
            pointer-events: none;
        }

        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(11, 45, 77, 0.08);
        }

        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label p {
            margin: 0;
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.35;
            text-align: center;
        }

        /* Large action icon above each label. */
        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label::before {
            display: block;
            margin-right: 0.55rem;
            font-size: 1.35rem;
            line-height: 1;
            font-weight: 700;
        }

        /* Enable card. */
        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-child(1) {
            border-color: #86D7AA;
            color: #137A45;
        }

        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-child(1)::before {
            content: "✓";
        }

        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-child(1):has(input:checked) {
            border: 2px solid #1F9D59;
            background: #EAF8F0;
            box-shadow: 0 0 0 2px rgba(31, 157, 89, 0.10);
        }

        /* Don't Change card. */
        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-child(2) {
            border-color: #AFC1D2;
            color: #0B2D4D;
        }

        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-child(2)::before {
            content: "Ⅱ";
        }

        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-child(2):has(input:checked) {
            border: 2px solid #0B2D4D;
            background: #EAF1F7;
            box-shadow: 0 0 0 2px rgba(11, 45, 77, 0.10);
        }

        /* Disable card. */
        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-child(3) {
            border-color: #F1A4A4;
            color: #C93636;
        }

        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-child(3)::before {
            content: "✕";
        }

        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:nth-child(3):has(input:checked) {
            border: 2px solid #D94141;
            background: #FFF0F0;
            box-shadow: 0 0 0 2px rgba(217, 65, 65, 0.10);
        }

        /* Disabled placeholder controls. */
        div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:disabled) {
            border-color: #D9DEE5 !important;
            background: #F4F6F8 !important;
            color: #9AA3AD !important;
            box-shadow: none !important;
            transform: none !important;
            cursor: not-allowed;
            opacity: 0.78;
        }

        /* Stack cleanly on narrower screens. */
        @media (max-width: 800px) {
            div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] {
                grid-template-columns: 1fr;
            }

            div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] > label {
                min-height: 78px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_course_gating_section():
    """
    Render the active Course Gating controls.

    Returns:
        str:
            Selected Module Gating setting.
    """

    render_course_feature_header(
        icon="🔒",
        number=1,
        title="Course Gating",
        description=(
            "Configure sequential module progression, "
            "prerequisite chaining, and completion requirements."
        )
    )

    module_gating = st.radio(
        "Course Gating Action",
        options=[
            "Enable",
            "Don't Change",
            "Disable"
        ],
        index=1,
        horizontal=True,
        label_visibility="collapsed",
        key="course_module_gating",
        help=(
            "Choose whether to enable Course Gating, leave the "
            "current Canvas configuration unchanged, or disable it."
        )
    )

    if module_gating == "Enable":
        st.caption(
            "Enable sequential progress, chain modules in Canvas "
            "course order, and apply completion requirements to "
            "supported module items."
        )

    elif module_gating == "Disable":
        st.caption(
            "Remove sequential progress, module prerequisites, and "
            "module-item completion requirements."
        )

    else:
        st.caption(
            "Leave the current Course Gating configuration unchanged."
        )

    return module_gating


def render_soft_zero_section():
    """Render automatic missing-submission grade controls."""

    render_course_feature_header(
        icon="⚠️",
        number=2,
        title="Soft Zero",
        description=(
            "Automatically apply a preferred grade to eligible "
            "missing submissions."
        )
    )

    soft_zero = st.radio(
        "Soft Zero Action",
        options=[
            "Enable",
            "Don't Change",
            "Disable"
        ],
        index=1,
        horizontal=True,
        label_visibility="collapsed",
        key="course_soft_zero",
        help=(
            "Choose whether Canvas should automatically grade "
            "eligible missing submissions."
        )
    )

    if soft_zero == "Enable":
        missing_grade = st.number_input(
            "Missing Submission Grade (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0,
            key="course_missing_submission_grade",
            help=(
                "Enter the percentage grade Canvas should assign "
                "to eligible missing submissions."
            )
        )

        st.caption(
            "Enter a value between 0 and 100. Late-submission "
            "deductions are not changed by this feature."
        )

    elif soft_zero == "Disable":
        missing_grade = None
        st.caption(
            "Turn off automatic grades for missing submissions. "
            "Late-submission deductions remain unchanged."
        )

    else:
        missing_grade = None
        st.caption(
            "Leave the current missing-submission policy unchanged."
        )

    return soft_zero, missing_grade


def render_due_dates_section():
    """
    Render the planned Due Dates section.
    """

    render_course_feature_header(
        icon="📅",
        number=3,
        title="Due Dates",
        description=(
            "Manage course-wide assignment and assessment "
            "due-date changes."
        )
    )

    st.info(
        "Due Dates is planned for a later Version 0.2 Alpha "
        "development phase."
    )


# ============================================================
# SOFT ZERO PREVIEW AND RESULTS
# ============================================================


def format_percent(value):
    if value is None:
        return "Not Applicable"
    return f"{float(value):g}%"


def display_soft_zero_preview(preview):
    if not preview:
        return

    st.markdown("### Soft Zero Preview")

    current = (
        f"Enabled — {format_percent(preview.get('current_grade_percent'))}"
        if preview.get("current_enabled")
        else "Disabled"
    )

    requested = (
        f"Enabled — {format_percent(preview.get('requested_grade_percent'))}"
        if preview.get("requested_enabled")
        else "Disabled"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.caption("CURRENT CONFIGURATION")
        st.write(current)
    with col2:
        st.caption("REQUESTED CONFIGURATION")
        st.write(requested)

    if preview.get("would_change"):
        st.info("The missing-submission policy will be updated.")
    else:
        st.success("The requested Soft Zero configuration is already set.")


def display_soft_zero_execution_results(result):
    if not result:
        return

    st.markdown("### Soft Zero Results")
    if result.get("success"):
        st.success(result.get("message"))
    else:
        st.error(result.get("message", "Soft Zero update failed."))


# ============================================================
# MAIN COURSE MANAGEMENT WORKSPACE
# ============================================================


def render_course_workspace():
    """Render the Course Management workspace."""

    initialize_course_workspace_state()
    render_course_choice_styles()

    st.markdown("## 📚 Course Management")
    st.write(
        "Configure course-wide administrative settings "
        "across Canvas courses."
    )
    st.markdown("---")

    scope = st.session_state.get("canvas_scope", "Single Course")
    target_id = st.session_state.get("canvas_target_id", "")

    render_current_course_target(scope=scope, target_id=target_id)

    if scope != "Single Course":
        st.info(
            "Sub-Account Course Management is not enabled yet. "
            "Select Single Course in the sidebar to use the "
            "current Course Management tools."
        )
        return

    module_gating = render_course_gating_section()
    soft_zero, missing_grade = render_soft_zero_section()
    render_due_dates_section()

    render_course_feature_header(
        icon="🔍",
        number=4,
        title="Preview Changes",
        description=(
            "Review proposed Course Management changes before "
            "anything is written to Canvas."
        )
    )

    preview_button = st.button(
        "Generate Preview",
        type="primary",
        use_container_width=True,
        key="course_generate_preview"
    )

    if preview_button:
        st.session_state.course_execution_results = None
        st.session_state.course_confirm_apply = False

        if not str(target_id).strip():
            clear_course_preview()
            st.error("Enter a Course ID in the sidebar before generating a Preview.")

        elif module_gating == "Don't Change" and soft_zero == "Don't Change":
            clear_course_preview()
            st.warning("Select at least one Course Management change before generating a Preview.")

        else:
            canvas, connection_error = get_course_canvas_connection()

            if connection_error:
                clear_course_preview()
                st.error(connection_error)
            else:
                bundle = {
                    "module_gating": None,
                    "soft_zero": None
                }
                preview_error = None

                with st.spinner("Loading current course settings and building Preview..."):
                    if module_gating != "Don't Change":
                        gating_preview = build_single_course_module_gating_preview(
                            canvas=canvas,
                            course_id=str(target_id).strip(),
                            setting=module_gating
                        )
                        if not gating_preview.get("success"):
                            preview_error = gating_preview.get("message")
                        else:
                            bundle["module_gating"] = gating_preview

                    if preview_error is None and soft_zero != "Don't Change":
                        soft_preview = build_single_course_soft_zero_preview(
                            canvas=canvas,
                            course_id=str(target_id).strip(),
                            setting=soft_zero,
                            grade_percent=missing_grade
                        )
                        if not soft_preview.get("success"):
                            preview_error = soft_preview.get("message")
                        else:
                            bundle["soft_zero"] = soft_preview

                if preview_error:
                    clear_course_preview()
                    st.error(preview_error)
                else:
                    st.session_state.course_preview = bundle
                    st.session_state.course_preview_signature = build_course_preview_signature(
                        scope=scope,
                        target_id=target_id,
                        module_gating=module_gating,
                        soft_zero=soft_zero,
                        missing_grade=missing_grade
                    )

    preview_bundle = st.session_state.get("course_preview")

    if preview_bundle:
        gating_preview = preview_bundle.get("module_gating")
        soft_preview = preview_bundle.get("soft_zero")

        if gating_preview:
            display_course_preview(gating_preview)

        if soft_preview:
            st.markdown("---")
            display_soft_zero_preview(soft_preview)

        current_signature = build_course_preview_signature(
            scope=scope,
            target_id=target_id,
            module_gating=module_gating,
            soft_zero=soft_zero,
            missing_grade=missing_grade
        )
        preview_is_current = (
            current_signature == st.session_state.get("course_preview_signature")
        )

        if not preview_is_current:
            st.warning(
                "The target or requested settings changed after this Preview. "
                "Generate a new Preview before applying changes."
            )

        gating_counts = (gating_preview or {}).get("counts") or {}
        gating_changes = gating_counts.get("modules_would_change", 0)
        load_failures = gating_counts.get("module_item_load_failures", 0)
        soft_changes = bool((soft_preview or {}).get("would_change", False))
        changes_exist = gating_changes > 0 or soft_changes

        render_course_feature_header(
            icon="✅",
            number=5,
            title="Apply Changes",
            description=(
                "Confirm and execute the reviewed changes "
                "against the selected Canvas course."
            )
        )

        if load_failures > 0:
            st.error(
                "Apply Changes is unavailable because the Preview "
                "could not inspect all module items."
            )
        elif not changes_exist:
            st.success("All requested Course Management settings are already configured.")
        else:
            requested_labels = []
            if gating_preview and gating_changes > 0:
                requested_labels.append(f"Course Gating: {module_gating}")
            if soft_preview and soft_changes:
                if soft_zero == "Enable":
                    requested_labels.append(
                        f"Soft Zero: Enable at {float(missing_grade):g}%"
                    )
                else:
                    requested_labels.append("Soft Zero: Disable")

            st.warning(
                "This operation will apply: " + "; ".join(requested_labels)
            )

            confirm_apply = st.checkbox(
                "I have reviewed the Preview and confirm that I want to apply these Course Management changes.",
                key="course_confirm_apply"
            )

            apply_button = st.button(
                "Apply Changes",
                type="primary",
                use_container_width=True,
                disabled=(not confirm_apply or not preview_is_current),
                key="course_apply_changes"
            )

            if apply_button:
                canvas, connection_error = get_course_canvas_connection()

                if connection_error:
                    st.error(connection_error)
                else:
                    execution_bundle = {
                        "module_gating": None,
                        "soft_zero": None
                    }

                    with st.spinner("Applying Course Management changes in Canvas..."):
                        if gating_preview and gating_changes > 0:
                            execution_bundle["module_gating"] = execute_single_course_module_gating(
                                canvas=canvas,
                                course_id=str(target_id).strip(),
                                setting=module_gating
                            )

                        if soft_preview and soft_changes:
                            execution_bundle["soft_zero"] = execute_single_course_soft_zero(
                                canvas=canvas,
                                course_id=str(target_id).strip(),
                                setting=soft_zero,
                                grade_percent=missing_grade
                            )

                    st.session_state.course_execution_results = execution_bundle
                    st.session_state.course_preview = None
                    st.session_state.course_preview_signature = None
                    st.rerun()

    execution_bundle = st.session_state.get("course_execution_results")

    if execution_bundle:
        gating_result = execution_bundle.get("module_gating")
        soft_result = execution_bundle.get("soft_zero")

        if gating_result:
            display_course_execution_results(gating_result)

        if soft_result:
            st.markdown("---")
            display_soft_zero_execution_results(soft_result)

        st.info(
            "The previous Preview has been cleared because Canvas may now "
            "contain updated values. Generate a new Preview before applying "
            "another change."
        )
