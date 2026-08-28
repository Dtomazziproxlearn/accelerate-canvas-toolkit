# ============================================================
# ACCELERATE CANVAS ADMINISTRATION SUITE
# Course Management Tools
#
# CURRENT VERSION:
# - Single-course Course Management foundation
# - Module Gating v2
# - Enable and Disable support
# - Read-only gating Preview
# - Controlled gating execution
#
# MODULE GATING V2:
#
# Supported selections:
# - Don't Change
# - Enable
# - Disable
#
# Enabling Module Gating performs three operations:
#
# 1. Enable sequential progress on every module.
#
# 2. Chain modules in Canvas position order:
#
#       Module 1 -> No prerequisite
#       Module 2 -> Requires Module 1
#       Module 3 -> Requires Module 2
#       etc.
#
# 3. Apply completion requirements to supported module items:
#
#       Page          -> must_view
#       File          -> must_view
#       ExternalUrl   -> must_view
#       ExternalTool  -> must_view
#       Assignment    -> must_submit
#       Discussion    -> must_contribute
#       Quiz          -> must_submit
#
# Disabling Module Gating performs three operations:
#
# 1. Disable sequential progress on every module.
#
# 2. Remove every module prerequisite.
#
# 3. Remove every module-item completion requirement.
#
# IMPORTANT:
#
# Preview functions in this file are READ ONLY.
#
# Canvas is modified only when
# execute_single_course_module_gating()
# is explicitly called by the application after administrator
# confirmation.
# ============================================================


# ============================================================
# MODULE ITEM COMPLETION REQUIREMENTS
# ============================================================

MODULE_ITEM_REQUIREMENTS = {

    "Page":
        "must_view",

    "File":
        "must_view",

    "ExternalUrl":
        "must_view",

    "ExternalTool":
        "must_view",

    "Assignment":
        "must_submit",

    "Discussion":
        "must_contribute",

    "Quiz":
        "must_submit"
}


# ============================================================
# READABLE REQUIREMENT LABELS
# ============================================================

REQUIREMENT_LABELS = {

    "must_view":
        "Must View",

    "must_submit":
        "Must Submit",

    "must_contribute":
        "Must Contribute"
}


# ============================================================
# MODULE SORTING
# ============================================================


def sort_modules_by_position(modules):
    """
    Return modules sorted according to Canvas module position.

    Canvas normally returns modules in course order, but the
    gating engine explicitly sorts by the position field rather
    than relying on API response order.

    Modules without a valid position are placed after modules
    with valid positions.
    """

    def module_sort_key(module):

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
        key=module_sort_key
    )


# ============================================================
# MODULE ITEM REQUIREMENT HELPERS
# ============================================================


def get_module_item_requirement(
    item
):
    """
    Determine the completion requirement that should be applied
    to one Canvas module item.

    Returns:
        requirement type string

        Examples:
            must_view
            must_submit
            must_contribute

        Returns None when the item type is not managed by
        Module Gating v1.
    """

    item_type = (
        item.get("type")
        or ""
    )

    return MODULE_ITEM_REQUIREMENTS.get(
        item_type
    )


def get_requirement_label(
    requirement_type
):
    """
    Convert a Canvas requirement type into a readable label.
    """

    return REQUIREMENT_LABELS.get(
        requirement_type,
        requirement_type
    )


# ============================================================
# CURRENT REQUIREMENT HELPER
# ============================================================


def get_current_completion_requirement(
    item
):
    """
    Retrieve the current completion requirement type from a
    Canvas module item.

    Canvas may return:

        completion_requirement = {
            "type": "must_view"
        }

    If no completion requirement exists, returns None.
    """

    completion_requirement = (
        item.get(
            "completion_requirement"
        )
        or {}
    )

    return completion_requirement.get(
        "type"
    )


# ============================================================
# MODULE PREREQUISITE HELPERS
# ============================================================


