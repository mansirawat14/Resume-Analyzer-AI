def generate_chatbot_response(
    user_message,
    resume_data=None
):
    """
    Generate a response to a user's resume-related question.
    """

    if not user_message:
        return {
            "success": False,
            "message": "Please enter a message."
        }

    message = user_message.lower().strip()

    # ---------------------------------------------------------
    # No resume uploaded
    # ---------------------------------------------------------

    if not resume_data:
        return {
            "success": True,
            "response": (
                "Please upload and analyze your resume first. "
                "Then I can answer questions about your "
                "resume, skills, ATS score, projects, "
                "experience, and job match."
            )
        }

    # ---------------------------------------------------------
    # Resume Score
    # ---------------------------------------------------------

    if (
        "resume score" in message
        or "resume rating" in message
    ):
        score = resume_data.get(
            "resume_score"
        )

        return {
            "success": True,
            "response": (
                f"Your current resume score is "
                f"{score}/100."
            )
        }

    # ---------------------------------------------------------
    # ATS Score
    # ---------------------------------------------------------

    if "ats" in message:
        score = resume_data.get(
            "ats_score"
        )

        return {
            "success": True,
            "response": (
                f"Your current ATS score is "
                f"{score}/100."
            )
        }

    # ---------------------------------------------------------
    # Job Match
    # ---------------------------------------------------------

    if (
        "job match" in message
        or "match" in message
    ):
        job_match = resume_data.get(
            "job_match",
            {}
        )

        percentage = job_match.get(
            "match_percentage"
        )

        if percentage is None:
            return {
                "success": True,
                "response": (
                    "No job description was provided, "
                    "so a job match percentage cannot "
                    "be calculated yet."
                )
            }

        return {
            "success": True,
            "response": (
                f"Your current job skill match is "
                f"{percentage}%."
            )
        }

    # ---------------------------------------------------------
    # Missing Skills
    # ---------------------------------------------------------

    if (
        "missing skill" in message
        or "missing skills" in message
        or "skill gap" in message
        or "skill gaps" in message
    ):
        job_match = resume_data.get(
            "job_match",
            {}
        )

        missing_skills = job_match.get(
            "missing_skills",
            []
        )

        if not missing_skills:
            return {
                "success": True,
                "response": (
                    "No missing job-required skills "
                    "were identified."
                )
            }

        skills = ", ".join(
            missing_skills
        )

        return {
            "success": True,
            "response": (
                f"The main missing skills identified "
                f"from the job description are: "
                f"{skills}."
            )
        }

    # ---------------------------------------------------------
    # Strengths
    # ---------------------------------------------------------

    if (
        "strength" in message
        or "strong point" in message
        or "strong points" in message
    ):
        strengths = resume_data.get(
            "top_strengths",
            []
        )

        if not strengths:
            return {
                "success": True,
                "response": (
                    "No specific strengths have been "
                    "identified yet."
                )
            }

        strength_names = [
            item.get("strength")
            for item in strengths
            if item.get("strength")
        ]

        return {
            "success": True,
            "response": (
                "Your main resume strengths are: "
                + ", ".join(strength_names)
                + "."
            )
        }

    # ---------------------------------------------------------
    # AI Suggestions
    # ---------------------------------------------------------

    if (
        "suggestion" in message
        or "improve" in message
        or "improvement" in message
    ):
        suggestions = resume_data.get(
            "ai_suggestions",
            []
        )

        if not suggestions:
            return {
                "success": True,
                "response": (
                    "No specific improvement "
                    "suggestions are available yet."
                )
            }

        suggestion_text = []

        for item in suggestions:
            category = item.get(
                "category",
                "General"
            )

            suggestion = item.get(
                "suggestion",
                ""
            )

            suggestion_text.append(
                f"{category}: {suggestion}"
            )

        return {
            "success": True,
            "response": "Here are some suggestions: "
            + " ".join(suggestion_text)
        }

    # ---------------------------------------------------------
    # Default response
    # ---------------------------------------------------------

    return {
        "success": True,
        "response": (
            "I can help you understand your resume "
            "analysis. You can ask me about your "
            "resume score, ATS score, job match, "
            "missing skills, strengths, or "
            "improvement suggestions."
        )
    }
