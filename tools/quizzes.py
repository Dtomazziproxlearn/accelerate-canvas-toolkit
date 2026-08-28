# ============================================================
# ACCELERATE CANVAS ADMINISTRATION SUITE
# Quiz & Exam Tools
#
# Contains quiz-specific business logic.
#
# CURRENT VERSION:
# - Read-only Preview logic
# - Quiz / Exam title classification
# - Setting dependency validation
# - Canvas update payload construction
# - Controlled single-course execution engine
#
# IMPORTANT:
# Nothing in this file executes automatically.
# Canvas is modified only when execute_single_course_changes()
# is explicitly called by the application.
# ============================================================


# ============================================================
# ASSESSMENT CLASSIFICATION
# ============================================================


def classify_assessment(title):
    """
    Classify an assessment based on its title.

    Rules:
        - Title containing "exam" -> Exam
        - Title containing "quiz" -> Quiz
        - Otherwise -> Other

    Matching is case-insensitive.

    Exam is checked first so that a title containing both
    "quiz" and "exam" is treated as an Exam.
    """

    normalized_title = (title or "").lower()

    if "exam" in normalized_title:
        return "Exam"

    if "quiz" in normalized_title:
        return "Quiz"

    return "Other"


# ============================================================
# CURRENT CANVAS VALUE HELPERS
# ============================================================


def get_allowed_attempts(quiz):
    """
    Return the raw Canvas allowed_attempts value.
    """

    return quiz.get("allowed_attempts")


def current_attempt_limit(quiz):
    """
    Convert Canvas allowed_attempts into a readable value.

    Canvas Classic Quizzes commonly uses -1 for Unlimited.
    """

    value = get_allowed_attempts(quiz)

    if value == -1:
        return "Unlimited"

    if value is None:
        return "Unknown"

    return str(value)


def has_multiple_attempts(quiz):
    """
    Determine whether the quiz currently allows more than
    one attempt.
    """

    value = get_allowed_attempts(quiz)

    if value == -1:
        return True

    if isinstance(value, int) and value >= 2:
        return True

    return False


def current_scoring_method(quiz):
    """
    Convert Canvas scoring_policy into a readable value.
    """

    value = quiz.get("scoring_policy")

    mapping = {
        "keep_highest": "Highest",
        "keep_latest": "Latest",
        "keep_average": "Average"
    }

    return mapping.get(
        value,
        value or "Unknown"
    )


def enabled_disabled(value):
    """
    Convert a Boolean Canvas setting into readable text.
    """

    if value is True:
        return "Enabled"

    if value is False:
        return "Disabled"

    return "Unknown"


# ============================================================
# RESPONSE VISIBILITY HELPERS
# ============================================================


def responses_are_shown(quiz):
    """
    Determine whether students are currently allowed to see
    their quiz responses.

    Canvas Classic Quizzes uses hide_results.

    hide_results == "always"
        -> students cannot see quiz responses

    Any other value
        -> responses are treated as available for review
    """

    return quiz.get("hide_results") != "always"


def current_response_visibility(quiz):
    """
    Return a readable current value for whether student quiz
    responses are shown.
    """

    if responses_are_shown(quiz):
        return "Allow"

    return "Do Not Allow"


def correct_answers_are_shown(quiz):
    """
    Determine whether Canvas currently allows students to see
    correct answers.

    Prefer show_correct_answers when Canvas provides it.

    Fall back to the inverse hide_correct_answers field if
    Canvas returns that field instead.
    """

    if "show_correct_answers" in quiz:

        value = quiz.get(
            "show_correct_answers"
        )

        if value is True:
            return True

        if value is False:
            return False

    if "hide_correct_answers" in quiz:

        value = quiz.get(
            "hide_correct_answers"
        )

        if value is True:
            return False

        if value is False:
            return True

    # If neither field provides a usable Boolean value,
    # treat Canvas's normal/default state as showing
    # correct answers when responses are available.

    return True


