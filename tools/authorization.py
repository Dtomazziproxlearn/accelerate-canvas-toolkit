# ============================================================
# ACCELERATE CANVAS ADMINISTRATION SUITE
# Course Authorization Service
#
# PURPOSE:
# Verify that a selected Canvas course appears to be an
# eligible Accelerate Education course before management tools
# are unlocked.
#
# CUSTOMER-FACING BEHAVIOR:
# - Successful verification unlocks the selected course.
# - Failed verification keeps controls locked.
# - The customer-facing message does NOT reveal the internal
#   verification rules.
#
# INTERNAL VERIFICATION RULES:
# 1. The first Canvas module must be named "Resources".
# 2. At least two of the following three title markers must be
#    found among the items in that first module:
#
#       - Getting Started
#       - Online Learning
#       - Teacher's Guide
#
# IMPORTANT:
# This is an application-level eligibility check. It is not a
# cryptographic proof of course ownership.
# ============================================================


# ============================================================
# VERIFICATION CONSTANTS
# ============================================================

REQUIRED_FIRST_MODULE_NAME = "resources"

COURSE_MARKERS = {
    "getting_started": (
        "getting started",
    ),
    "online_learning": (
        "online learning",
    ),
    "teachers_guide": (
        "teacher's guide",
        "teachers guide",
        "teacher guide",
    ),
}

MINIMUM_REQUIRED_MARKERS = 2


# ============================================================
# NORMALIZATION HELPERS
# ============================================================


def normalize_text(value):
    """
    Normalize a Canvas-provided string for comparison.

    Returns:
        Lowercase, trimmed text with repeated whitespace
        collapsed.
    """

    if value is None:
        return ""

    normalized = str(value).strip().casefold()

    return " ".join(
        normalized.split()
    )


# ============================================================
# MODULE SORTING
# ============================================================


def sort_modules_by_position(modules):
    """
    Return modules in Canvas course order.

    Modules with a valid integer position are placed first.
    Modules without a valid position are placed afterward.
    """

    def sort_key(module):

        position = module.get(
            "position"
        )

        if isinstance(
            position,
            int
        ):

            return (
                0,
                position,
                module.get("id") or 0
            )

        return (
            1,
            999999,
            module.get("id") or 0
        )

    return sorted(
        modules,
        key=sort_key
    )


# ============================================================
# MARKER MATCHING
# ============================================================


def find_course_markers(module_items):
    """
    Search first-module item titles for the internal Accelerate
    course markers.

    Returns:
        dict where each marker key maps to a Boolean.
    """

    marker_results = {
        marker_name: False
        for marker_name in COURSE_MARKERS
    }

    for item in module_items:

        item_title = normalize_text(
            item.get("title")
        )

        if not item_title:

            continue

        for marker_name, phrases in COURSE_MARKERS.items():

            if marker_results[
                marker_name
            ]:

                continue

            if any(
                phrase in item_title
                for phrase in phrases
            ):

                marker_results[
                    marker_name
                ] = True

    return marker_results


# ============================================================
# STANDARD RESULT BUILDERS
# ============================================================


def build_failed_result(
    reason,
    diagnostics=None,
    technical_message=None
):
    """
    Build a standard failed verification response.

    The public message intentionally does not disclose the
    internal verification criteria.
    """

    return {
        "success": True,
        "verified": False,
        "message": (
            "The selected course could not be verified as an "
            "eligible Accelerate Education course. No changes "
            "can be previewed or applied. Please enter another "
            "Course ID or contact Accelerate Education Support "
            "for assistance."
        ),
        "reason": reason,
        "diagnostics": diagnostics or {},
        "technical_message": technical_message,
        "course": None,
    }


def build_error_result(
    message,
    reason,
    diagnostics=None
):
    """
    Build a verification result when Canvas data could not be
    inspected successfully.

    success=False means the verification process itself failed,
    rather than the selected course simply being ineligible.
    """

    return {
        "success": False,
        "verified": False,
        "message": message,
        "reason": reason,
        "diagnostics": diagnostics or {},
        "technical_message": message,
        "course": None,
    }


# ============================================================
# VERIFY ACCELERATE COURSE
# ============================================================


