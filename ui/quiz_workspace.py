import streamlit as st

from canvas import CanvasAPI
from tools.quizzes import (
    build_single_course_preview,
    execute_single_course_changes
)


# ============================================================
# ACCELERATE CANVAS ADMINISTRATION SUITE
# Quiz & Exam Management Workspace
#
# CURRENT VERSION:
# - Single Course Preview
# - Setting dependency controls
# - Guarded Apply Changes workflow
# - Explicit administrator confirmation
# - Per-assessment execution results
# ============================================================


def render_quiz_workspace():
    """
    Render the Quiz & Exam Management workspace.
    """

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.markdown(
        "## 🧠 Quiz & Exam Management"
    )

    st.write(
        "Configure Classic Quiz and exam settings across a single "
        "Canvas course or all courses within a selected sub-account."
    )

    st.markdown("---")

    # ========================================================
    # 1. SELECT ASSESSMENT TYPE
    # ========================================================

    st.markdown(
        "### 1. Select Assessment Type"
    )

    st.caption(
        "Choose which assessments should receive "
        "the requested changes."
    )

    assessment_type = st.radio(
        "Assessment Type",
        options=[
            "Quizzes",
            "Exams",
            "Both"
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="quiz_assessment_type"
    )

    if assessment_type == "Quizzes":

        st.info(
            'Classic Quizzes containing the word "quiz" '
            "in the title will be targeted."
        )

    elif assessment_type == "Exams":

        st.info(
            'Classic Quizzes containing the word "exam" '
            "in the title will be targeted."
        )

    else:

        st.info(
            'Classic Quizzes containing either "quiz" '
            'or "exam" in the title will be targeted.'
        )

    st.markdown("---")

    # ========================================================
    # 2. ATTEMPT SETTINGS
    # ========================================================

    st.markdown(
        "### 2. Attempt Settings"
    )

    st.caption(
        'Choose only the settings you want to modify. '
        'Leave a setting on "Don\'t Change" to preserve '
        "its existing Canvas value."
    )

    attempt_col1, attempt_col2 = st.columns(
        2,
        gap="large"
    )

    # --------------------------------------------------------
    # ATTEMPT LIMIT
    # --------------------------------------------------------

    with attempt_col1:

        st.markdown(
            "#### Attempt Limit"
        )

        attempt_limit = st.selectbox(
            "Attempt Limit",
            options=[
                "Don't Change",
                "Unlimited",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10"
            ],
            label_visibility="collapsed",
            key="quiz_attempt_limit"
        )

        st.caption(
            "Set the number of attempts students are allowed."
        )

    # --------------------------------------------------------
    # ATTEMPT TO RECORD DEPENDENCY
    # --------------------------------------------------------

    attempt_record_disabled = (
        attempt_limit == "1"
    )

    # --------------------------------------------------------
    # ATTEMPT TO RECORD
    # --------------------------------------------------------

    with attempt_col2:

        st.markdown(
            "#### Attempt to Record"
        )

        if attempt_record_disabled:

            attempt_record = "Don't Change"

            st.selectbox(
                "Attempt to Record",
                options=[
                    "Not Applicable"
                ],
                disabled=True,
                label_visibility="collapsed",
                key="quiz_attempt_record_disabled"
            )

            st.caption(
                "Not applicable when only one attempt is allowed."
            )

        else:

            attempt_record = st.selectbox(
                "Attempt to Record",
                options=[
                    "Don't Change",
                    "Highest",
                    "Latest",
                    "Average"
                ],
                label_visibility="collapsed",
                key="quiz_attempt_record"
            )

            if attempt_limit == "Don't Change":

                st.caption(
                    "Availability will be evaluated for each "
                    "assessment based on its current attempt limit."
                )

            else:

                st.caption(
                    "Choose how Canvas records the score "
                    "when multiple attempts are allowed."
                )

                # =================================================
                # NEW:
                # Explain Canvas behavior when a quiz changes from
                # one attempt to multiple attempts without an
                # explicit scoring method being selected.
                # =================================================

                if attempt_record == "Don't Change":

                    st.info(
                        "When changing an assessment from one attempt "
                        "to multiple attempts, Canvas requires an attempt "
                        "scoring method. If Attempt to Record is left as "
                        "\"Don't Change\" and no previous scoring method "
                        "applies, Canvas will use its default scoring "
                        "method: Highest."
                    )

    st.markdown("---")

    # ========================================================
    # 3. DELIVERY SETTINGS
    # ========================================================

    st.markdown(
        "### 3. Delivery Settings"
    )

    st.caption(
        "Enable, disable, or preserve each existing "
        "Canvas assessment setting."
    )

    delivery_col1, delivery_col2 = st.columns(
        2,
        gap="large"
    )

    # --------------------------------------------------------
    # SHUFFLE ANSWERS
    # --------------------------------------------------------

    with delivery_col1:

        st.markdown(
            "#### Shuffle Answers"
        )

        shuffle_answers = st.radio(
            "Shuffle Answers",
            options=[
                "Don't Change",
                "Enable",
                "Disable"
            ],
            horizontal=True,
            label_visibility="collapsed",
            key="quiz_shuffle_answers"
        )

    # --------------------------------------------------------
    # SHOW ONE QUESTION AT A TIME
    # --------------------------------------------------------

    with delivery_col2:

        st.markdown(
            "#### Show One Question at a Time"
        )

        one_question_at_a_time = st.radio(
            "Show One Question at a Time",
            options=[
                "Don't Change",
                "Enable",
                "Disable"
            ],
            horizontal=True,
            label_visibility="collapsed",
            key="quiz_one_question"
        )

    st.markdown("---")

    # ========================================================
    # 4. ASSESSMENT REVIEW SETTINGS
    # ========================================================

    st.markdown(
        "### 4. Assessment Review Settings"
    )

    st.caption(
        "Control what students are allowed to review "
        "after submitting an assessment."
    )

    review_col1, review_col2 = st.columns(
        2,
        gap="large"
    )

    # --------------------------------------------------------
    # SHOW STUDENT QUIZ RESPONSES
    # --------------------------------------------------------

    with review_col1:

        st.markdown(
            "#### Show Student Quiz Responses"
        )

        show_responses = st.radio(
            "Show Student Quiz Responses",
            options=[
                "Don't Change",
                "Allow",
                "Do Not Allow"
            ],
            horizontal=True,
            label_visibility="collapsed",
            key="quiz_show_responses"
        )

        st.caption(
            "Control whether students may review "
            "their submitted quiz responses."
        )

    # --------------------------------------------------------
    # CORRECT ANSWER DEPENDENCY
    # --------------------------------------------------------

    correct_answers_disabled = (
        show_responses == "Do Not Allow"
    )

    # --------------------------------------------------------
    # SHOW CORRECT ANSWERS
    # --------------------------------------------------------

    with review_col2:

        st.markdown(
            "#### Show Correct Answers"
        )

        if correct_answers_disabled:

            show_correct_answers = (
                "Don't Change"
            )

            st.radio(
                "Show Correct Answers",
                options=[
                    "Not Applicable"
                ],
                disabled=True,
                label_visibility="collapsed",
                key="quiz_show_correct_answers_disabled"
            )

            st.caption(
                "Not applicable when student quiz "
                "responses are not shown."
            )

        else:

            show_correct_answers = st.radio(
                "Show Correct Answers",
                options=[
                    "Don't Change",
                    "Allow",
                    "Do Not Allow"
                ],
                horizontal=True,
                label_visibility="collapsed",
                key="quiz_show_correct_answers"
            )

            if show_responses == "Don't Change":

                st.caption(
                    "Availability will be evaluated for each "
                    "assessment based on its current response "
                    "visibility."
                )

            else:

                st.caption(
                    "Control whether students may see "
                    "the correct answers."
                )

    # ========================================================
    # 5. EXAM PASSWORD
    # ========================================================

    password_action = "Don't Change"
    exam_password = ""

    if assessment_type in [
        "Exams",
        "Both"
    ]:

        st.markdown("---")

        st.markdown(
            "### 5. Exam Password"
        )

        st.caption(
            "Password changes apply only to assessments "
            'identified by the word "exam" in the title.'
        )

        password_action = st.radio(
            "Exam Password Action",
            options=[
                "Don't Change",
                "Set / Replace Password",
                "Remove Password"
            ],
            horizontal=True,
            key="exam_password_action"
        )

        if (
            password_action
            == "Set / Replace Password"
        ):

            exam_password = st.text_input(
                "Exam Password",
                type="password",
                placeholder=(
                    "Enter the password to apply to exams"
                ),
                key="exam_password_input"
            )

            st.caption(
                "The password itself will not be displayed "
                "in Preview results."
            )

        elif (
            password_action
            == "Remove Password"
        ):

            st.warning(
                "Preview will identify targeted exams whose "
                "password setting would be removed."
            )

    # ========================================================
    # BUILD SETTINGS OBJECT
    # ========================================================

    settings = {

        "assessment_type":
            assessment_type,

        "attempt_limit":
            attempt_limit,

        "attempt_record":
            attempt_record,

        "shuffle_answers":
            shuffle_answers,

        "one_question_at_a_time":
            one_question_at_a_time,

        "show_responses":
            show_responses,

        "show_correct_answers":
            show_correct_answers,

        "password_action":
            password_action,

        "exam_password":
            exam_password
    }

    # ========================================================
    # DETERMINE WHETHER A CHANGE WAS REQUESTED
    # ========================================================

    change_requested = any(
        [
            attempt_limit
            != "Don't Change",

            attempt_record
            != "Don't Change",

            shuffle_answers
            != "Don't Change",

            one_question_at_a_time
            != "Don't Change",

            show_responses
            != "Don't Change",

            show_correct_answers
            != "Don't Change",

            password_action
            != "Don't Change"
        ]
    )

    # ========================================================
    # READ CURRENT CONNECTION / TARGET VALUES
    # ========================================================

    canvas_url = st.session_state.get(
        "canvas_url_input",
        ""
    ).strip().rstrip("/")

    api_token = st.session_state.get(
        "canvas_api_token_input",
        ""
    ).strip()

    target_scope = st.session_state.get(
        "canvas_scope",
        "Single Course"
    )

    target_id = st.session_state.get(
        "canvas_target_id",
        ""
    ).strip()

    # ========================================================
    # CURRENT CONFIGURATION SIGNATURE
    # ========================================================

    current_signature = {

        "canvas_url":
            canvas_url,

        "target_scope":
            target_scope,

        "target_id":
            target_id,

        "assessment_type":
            assessment_type,

        "attempt_limit":
            attempt_limit,

        "attempt_record":
            attempt_record,

        "shuffle_answers":
            shuffle_answers,

        "one_question_at_a_time":
            one_question_at_a_time,

        "show_responses":
            show_responses,

        "show_correct_answers":
            show_correct_answers,

        "password_action":
            password_action,

        "exam_password_supplied":
            bool(
                exam_password.strip()
            )
    }

    # ========================================================
    # PREVIEW SECTION
    # ========================================================

    st.markdown("---")

    if assessment_type == "Quizzes":

        preview_step_number = 5

    else:

        preview_step_number = 6

    st.markdown(
        f"### {preview_step_number}. Preview Changes"
    )

    st.write(
        "Review the affected course, assessments, and proposed "
        "setting changes before anything is applied."
    )

    st.warning(
        "Preview Mode is read-only. "
        "No Canvas settings will be modified."
    )

    preview_clicked = st.button(
        "Preview Changes",
        type="primary",
        use_container_width=True,
        disabled=not change_requested,
        key="quiz_preview_button"
    )

    if not change_requested:

        st.caption(
            "Select at least one setting to modify "
            "before previewing."
        )

    # ========================================================
    # RUN PREVIEW
    # ========================================================

    if preview_clicked:

        st.session_state.pop(
            "quiz_preview_signature",
            None
        )

        st.session_state.pop(
            "quiz_preview_result",
            None
        )

        st.session_state.pop(
            "quiz_preview_settings",
            None
        )

        st.session_state.pop(
            "quiz_apply_confirmation",
            None
        )

        # ====================================================
        # VALIDATE CANVAS CONNECTION
        # ====================================================

        if not st.session_state.get(
            "canvas_connected",
            False
        ):

            st.error(
                "Connect to Canvas using the Test Connection "
                "button before previewing changes."
            )

            return settings

        # ====================================================
        # VALIDATE CONNECTION INFORMATION
        # ====================================================

        if not canvas_url:

            st.error(
                "The Canvas URL is unavailable. "
                "Enter the Canvas URL and test "
                "the connection again."
            )

            return settings

        if not api_token:

            st.error(
                "The Canvas API token is unavailable. "
                "Enter the token and test "
                "the connection again."
            )

            return settings

        # ====================================================
        # VALIDATE TARGET ID
        # ====================================================

        if not target_id:

            if target_scope == "Single Course":

                st.error(
                    "Enter a Course ID in the sidebar "
                    "before previewing changes."
                )

            else:

                st.error(
                    "Enter a Sub-Account ID in the sidebar "
                    "before previewing changes."
                )

            return settings

        if not target_id.isdigit():

            if target_scope == "Single Course":

                st.error(
                    "Course ID must contain numbers only."
                )

            else:

                st.error(
                    "Sub-Account ID must contain numbers only."
                )

            return settings

        # ====================================================
        # SINGLE COURSE ONLY FOR CURRENT VERSION
        # ====================================================

        if target_scope == "Sub-Account":

            st.info(
                "Sub-Account Preview is not enabled yet. "
                "Single Course Preview is being "
                "validated first."
            )

            return settings

        # ====================================================
        # VALIDATE EXAM PASSWORD
        # ====================================================

        if (
            password_action
            == "Set / Replace Password"
            and not exam_password.strip()
        ):

            st.error(
                "Enter an exam password before previewing "
                "the requested password change."
            )

            return settings

        # ====================================================
        # CREATE CANVAS API CONNECTION
        # ====================================================

        canvas = CanvasAPI(
            canvas_url=canvas_url,
            api_token=api_token
        )

        # ====================================================
        # GENERATE READ-ONLY PREVIEW
        # ====================================================

        with st.spinner(
            "Reading course and assessment settings "
            "from Canvas..."
        ):

            result = build_single_course_preview(
                canvas=canvas,
                course_id=target_id,
                settings=settings
            )

        # ====================================================
        # PREVIEW FAILURE
        # ====================================================

        if not result["success"]:

            st.error(
                result["message"]
            )

            return settings

        # ====================================================
        # STORE VALID PREVIEW
        # ====================================================

        st.session_state[
            "quiz_preview_signature"
        ] = current_signature.copy()

        st.session_state[
            "quiz_preview_result"
        ] = result

        st.session_state[
            "quiz_preview_settings"
        ] = settings.copy()

        st.session_state[
            "quiz_preview_settings"
        ][
            "exam_password"
        ] = ""

    # ========================================================
    # LOAD STORED PREVIEW
    # ========================================================

    stored_preview = st.session_state.get(
        "quiz_preview_result"
    )

    stored_signature = st.session_state.get(
        "quiz_preview_signature"
    )

    # ========================================================
    # DETERMINE WHETHER PREVIEW IS STILL CURRENT
    # ========================================================

    preview_is_current = (
        stored_preview is not None
        and stored_signature
        == current_signature
    )

    # ========================================================
    # IF SETTINGS CHANGED AFTER PREVIEW
    # ========================================================

    if (
        stored_preview is not None
        and not preview_is_current
    ):

        st.warning(
            "The target or requested settings changed after "
            "the last Preview. Generate a new Preview before "
            "applying changes."
        )

    # ========================================================
    # DISPLAY CURRENT VALID PREVIEW
    # ========================================================

    if preview_is_current:

        result = stored_preview

        course = result[
            "course"
        ]

        counts = result[
            "counts"
        ]

        assessments = result[
            "assessments"
        ]

        st.success(
            "Preview generated successfully. "
            "No Canvas changes were made."
        )

        # ====================================================
        # COURSE INFORMATION
        # ====================================================

        st.markdown("---")

        st.markdown(
            "### Preview Results"
        )

        st.markdown(
            f"## {course['name']}"
        )

        st.caption(
            f"Canvas Course ID: "
            f"{course['id']}"
        )

        if course.get(
            "course_code"
        ):

            st.caption(
                f"Course Code: "
                f"{course['course_code']}"
            )

        # ====================================================
        # SUMMARY METRICS
        # ====================================================

        metric1, metric2, metric3 = (
            st.columns(3)
        )

        with metric1:

            st.metric(
                "Assessments Found",
                counts["total"]
            )

        with metric2:

            st.metric(
                "Quizzes",
                counts["quizzes"]
            )

        with metric3:

            st.metric(
                "Exams",
                counts["exams"]
            )

        # ====================================================
        # NO MATCHING ASSESSMENTS
        # ====================================================

        if not assessments:

            st.warning(
                "No Classic Quizzes matched the selected "
                "Quiz / Exam title rules in this course."
            )

            st.info(
                "No changes were made to Canvas."
            )

            return settings

        # ====================================================
        # PROPOSED CHANGES
        # ====================================================

        st.markdown("---")

        st.markdown(
            "### Proposed Changes"
        )

        st.caption(
            "Each assessment below shows its current Canvas "
            "setting and the requested setting."
        )

        would_change_count = 0

        # ====================================================
        # DISPLAY EACH TARGETED ASSESSMENT
        # ====================================================

        for assessment in assessments:

            title = assessment[
                "title"
            ]

            classification = assessment[
                "classification"
            ]

            assessment_id = assessment[
                "id"
            ]

            changes = assessment[
                "changes"
            ]

            expander_title = (
                f"{classification}: {title}"
            )

            with st.expander(
                expander_title,
                expanded=True
            ):

                st.caption(
                    f"Canvas Assessment ID: "
                    f"{assessment_id}"
                )

                if not changes:

                    st.info(
                        "No requested settings apply "
                        "to this assessment."
                    )

                    continue

                table_rows = []

                for change in changes:

                    current_value = change[
                        "current"
                    ]

                    requested_value = change[
                        "requested"
                    ]

                    note = change.get(
                        "note"
                    )

                    if (
                        current_value
                        == "Not Applicable"
                        and requested_value
                        == "Not Applicable"
                    ):

                        status = (
                            "Not Applicable"
                        )

                    elif (
                        current_value
                        == requested_value
                    ):

                        status = (
                            "Already Set"
                        )

                    else:

                        status = (
                            "Would Change"
                        )

                        would_change_count += 1

                    row = {

                        "Setting":
                            change["setting"],

                        "Current":
                            current_value,

                        "Requested":
                            requested_value,

                        "Status":
                            status
                    }

                    if note:

                        row["Note"] = note

                    table_rows.append(
                        row
                    )

                st.table(
                    table_rows
                )

        # ====================================================
        # READ-ONLY PREVIEW CONFIRMATION
        # ====================================================

        st.markdown("---")

        st.info(
            "READ-ONLY PREVIEW COMPLETE — "
            "No changes have been sent to Canvas."
        )

        # ====================================================
        # APPLY CHANGES SECTION
        # ====================================================

        apply_step_number = (
            preview_step_number + 1
        )

        st.markdown("---")

        st.markdown(
            f"### {apply_step_number}. Apply Changes"
        )

        if would_change_count == 0:

            st.success(
                "Everything selected is already configured "
                "as requested, or the selected settings are "
                "not applicable. No Canvas update is needed."
            )

            return settings

        st.warning(
            "Applying changes will modify Canvas. "
            "Review the Preview above before continuing."
        )

        st.write(
            f"This Preview contains "
            f"**{would_change_count} setting change(s)** "
            "across the targeted assessments."
        )

        # ====================================================
        # EXPLICIT CONFIRMATION
        # ====================================================

        confirmation = st.checkbox(
            (
                "I reviewed the Preview and understand that "
                "clicking Apply Changes will modify Canvas."
            ),
            key="quiz_apply_confirmation"
        )

        st.caption(
            "For the first live test, use a test course and "
            "select only one setting change. Verify the result "
            "directly in Canvas before running broader updates."
        )

        apply_clicked = st.button(
            "Apply Changes",
            type="primary",
            use_container_width=True,
            disabled=not confirmation,
            key="quiz_apply_button"
        )

        # ====================================================
        # EXECUTE CHANGES
        # ====================================================

        if apply_clicked:

            # ------------------------------------------------
            # RE-CHECK PREVIEW SIGNATURE
            # ------------------------------------------------

            latest_signature = {

                "canvas_url":
                    st.session_state.get(
                        "canvas_url_input",
                        ""
                    ).strip().rstrip("/"),

                "target_scope":
                    st.session_state.get(
                        "canvas_scope",
                        "Single Course"
                    ),

                "target_id":
                    st.session_state.get(
                        "canvas_target_id",
                        ""
                    ).strip(),

                "assessment_type":
                    assessment_type,

                "attempt_limit":
                    attempt_limit,

                "attempt_record":
                    attempt_record,

                "shuffle_answers":
                    shuffle_answers,

                "one_question_at_a_time":
                    one_question_at_a_time,

                "show_responses":
                    show_responses,

                "show_correct_answers":
                    show_correct_answers,

                "password_action":
                    password_action,

                "exam_password_supplied":
                    bool(
                        exam_password.strip()
                    )
            }

            if (
                latest_signature
                != st.session_state.get(
                    "quiz_preview_signature"
                )
            ):

                st.error(
                    "The target or requested settings changed "
                    "after Preview. Generate a new Preview "
                    "before applying changes."
                )

                return settings

            # ------------------------------------------------
            # RE-CHECK CONNECTION
            # ------------------------------------------------

            if not st.session_state.get(
                "canvas_connected",
                False
            ):

                st.error(
                    "The Canvas connection is no longer "
                    "confirmed. Test the connection again "
                    "before applying changes."
                )

                return settings

            # ------------------------------------------------
            # RE-CHECK SINGLE COURSE MODE
            # ------------------------------------------------

            if target_scope != "Single Course":

                st.error(
                    "Apply Changes is currently enabled only "
                    "for Single Course mode."
                )

                return settings

            # ------------------------------------------------
            # VALIDATE PASSWORD AGAIN
            # ------------------------------------------------

            if (
                password_action
                == "Set / Replace Password"
                and not exam_password.strip()
            ):

                st.error(
                    "Enter the exam password again before "
                    "applying the requested password change."
                )

                return settings

            # ------------------------------------------------
            # CREATE FRESH CANVAS API CONNECTION
            # ------------------------------------------------

            canvas = CanvasAPI(
                canvas_url=canvas_url,
                api_token=api_token
            )

            # ------------------------------------------------
            # EXECUTE
            # ------------------------------------------------

            with st.spinner(
                "Applying approved changes to Canvas..."
            ):

                execution_result = (
                    execute_single_course_changes(
                        canvas=canvas,
                        course_id=target_id,
                        settings=settings
                    )
                )

            # =================================================
            # EXECUTION RESULTS
            # =================================================

            st.markdown("---")

            st.markdown(
                "### Execution Results"
            )

            execution_counts = (
                execution_result[
                    "counts"
                ]
            )

            result_col1, result_col2, (
                result_col3
            ), result_col4 = st.columns(
                4
            )

            with result_col1:

                st.metric(
                    "Targeted",
                    execution_counts[
                        "targeted"
                    ]
                )

            with result_col2:

                st.metric(
                    "Updated",
                    execution_counts[
                        "updated"
                    ]
                )

            with result_col3:

                st.metric(
                    "Skipped",
                    execution_counts[
                        "skipped"
                    ]
                )

            with result_col4:

                st.metric(
                    "Failed",
                    execution_counts[
                        "failed"
                    ]
                )

            # ------------------------------------------------
            # OVERALL STATUS
            # ------------------------------------------------

            if execution_counts[
                "failed"
            ] == 0:

                st.success(
                    execution_result[
                        "message"
                    ]
                )

            else:

                st.error(
                    execution_result[
                        "message"
                    ]
                )

            # ------------------------------------------------
            # PER-ASSESSMENT RESULTS
            # ------------------------------------------------

            execution_rows = []

            for item in execution_result[
                "results"
            ]:

                updated_fields = (
                    ", ".join(
                        item[
                            "updated_fields"
                        ]
                    )
                    if item[
                        "updated_fields"
                    ]
                    else "None"
                )

                execution_rows.append(
                    {
                        "Assessment":
                            item[
                                "title"
                            ],

                        "Type":
                            item[
                                "classification"
                            ],

                        "Status":
                            item[
                                "status"
                            ],

                        "Updated Fields":
                            updated_fields,

                        "Message":
                            item[
                                "message"
                            ]
                    }
                )

            if execution_rows:

                st.dataframe(
                    execution_rows,
                    use_container_width=True,
                    hide_index=True
                )

            # ------------------------------------------------
            # INVALIDATE THE OLD PREVIEW AFTER EXECUTION
            # ------------------------------------------------

            st.session_state.pop(
                "quiz_preview_signature",
                None
            )

            st.session_state.pop(
                "quiz_preview_result",
                None
            )

            st.session_state.pop(
                "quiz_preview_settings",
                None
            )

            st.info(
                "The previous Preview has been cleared because "
                "Canvas may now contain updated values. Generate "
                "a new Preview before applying another change."
            )

    # ========================================================
    # RETURN CURRENT SETTINGS
    # ========================================================

    return settings