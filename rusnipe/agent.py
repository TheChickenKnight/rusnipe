import subprocess
import os
from time import monotonic
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from datetime import date
import requests


env_path = os.path.join(os.path.dirname(__file__), ".env")

with open(env_path, "r", encoding="utf-8") as env_file:
    for raw_line in env_file:
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)

SUBJECT_NAME_TO_CODE: dict[str, str] = {
    "accounting": "010",
    "economics": "070",
    "art": "080",
    "arts": "080",
    "biology": "119",
    "chemistry": "160",
    "computer science": "198",
    "cs": "198",
    "journalism": "420",
    "mechanical engineering": "440",
    "history": "510",
    "management": "533",
    "visual arts": "550",
    "linguistics": "563",
    "latin american studies": "574",
    "physics": "615",
    "marketing": "630",
    "mathematics": "640",
    "math": "640",
    "electrical engineering": "650",
    "music": "700",
    "political science": "730",
    "statistics": "750",
    "philosophy": "790",
    "sociology": "920",
    "psychology": "988",
    "english": "355",
    "finance": "390",
    "supply chain management": "620",
    "information technology": "381",
    "data science": "960",
    "environmental science": "573",
    "food science": "375",
    "marine science": "776",
    "genetics": "216",
    "microbiology": "447",
    "theater arts": "966",
    "dance": "965",
    "middle eastern studies": "685",
}

TERM_MAP = {"fall": "9", "summer": "7", "spring": "1", "winter": "0"}
LEVEL_MAP = {"100": "1", "200": "2", "300": "3", "400": "4", "500": "5", "600": "6"}
_CLASS_DETAILS_CACHE: dict[str, tuple[float, list[dict]]] = {}


def _normalize_subject_value(value: str) -> str | None:
    raw = str(value).strip()
    if not raw:
        return None
    if raw.isdigit():
        return raw.zfill(3)
    return SUBJECT_NAME_TO_CODE.get(raw.lower(), raw)


def _get_course_subject_and_level(course_item: dict, core_codes: list[dict]) -> tuple[str, str, dict]:
    """
    Extract subject code and level from a course item.
    Falls back to top-level fields if coreCodes is empty or missing.
    Returns (subject, level, first_code_dict).
    """
    if core_codes:
        first_code = core_codes[0]
        subject = str(first_code.get("subject", "")).strip()
        level = str(first_code.get("level", "")).strip()
    else:
        first_code = {}
        subject = str(course_item.get("subject", "")).strip()
        level = str(course_item.get("level", "")).strip()

    return subject, level, first_code


