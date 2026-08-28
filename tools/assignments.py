# ============================================================
# ACCELERATE CANVAS ADMINISTRATION SUITE
# Assignment Management Tools
#
# Contains assignment-specific business logic.
#
# CURRENT VERSION:
# - Single-course Assignment Management
# - Strict Canvas Assignment eligibility filtering
# - Assignment Attempt Limit Preview
# - Controlled assignment update payload construction
# - Controlled single-course execution engine
#
# IMPORTANT:
# This engine manages TRUE Canvas assignments only.
#
# It intentionally ignores:
# - Classic Quizzes / Exams
# - Discussion assignments
# - On-paper assignments
# - No-submission assignments
#
# Nothing in this file executes automatically.
# Canvas is modified only when
# execute_single_course_assignment_changes()
# is explicitly called by the application.
# ============================================================


# ============================================================
# ELIGIBLE ASSIGNMENT SUBMISSION TYPES
#
# Assignment Management is intentionally restrictive.
#
# An item must contain at least one of these submission types
# before it can be managed by this engine.
# ============================================================

ELIGIBLE_ASSIGNMENT_SUBMISSION_TYPES = {
    "online_upload",
    "online_text_entry",
    "online_url",
    "media_recording",
    "student_annotation"
}


# ============================================================
# ASSIGNMENT ELIGIBILITY
# ============================================================


def get_assignment_eligibility(assignment):
    """
    Determine whether an item returned by the Canvas
    Assignments API is a true assignment that should be
    managed by Assignment Management.

    Current rules:

    INCLUDE:
        True Canvas assignments using at least one supported
        online assignment submission type.

    EXCLUDE:
        Classic Quizzes / Exams
        Discussion assignments
        On-paper-only assignments
        No-submission assignments
        Any unsupported assignment-like Canvas object

    Returns:
        dict containing:
            eligible
            reason
    """

    submission_types = (
        assignment.get("submission_types")
        or []
    )

    submission_type_set = set(
        submission_types
    )

    # --------------------------------------------------------
    # EXCLUDE CLASSIC QUIZZES / EXAMS
    #
    # Classic Quizzes are also represented through the Canvas
    # Assignments API and normally use online_quiz.
    #
    # They belong exclusively to Quiz & Exam Management.
    # --------------------------------------------------------

    if "online_quiz" in submission_type_set:

        return {
            "eligible": False,
            "reason": "Quiz or exam."
        }


    # --------------------------------------------------------
    # EXCLUDE DISCUSSION ASSIGNMENTS
    #
    # Graded discussions may also appear through the Canvas
    # Assignments API.
    #
    # Discussion attempt limits are not managed by this tool.
    #
    # We check both the submission type and the associated
    # discussion_topic relationship for defense in depth.
    # --------------------------------------------------------

    if "discussion_topic" in submission_type_set:

        return {
            "eligible": False,
            "reason": "Discussion."
        }

    if assignment.get("discussion_topic"):

        return {
            "eligible": False,
            "reason": "Discussion."
        }


    # --------------------------------------------------------
    # EXCLUDE ITEMS WITHOUT SUBMISSION TYPES
    # --------------------------------------------------------

    if not submission_type_set:

        return {
            "eligible": False,
            "reason": (
                "No eligible assignment submission type."
            )
        }


    # --------------------------------------------------------
    # REQUIRE A TRUE ONLINE ASSIGNMENT SUBMISSION TYPE
    #
    # This is the key protection.
    #
    # Instead of assuming that anything not identified as a
    # quiz is an assignment, the item must positively match
    # at least one supported Canvas assignment submission type.
    #
    # This prevents discussions and other Canvas objects from
    # accidentally entering the Assignment Management engine.
    # --------------------------------------------------------

    eligible_types = (
        submission_type_set
        & ELIGIBLE_ASSIGNMENT_SUBMISSION_TYPES
    )

    if not eligible_types:

        return {
            "eligible": False,
            "reason": (
                "Not an eligible online Canvas assignment."
            )
        }


    # --------------------------------------------------------
    # ELIGIBLE TRUE CANVAS ASSIGNMENT
    # --------------------------------------------------------

    return {
        "eligible": True,
        "reason": None
    }


