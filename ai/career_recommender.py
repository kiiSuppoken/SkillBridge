def recommend_career(skills):
    """
    Menentukan karier berdasarkan kecocokan skill.
    """

    programming = int(skills.get("programming", 0))
    problem_solving = int(skills.get("problem_solving", 0))
    communication = int(skills.get("communication", 0))
    design = int(skills.get("design", 0))

    careers = {

        "software_engineer": (
            programming * 0.45 +
            problem_solving * 0.40 +
            communication * 0.05 +
            design * 0.10
        ),

        "uiux": (
            design * 0.50 +
            communication * 0.25 +
            problem_solving * 0.15 +
            programming * 0.10
        ),

        "data_analyst": (
            problem_solving * 0.45 +
            programming * 0.30 +
            communication * 0.15 +
            design * 0.10
        ),

        "cybersecurity": (
            problem_solving * 0.50 +
            programming * 0.30 +
            communication * 0.10 +
            design * 0.10
        ),

        "network_engineer": (
            problem_solving * 0.40 +
            programming * 0.30 +
            communication * 0.20 +
            design * 0.10
        )
    }

    recommended = max(
        careers,
        key=careers.get
    )

    return {
        "career": recommended,
        "scores": careers
    }