def checkClasses(
    term: str,
    *,
    credits: str | None = None,
    school: str | None = None,
    keywords: list[str] | None = None,
    level: str | None = None,
    subject: str | list[str] | None = None,
) -> dict:
    """Checks for classes at Rutgers University based on the provided parameters.

    Args:
        term (str): The term to check for classes (e.g., "fall", "spring", "summer", "winter").
        credits (str, optional): The number of credits for the class (e.g., "3", "4", "1", "1.5").
        school (str, optional): The school offering the class. Valid values include:
            "School of Arts and Sciences", "School of Engineering",
            "School of Environmental and Biological Sciences",
            "Rutgers Business School - Newark/New Brunswick  - New Brunswick Campus",
            "Mason Gross School of the Arts (Undergrad)", "Mason Gross School of the Arts (Graduate)",
            "Ernest Mario School of Pharmacy (Undergrad)", "Ernest Mario School of Pharmacy (Graduate)",
            "School of Communication and Information (Graduate)",
            "School of Communication and Information  (Undergraduate)",
            "School of Management and Labor Relations  (Undergraduate)",
            "School of Management and Labor Relations  (Graduate)",
            "Graduate School of Education (U)", "Graduate School of Education",
            "School of Nursing - New Brunswick (UG)", "The Graduate School - Newark",
            "Graduate School of Applied and Professional Psychology",
            "Edward J. Bloustein School of Planning and  Public Policy (Undergraduate)",
            "Edward J. Bloustein School of Planning and  Public Policy (Graduate)",
            "School of Social Work (U)", "School of Social Work",
            "Rutgers Business School - Newark/New Brunswick  (Graduate)",
            "The School of Graduate Studies - New Brunswick",
            "School of Public Health", "Office of the Provost".
        keywords (list[str], optional): Keywords to search for in the class title or description.
        level (str, optional): Course level: "100", "200", "300", "400", "500", or "600" (graduate).
        subject (str | list[str], optional): Subject name(s) or Rutgers subject code(s).
            Examples: "english", "355", "computer science", "198", ["math", "statistics"].

    Returns:
        dict: Matching courses with filters applied, capped at 25 results.
    """
    today = date.today()

    resolved_term = TERM_MAP.get(str(term).strip().lower(), "9")  # default to fall

    resolved_level: str | None = None
    if level is not None:
        normalized_level = str(level).strip()
        resolved_level = LEVEL_MAP.get(normalized_level)

    normalized_subjects: set[str] | None = None
    if subject:
        if isinstance(subject, list):
            raw_values = [str(v).strip() for v in subject if str(v).strip()]
        else:
            raw_values = [part.strip() for part in str(subject).split(",") if part.strip()]

        converted = {_normalize_subject_value(v) for v in raw_values}
        normalized_subjects = {v for v in converted if v}

    normalized_keywords: list[str] = []
    if isinstance(keywords, list):
        normalized_keywords = [str(k).strip().lower() for k in keywords if str(k).strip()]
    elif isinstance(keywords, str):
        normalized_keywords = [part.strip().lower() for part in keywords.split(",") if part.strip()]

    if credits is not None:
        credits = str(credits).strip() or None
    if school is not None:
        school = str(school).strip() or None

    url = (
        f"https://classes.rutgers.edu/soc/api/courses.json"
        f"?campus=NB&year={today.year}&term={resolved_term}"
    )
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return {"error": f"Failed to fetch Rutgers class data: {exc}"}

    matches = []
    for course_item in data:
        if credits:
            item_credits = course_item.get("credits")
            try:
                if float(item_credits) != float(credits):
                    continue
            except (TypeError, ValueError):
                if str(item_credits).strip() != credits:
                    continue

        if school:
            course_school = (course_item.get("school") or {}).get("description", "")
            if course_school != school:
                continue

        core_codes = course_item.get("coreCodes") or []
        course_subject, course_level, first_code = _get_course_subject_and_level(
            course_item, core_codes
        )

        if normalized_subjects and course_subject not in normalized_subjects:
            continue

        if resolved_level and not course_level.startswith(resolved_level):
            continue

        if normalized_keywords:
            haystack = " ".join([
                course_item.get("title", ""),
                course_item.get("subjectDescription", ""),
                course_item.get("expandedTitle", ""),
            ]).lower()
            if not any(kw in haystack for kw in normalized_keywords):
                continue

        matches.append((course_item, first_code))

    preview = []
    for course_item, first_code in matches[:25]:
        preview.append({
            "courseId": course_item.get("courseId") or course_item.get("offeringUnitCode"),
            "subject": first_code.get("subject") or course_item.get("subject"),
            "course": first_code.get("course") or course_item.get("courseNumber"),
            "level": first_code.get("level") or course_item.get("level"),
            "title": course_item.get("title") or course_item.get("expandedTitle"),
            "credits": course_item.get("credits"),
            "school": (course_item.get("school") or {}).get("description"),
        })

    return {
        "filters": {
            "term": resolved_term,
            "credits": credits,
            "school": school,
            "keywords": normalized_keywords or None,
            "level": resolved_level,
            "subject": sorted(normalized_subjects) if normalized_subjects else None,
        },
        "total_matches": len(matches),
        "preview_count": len(preview),
        "preview": preview,
        "note": "Preview is capped at 25 courses.",
    }

