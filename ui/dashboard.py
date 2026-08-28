import streamlit as st


# ============================================================
# ACCELERATE CANVAS ADMINISTRATION SUITE
# Administration Dashboard
# ============================================================


def open_module(module_name):
    """
    Set the selected administration module as active.
    """

    st.session_state.active_module = module_name


def render_dashboard():
    """
    Render the main administration dashboard.

    Users select an administration module from this screen.
    """

    # --------------------------------------------------------
    # DASHBOARD INTRODUCTION
    # --------------------------------------------------------

    st.markdown("## Administration Dashboard")

    st.write(
        "Choose an administration module to configure and apply "
        "bulk changes across Canvas courses."
    )

    st.markdown("<br>", unsafe_allow_html=True)


    # --------------------------------------------------------
    # DASHBOARD CARD STYLES
    # --------------------------------------------------------

    st.markdown(
        """
        <style>

        .module-card {
            background-color: white;
            border-radius: 14px;
            padding: 24px;
            min-height: 215px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 2px 8px rgba(31, 55, 104, 0.08);
            margin-bottom: 10px;
        }

        .module-card-title {
            color: #1F3768;
            font-size: 21px;
            font-weight: 700;
            margin-top: 14px;
            margin-bottom: 10px;
        }

        .module-card-description {
            color: #4B5563;
            font-size: 15px;
            line-height: 1.6;
        }

        .module-icon {
            font-size: 32px;
            line-height: 1;
        }

        .module-accent-navy {
            border-top: 6px solid #1F3768;
        }

        .module-accent-coral {
            border-top: 6px solid #E67E73;
        }

        .module-accent-green {
            border-top: 6px solid #69A88D;
        }

        .module-accent-blue {
            border-top: 6px solid #79B8D8;
        }

        .module-accent-yellow {
            border-top: 6px solid #E7B84B;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # FIRST ROW
    # ========================================================

    col1, col2, col3 = st.columns(3, gap="large")


    # --------------------------------------------------------
    # COURSE MANAGEMENT
    # --------------------------------------------------------

    with col1:

        st.markdown(
            """
<div class="module-card module-accent-navy">
    <div class="module-icon">📚</div>
    <div class="module-card-title">Course Management</div>
    <div class="module-card-description">
        Manage course-wide administrative settings including
        module gating and soft-zero policies.
    </div>
</div>
            """,
            unsafe_allow_html=True
        )

        st.button(
            "Open Course Management →",
            key="open_course",
            use_container_width=True,
            on_click=open_module,
            args=("course",)
        )


    # --------------------------------------------------------
    # ASSIGNMENT MANAGEMENT
    # --------------------------------------------------------

    with col2:

        st.markdown(
            """
<div class="module-card module-accent-coral">
    <div class="module-icon">📝</div>
    <div class="module-card-title">Assignment Management</div>
    <div class="module-card-description">
        Bulk configure assignment attempt limits and related
        assignment-level settings.
    </div>
</div>
            """,
            unsafe_allow_html=True
        )

        st.button(
            "Open Assignment Management →",
            key="open_assignments",
            use_container_width=True,
            on_click=open_module,
            args=("assignments",)
        )


    # --------------------------------------------------------
    # QUIZ & EXAM MANAGEMENT
    # --------------------------------------------------------

    with col3:

        st.markdown(
            """
<div class="module-card module-accent-green">
    <div class="module-icon">🧠</div>
    <div class="module-card-title">Quiz &amp; Exam Management</div>
    <div class="module-card-description">
        Configure Classic Quiz and exam attempts, scoring,
        visibility, passwords, and delivery settings.
    </div>
</div>
            """,
            unsafe_allow_html=True
        )

        st.button(
            "Open Quiz & Exam Management →",
            key="open_quizzes",
            use_container_width=True,
            on_click=open_module,
            args=("quizzes",)
        )


    # ========================================================
    # SECOND ROW
    # ========================================================

    st.markdown("<br>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3, gap="large")


    # --------------------------------------------------------
    # REPORTS
    # --------------------------------------------------------

    with col4:

        st.markdown(
            """
<div class="module-card module-accent-blue">
    <div class="module-icon">📊</div>
    <div class="module-card-title">Reports</div>
    <div class="module-card-description">
        Review previews, completed operations, change summaries,
        and downloadable administration reports.
    </div>
</div>
            """,
            unsafe_allow_html=True
        )

        st.button(
            "Open Reports →",
            key="open_reports",
            use_container_width=True,
            on_click=open_module,
            args=("reports",)
        )


    # --------------------------------------------------------
    # SETTINGS
    # --------------------------------------------------------

    with col5:

        st.markdown(
            """
<div class="module-card module-accent-yellow">
    <div class="module-icon">⚙️</div>
    <div class="module-card-title">Settings</div>
    <div class="module-card-description">
        Manage application preferences and administrative
        configuration for the suite.
    </div>
</div>
            """,
            unsafe_allow_html=True
        )

        st.button(
            "Open Settings →",
            key="open_settings",
            use_container_width=True,
            on_click=open_module,
            args=("settings",)
        )


    # --------------------------------------------------------
    # RESERVED SPACE
    # --------------------------------------------------------

    with col6:

        st.empty()