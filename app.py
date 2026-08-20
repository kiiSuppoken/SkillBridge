from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from ai.skill_analyzer import analyze_skills
from ai.career_recommender import recommend_career

import json
import os


app = Flask(__name__)

app.secret_key = "skillbridge-secret-key"


# =========================================================
# LOAD ROADMAP DATA
# =========================================================

def load_roadmaps():

    path = os.path.join(
        app.root_path,
        "data",
        "roadmaps.json"
    )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


# =========================================================
# LOAD LESSON DATA
# =========================================================

def load_lessons():

    path = os.path.join(
        app.root_path,
        "data",
        "lessons.json"
    )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# ASSESSMENT
# =========================================================

@app.route("/assessment", methods=["GET", "POST"])
def assessment():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        skills = {

            "programming": request.form.get(
                "programming",
                0
            ),

            "problem_solving": request.form.get(
                "problem_solving",
                0
            ),

            "communication": request.form.get(
                "communication",
                0
            ),

            "design": request.form.get(
                "design",
                0
            )
        }

        selected_career = request.form.get(
            "career"
        )

        # =====================================================
        # AI ANALYSIS
        # =====================================================

        skill_analysis = analyze_skills(
            skills
        )

        career_result = recommend_career(
            skills
        )

        # =====================================================
        # SAVE SESSION
        # =====================================================

        session["username"] = username

        session["career"] = selected_career

        session["skill_analysis"] = skill_analysis

        session["career_result"] = career_result

        if "xp" not in session:

            session["xp"] = 0

        if "completed_quests" not in session:

            session["completed_quests"] = []

        # =====================================================
        # RESULT
        # =====================================================

        return render_template(
            "result.html",
            username=username,
            selected_career=selected_career,
            skill_analysis=skill_analysis,
            career_result=career_result
        )

    return render_template(
        "assessment.html"
    )


# =========================================================
# LEARNING ROADMAP
# =========================================================

@app.route("/learning")
def learning():

    career = request.args.get(
        "career",
        session.get(
            "career",
            "software_engineer"
        )
    )

    roadmaps = load_roadmaps()

    lessons = roadmaps.get(
        career,
        []
    )

    completed_quests = session.get(
        "completed_quests",
        []
    )

    lesson_data = load_lessons()

    career_lessons = lesson_data.get(
        career,
        {}
    )


    # =====================================================
    # TOTAL PROGRESS
    # =====================================================

    total_quests = 0

    completed_count = 0

    for lesson_id, lesson in career_lessons.items():

        quests = lesson.get(
            "quests",
            []
        )

        total_quests += len(
            quests
        )

        for index in range(
            len(quests)
        ):

            quest_key = (
                f"{career}:{lesson_id}:{index}"
            )

            if quest_key in completed_quests:

                completed_count += 1


    if total_quests > 0:

        progress = int(
            (
                completed_count
                / total_quests
            ) * 100
        )

    else:

        progress = 0


    # =====================================================
    # LESSON STATUS
    # =====================================================

    previous_completed = True

    for lesson in lessons:

        lesson_id = str(
            lesson.get("id")
        )

        lesson_info = career_lessons.get(
            lesson_id,
            {}
        )

        quests = lesson_info.get(
            "quests",
            []
        )

        quest_count = len(
            quests
        )

        lesson_completed_count = 0


        for index in range(
            quest_count
        ):

            quest_key = (
                f"{career}:{lesson_id}:{index}"
            )

            if quest_key in completed_quests:

                lesson_completed_count += 1


        if quest_count > 0:

            lesson_progress = int(
                (
                    lesson_completed_count
                    / quest_count
                ) * 100
            )

        else:

            lesson_progress = 0


        lesson["locked"] = not previous_completed

        lesson["completed"] = (
            quest_count > 0
            and lesson_completed_count == quest_count
        )

        lesson["progress"] = lesson_progress

        lesson["quest_count"] = quest_count

        lesson["completed_count"] = (
            lesson_completed_count
        )

        lesson["xp"] = sum(
            quest.get(
                "xp",
                0
            )
            for quest in quests
        )


        previous_completed = lesson["completed"]


    return render_template(
        "learning.html",
        career=career,
        lessons=lessons,
        progress=progress,
        xp=session.get(
            "xp",
            0
        )
    )


