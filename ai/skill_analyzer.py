def analyze_skills(skills):
    """
    Menganalisis kemampuan user berdasarkan skor assessment.
    """

    if not skills:
        return {
            "average": 0,
            "strongest": None,
            "weakest": None,
            "scores": {},
            "skill_status": {},
            "recommendations": []
        }

    # =====================================================
    # KONVERSI SCORE
    # =====================================================

    skill_scores = {}

    for key, value in skills.items():

        try:
            skill_scores[key] = int(value)

        except (ValueError, TypeError):

            skill_scores[key] = 0

    # =====================================================
    # RATA-RATA
    # =====================================================

    average = round(
        sum(skill_scores.values())
        / len(skill_scores)
    )

    # =====================================================
    # SKILL TERKUAT & TERLEMAH
    # =====================================================

    strongest = max(
        skill_scores,
        key=skill_scores.get
    )

    weakest = min(
        skill_scores,
        key=skill_scores.get
    )

    # =====================================================
    # STATUS SKILL
    # =====================================================

    skill_status = {}

    for skill, score in skill_scores.items():

        if score >= 80:

            status = "Excellent"

        elif score >= 60:

            status = "Good"

        elif score >= 40:

            status = "Developing"

        else:

            status = "Needs Improvement"

        skill_status[skill] = {
            "score": score,
            "status": status
        }

    # =====================================================
    # REKOMENDASI
    # =====================================================

    recommendations = []

    for skill, score in skill_scores.items():

        if score < 40:

            recommendations.append({
                "skill": skill,
                "priority": "High",
                "message": (
                    f"Skill {skill.replace('_', ' ')} "
                    "perlu menjadi prioritas utama."
                )
            })

        elif score < 60:

            recommendations.append({
                "skill": skill,
                "priority": "Medium",
                "message": (
                    f"Skill {skill.replace('_', ' ')} "
                    "masih perlu dikembangkan."
                )
            })

    # =====================================================
    # HASIL ANALISIS
    # =====================================================

    return {
        "average": average,
        "strongest": strongest,
        "weakest": weakest,
        "scores": skill_scores,
        "skill_status": skill_status,
        "recommendations": recommendations
    }