def assignment_is_eligible(assignment):
    """
    Convenience helper returning only True or False.

    This same eligibility check is used by both Preview and
    execution so an excluded Canvas object cannot accidentally
    receive an Assignment Management update.
    """

    result = get_assignment_eligibility(
        assignment
    )

    return result["eligible"]


# ============================================================
# CURRENT CANVAS VALUE HELPERS
# ============================================================


def get_allowed_attempts(assignment):
    """
    Return the raw Canvas allowed_attempts value.

    Canvas commonly represents Unlimited attempts as -1.
    """

    return assignment.get(
        "allowed_attempts"
    )


def current_attempt_limit(assignment):
    """
    Convert Canvas allowed_attempts into a readable value.

    Canvas:
        -1   -> Unlimited
        1    -> 1
        2    -> 2
        etc.
    """

    value = get_allowed_attempts(
        assignment
    )

    if value == -1:

        return "Unlimited"

    if value is None:

        return "Unknown"

    return str(value)


# ============================================================
# REQUESTED VALUE HELPERS
# ============================================================


def requested_attempt_limit(setting):
    """
    Convert the UI selection into a readable Preview value.
    """

    if setting == "Don't Change":

        return "No Change"

    return setting


def canvas_attempt_limit(setting):
    """
    Convert the UI Attempt Limit selection into the Canvas
    API value.

    UI:
        Unlimited -> -1
        "1"       -> 1
        "2"       -> 2
        ...
        "10"      -> 10
    """

    if setting == "Unlimited":

        return -1

    return int(setting)


# ============================================================
# BUILD ASSIGNMENT CHANGE ROWS
# ============================================================


def build_assignment_change_rows(
    assignment,
    settings
):
    """
    Build the human-readable Preview rows for one assignment.

    Returns:
        list of setting comparison dictionaries.
    """

    rows = []

    requested_limit = settings.get(
        "attempt_limit",
        "Don't Change"
    )


    # --------------------------------------------------------
    # ATTEMPT LIMIT
    # --------------------------------------------------------

    if requested_limit != "Don't Change":

        current_value = (
            current_attempt_limit(
                assignment
            )
        )

        requested_value = (
            requested_attempt_limit(
                requested_limit
            )
        )

        if current_value == requested_value:

            status = "Already Set"

        else:

            status = "Would Change"

        rows.append(
            {
                "setting":
                    "Attempt Limit",

                "current":
                    current_value,

                "requested":
                    requested_value,

                "status":
                    status,

                "note":
                    None
            }
        )

    return rows


# ============================================================
# BUILD SINGLE COURSE ASSIGNMENT PREVIEW
# ============================================================


