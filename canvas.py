import requests


# ============================================================
# ACCELERATE CANVAS ADMINISTRATION SUITE
# Canvas API Service
#
# Central service for communication with the Canvas REST API.
# UI files should NOT make Canvas API requests directly.
# ============================================================


class CanvasAPI:

    def __init__(self, canvas_url, api_token):

        self.canvas_url = canvas_url.strip().rstrip("/")
        self.api_token = api_token.strip()

        self.headers = {
            "Authorization": f"Bearer {self.api_token}"
        }


    # ========================================================
    # INTERNAL GET REQUEST
    # ========================================================

    def get(self, endpoint, params=None):
        """
        Perform a read-only GET request against Canvas.
        """

        url = f"{self.canvas_url}{endpoint}"

        try:

            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30
            )

        except requests.exceptions.Timeout:

            return {
                "success": False,
                "data": None,
                "message": (
                    "Canvas did not respond within the expected time."
                ),
                "status_code": None
            }

        except requests.exceptions.ConnectionError:

            return {
                "success": False,
                "data": None,
                "message": (
                    "Unable to connect to Canvas. "
                    "Check the Canvas URL and internet connection."
                ),
                "status_code": None
            }

        except requests.exceptions.RequestException as error:

            return {
                "success": False,
                "data": None,
                "message": (
                    f"Canvas request error: {error}"
                ),
                "status_code": None
            }

        if response.status_code == 200:

            try:

                return {
                    "success": True,
                    "data": response.json(),
                    "message": "Request successful.",
                    "status_code": response.status_code
                }

            except ValueError:

                return {
                    "success": False,
                    "data": None,
                    "message": (
                        "Canvas returned an unreadable response."
                    ),
                    "status_code": response.status_code
                }

        if response.status_code in [401, 403]:

            return {
                "success": False,
                "data": None,
                "message": (
                    "Canvas rejected the request. "
                    "Check the API token and permissions."
                ),
                "status_code": response.status_code
            }

        if response.status_code == 404:

            return {
                "success": False,
                "data": None,
                "message": (
                    "The requested Canvas resource "
                    "could not be found."
                ),
                "status_code": response.status_code
            }

        return {
            "success": False,
            "data": None,
            "message": (
                f"Canvas returned HTTP "
                f"{response.status_code}."
            ),
            "status_code": response.status_code
        }


    # ========================================================
    # PAGINATED GET REQUEST
    # ========================================================

    def get_paginated(self, endpoint, params=None):
        """
        Retrieve all pages from a Canvas list endpoint.

        This method performs GET requests only.
        """

        url = f"{self.canvas_url}{endpoint}"

        request_params = dict(
            params or {}
        )

        if "per_page" not in request_params:

            request_params[
                "per_page"
            ] = 100

        all_items = []

        try:

            while url:

                response = requests.get(
                    url,
                    headers=self.headers,
                    params=request_params,
                    timeout=30
                )

                if response.status_code != 200:

                    if response.status_code in [401, 403]:

                        message = (
                            "Canvas rejected the request. "
                            "Check the API token and permissions."
                        )

                    elif response.status_code == 404:

                        message = (
                            "The requested Canvas resource "
                            "could not be found."
                        )

                    else:

                        message = (
                            f"Canvas returned HTTP "
                            f"{response.status_code}."
                        )

                    return {
                        "success": False,
                        "data": None,
                        "message": message
                    }

                try:

                    page_data = response.json()

                except ValueError:

                    return {
                        "success": False,
                        "data": None,
                        "message": (
                            "Canvas returned an unreadable response."
                        )
                    }

                if isinstance(
                    page_data,
                    list
                ):

                    all_items.extend(
                        page_data
                    )

                else:

                    return {
                        "success": False,
                        "data": None,
                        "message": (
                            "Canvas returned an unexpected "
                            "list response."
                        )
                    }

                next_link = (
                    response.links.get(
                        "next"
                    )
                )

                if next_link:

                    url = next_link.get(
                        "url"
                    )

                    # The next Canvas URL already contains
                    # its pagination query parameters.

                    request_params = None

                else:

                    url = None

        except requests.exceptions.Timeout:

            return {
                "success": False,
                "data": None,
                "message": (
                    "Canvas did not respond within "
                    "the expected time."
                )
            }

        except requests.exceptions.ConnectionError:

            return {
                "success": False,
                "data": None,
                "message": (
                    "Unable to connect to Canvas."
                )
            }

        except requests.exceptions.RequestException as error:

            return {
                "success": False,
                "data": None,
                "message": (
                    f"Canvas request error: {error}"
                )
            }

        return {
            "success": True,
            "data": all_items,
            "message": "Request successful."
        }


    # ========================================================
    # INTERNAL FORM-ENCODED PUT REQUEST
    # ========================================================

    def put(self, endpoint, data=None):
        """
        Perform a controlled form-encoded PUT request.

        This method CAN modify Canvas data.

        Retained for compatibility with future Canvas endpoints
        that may require form-encoded parameters.
        """

        url = f"{self.canvas_url}{endpoint}"

        try:

            response = requests.put(
                url,
                headers=self.headers,
                data=data,
                timeout=30
            )

        except requests.exceptions.Timeout:

            return {
                "success": False,
                "data": None,
                "message": (
                    "Canvas did not respond within the expected time. "
                    "The update result could not be confirmed."
                ),
                "status_code": None
            }

        except requests.exceptions.ConnectionError:

            return {
                "success": False,
                "data": None,
                "message": (
                    "The connection to Canvas failed while attempting "
                    "the update."
                ),
                "status_code": None
            }

        except requests.exceptions.RequestException as error:

            return {
                "success": False,
                "data": None,
                "message": (
                    f"Canvas update request error: {error}"
                ),
                "status_code": None
            }

        return self._handle_update_response(
            response
        )


    # ========================================================
    # INTERNAL JSON PUT REQUEST
    # ========================================================

    def put_json(
        self,
        endpoint,
        json_data=None
    ):
        """
        Perform a controlled JSON PUT request against Canvas.

        IMPORTANT:
        This method CAN modify Canvas data.

        Used by API operations that require nested JSON
        payloads, including Classic Quiz, Assignment,
        Module, and Module Item updates.
        """

        url = f"{self.canvas_url}{endpoint}"

        try:

            response = requests.put(
                url,
                headers=self.headers,
                json=json_data,
                timeout=30
            )

        except requests.exceptions.Timeout:

            return {
                "success": False,
                "data": None,
                "message": (
                    "Canvas did not respond within the expected time. "
                    "The update result could not be confirmed."
                ),
                "status_code": None
            }

        except requests.exceptions.ConnectionError:

            return {
                "success": False,
                "data": None,
                "message": (
                    "The connection to Canvas failed while attempting "
                    "the update."
                ),
                "status_code": None
            }

        except requests.exceptions.RequestException as error:

            return {
                "success": False,
                "data": None,
                "message": (
                    f"Canvas update request error: {error}"
                ),
                "status_code": None
            }

        return self._handle_update_response(
            response
        )


    # ========================================================
    # INTERNAL FORM-ENCODED POST REQUEST
    # ========================================================

    def post(self, endpoint, data=None):
        """
        Perform a controlled form-encoded POST request.

        This method CAN create Canvas data.
        """

        url = f"{self.canvas_url}{endpoint}"

        try:

            response = requests.post(
                url,
                headers=self.headers,
                data=data,
                timeout=30
            )

        except requests.exceptions.Timeout:

            return {
                "success": False,
                "data": None,
                "message": (
                    "Canvas did not respond within the expected time. "
                    "The create result could not be confirmed."
                ),
                "status_code": None
            }

        except requests.exceptions.ConnectionError:

            return {
                "success": False,
                "data": None,
                "message": (
                    "The connection to Canvas failed while attempting "
                    "to create the resource."
                ),
                "status_code": None
            }

        except requests.exceptions.RequestException as error:

            return {
                "success": False,
                "data": None,
                "message": f"Canvas create request error: {error}",
                "status_code": None
            }

        return self._handle_update_response(response)


    # ========================================================
    # INTERNAL FORM-ENCODED PATCH REQUEST
    # ========================================================

    def patch(self, endpoint, data=None):
        """
        Perform a controlled form-encoded PATCH request.

        This method CAN modify Canvas data.
        """

        url = f"{self.canvas_url}{endpoint}"

        try:

            response = requests.patch(
                url,
                headers=self.headers,
                data=data,
                timeout=30
            )

        except requests.exceptions.Timeout:

            return {
                "success": False,
                "data": None,
                "message": (
                    "Canvas did not respond within the expected time. "
                    "The update result could not be confirmed."
                ),
                "status_code": None
            }

        except requests.exceptions.ConnectionError:

            return {
                "success": False,
                "data": None,
                "message": (
                    "The connection to Canvas failed while attempting "
                    "the update."
                ),
                "status_code": None
            }

        except requests.exceptions.RequestException as error:

            return {
                "success": False,
                "data": None,
                "message": f"Canvas update request error: {error}",
                "status_code": None
            }

        return self._handle_update_response(response)


    # ========================================================
    # SHARED UPDATE RESPONSE HANDLER
    # ========================================================

    def _handle_update_response(
        self,
        response
    ):
        """
        Convert a Canvas write response into the standard
        CanvasAPI result dictionary.
        """

        if (
            200
            <= response.status_code
            < 300
        ):

            try:

                response_data = (
                    response.json()
                )

            except ValueError:

                response_data = None

            return {
                "success": True,
                "data": response_data,
                "message": (
                    "Canvas update completed successfully."
                ),
                "status_code": response.status_code
            }

        if response.status_code in [401, 403]:

            return {
                "success": False,
                "data": None,
                "message": (
                    "Canvas rejected the update. "
                    "Check the API token and "
                    "administrative permissions."
                ),
                "status_code": response.status_code
            }

        if response.status_code == 404:

            return {
                "success": False,
                "data": None,
                "message": (
                    "The requested Canvas resource "
                    "could not be found."
                ),
                "status_code": response.status_code
            }

        if response.status_code == 400:

            return {
                "success": False,
                "data": None,
                "message": (
                    "Canvas rejected the requested settings. "
                    "One or more update values may be invalid."
                ),
                "status_code": response.status_code
            }

        if response.status_code == 429:

            return {
                "success": False,
                "data": None,
                "message": (
                    "Canvas temporarily rate-limited "
                    "the update request. "
                    "Wait briefly before trying again."
                ),
                "status_code": response.status_code
            }

        return {
            "success": False,
            "data": None,
            "message": (
                f"Canvas returned HTTP "
                f"{response.status_code} "
                "while attempting the update."
            ),
            "status_code": response.status_code
        }


    # ========================================================
    # TEST CONNECTION
    # ========================================================

    def test_connection(self):

        result = self.get(
            "/api/v1/users/self/profile"
        )

        if not result[
            "success"
        ]:

            return {
                "success": False,
                "message": result["message"],
                "user_name": None,
                "user_id": None
            }

        user_data = result[
            "data"
        ]

        return {
            "success": True,

            "message": (
                "Canvas connection successful."
            ),

            "user_name": (
                user_data.get("name")
                or user_data.get(
                    "short_name"
                )
                or "Canvas User"
            ),

            "user_id":
                user_data.get("id")
        }


    # ========================================================
    # GET COURSE
    # ========================================================

    def get_course(
        self,
        course_id
    ):
        """
        Retrieve one Canvas course.

        READ ONLY.
        """

        return self.get(
            f"/api/v1/courses/{course_id}"
        )


    # ========================================================
    # GET CLASSIC QUIZZES
    # ========================================================

    def get_classic_quizzes(
        self,
        course_id
    ):
        """
        Retrieve Classic Quizzes for one course.

        READ ONLY.
        """

        return self.get_paginated(
            (
                f"/api/v1/courses/"
                f"{course_id}/quizzes"
            )
        )


    # ========================================================
    # UPDATE CLASSIC QUIZ
    # ========================================================

    def update_classic_quiz(
        self,
        course_id,
        quiz_id,
        quiz_settings
    ):
        """
        Update selected settings for one Canvas Classic Quiz.

        Canvas endpoint:

        PUT /api/v1/courses/:course_id/quizzes/:quiz_id

        IMPORTANT:
        Only settings supplied in quiz_settings are sent.
        """

        if not isinstance(
            quiz_settings,
            dict
        ):

            return {
                "success": False,
                "data": None,
                "message": (
                    "Quiz settings must be provided "
                    "as a dictionary."
                ),
                "status_code": None
            }

        if not quiz_settings:

            return {
                "success": False,
                "data": None,
                "message": (
                    "No quiz settings were supplied "
                    "for the update."
                ),
                "status_code": None
            }

        payload = {
            "quiz": dict(
                quiz_settings
            )
        }

        return self.put_json(
            (
                f"/api/v1/courses/"
                f"{course_id}/quizzes/{quiz_id}"
            ),
            json_data=payload
        )


    # ========================================================
    # GET ASSIGNMENTS
    # ========================================================

    def get_assignments(
        self,
        course_id
    ):
        """
        Retrieve all assignments for one Canvas course.

        Pagination is handled automatically.

        READ ONLY.

        Canvas may return quizzes and other assignment-backed
        objects through this endpoint. The Assignment
        Management business layer is responsible for filtering.
        """

        return self.get_paginated(
            (
                f"/api/v1/courses/"
                f"{course_id}/assignments"
            )
        )


    # ========================================================
    # UPDATE ASSIGNMENT
    # ========================================================

    def update_assignment(
        self,
        course_id,
        assignment_id,
        assignment_settings
    ):
        """
        Update selected settings for one Canvas assignment.

        Canvas endpoint:

        PUT /api/v1/courses/:course_id/assignments/:assignment_id

        IMPORTANT:
        Only settings supplied in assignment_settings are sent.
        """

        if not isinstance(
            assignment_settings,
            dict
        ):

            return {
                "success": False,
                "data": None,
                "message": (
                    "Assignment settings must be provided "
                    "as a dictionary."
                ),
                "status_code": None
            }

        if not assignment_settings:

            return {
                "success": False,
                "data": None,
                "message": (
                    "No assignment settings were supplied "
                    "for the update."
                ),
                "status_code": None
            }

        payload = {
            "assignment": dict(
                assignment_settings
            )
        }

        return self.put_json(
            (
                f"/api/v1/courses/"
                f"{course_id}/assignments/"
                f"{assignment_id}"
            ),
            json_data=payload
        )


    # ========================================================
    # GET MODULES
    # ========================================================

    def get_modules(
        self,
        course_id
    ):
        """
        Retrieve all modules for one Canvas course.

        Canvas endpoint:

        GET /api/v1/courses/:course_id/modules

        Pagination is handled automatically.

        READ ONLY.

        The Course Management business layer should explicitly
        sort returned modules by Canvas position before building
        a prerequisite chain.
        """

        return self.get_paginated(
            (
                f"/api/v1/courses/"
                f"{course_id}/modules"
            )
        )


    # ========================================================
    # GET MODULE ITEMS
    # ========================================================

    def get_module_items(
        self,
        course_id,
        module_id
    ):
        """
        Retrieve all items contained in one Canvas module.

        Canvas endpoint:

        GET /api/v1/courses/:course_id/modules/:module_id/items

        Pagination is handled automatically.

        READ ONLY.
        """

        return self.get_paginated(
            (
                f"/api/v1/courses/"
                f"{course_id}/modules/"
                f"{module_id}/items"
            )
        )


    # ========================================================
    # UPDATE MODULE
    # ========================================================

    def update_module(
        self,
        course_id,
        module_id,
        module_settings
    ):
        """
        Update selected settings for one Canvas module.

        Canvas endpoint:

        PUT /api/v1/courses/:course_id/modules/:module_id

        Example module_settings:

            {
                "require_sequential_progress": True
            }

        Or:

            {
                "require_sequential_progress": True,
                "prerequisite_module_ids": [12345]
            }

        The request is sent as nested JSON:

            {
                "module": {
                    ...
                }
            }

        IMPORTANT:
        Only settings supplied in module_settings are sent.
        """

        # ----------------------------------------------------
        # VALIDATE SETTINGS
        # ----------------------------------------------------

        if not isinstance(
            module_settings,
            dict
        ):

            return {
                "success": False,
                "data": None,
                "message": (
                    "Module settings must be provided "
                    "as a dictionary."
                ),
                "status_code": None
            }

        if not module_settings:

            return {
                "success": False,
                "data": None,
                "message": (
                    "No module settings were supplied "
                    "for the update."
                ),
                "status_code": None
            }

        # ----------------------------------------------------
        # BUILD NESTED JSON PAYLOAD
        # ----------------------------------------------------

        payload = {
            "module": dict(
                module_settings
            )
        }

        # ----------------------------------------------------
        # SEND JSON UPDATE
        # ----------------------------------------------------

        return self.put_json(
            (
                f"/api/v1/courses/"
                f"{course_id}/modules/"
                f"{module_id}"
            ),
            json_data=payload
        )


    # ========================================================
    # UPDATE MODULE ITEM
    # ========================================================

    def update_module_item(
        self,
        course_id,
        module_id,
        item_id,
        item_settings
    ):
        """
        Update selected settings for one Canvas module item.

        Canvas endpoint:

        PUT /api/v1/courses/:course_id/modules/:module_id/items/:item_id

        Module Gating v1 uses this method to apply completion
        requirements.

        Example item_settings:

            {
                "completion_requirement": {
                    "type": "must_view"
                }
            }

        The request is sent as nested JSON:

            {
                "module_item": {
                    "completion_requirement": {
                        "type": "must_view"
                    }
                }
            }

        IMPORTANT:
        Only settings supplied in item_settings are sent.
        """

        # ----------------------------------------------------
        # VALIDATE SETTINGS
        # ----------------------------------------------------

        if not isinstance(
            item_settings,
            dict
        ):

            return {
                "success": False,
                "data": None,
                "message": (
                    "Module item settings must be provided "
                    "as a dictionary."
                ),
                "status_code": None
            }

        if not item_settings:

            return {
                "success": False,
                "data": None,
                "message": (
                    "No module item settings were supplied "
                    "for the update."
                ),
                "status_code": None
            }

        # ----------------------------------------------------
        # BUILD NESTED JSON PAYLOAD
        # ----------------------------------------------------

        payload = {
            "module_item": dict(
                item_settings
            )
        }

        # ----------------------------------------------------
        # SEND JSON UPDATE
        # ----------------------------------------------------

        return self.put_json(
            (
                f"/api/v1/courses/"
                f"{course_id}/modules/"
                f"{module_id}/items/"
                f"{item_id}"
            ),
            json_data=payload
        )

    # ========================================================
    # GET COURSE LATE POLICY
    # ========================================================

    def get_late_policy(self, course_id):
        """Retrieve the Late Policy for one Canvas course. READ ONLY."""

        return self.get(
            f"/api/v1/courses/{course_id}/late_policy"
        )


    # ========================================================
    # CREATE COURSE LATE POLICY
    # ========================================================

    def create_late_policy(self, course_id, late_policy_settings):
        """Create the single Late Policy allowed for a Canvas course."""

        if not isinstance(late_policy_settings, dict) or not late_policy_settings:
            return {
                "success": False,
                "data": None,
                "message": "Late Policy settings must be a non-empty dictionary.",
                "status_code": None
            }

        payload = {
            f"late_policy[{key}]": (
                "true"
                if value is True
                else "false"
                if value is False
                else value
            )
            for key, value in late_policy_settings.items()
        }

        return self.post(
            f"/api/v1/courses/{course_id}/late_policy",
            data=payload
        )


    # ========================================================
    # UPDATE COURSE LATE POLICY
    # ========================================================

    def update_late_policy(self, course_id, late_policy_settings):
        """Patch selected Late Policy settings for a Canvas course."""

        if not isinstance(late_policy_settings, dict) or not late_policy_settings:
            return {
                "success": False,
                "data": None,
                "message": "Late Policy settings must be a non-empty dictionary.",
                "status_code": None
            }

        payload = {
            f"late_policy[{key}]": (
                "true"
                if value is True
                else "false"
                if value is False
                else value
            )
            for key, value in late_policy_settings.items()
        }

        return self.patch(
            f"/api/v1/courses/{course_id}/late_policy",
            data=payload
        )