def verify_accelerate_course(
    canvas,
    course_id
):
    """
    Verify whether one Canvas course appears eligible for use
    with the Accelerate Canvas Administration Suite.

    READ ONLY.

    Verification sequence:

    1. Retrieve the course.
    2. Retrieve all modules.
    3. Sort modules by Canvas position.
    4. Require the first module name to equal "Resources".
    5. Retrieve items from the first module.
    6. Require at least two of the three internal title-marker
       categories.

    Returns:
        {
            "success": bool,
            "verified": bool,
            "message": str,
            "reason": str,
            "diagnostics": dict,
            "technical_message": str | None,
            "course": dict | None
        }

    Customer-facing UI should display only:
        verified
        message
        course

    Internal support logging may use:
        reason
        diagnostics
        technical_message
    """

    normalized_course_id = str(
        course_id
        or ""
    ).strip()

    if not normalized_course_id:

        return build_error_result(
            message=(
                "Enter a Course ID before verifying the course."
            ),
            reason="missing_course_id"
        )

    course_result = canvas.get_course(
        normalized_course_id
    )

    if not course_result.get(
        "success"
    ):

        return build_error_result(
            message=(
                "The selected course could not be loaded from "
                "Canvas. Check the Course ID and your Canvas "
                "permissions, then try again."
            ),
            reason="course_load_failed",
            diagnostics={
                "course_id":
                    normalized_course_id
            }
        )

    course = (
        course_result.get("data")
        or {}
    )

    modules_result = canvas.get_modules(
        normalized_course_id
    )

    if not modules_result.get(
        "success"
    ):

        return build_error_result(
            message=(
                "The course was found, but its modules could "
                "not be inspected. Please try again or contact "
                "Accelerate Education Support."
            ),
            reason="module_load_failed",
            diagnostics={
                "course_id":
                    normalized_course_id,

                "canvas_message":
                    modules_result.get(
                        "message"
                    )
            }
        )

    modules = (
        modules_result.get("data")
        or []
    )

    sorted_modules = sort_modules_by_position(
        modules
    )

    if not sorted_modules:

        return build_failed_result(
            reason="no_modules_found",
            diagnostics={
                "course_id":
                    normalized_course_id,

                "module_count":
                    0
            }
        )

    first_module = sorted_modules[0]

    first_module_id = first_module.get(
        "id"
    )

    first_module_name = normalize_text(
        first_module.get("name")
    )

    if (
        first_module_name
        != REQUIRED_FIRST_MODULE_NAME
    ):

        return build_failed_result(
            reason="first_module_not_resources",
            diagnostics={
                "course_id":
                    normalized_course_id,

                "first_module_id":
                    first_module_id,

                "first_module_name":
                    first_module.get("name"),

                "normalized_first_module_name":
                    first_module_name,

                "module_count":
                    len(sorted_modules)
            }
        )

    items_result = canvas.get_module_items(
        course_id=normalized_course_id,
        module_id=first_module_id
    )

    if not items_result.get(
        "success"
    ):

        return build_error_result(
            message=(
                "The course was found, but its eligibility "
                "could not be verified. Please try again or "
                "contact Accelerate Education Support."
            ),
            reason="resources_items_load_failed",
            diagnostics={
                "course_id":
                    normalized_course_id,

                "first_module_id":
                    first_module_id,

                "canvas_message":
                    items_result.get(
                        "message"
                    )
            }
        )

    module_items = (
        items_result.get("data")
        or []
    )

    marker_results = find_course_markers(
        module_items
    )

    markers_found = sum(
        1
        for found in marker_results.values()
        if found
    )

    if (
        markers_found
        < MINIMUM_REQUIRED_MARKERS
    ):

        return build_failed_result(
            reason="insufficient_course_markers",
            diagnostics={
                "course_id":
                    normalized_course_id,

                "first_module_id":
                    first_module_id,

                "first_module_name":
                    first_module.get("name"),

                "module_item_count":
                    len(module_items),

                "markers_found":
                    markers_found,

                "marker_results":
                    marker_results
            }
        )

    return {
        "success": True,
        "verified": True,
        "message": (
            "Accelerate Education course verified. This course "
            "is eligible for administration through the "
            "Accelerate Canvas Administration Suite."
        ),
        "reason": "verified",
        "diagnostics": {
            "course_id":
                normalized_course_id,

            "first_module_id":
                first_module_id,

            "first_module_name":
                first_module.get("name"),

            "module_item_count":
                len(module_items),

            "markers_found":
                markers_found,

            "marker_results":
                marker_results
        },
        "technical_message": None,
        "course": {
            "id":
                course.get("id"),

            "name":
                (
                    course.get("name")
                    or course.get("course_code")
                    or f"Course {normalized_course_id}"
                ),

            "course_code":
                course.get("course_code")
        }
    }