def build_single_course_assignment_preview(
    canvas,
    course_id,
    settings
):
    """
    Build a READ-ONLY Assignment Management Preview for one
    Canvas course.

    Only true eligible Canvas assignments are included in the
    Assignment Management Preview.

    Quizzes, exams, discussions, on-paper assignments,
    no-submission items, and unsupported Canvas objects are
    silently ignored by the management engine.

    No Canvas modifications are performed.

    Returns:
        dict containing:
            success
            message
            course
            assignments
            excluded_assignments
            counts
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

            "assignments": [],

            "excluded_assignments": [],

            "counts": {
                "total_found": 0,
                "eligible": 0,
                "would_change": 0,
                "already_set": 0,
                "excluded": 0
            }
        }

    course = course_result["data"]


    # ========================================================
    # GET ASSIGNMENTS
    # ========================================================

    assignment_result = (
        canvas.get_assignments(
            course_id
        )
    )

    if not assignment_result[
        "success"
    ]:

        return {
            "success": False,

            "message": (
                "The course was found, but its assignments "
                "could not be loaded. "
                + assignment_result["message"]
            ),

            "course": course,

            "assignments": [],

            "excluded_assignments": [],

            "counts": {
                "total_found": 0,
                "eligible": 0,
                "would_change": 0,
                "already_set": 0,
                "excluded": 0
            }
        }

    assignments = assignment_result[
        "data"
    ]

    targeted = []

    excluded_count = 0


    # ========================================================
    # CLASSIFY ASSIGNMENTS
    # ========================================================

    for assignment in assignments:

        eligibility = (
            get_assignment_eligibility(
                assignment
            )
        )


        # ----------------------------------------------------
        # SILENTLY IGNORE NON-ASSIGNMENT OBJECTS
        #
        # These are intentionally NOT added to a visible
        # excluded-items list.
        # ----------------------------------------------------

        if not eligibility[
            "eligible"
        ]:

            excluded_count += 1

            continue


        # ----------------------------------------------------
        # TRUE ELIGIBLE ASSIGNMENT
        # ----------------------------------------------------

        assignment_id = assignment.get(
            "id"
        )

        assignment_name = (
            assignment.get("name")
            or "Untitled Assignment"
        )

        rows = (
            build_assignment_change_rows(
                assignment=assignment,
                settings=settings
            )
        )

        current_limit = (
            current_attempt_limit(
                assignment
            )
        )

        requested_limit = (
            settings.get(
                "attempt_limit",
                "Don't Change"
            )
        )

        if (
            requested_limit
            == "Don't Change"
        ):

            overall_status = (
                "No Change Requested"
            )

        elif (
            current_limit
            == requested_limit
        ):

            overall_status = (
                "Already Set"
            )

        else:

            overall_status = (
                "Would Change"
            )

        targeted.append(
            {
                "id":
                    assignment_id,

                "name":
                    assignment_name,

                "submission_types":
                    assignment.get(
                        "submission_types",
                        []
                    ),

                "current_attempt_limit":
                    current_limit,

                "requested_attempt_limit":
                    requested_attempt_limit(
                        requested_limit
                    ),

                "status":
                    overall_status,

                "changes":
                    rows
            }
        )


    # ========================================================
    # COUNTS
    # ========================================================

    would_change_count = sum(
        1
        for item in targeted
        if item["status"]
        == "Would Change"
    )

    already_set_count = sum(
        1
        for item in targeted
        if item["status"]
        == "Already Set"
    )


    # ========================================================
    # RETURN PREVIEW
    #
    # IMPORTANT:
    #
    # total_found now represents the number of true assignments
    # managed by this engine, NOT every raw object returned by
    # the Canvas Assignments API.
    #
    # excluded_assignments intentionally remains empty so the
    # UI does not display quizzes, exams, discussions, etc.
    # ========================================================

    return {
        "success": True,

        "message":
            "Assignment Preview generated successfully.",

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

        "assignments":
            targeted,

        "excluded_assignments":
            [],

        "counts": {

            "total_found":
                len(targeted),

            "eligible":
                len(targeted),

            "would_change":
                would_change_count,

            "already_set":
                already_set_count,

            "excluded":
                excluded_count
        }
    }


# ============================================================
# BUILD ASSIGNMENT UPDATE PAYLOAD
# ============================================================


def build_assignment_update_payload(
    assignment,
    settings
):
    """
    Build the minimal Canvas update payload for one assignment.

    SAFETY RULES:

    1. Only true eligible Canvas assignments can be updated.
    2. Quizzes and exams cannot be updated by this engine.
    3. Discussions cannot be updated by this engine.
    4. Unsupported assignment-like objects cannot be updated.
    5. "Don't Change" sends no update.
    6. Assignments already at the requested value are skipped.
    7. Only allowed_attempts is included in the payload.

    Returns:
        dict of Canvas assignment fields.

    An empty dict means no write is required.
    """

    payload = {}


    # ========================================================
    # VERIFY STRICT ELIGIBILITY
    #
    # This check is intentionally repeated during execution.
    #
    # Preview eligibility alone is NEVER trusted as permission
    # to write to Canvas.
    # ========================================================

    if not assignment_is_eligible(
        assignment
    ):

        return payload


    # ========================================================
    # ATTEMPT LIMIT
    # ========================================================

    requested_limit = settings.get(
        "attempt_limit",
        "Don't Change"
    )

    if requested_limit == "Don't Change":

        return payload

    requested_limit_value = (
        canvas_attempt_limit(
            requested_limit
        )
    )

    current_limit_value = (
        get_allowed_attempts(
            assignment
        )
    )

    if (
        current_limit_value
        != requested_limit_value
    ):

        payload[
            "allowed_attempts"
        ] = requested_limit_value

    return payload


# ============================================================
# EXECUTE SINGLE COURSE ASSIGNMENT CHANGES
# ============================================================


def execute_single_course_assignment_changes(
    canvas,
    course_id,
    settings
):
    """
    Execute requested Assignment Management changes for one
    Canvas course.

    THIS FUNCTION CAN MODIFY CANVAS.

    Only true eligible Canvas assignments can reach the
    update call.

    Quizzes, exams, discussions, on-paper assignments,
    no-submission items, and unsupported Canvas objects are
    silently ignored.

    It must only be called after the administrator has:

        1. Generated Preview
        2. Reviewed the proposed changes
        3. Explicitly confirmed execution

    Each eligible assignment is processed independently.

    A failure on one assignment does not stop remaining
    assignments from being processed.

    Returns:
        dict containing:
            success
            message
            results
            counts
    """


    # ========================================================
    # RELOAD CURRENT ASSIGNMENTS
    #
    # We intentionally re-read Canvas immediately before
    # execution rather than trusting stale Preview data.
    # ========================================================

    assignment_result = (
        canvas.get_assignments(
            course_id
        )
    )

    if not assignment_result[
        "success"
    ]:

        return {
            "success": False,

            "message": (
                "Unable to reload the course assignments "
                "before applying changes. "
                + assignment_result[
                    "message"
                ]
            ),

            "results": [],

            "counts": {
                "found": 0,
                "eligible": 0,
                "updated": 0,
                "skipped": 0,
                "excluded": 0,
                "failed": 0
            }
        }

    assignments = assignment_result[
        "data"
    ]

    results = []

    eligible_count = 0
    excluded_count = 0


    # ========================================================
    # PROCESS ASSIGNMENTS
    # ========================================================

    for assignment in assignments:

        eligibility = (
            get_assignment_eligibility(
                assignment
            )
        )


        # ----------------------------------------------------
        # SILENTLY IGNORE NON-ASSIGNMENT OBJECTS
        # ----------------------------------------------------

        if not eligibility[
            "eligible"
        ]:

            excluded_count += 1

            continue


        # ----------------------------------------------------
        # TRUE ELIGIBLE ASSIGNMENT
        # ----------------------------------------------------

        eligible_count += 1

        assignment_id = assignment.get(
            "id"
        )

        assignment_name = (
            assignment.get("name")
            or "Untitled Assignment"
        )


        # ----------------------------------------------------
        # BUILD MINIMAL UPDATE PAYLOAD
        #
        # build_assignment_update_payload() performs its own
        # eligibility check again for additional protection.
        # ----------------------------------------------------

        payload = (
            build_assignment_update_payload(
                assignment=assignment,
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
                        assignment_id,

                    "name":
                        assignment_name,

                    "status":
                        "Skipped",

                    "message":
                        (
                            "Assignment already matches "
                            "the requested setting, or no "
                            "change was requested."
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
            canvas.update_assignment(
                course_id=course_id,
                assignment_id=assignment_id,
                assignment_settings=payload
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
                        assignment_id,

                    "name":
                        assignment_name,

                    "status":
                        "Updated",

                    "message":
                        (
                            "Assignment updated "
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
                        assignment_id,

                    "name":
                        assignment_name,

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


    # ========================================================
    # OVERALL RESULT
    # ========================================================

    overall_success = (
        failed_count == 0
    )

    if failed_count == 0:

        message = (
            "Assignment processing completed successfully."
        )

    else:

        message = (
            "Assignment processing completed with "
            f"{failed_count} failed assignment(s)."
        )

    return {
        "success":
            overall_success,

        "message":
            message,

        "results":
            results,

        "counts": {

            # "found" now means true assignments managed
            # by this engine rather than raw Canvas API items.

            "found":
                eligible_count,

            "eligible":
                eligible_count,

            "updated":
                updated_count,

            "skipped":
                skipped_count,

            "excluded":
                excluded_count,

            "failed":
                failed_count
        }
    }