def get_current_prerequisite_ids(
    module
):
    """
    Retrieve current prerequisite module IDs from a Canvas
    module object.

    Canvas may return prerequisite information in different
    response structures depending on context.

    This helper safely normalizes the known forms into a list
    of module IDs.
    """

    prerequisite_ids = []


    # --------------------------------------------------------
    # DIRECT ID LIST
    # --------------------------------------------------------

    direct_ids = module.get(
        "prerequisite_module_ids"
    )

    if isinstance(
        direct_ids,
        list
    ):

        for prerequisite_id in direct_ids:

            if prerequisite_id is not None:

                prerequisite_ids.append(
                    prerequisite_id
                )


    # --------------------------------------------------------
    # PREREQUISITE MODULE OBJECTS
    # --------------------------------------------------------

    prerequisite_modules = module.get(
        "prerequisite_modules"
    )

    if isinstance(
        prerequisite_modules,
        list
    ):

        for prerequisite in prerequisite_modules:

            if not isinstance(
                prerequisite,
                dict
            ):

                continue

            prerequisite_id = (
                prerequisite.get("id")
            )

            if (
                prerequisite_id is not None
                and prerequisite_id
                not in prerequisite_ids
            ):

                prerequisite_ids.append(
                    prerequisite_id
                )

    return prerequisite_ids


# ============================================================
# MODULE GATING STATUS
# ============================================================


def module_gating_status(
    module,
    expected_prerequisite_id
):
    """
    Determine whether one module already matches the requested
    Module Gating v1 configuration.

    A module is considered configured when:

    1. Sequential progress is enabled.

    2. For the first module:
       No prerequisite is required by this engine.

    3. For every later module:
       The immediately preceding module is already present as
       its prerequisite.

    IMPORTANT:
    This helper does not determine module-item completion
    requirements. Those are evaluated separately.
    """

    sequential_enabled = bool(
        module.get(
            "require_sequential_progress",
            False
        )
    )

    current_prerequisites = (
        get_current_prerequisite_ids(
            module
        )
    )


    # --------------------------------------------------------
    # FIRST MODULE
    # --------------------------------------------------------

    if expected_prerequisite_id is None:

        prerequisite_matches = (
            len(
                current_prerequisites
            )
            == 0
        )


    # --------------------------------------------------------
    # LATER MODULE
    # --------------------------------------------------------

    else:

        prerequisite_matches = (
            expected_prerequisite_id
            in current_prerequisites
        )

    return {
        "sequential_enabled":
            sequential_enabled,

        "prerequisite_matches":
            prerequisite_matches,

        "module_matches":
            (
                sequential_enabled
                and prerequisite_matches
            ),

        "current_prerequisite_ids":
            current_prerequisites
    }


# ============================================================
# MODULE GATING DISABLED STATUS
# ============================================================


def module_gating_disabled_status(
    module
):
    """
    Determine whether one module already matches the requested
    disabled Module Gating configuration.

    A module is considered disabled when:

    1. Sequential progress is turned off.
    2. No module prerequisites remain.
    """

    sequential_enabled = bool(
        module.get(
            "require_sequential_progress",
            False
        )
    )

    current_prerequisites = (
        get_current_prerequisite_ids(
            module
        )
    )

    module_matches = (
        not sequential_enabled
        and len(current_prerequisites) == 0
    )

    return {
        "sequential_enabled":
            sequential_enabled,

        "prerequisite_matches":
            len(current_prerequisites) == 0,

        "module_matches":
            module_matches,

        "current_prerequisite_ids":
            current_prerequisites
    }


# ============================================================
# BUILD MODULE CHAIN
# ============================================================


def build_module_chain(
    modules
):
    """
    Build the expected prerequisite chain for a sorted list of
    Canvas modules.

    Returns:
        list of dictionaries containing:

            module
            expected_prerequisite_id
            expected_prerequisite_name
    """

    sorted_modules = (
        sort_modules_by_position(
            modules
        )
    )

    chain = []

    previous_module = None

    for module in sorted_modules:

        if previous_module:

            expected_prerequisite_id = (
                previous_module.get("id")
            )

            expected_prerequisite_name = (
                previous_module.get("name")
                or (
                    f"Module "
                    f"{expected_prerequisite_id}"
                )
            )

        else:

            expected_prerequisite_id = None

            expected_prerequisite_name = None

        chain.append(
            {
                "module":
                    module,

                "expected_prerequisite_id":
                    expected_prerequisite_id,

                "expected_prerequisite_name":
                    expected_prerequisite_name
            }
        )

        previous_module = module

    return chain