def current_correct_answer_visibility(quiz):
    """
    Return a readable current value for whether correct answers
    are shown.

    Correct-answer visibility is meaningful only when students
    can review their quiz responses.
    """

    if not responses_are_shown(
        quiz
    ):

        return "Not Applicable"

    if correct_answers_are_shown(
        quiz
    ):

        return "Allow"

    return "Do Not Allow"


# ============================================================
# REQUESTED VALUE HELPERS
# ============================================================


def requested_attempt_limit(setting):

    if setting == "Don't Change":
        return "No Change"

    return setting


def requested_scoring_method(setting):

    if setting == "Don't Change":
        return "No Change"

    return setting


def requested_enable_disable(setting):

    if setting == "Don't Change":
        return "No Change"

    if setting == "Enable":
        return "Enabled"

    if setting == "Disable":
        return "Disabled"

    return setting


def requested_allow(setting):

    if setting == "Don't Change":
        return "No Change"

    return setting


# ============================================================
# DEPENDENCY HELPERS
# ============================================================


def resulting_multiple_attempts(
    quiz,
    requested_attempt_limit_value
):
    """
    Determine whether multiple attempts will be available after
    considering the requested Attempt Limit.

    If Attempt Limit is "Don't Change", use the current value.

    Unlimited or 2+ supports Attempt to Record.
    """

    if (
        requested_attempt_limit_value
        == "Don't Change"
    ):

        return has_multiple_attempts(
            quiz
        )

    if (
        requested_attempt_limit_value
        == "Unlimited"
    ):

        return True

    try:

        numeric_value = int(
            requested_attempt_limit_value
        )

        return numeric_value >= 2

    except (TypeError, ValueError):

        return False


def resulting_responses_are_shown(
    quiz,
    requested_response_setting
):
    """
    Determine whether student quiz responses will be shown after
    considering the requested setting.

    If "Don't Change" is selected, use the current Canvas value.
    """

    if (
        requested_response_setting
        == "Allow"
    ):

        return True

    if (
        requested_response_setting
        == "Do Not Allow"
    ):

        return False

    return responses_are_shown(
        quiz
    )


# ============================================================
# PREVIEW CHANGE ROW BUILDER
# ============================================================