def getClass(
    subject: str,
    course: str,
    term: str,
) -> dict:
    """Gets detailed information about a specific class based on its courseId.

    Args:
        subject (str): The subject number of the course (e.g., "013").
        course (str): The course number (e.g., "120").
        term (str): The term to check for the class (e.g., "fall", "spring", "summer", "winter").

    Returns:
        dict: Detailed information about the class, or an error message if not found.
    """
    resolved_term = TERM_MAP.get(str(term).strip().lower(), "9")
    url = ( 
        f"https://classes.rutgers.edu/soc/api/courses.json"
        f"?campus=NB&year={date.today().year}&term={resolved_term}"
    )
    try:
        cached_entry = _CLASS_DETAILS_CACHE.get(url)
        if cached_entry and (monotonic() - cached_entry[0]) < 60:
            data = cached_entry[1]
        else:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()
            _CLASS_DETAILS_CACHE[url] = (monotonic(), data)

        for course_item in data:
            if (len(course_item["coreCodes"]) == 0):
                continue
            if (course_item["coreCodes"][0]["subject"] == subject and course_item["coreCodes"][0]["course"] == course):
                return course_item
        return {"error": f"Class not found for {subject}:{course}"}
    except requests.RequestException as exc:
        return {"error": f"Failed to fetch class details for {subject}:{course}: {exc}"}


litellm_model = os.getenv("LITELLM_MODEL")
api_key = os.getenv("LITELLM_API_KEY")

root_agent = LlmAgent(
    model=LiteLlm(
        model=litellm_model if litellm_model else "gemini/gemini-2.0-flash",
        api_key=api_key if api_key else None,
    ),
    name="rutgers_class_assistant",
    description="An agent that helps students find classes at Rutgers University.",
    instruction=(
        "You are a helpful Rutgers University class search assistant.\n\n"

        "## Tools\n"
        "You have two tools: `checkClasses` and `getClass`. \n"
        "Do not call any other tool name (e.g. find_classes, search_classes, get_classes, rusnipe). \n"
        "If you need to look up multiple classes, you must use `checkClasses`.\n"
        "If you need to look up specific class details, you must use `getClass`.\n\n"

        "## When to call checkClasses\n"
        "Only call checkClasses when the user is explicitly asking to search, find, browse, \n"
        "or filter Rutgers classes. Do NOT call it for greetings, small talk, or unrelated questions.\n\n"

        "## Before calling checkClasses\n"
        "- If the user has not provided a term (fall/spring/summer/winter), ask for it before calling the tool.\n"
        "- Map common subject names to Rutgers subject codes (e.g. English → 355, Math → 640, CS → 198).\n"
        "- Include every filter the user mentioned (term, credits, school, keywords, level, subject) \n"
        "in a single checkClasses call. Never drop provided filters.\n\n"

        "## After checkClasses returns\n"
        "- Always respond in plain, conversational English. NEVER output raw JSON or Python dicts to the user.\n"
        "- Summarize the results clearly. For example:\n"
        "  'I found 12 English classes with 3 credits this spring. Here are the first few:\n"
        "   • EXPOSITORY WRITING (355:101) – 3 credits, School of Arts and Sciences\n"
        "   • WRITING FOR BUSINESS (355:201) – 3 credits, School of Arts and Sciences'\n"
        "- If total_matches is 0, tell the user no classes matched and suggest loosening a filter.\n"
        "- If total_matches > 25, mention that only the first 25 are shown and suggest refining the search.\n"
        "- List results as bullet points with: title, course code, credits, and school.\n\n"

        "## When to call getClass\n"
        "Only call getClass when the user is asking for specific details about a single class, like the class index, or availability. Do NOT call it for general searches or browsing.\n\n"

        "## General behavior\n"
        "- Be concise and friendly.\n"
        "- Never expose internal tool names, JSON structures, or raw API data to the user.\n"
        "- If the user asks a follow-up about the results, answer based on the data already returned."
    ),
    tools=[checkClasses, getClass],
)