# ============================================================
# BUILD SINGLE COURSE MODULE GATING PREVIEW
# ============================================================


def build_single_course_module_gating_preview(
    canvas,
    course_id,
    setting
):
    """
    Build a READ-ONLY Preview for Module Gating.

    No Canvas modifications are performed.

    Supported setting values:

        Don't Change
        Enable
        Disable

    Enable Preview:
    - Evaluates sequential module progress.
    - Builds the expected prerequisite chain.
    - Evaluates completion requirements for supported items.

    Disable Preview:
    - Evaluates whether sequential progress is disabled.
    - Finds every module prerequisite that would be removed.
    - Finds every module-item completion requirement that
      would be removed, regardless of item type.

    Returns:
        dict containing Preview information.
    """

    if setting not in [
        "Don't Change",
        "Enable",
        "Disable"
    ]:

        return {
            "success": False,
            "message": "Unsupported Module Gating setting.",
            "course": None,
            "modules": [],
            "counts": {}
        }

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
            "modules": [],
            "counts": {}
        }

    course = course_result["data"]

    modules_result = canvas.get_modules(
        course_id
    )

    if not modules_result["success"]:

        return {
            "success": False,
            "message": (
                "The course was found, but its modules "
                "could not be loaded. "
                + modules_result["message"]
            ),
            "course": course,
            "modules": [],
            "counts": {}
        }

    modules = modules_result["data"] or []
    module_chain = build_module_chain(
        modules
    )

    preview_modules = []

    total_module_items = 0
    supported_module_items = 0
    unsupported_module_items = 0
    item_requirements_would_change = 0
    item_requirements_already_set = 0
    modules_would_change = 0
    modules_already_configured = 0
    module_item_load_failures = 0

    for chain_entry in module_chain:

        module = chain_entry["module"]
        module_id = module.get("id")
        module_name = (
            module.get("name")
            or f"Module {module_id}"
        )

        if setting == "Enable":

            expected_prerequisite_id = (
                chain_entry[
                    "expected_prerequisite_id"
                ]
            )

            expected_prerequisite_name = (
                chain_entry[
                    "expected_prerequisite_name"
                ]
            )

            status = module_gating_status(
                module=module,
                expected_prerequisite_id=(
                    expected_prerequisite_id
                )
            )

            sequential_progress_requested = True

        else:

            expected_prerequisite_id = None
            expected_prerequisite_name = None

            status = module_gating_disabled_status(
                module
            )

            sequential_progress_requested = False

        items_result = canvas.get_module_items(
            course_id=course_id,
            module_id=module_id
        )

        module_items = []
        module_item_error = None

        if items_result["success"]:

            module_items = (
                items_result["data"]
                or []
            )

        else:

            module_item_error = (
                items_result["message"]
            )

            module_item_load_failures += 1

        module_supported_items = 0
        module_unsupported_items = 0
        module_items_would_change = 0
        module_items_already_set = 0

        requirement_summary = {
            "Must View": 0,
            "Must Submit": 0,
            "Must Contribute": 0,
            "Other Requirements": 0
        }

        for item in module_items:

            total_module_items += 1

            current_requirement = (
                get_current_completion_requirement(
                    item
                )
            )

            if setting == "Disable":

                # Every module item is inspectable during a
                # disable operation. Any existing completion
                # requirement will be removed.
                supported_module_items += 1
                module_supported_items += 1

                if current_requirement is None:

                    item_requirements_already_set += 1
                    module_items_already_set += 1

                else:

                    item_requirements_would_change += 1
                    module_items_would_change += 1

                    requirement_label = (
                        get_requirement_label(
                            current_requirement
                        )
                    )

                    if (
                        requirement_label
                        in requirement_summary
                    ):

                        requirement_summary[
                            requirement_label
                        ] += 1

                    else:

                        requirement_summary[
                            "Other Requirements"
                        ] += 1

                continue

            requirement_type = (
                get_module_item_requirement(
                    item
                )
            )

            if requirement_type is None:

                unsupported_module_items += 1
                module_unsupported_items += 1
                continue

            supported_module_items += 1
            module_supported_items += 1

            requirement_label = (
                get_requirement_label(
                    requirement_type
                )
            )

            if (
                requirement_label
                in requirement_summary
            ):

                requirement_summary[
                    requirement_label
                ] += 1

            if (
                current_requirement
                == requirement_type
            ):

                item_requirements_already_set += 1
                module_items_already_set += 1

            else:

                item_requirements_would_change += 1
                module_items_would_change += 1

        module_requires_change = (
            not status["module_matches"]
            or module_items_would_change > 0
            or module_item_error is not None
        )

        if module_requires_change:

            modules_would_change += 1

        else:

            modules_already_configured += 1

        preview_modules.append(
            {
                "id":
                    module_id,

                "name":
                    module_name,

                "position":
                    module.get("position"),

                "published":
                    module.get("published"),

                "sequential_progress_current":
                    bool(
                        module.get(
                            "require_sequential_progress",
                            False
                        )
                    ),

                "sequential_progress_requested":
                    sequential_progress_requested,

                "current_prerequisite_ids":
                    status[
                        "current_prerequisite_ids"
                    ],

                "expected_prerequisite_id":
                    expected_prerequisite_id,

                "expected_prerequisite_name":
                    expected_prerequisite_name,

                "module_settings_match":
                    status["module_matches"],

                "module_items_found":
                    len(module_items),

                "supported_items":
                    module_supported_items,

                "unsupported_items":
                    module_unsupported_items,

                "item_requirements_would_change":
                    module_items_would_change,

                "item_requirements_already_set":
                    module_items_already_set,

                "requirement_summary":
                    requirement_summary,

                "module_item_error":
                    module_item_error,

                "status":
                    (
                        "Would Change"
                        if module_requires_change
                        else "Already Set"
                    )
            }
        )

    if not preview_modules:

        current_configuration = (
            "No Modules Found"
        )

    elif (
        modules_would_change == 0
        and module_item_load_failures == 0
    ):

        if setting == "Enable":

            current_configuration = (
                "Fully Enabled"
            )

        else:

            current_configuration = (
                "Fully Disabled"
            )

    else:

        if setting == "Enable":

            current_configuration = (
                "Mixed / Not Fully Enabled"
            )

        else:

            current_configuration = (
                "Mixed / Not Fully Disabled"
            )

    return {
        "success": True,

        "message":
            "Module Gating Preview generated successfully.",

        "course": {
            "id":
                course.get("id"),

            "name":
                (
                    course.get("name")
                    or course.get("course_code")
                    or f"Course {course_id}"
                ),

            "course_code":
                course.get("course_code")
        },

        "setting":
            setting,

        "current_configuration":
            current_configuration,

        "modules":
            preview_modules,

        "counts": {
            "modules_found":
                len(preview_modules),

            "modules_would_change":
                modules_would_change,

            "modules_already_configured":
                modules_already_configured,

            "module_items_found":
                total_module_items,

            "supported_module_items":
                supported_module_items,

            "unsupported_module_items":
                unsupported_module_items,

            "item_requirements_would_change":
                item_requirements_would_change,

            "item_requirements_already_set":
                item_requirements_already_set,

            "module_item_load_failures":
                module_item_load_failures
        }
    }


# ============================================================
# BUILD MODULE UPDATE SETTINGS
# ============================================================


def build_module_update_settings(
    setting,
    expected_prerequisite_id=None
):
    """
    Build requested Canvas module settings.

    Enable:
    - Turns on sequential progress.
    - Assigns the preceding module as prerequisite when one
      exists.

    Disable:
    - Turns off sequential progress.
    - Sends an empty prerequisite list so every prerequisite
      is removed.
    """

    if setting == "Disable":

        return {
            "require_sequential_progress":
                False,

            "prerequisite_module_ids":
                []
        }

    module_settings = {
        "require_sequential_progress":
            True
    }

    if expected_prerequisite_id is not None:

        module_settings[
            "prerequisite_module_ids"
        ] = [
            expected_prerequisite_id
        ]

    else:

        # Explicitly clear prerequisites from the first module
        # in case a previous configuration added one.
        module_settings[
            "prerequisite_module_ids"
        ] = []

    return module_settings


# ============================================================
# EXECUTE SINGLE COURSE MODULE GATING
# ============================================================


def execute_single_course_module_gating(
    canvas,
    course_id,
    setting
):
    """
    Enable or Disable Module Gating for one Canvas course.

    THIS FUNCTION CAN MODIFY CANVAS.

    Supported settings:

        Enable
        Disable

    Enable:
    - Enables sequential progress.
    - Chains modules using prerequisites.
    - Applies supported completion requirements.

    Disable:
    - Disables sequential progress.
    - Removes all module prerequisites.
    - Removes all module-item completion requirements.

    One failed module or item does not stop processing of the
    remaining course.

    This function must only be called after Preview and explicit
    administrator confirmation.
    """

    if setting not in [
        "Enable",
        "Disable"
    ]:

        return {
            "success": False,

            "message": (
                "No executable Module Gating change "
                "was requested."
            ),

            "setting": setting,

            "module_results": [],

            "item_results": [],

            "counts": {
                "modules_found": 0,
                "modules_updated": 0,
                "modules_failed": 0,
                "items_found": 0,
                "items_updated": 0,
                "items_skipped": 0,
                "items_failed": 0
            }
        }

    modules_result = canvas.get_modules(
        course_id
    )

    if not modules_result["success"]:

        return {
            "success": False,

            "message": (
                "Unable to reload the course modules "
                "before applying Module Gating. "
                + modules_result["message"]
            ),

            "setting": setting,

            "module_results": [],

            "item_results": [],

            "counts": {
                "modules_found": 0,
                "modules_updated": 0,
                "modules_failed": 0,
                "items_found": 0,
                "items_updated": 0,
                "items_skipped": 0,
                "items_failed": 0
            }
        }

    modules = (
        modules_result["data"]
        or []
    )

    module_chain = build_module_chain(
        modules
    )

    module_results = []
    item_results = []
    items_found = 0

    for chain_entry in module_chain:

        module = chain_entry["module"]
        module_id = module.get("id")
        module_name = (
            module.get("name")
            or f"Module {module_id}"
        )

        if setting == "Enable":

            expected_prerequisite_id = (
                chain_entry[
                    "expected_prerequisite_id"
                ]
            )

            expected_prerequisite_name = (
                chain_entry[
                    "expected_prerequisite_name"
                ]
            )

        else:

            expected_prerequisite_id = None
            expected_prerequisite_name = None

        module_settings = (
            build_module_update_settings(
                setting=setting,
                expected_prerequisite_id=(
                    expected_prerequisite_id
                )
            )
        )

        module_update_result = canvas.update_module(
            course_id=course_id,
            module_id=module_id,
            module_settings=module_settings
        )

        if module_update_result["success"]:

            if setting == "Enable":

                module_message = (
                    "Sequential progress and prerequisite "
                    "settings updated successfully."
                )

            else:

                module_message = (
                    "Sequential progress disabled and all "
                    "module prerequisites removed."
                )

            module_results.append(
                {
                    "id":
                        module_id,

                    "name":
                        module_name,

                    "status":
                        "Updated",

                    "prerequisite":
                        expected_prerequisite_name,

                    "message":
                        module_message
                }
            )

        else:

            module_results.append(
                {
                    "id":
                        module_id,

                    "name":
                        module_name,

                    "status":
                        "Failed",

                    "prerequisite":
                        expected_prerequisite_name,

                    "message":
                        module_update_result["message"]
                }
            )

        items_result = canvas.get_module_items(
            course_id=course_id,
            module_id=module_id
        )

        if not items_result["success"]:

            item_results.append(
                {
                    "module_id":
                        module_id,

                    "module_name":
                        module_name,

                    "item_id":
                        None,

                    "item_name":
                        "Module Items",

                    "item_type":
                        None,

                    "requirement":
                        None,

                    "status":
                        "Failed",

                    "message":
                        (
                            "Unable to load module items. "
                            + items_result["message"]
                        )
                }
            )

            continue

        module_items = (
            items_result["data"]
            or []
        )

        for item in module_items:

            items_found += 1

            item_id = item.get("id")
            item_name = (
                item.get("title")
                or "Untitled Module Item"
            )
            item_type = (
                item.get("type")
                or ""
            )

            current_requirement = (
                get_current_completion_requirement(
                    item
                )
            )

            if setting == "Disable":

                if current_requirement is None:

                    item_results.append(
                        {
                            "module_id":
                                module_id,

                            "module_name":
                                module_name,

                            "item_id":
                                item_id,

                            "item_name":
                                item_name,

                            "item_type":
                                item_type,

                            "requirement":
                                None,

                            "status":
                                "Skipped",

                            "message":
                                (
                                    "No completion requirement "
                                    "is currently set."
                                )
                        }
                    )

                    continue

                # Canvas removes a module-item completion
                # requirement when completion_requirement is
                # supplied as an empty object.
                item_settings = {
                    "completion_requirement": {}
                }

                item_update_result = (
                    canvas.update_module_item(
                        course_id=course_id,
                        module_id=module_id,
                        item_id=item_id,
                        item_settings=item_settings
                    )
                )

                requirement_label = (
                    get_requirement_label(
                        current_requirement
                    )
                )

                if item_update_result["success"]:

                    item_results.append(
                        {
                            "module_id":
                                module_id,

                            "module_name":
                                module_name,

                            "item_id":
                                item_id,

                            "item_name":
                                item_name,

                            "item_type":
                                item_type,

                            "requirement":
                                requirement_label,

                            "status":
                                "Updated",

                            "message":
                                (
                                    "Completion requirement "
                                    "removed successfully."
                                )
                        }
                    )

                else:

                    item_results.append(
                        {
                            "module_id":
                                module_id,

                            "module_name":
                                module_name,

                            "item_id":
                                item_id,

                            "item_name":
                                item_name,

                            "item_type":
                                item_type,

                            "requirement":
                                requirement_label,

                            "status":
                                "Failed",

                            "message":
                                item_update_result["message"]
                        }
                    )

                continue

            requirement_type = (
                get_module_item_requirement(
                    item
                )
            )

            if requirement_type is None:

                item_results.append(
                    {
                        "module_id":
                            module_id,

                        "module_name":
                            module_name,

                        "item_id":
                            item_id,

                        "item_name":
                            item_name,

                        "item_type":
                            item_type,

                        "requirement":
                            None,

                        "status":
                            "Skipped",

                        "message":
                            (
                                "Module item type is not "
                                "managed by Module Gating."
                            )
                    }
                )

                continue

            if (
                current_requirement
                == requirement_type
            ):

                item_results.append(
                    {
                        "module_id":
                            module_id,

                        "module_name":
                            module_name,

                        "item_id":
                            item_id,

                        "item_name":
                            item_name,

                        "item_type":
                            item_type,

                        "requirement":
                            get_requirement_label(
                                requirement_type
                            ),

                        "status":
                            "Skipped",

                        "message":
                            (
                                "Completion requirement "
                                "already matches."
                            )
                    }
                )

                continue

            item_settings = {
                "completion_requirement": {
                    "type":
                        requirement_type
                }
            }

            item_update_result = (
                canvas.update_module_item(
                    course_id=course_id,
                    module_id=module_id,
                    item_id=item_id,
                    item_settings=item_settings
                )
            )

            if item_update_result["success"]:

                item_results.append(
                    {
                        "module_id":
                            module_id,

                        "module_name":
                            module_name,

                        "item_id":
                            item_id,

                        "item_name":
                            item_name,

                        "item_type":
                            item_type,

                        "requirement":
                            get_requirement_label(
                                requirement_type
                            ),

                        "status":
                            "Updated",

                        "message":
                            (
                                "Completion requirement "
                                "updated successfully."
                            )
                    }
                )

            else:

                item_results.append(
                    {
                        "module_id":
                            module_id,

                        "module_name":
                            module_name,

                        "item_id":
                            item_id,

                        "item_name":
                            item_name,

                        "item_type":
                            item_type,

                        "requirement":
                            get_requirement_label(
                                requirement_type
                            ),

                        "status":
                            "Failed",

                        "message":
                            item_update_result["message"]
                    }
                )

    modules_updated = sum(
        1
        for result in module_results
        if result["status"] == "Updated"
    )

    modules_failed = sum(
        1
        for result in module_results
        if result["status"] == "Failed"
    )

    items_updated = sum(
        1
        for result in item_results
        if result["status"] == "Updated"
    )

    items_skipped = sum(
        1
        for result in item_results
        if result["status"] == "Skipped"
    )

    items_failed = sum(
        1
        for result in item_results
        if result["status"] == "Failed"
    )

    overall_success = (
        modules_failed == 0
        and items_failed == 0
    )

    if overall_success:

        if setting == "Enable":

            message = (
                "Module Gating was enabled successfully."
            )

        else:

            message = (
                "Module Gating was disabled successfully. "
                "All module prerequisites and completion "
                "requirements were removed."
            )

    else:

        message = (
            f"Module Gating {setting.lower()} operation "
            "completed with "
            f"{modules_failed} module failure(s) and "
            f"{items_failed} module item failure(s)."
        )

    return {
        "success":
            overall_success,

        "message":
            message,

        "setting":
            setting,

        "module_results":
            module_results,

        "item_results":
            item_results,

        "counts": {
            "modules_found":
                len(module_chain),

            "modules_updated":
                modules_updated,

            "modules_failed":
                modules_failed,

            "items_found":
                items_found,

            "items_updated":
                items_updated,

            "items_skipped":
                items_skipped,

            "items_failed":
                items_failed
        }
    }

# ============================================================
# SOFT ZERO / MISSING SUBMISSION POLICY
# ============================================================


def validate_missing_submission_grade(grade_percent):
    """Validate and normalize a requested missing-submission grade."""

    try:
        normalized_grade = float(grade_percent)
    except (TypeError, ValueError):
        return {
            "success": False,
            "grade_percent": None,
            "message": "Missing submission grade must be a number between 0 and 100."
        }

    if normalized_grade < 0 or normalized_grade > 100:
        return {
            "success": False,
            "grade_percent": None,
            "message": "Missing submission grade must be between 0 and 100."
        }

    return {
        "success": True,
        "grade_percent": normalized_grade,
        "message": "Missing submission grade is valid."
    }


def extract_late_policy(result):
    """Normalize Canvas's {late_policy: {...}} response wrapper."""

    data = result.get("data") if isinstance(result, dict) else None

    if not isinstance(data, dict):
        return None

    wrapped = data.get("late_policy")

    if isinstance(wrapped, dict):
        return wrapped

    # Defensive fallback for Canvas instances returning the object directly.
    if "missing_submission_deduction_enabled" in data:
        return data

    return None


def deduction_to_grade(deduction_percent):
    """Convert Canvas's deduction percentage into the grade users see."""

    try:
        deduction = float(deduction_percent)
    except (TypeError, ValueError):
        deduction = 100.0

    return max(0.0, min(100.0, 100.0 - deduction))


def grade_to_deduction(grade_percent):
    """Convert a desired missing grade into Canvas deduction percentage."""

    return 100.0 - float(grade_percent)


def build_single_course_soft_zero_preview(
    canvas,
    course_id,
    setting,
    grade_percent=None
):
    """Build a read-only Preview for automatic missing-submission grades."""

    if setting not in ["Don't Change", "Enable", "Disable"]:
        return {
            "success": False,
            "message": "Unsupported Soft Zero setting.",
            "course": None
        }

    if setting == "Enable":
        validation = validate_missing_submission_grade(grade_percent)
        if not validation["success"]:
            return {
                "success": False,
                "message": validation["message"],
                "course": None
            }
        requested_grade = validation["grade_percent"]
    else:
        requested_grade = None

    course_result = canvas.get_course(course_id)
    if not course_result["success"]:
        return {
            "success": False,
            "message": "Unable to load the selected course. " + course_result["message"],
            "course": None
        }

    course = course_result["data"]
    late_policy_result = canvas.get_late_policy(course_id)

    policy_exists = late_policy_result.get("success", False)
    late_policy = extract_late_policy(late_policy_result) if policy_exists else None

    if not policy_exists and late_policy_result.get("status_code") != 404:
        return {
            "success": False,
            "message": "Unable to load the course Late Policy. " + late_policy_result.get("message", ""),
            "course": None
        }

    current_enabled = bool(
        (late_policy or {}).get("missing_submission_deduction_enabled", False)
    )

    current_grade = (
        deduction_to_grade((late_policy or {}).get("missing_submission_deduction"))
        if current_enabled
        else None
    )

    requested_enabled = setting == "Enable"

    if setting == "Enable":
        would_change = (
            not current_enabled
            or current_grade is None
            or abs(current_grade - requested_grade) > 0.0001
        )
    elif setting == "Disable":
        would_change = current_enabled
    else:
        would_change = False

    return {
        "success": True,
        "message": "Soft Zero Preview generated successfully.",
        "course": {
            "id": course.get("id"),
            "name": course.get("name") or course.get("course_code") or f"Course {course_id}",
            "course_code": course.get("course_code")
        },
        "setting": setting,
        "policy_exists": policy_exists,
        "current_enabled": current_enabled,
        "current_grade_percent": current_grade,
        "requested_enabled": requested_enabled,
        "requested_grade_percent": requested_grade,
        "would_change": would_change
    }


def execute_single_course_soft_zero(
    canvas,
    course_id,
    setting,
    grade_percent=None
):
    """Enable or disable automatic missing-submission grading."""

    if setting not in ["Enable", "Disable"]:
        return {
            "success": False,
            "message": "No executable Soft Zero change was requested.",
            "status": "Failed"
        }

    if setting == "Enable":
        validation = validate_missing_submission_grade(grade_percent)
        if not validation["success"]:
            return {
                "success": False,
                "message": validation["message"],
                "status": "Failed"
            }
        normalized_grade = validation["grade_percent"]
    else:
        normalized_grade = None

    current_result = canvas.get_late_policy(course_id)
    policy_exists = current_result.get("success", False)

    if not policy_exists and current_result.get("status_code") != 404:
        return {
            "success": False,
            "message": "Unable to confirm the current Late Policy. " + current_result.get("message", ""),
            "status": "Failed"
        }

    if setting == "Enable":
        settings = {
            "missing_submission_deduction_enabled": True,
            "missing_submission_deduction": grade_to_deduction(normalized_grade)
        }
    else:
        settings = {
            "missing_submission_deduction_enabled": False
        }

    if policy_exists:
        update_result = canvas.update_late_policy(course_id, settings)
        operation = "Updated"
    else:
        update_result = canvas.create_late_policy(course_id, settings)
        operation = "Created"

    if not update_result["success"]:
        return {
            "success": False,
            "message": update_result["message"],
            "status": "Failed",
            "operation": operation
        }

    if setting == "Enable":
        message = f"Automatic missing-submission grading was enabled at {normalized_grade:g}%."
    else:
        message = "Automatic missing-submission grading was disabled."

    return {
        "success": True,
        "message": message,
        "status": "Updated",
        "operation": operation,
        "setting": setting,
        "grade_percent": normalized_grade
    }