def build_change_rows(
    quiz,
    classification,
    settings
):
    """
    Build the human-readable Preview rows for one assessment.

    This centralizes Preview comparison logic so the same
    dependency rules can also be used by the execution engine.
    """

    rows = []

    # --------------------------------------------------------
    # ATTEMPT LIMIT
    # --------------------------------------------------------

    if (
        settings["attempt_limit"]
        != "Don't Change"
    ):

        rows.append(
            {
                "setting":
                    "Attempt Limit",

                "current":
                    current_attempt_limit(
                        quiz
                    ),

                "requested":
                    requested_attempt_limit(
                        settings[
                            "attempt_limit"
                        ]
                    ),

                "note":
                    None
            }
        )

    # --------------------------------------------------------
    # ATTEMPT TO RECORD
    # --------------------------------------------------------

    if (
        settings["attempt_record"]
        != "Don't Change"
    ):

        multiple_attempts_available = (
            resulting_multiple_attempts(
                quiz,
                settings[
                    "attempt_limit"
                ]
            )
        )

        if multiple_attempts_available:

            rows.append(
                {
                    "setting":
                        "Attempt to Record",

                    "current":
                        current_scoring_method(
                            quiz
                        ),

                    "requested":
                        requested_scoring_method(
                            settings[
                                "attempt_record"
                            ]
                        ),

                    "note":
                        None
                }
            )

        else:

            rows.append(
                {
                    "setting":
                        "Attempt to Record",

                    "current":
                        "Not Applicable",

                    "requested":
                        "Not Applicable",

                    "note":
                        (
                            "Only applicable when "
                            "2 or more attempts "
                            "are allowed."
                        )
                }
            )

    # --------------------------------------------------------
    # SHUFFLE ANSWERS
    # --------------------------------------------------------

    if (
        settings["shuffle_answers"]
        != "Don't Change"
    ):

        rows.append(
            {
                "setting":
                    "Shuffle Answers",

                "current":
                    enabled_disabled(
                        quiz.get(
                            "shuffle_answers"
                        )
                    ),

                "requested":
                    requested_enable_disable(
                        settings[
                            "shuffle_answers"
                        ]
                    ),

                "note":
                    None
            }
        )

    # --------------------------------------------------------
    # ONE QUESTION AT A TIME
    # --------------------------------------------------------

    if (
        settings[
            "one_question_at_a_time"
        ]
        != "Don't Change"
    ):

        rows.append(
            {
                "setting":
                    "Show One Question at a Time",

                "current":
                    enabled_disabled(
                        quiz.get(
                            "one_question_at_a_time"
                        )
                    ),

                "requested":
                    requested_enable_disable(
                        settings[
                            "one_question_at_a_time"
                        ]
                    ),

                "note":
                    None
            }
        )

    # --------------------------------------------------------
    # SHOW STUDENT QUIZ RESPONSES
    # --------------------------------------------------------

    if (
        settings["show_responses"]
        != "Don't Change"
    ):

        rows.append(
            {
                "setting":
                    "Show Student Quiz Responses",

                "current":
                    current_response_visibility(
                        quiz
                    ),

                "requested":
                    requested_allow(
                        settings[
                            "show_responses"
                        ]
                    ),

                "note":
                    None
            }
        )

    # --------------------------------------------------------
    # SHOW CORRECT ANSWERS
    #
    # Only applies if student responses will be shown.
    # --------------------------------------------------------

    if (
        settings[
            "show_correct_answers"
        ]
        != "Don't Change"
    ):

        responses_available = (
            resulting_responses_are_shown(
                quiz,
                settings[
                    "show_responses"
                ]
            )
        )

        if responses_available:

            rows.append(
                {
                    "setting":
                        "Show Correct Answers",

                    "current":
                        current_correct_answer_visibility(
                            quiz
                        ),

                    "requested":
                        requested_allow(
                            settings[
                                "show_correct_answers"
                            ]
                        ),

                    "note":
                        None
                }
            )

        else:

            rows.append(
                {
                    "setting":
                        "Show Correct Answers",

                    "current":
                        "Not Applicable",

                    "requested":
                        "Not Applicable",

                    "note":
                        (
                            "Not applicable when "
                            "student quiz responses "
                            "are not shown."
                        )
                }
            )

    # --------------------------------------------------------
    # EXAM PASSWORD
    # --------------------------------------------------------

    if (
        classification == "Exam"
        and settings[
            "password_action"
        ]
        != "Don't Change"
    ):

        current_password_state = (
            "Password Set"
            if quiz.get(
                "has_access_code"
            )
            else "No Password"
        )

        if (
            settings[
                "password_action"
            ]
            == "Set / Replace Password"
        ):

            requested_password_state = (
                "Set / Replace Password"
            )

        else:

            requested_password_state = (
                "Remove Password"
            )

        rows.append(
            {
                "setting":
                    "Exam Password",

                "current":
                    current_password_state,

                "requested":
                    requested_password_state,

                "note":
                    None
            }
        )

    return rows


# ============================================================
# TARGET MATCHING
# ============================================================


def assessment_matches_target(
    classification,
    assessment_type
):
    """
    Determine whether an assessment classification matches
    the administrator's selected target type.
    """

    if (
        assessment_type == "Quizzes"
        and classification == "Quiz"
    ):

        return True

    if (
        assessment_type == "Exams"
        and classification == "Exam"
    ):

        return True

    if (
        assessment_type == "Both"
        and classification in [
            "Quiz",
            "Exam"
        ]
    ):

        return True

    return False


# ============================================================
# BUILD SINGLE COURSE PREVIEW
# ============================================================