# =========================================================
# LESSON
# =========================================================

@app.route("/lesson")
def lesson():

    career = request.args.get(
        "career",
        session.get(
            "career",
            "software_engineer"
        )
    )

    lesson_id = request.args.get(
        "lesson_id"
    )

    lesson_data = load_lessons()

    career_lessons = lesson_data.get(
        career,
        {}
    )

    current_lesson = career_lessons.get(
        lesson_id
    )

    if current_lesson is None:

        return (
            "Lesson tidak ditemukan",
            404
        )


    completed_quests = session.get(
        "completed_quests",
        []
    )

    completed = []


    for index in range(
        len(
            current_lesson.get(
                "quests",
                []
            )
        )
    ):

        quest_key = (
            f"{career}:{lesson_id}:{index}"
        )

        completed.append(
            quest_key in completed_quests
        )


    return render_template(
        "lesson.html",

        career=career,

        lesson=current_lesson,

        completed=completed,

        xp=session.get(
            "xp",
            0
        ),

        quest_message=session.pop(
            "quest_message",
            None
        ),

        quest_correct=session.pop(
            "quest_correct",
            False
        )
    )


# =========================================================
# NORMALIZE ANSWER
# =========================================================

def normalize_answer(answer):

    return (
        answer
        .strip()
        .lower()
        .replace(
            "_",
            " "
        )
        .replace(
            "-",
            " "
        )
    )


# =========================================================
# CHECK ANSWER
# =========================================================

def check_answer(
    user_answer,
    correct_answer
):

    user_answer = normalize_answer(
        user_answer
    )

    correct_answer = normalize_answer(
        correct_answer
    )

    if correct_answer in user_answer:

        return True

    return False


# =========================================================
# COMPLETE QUEST
# =========================================================

@app.route(
    "/complete-quest",
    methods=["POST"]
)
def complete_quest():

    career = request.form.get(
        "career"
    )

    lesson_id = request.form.get(
        "lesson_id"
    )

    answer = request.form.get(
        "answer",
        ""
    ).strip()


    try:

        quest_index = int(
            request.form.get(
                "quest_index",
                0
            )
        )

    except ValueError:

        quest_index = 0


    # =====================================================
    # CEK DATA
    # =====================================================

    if not career or not lesson_id:

        return (
            "Data quest tidak lengkap",
            400
        )


    # =====================================================
    # JAWABAN KOSONG
    # =====================================================

    if not answer:

        session["quest_message"] = (
            "Jawaban tidak boleh kosong."
        )

        session["quest_correct"] = False

        return redirect(
            url_for(
                "lesson",
                career=career,
                lesson_id=lesson_id
            )
        )


    # =====================================================
    # LOAD LESSON
    # =====================================================

    lesson_data = load_lessons()

    lesson = (
        lesson_data
        .get(
            career,
            {}
        )
        .get(
            lesson_id
        )
    )

    if lesson is None:

        return (
            "Lesson tidak ditemukan",
            404
        )


    quests = lesson.get(
        "quests",
        []
    )


    # =====================================================
    # VALIDASI INDEX
    # =====================================================

    if (
        quest_index < 0
        or quest_index >= len(quests)
    ):

        return (
            "Quest tidak ditemukan",
            404
        )


    quest = quests[
        quest_index
    ]


    # =====================================================
    # QUEST KEY
    # =====================================================

    quest_key = (
        f"{career}:{lesson_id}:{quest_index}"
    )


    completed = session.get(
        "completed_quests",
        []
    )


    # =====================================================
    # SUDAH SELESAI
    # =====================================================

    if quest_key in completed:

        session["quest_message"] = (
            "Quest ini sudah diselesaikan."
        )

        session["quest_correct"] = True

        return redirect(
            url_for(
                "lesson",
                career=career,
                lesson_id=lesson_id
            )
        )


    # =====================================================
    # JAWABAN BENAR
    # =====================================================

    correct_answer = quest.get(
        "answer",
        ""
    )


    if not correct_answer:

        session["quest_message"] = (
            "Quest ini belum memiliki jawaban yang benar."
        )

        session["quest_correct"] = False

        return redirect(
            url_for(
                "lesson",
                career=career,
                lesson_id=lesson_id
            )
        )


    is_correct = check_answer(
        answer,
        correct_answer
    )


    # =====================================================
    # SALAH
    # =====================================================

    if not is_correct:

        session["quest_message"] = (
            "Jawaban belum tepat. "
            "Review kembali material dan coba lagi."
        )

        session["quest_correct"] = False

        return redirect(
            url_for(
                "lesson",
                career=career,
                lesson_id=lesson_id
            )
        )


    # =====================================================
    # BENAR
    # =====================================================

    xp = quest.get(
        "xp",
        0
    )


    completed.append(
        quest_key
    )

    session["completed_quests"] = (
        completed
    )


    session["xp"] = (
        session.get(
            "xp",
            0
        )
        + xp
    )


    session["quest_message"] = (
        f"Quest complete! +{xp} XP"
    )

    session["quest_correct"] = True


    return redirect(
        url_for(
            "lesson",
            career=career,
            lesson_id=lesson_id
        )
    )