def build_single_course_preview(
    canvas,
    course_id,
    settings
):
    """
    Build a READ-ONLY preview for one Canvas course.

    No Canvas modifications are performed.
    """

    # ========================================================
    # GET COURSE
    # ========================================================

    course_result = canvas.get_course(
        course_id
    )

    if not course_result["success"]:

        return {
            "success": False,
            "message": (
                "Unable to load the selected course. "
                + course_result["message"]
            ),
            "course": None,
            "assessments": [],
            "counts": {}
        }

    course = course_result["data"]

    # ========================================================
    # GET CLASSIC QUIZZES
    # ========================================================

    quiz_result = canvas.get_classic_quizzes(
        course_id
    )

    if not quiz_result["success"]:

        return {
            "success": False,
            "message": (
                "The course was found, but its Classic Quizzes "
                "could not be loaded. "
                + quiz_result["message"]
            ),
            "course": course,
            "assessments": [],
            "counts": {}
        }

    quizzes = quiz_result["data"]

    assessment_type = settings[
        "assessment_type"
    ]

    targeted = []

    # ========================================================
    # FILTER AND BUILD PREVIEW
    # ========================================================

    for quiz in quizzes:

        classification = classify_assessment(
            quiz.get("title")
        )

        if not assessment_matches_target(
            classification,
            assessment_type
        ):

            continue

        rows = build_change_rows(
            quiz=quiz,
            classification=classification,
            settings=settings
        )

        targeted.append(
            {
                "id":
                    quiz.get("id"),

                "title":
                    (
                        quiz.get("title")
                        or "Untitled Assessment"
                    ),

                "classification":
                    classification,

                "changes":
                    rows
            }
        )

    # ========================================================
    # COUNTS
    # ========================================================

    quiz_count = sum(
        1
        for item in targeted
        if item["classification"]
        == "Quiz"
    )

    exam_count = sum(
        1
        for item in targeted
        if item["classification"]
        == "Exam"
    )

    # ========================================================
    # RETURN PREVIEW
    # ========================================================

    return {
        "success": True,

        "message":
            "Preview generated successfully.",

        "course": {

            "id":
                course.get("id"),

            "name":
                (
                    course.get("name")
                    or course.get(
                        "course_code"
                    )
                    or f"Course {course_id}"
                ),

            "course_code":
                course.get(
                    "course_code"
                )
        },

        "assessments":
            targeted,

        "counts": {

            "total":
                len(targeted),

            "quizzes":
                quiz_count,

            "exams":
                exam_count
        }
    }


# ============================================================
# CANVAS UPDATE VALUE HELPERS
# ============================================================


def canvas_attempt_limit(setting):
    """
    Convert the UI Attempt Limit into the Canvas API value.

    Unlimited -> -1
    "3"       -> 3
    """

    if setting == "Unlimited":
        return -1

    return int(setting)


def canvas_scoring_policy(setting):
    """
    Convert UI scoring choice into Canvas scoring_policy.
    """

    mapping = {
        "Highest": "keep_highest",
        "Latest": "keep_latest",
        "Average": "keep_average"
    }

    return mapping.get(
        setting
    )


def canvas_enable_disable(setting):
    """
    Convert Enable / Disable into Boolean.
    """

    if setting == "Enable":
        return True

    if setting == "Disable":
        return False

    return None


# ============================================================
# BUILD QUIZ UPDATE PAYLOAD
# ============================================================


def build_quiz_update_payload(
    quiz,
    classification,
    settings
):
    """
    Build the minimal Canvas update payload for one assessment.

    SAFETY RULES:

    1. Only explicitly requested settings are considered.
    2. Already-set values are skipped where the Canvas state
       can be reliably compared.
    3. Not-applicable settings are skipped.
    4. Attempt to Record is only sent when multiple attempts
       will exist after the requested update.
    5. Show Correct Answers is only sent when responses will
       be available after the requested update.
    6. Exam passwords are only applied to assessments
       classified as Exam.

    Returns:
        dict of Canvas quiz fields.

    An empty dict means no write is required.
    """

    payload = {}

    # ========================================================
    # ATTEMPT LIMIT
    # ========================================================

    requested_limit = settings[
        "attempt_limit"
    ]

    if requested_limit != "Don't Change":

        requested_limit_value = (
            canvas_attempt_limit(
                requested_limit
            )
        )

        current_limit_value = (
            get_allowed_attempts(
                quiz
            )
        )

        if (
            current_limit_value
            != requested_limit_value
        ):

            payload[
                "allowed_attempts"
            ] = requested_limit_value

    # ========================================================
    # ATTEMPT TO RECORD
    # ========================================================

    requested_record = settings[
        "attempt_record"
    ]

    if (
        requested_record
        != "Don't Change"
        and resulting_multiple_attempts(
            quiz,
            requested_limit
        )
    ):

        requested_policy = (
            canvas_scoring_policy(
                requested_record
            )
        )

        current_policy = quiz.get(
            "scoring_policy"
        )

        if (
            requested_policy is not None
            and current_policy
            != requested_policy
        ):

            payload[
                "scoring_policy"
            ] = requested_policy

    # ========================================================
    # SHUFFLE ANSWERS
    #
    # UNCHANGED FOR THIS TEST.
    # ========================================================

    requested_shuffle = settings[
        "shuffle_answers"
    ]

    if (
        requested_shuffle
        != "Don't Change"
    ):

        requested_shuffle_value = (
            canvas_enable_disable(
                requested_shuffle
            )
        )

        current_shuffle_value = quiz.get(
            "shuffle_answers"
        )

        if (
            requested_shuffle_value
            is not None
            and current_shuffle_value
            != requested_shuffle_value
        ):

            payload[
                "shuffle_answers"
            ] = requested_shuffle_value

    # ========================================================
    # ONE QUESTION AT A TIME
    # ========================================================

    requested_one_question = settings[
        "one_question_at_a_time"
    ]

    if (
        requested_one_question
        != "Don't Change"
    ):

        requested_one_question_value = (
            canvas_enable_disable(
                requested_one_question
            )
        )

        current_one_question_value = (
            quiz.get(
                "one_question_at_a_time"
            )
        )

        if (
            requested_one_question_value
            is not None
            and current_one_question_value
            != requested_one_question_value
        ):

            payload[
                "one_question_at_a_time"
            ] = requested_one_question_value

    # ========================================================
    # SHOW STUDENT QUIZ RESPONSES
    # ========================================================

    requested_responses = settings[
        "show_responses"
    ]

    if (
        requested_responses
        == "Do Not Allow"
    ):

        if responses_are_shown(
            quiz
        ):

            payload[
                "hide_results"
            ] = "always"

    elif (
        requested_responses
        == "Allow"
    ):

        if not responses_are_shown(
            quiz
        ):

            payload[
                "hide_results"
            ] = ""

    # ========================================================
    # SHOW CORRECT ANSWERS
    #
    # EXPLICIT THREE-WAY MAPPING:
    #
    # Don't Change
    #     -> send no show_correct_answers field
    #
    # Allow
    #     -> show_correct_answers = True
    #
    # Do Not Allow
    #     -> show_correct_answers = False
    #
    # This intentionally matches the field used by the known
    # working independent Canvas script.
    #
    # Only applicable when student responses will be shown.
    # ========================================================

    requested_correct_answers = settings[
        "show_correct_answers"
    ]

    responses_will_be_shown = (
        resulting_responses_are_shown(
            quiz,
            requested_responses
        )
    )

    if responses_will_be_shown:

        if (
            requested_correct_answers
            == "Allow"
        ):

            payload[
                "show_correct_answers"
            ] = True

        elif (
            requested_correct_answers
            == "Do Not Allow"
        ):

            payload[
                "show_correct_answers"
            ] = False

        # If the value is "Don't Change", intentionally
        # add nothing to the payload.

    # ========================================================
    # EXAM PASSWORD
    # ========================================================

    if classification == "Exam":

        password_action = settings[
            "password_action"
        ]

        if (
            password_action
            == "Set / Replace Password"
        ):

            password_value = (
                settings.get(
                    "exam_password",
                    ""
                ).strip()
            )

            if password_value:

                payload[
                    "access_code"
                ] = password_value

        elif (
            password_action
            == "Remove Password"
        ):

            if quiz.get(
                "has_access_code"
            ):

                payload[
                    "access_code"
                ] = ""

    return payload


# ============================================================
# EXECUTE SINGLE COURSE CHANGES
# ============================================================


def execute_single_course_changes(
    canvas,
    course_id,
    settings
):
    """
    Execute requested Classic Quiz changes for one Canvas course.

    THIS FUNCTION CAN MODIFY CANVAS.

    It must only be called after the administrator has:
        1. Generated Preview
        2. Reviewed the proposed changes
        3. Explicitly confirmed execution

    Each assessment is processed independently.

    A failure on one assessment does not stop the remaining
    assessments from being processed.

    Returns:
        dict containing:
            success
            message
            results
            counts
    """

    # ========================================================
    # LOAD CURRENT QUIZZES AGAIN
    # ========================================================

    quiz_result = canvas.get_classic_quizzes(
        course_id
    )

    if not quiz_result[
        "success"
    ]:

        return {
            "success": False,

            "message": (
                "Unable to reload the course assessments "
                "before applying changes. "
                + quiz_result["message"]
            ),

            "results": [],

            "counts": {
                "targeted": 0,
                "updated": 0,
                "skipped": 0,
                "failed": 0
            }
        }

    quizzes = quiz_result[
        "data"
    ]

    assessment_type = settings[
        "assessment_type"
    ]

    results = []

    # ========================================================
    # PROCESS EACH TARGETED ASSESSMENT
    # ========================================================

    for quiz in quizzes:

        classification = (
            classify_assessment(
                quiz.get("title")
            )
        )

        if not assessment_matches_target(
            classification,
            assessment_type
        ):

            continue

        quiz_id = quiz.get(
            "id"
        )

        quiz_title = (
            quiz.get("title")
            or "Untitled Assessment"
        )

        # ----------------------------------------------------
        # BUILD MINIMAL UPDATE PAYLOAD
        # ----------------------------------------------------

        payload = (
            build_quiz_update_payload(
                quiz=quiz,
                classification=classification,
                settings=settings
            )
        )

        # ----------------------------------------------------
        # NOTHING NEEDS TO CHANGE
        # ----------------------------------------------------

        if not payload:

            results.append(
                {
                    "id":
                        quiz_id,

                    "title":
                        quiz_title,

                    "classification":
                        classification,

                    "status":
                        "Skipped",

                    "message":
                        (
                            "No applicable changes "
                            "were required."
                        ),

                    "updated_fields":
                        []
                }
            )

            continue

        # ----------------------------------------------------
        # SEND CONTROLLED UPDATE
        # ----------------------------------------------------

        update_result = (
            canvas.update_classic_quiz(
                course_id=course_id,
                quiz_id=quiz_id,
                quiz_settings=payload
            )
        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        if update_result[
            "success"
        ]:

            results.append(
                {
                    "id":
                        quiz_id,

                    "title":
                        quiz_title,

                    "classification":
                        classification,

                    "status":
                        "Updated",

                    "message":
                        (
                            "Assessment updated "
                            "successfully."
                        ),

                    "updated_fields":
                        list(
                            payload.keys()
                        )
                }
            )

        # ----------------------------------------------------
        # FAILURE
        # ----------------------------------------------------

        else:

            results.append(
                {
                    "id":
                        quiz_id,

                    "title":
                        quiz_title,

                    "classification":
                        classification,

                    "status":
                        "Failed",

                    "message":
                        update_result[
                            "message"
                        ],

                    "updated_fields":
                        list(
                            payload.keys()
                        )
                }
            )

    # ========================================================
    # RESULT COUNTS
    # ========================================================

    updated_count = sum(
        1
        for item in results
        if item["status"]
        == "Updated"
    )

    skipped_count = sum(
        1
        for item in results
        if item["status"]
        == "Skipped"
    )

    failed_count = sum(
        1
        for item in results
        if item["status"]
        == "Failed"
    )

    targeted_count = len(
        results
    )

    # ========================================================
    # OVERALL RESULT
    # ========================================================

    overall_success = (
        failed_count == 0
    )

    if failed_count == 0:

        message = (
            "Canvas processing completed successfully."
        )

    else:

        message = (
            "Canvas processing completed with "
            f"{failed_count} failed assessment(s)."
        )

    return {
        "success":
            overall_success,

        "message":
            message,

        "results":
            results,

        "counts": {

            "targeted":
                targeted_count,

            "updated":
                updated_count,

            "skipped":
                skipped_count,

            "failed":
                failed_count
        }
    }