# =========================================================
# PROGRESS DASHBOARD
# =========================================================

@app.route("/progress")
def progress():

    username = session.get(
        "username",
        "PLAYER"
    )

    career = session.get(
        "career",
        "software_engineer"
    )

    skill_analysis = session.get(
        "skill_analysis",
        {
            "average": 0,
            "strongest": None,
            "weakest": None,
            "scores": {},
            "skill_status": {},
            "recommendations": []
        }
    )

    xp = session.get(
        "xp",
        0
    )

    completed_quests = session.get(
        "completed_quests",
        []
    )


    # =====================================================
    # LOAD LESSON DATA
    # =====================================================

    lesson_data = load_lessons()

    career_lessons = lesson_data.get(
        career,
        {}
    )


    # =====================================================
    # TOTAL QUEST
    # =====================================================

    total_quests = 0

    for lesson_id, lesson in career_lessons.items():

        quests = lesson.get(
            "quests",
            []
        )

        total_quests += len(
            quests
        )


    # =====================================================
    # COMPLETED QUEST
    # =====================================================

    completed_count = 0

    for quest_key in completed_quests:

        if quest_key.startswith(
            f"{career}:"
        ):

            completed_count += 1


    # =====================================================
    # ROADMAP PROGRESS
    # =====================================================

    if total_quests > 0:

        progress_value = int(
            (
                completed_count
                / total_quests
            ) * 100
        )

    else:

        progress_value = 0


    # =====================================================
    # LEVEL
    # =====================================================

    level = (
        xp // 500
    ) + 1


    # =====================================================
    # RENDER
    # =====================================================

    return render_template(
        "progress.html",

        username=username,

        career=career,

        skill_analysis=skill_analysis,

        xp=xp,

        level=level,

        completed_count=completed_count,

        progress=progress_value
    )


# =========================================================
# RESET PROGRESS
# =========================================================

@app.route("/reset-progress")
def reset_progress():

    session["xp"] = 0

    session["completed_quests"] = []

    session.pop(
        "quest_message",
        None
    )

    session.pop(
        "quest_correct",
        None
    )

    return redirect(
        url_for(
            "learning",
            career=session.get(
                "career",
                "software_engineer"
            )
        )
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )