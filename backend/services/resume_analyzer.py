import re
import spacy


# =========================================================
# LOAD SPACY MODEL
# =========================================================

nlp = spacy.load("en_core_web_sm")


# =========================================================
# SKILL DATABASE
# =========================================================

SKILL_CATEGORIES = {
    "programming_languages": {
        "python", "java", "c", "c++", "c#", "javascript",
        "typescript", "php", "ruby", "go", "kotlin", "swift",
        "r", "matlab"
    },

    "frameworks": {
        "flask", "django", "fastapi", "react", "angular",
        "vue", "node.js", "express", "spring", "laravel",
        "bootstrap"
    },

    "libraries": {
        "numpy", "pandas", "matplotlib", "seaborn",
        "scikit-learn", "tensorflow", "pytorch", "spacy",
        "opencv", "requests", "beautifulsoup"
    },

    "databases": {
        "mysql", "postgresql", "sqlite", "mongodb",
        "oracle", "redis", "sql"
    },

    "tools_and_technologies": {
        "git", "github", "docker", "aws", "azure",
        "google cloud", "postman", "vs code",
        "visual studio code", "linux", "excel", "power bi",
        "html", "css", "rest", "rest api", "rest apis"
    }
}


# =========================================================
# REGEX PATTERNS
# =========================================================

EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

PHONE_PATTERN = (
    r"(?<!\d)(?:\+91[\s-]?)?"
    r"[6-9]\d{4}[\s-]?\d{5}(?!\d)"
)

LINKEDIN_PATTERN = (
    r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s|]+"
)

GITHUB_PATTERN = (
    r"(?:https?://)?(?:www\.)?github\.com/[^\s|]+"
)

URL_PATTERN = r"(?:https?://|www\.)[^\s|]+"


# =========================================================
# SECTION HEADINGS
# =========================================================

SECTION_NAMES = {
    "summary": [
        "professional summary",
        "professional summary objective",
        "summary",
        "objective",
        "career objective",
        "profile summary",
        "career summary",
        "profile"
    ],

    "education": [
        "education",
        "educational background",
        "academic background",
        "academic qualifications",
        "academic qualification",
        "educational qualifications",
        "educational qualification",
        "qualifications",
        "academic history"
    ],

    "skills": [
        "technical skills",
        "technical skill",
        "skills",
        "key skills",
        "core skills",
        "technical expertise",
        "technologies",
        "skills and technologies"
    ],

    "experience": [
        "work experience",
        "professional experience",
        "work history",
        "employment history",
        "professional history",
        "employment",
        "experience"
    ],

    "internships": [
        "internships",
        "internship",
        "internship experience",
        "internship history"
    ],

    "projects": [
        "projects",
        "project",
        "academic projects",
        "personal projects",
        "professional projects",
        "project experience",
        "project work"
    ],

    "certifications": [
        "certifications",
        "certification",
        "certificates",
        "certifications and training",
        "training and certifications",
        "professional certifications"
    ],

    "achievements": [
        "achievements",
        "achievement",
        "awards",
        "honors",
        "honours",
        "honors and awards",
        "awards and achievements",
        "accomplishments",
        "extra curricular achievements",
        "extracurricular achievements"
    ],

    "contact": [
        "contact",
        "contact information",
        "contact professional links",
        "professional links"
    ]
}


# =========================================================
# GENERAL HELPERS
# =========================================================

def clean_line(line):
    """
    Clean common PDF extraction artifacts.
    """

    if not line:
        return ""

    line = line.replace("(cid:127)", "•")
    line = line.replace("\x7f", "•")

    return line.strip()


def normalize_heading(line):
    """
    Convert a heading into a normalized form.

    Example:
        1. PROFESSIONAL SUMMARY / OBJECTIVE

    becomes:
        professional summary objective
    """

    line = clean_line(line)

    # Remove numbering
    line = re.sub(
        r"^\s*\d+\s*[\.\)]\s*",
        "",
        line
    )

    # Convert slash and ampersand into spaces
    line = line.replace("/", " ")
    line = line.replace("&", " ")

    # Remove other punctuation
    line = re.sub(
        r"[^a-zA-Z0-9 ]",
        " ",
        line.lower()
    )

    line = re.sub(
        r"\s+",
        " ",
        line
    )

    return line.strip()


def is_bullet(line):
    """
    Check whether a line is a bullet point.
    """

    line = clean_line(line)

    return (
        line.startswith("•")
        or line.startswith("-")
        or line.startswith("*")
        or line.startswith("▪")
        or line.startswith("◦")
    )


def remove_bullet(line):
    """
    Remove bullet symbols from a line.
    """

    line = clean_line(line)

    return re.sub(
        r"^[•\-\*▪◦]\s*",
        "",
        line
    ).strip()


def extract_dates(text):
    """
    Extract resume date ranges without returning
    individual years when they are already part
    of a date range.
    """

    if not text:
        return []

    month = (
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|"
        r"Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
        r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
        r"Nov(?:ember)?|Dec(?:ember)?)"
    )

    patterns = [
        # May 2026 – Jul 2026
        rf"{month}\s+(?:19|20)\d{{2}}\s*[-–—]\s*"
        rf"(?:{month}\s+)?(?:19|20)\d{{2}}",

        # 2024 – 2027
        r"(?:19|20)\d{2}\s*[-–—]\s*"
        r"(?:19|20)\d{2}",

        # 2025 – Present
        r"(?:19|20)\d{2}\s*[-–—]\s*"
        r"(?:present|current)",

        # May 2026
        rf"{month}\s+(?:19|20)\d{{2}}"
    ]

    results = []

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            text,
            re.IGNORECASE
        ):

            value = match.group(0).strip()

            if value not in results:
                results.append(value)

    return results

def extract_year(text):
    """
    Extract a year from text.
    """

    match = re.search(
        r"\b(?:19|20)\d{2}\b",
        text
    )

    return match.group(0) if match else None


def extract_percentage_or_cgpa(text):
    """
    Extract percentage or CGPA.

    Examples:
        CGPA: 8.4/10
        Percentage: 86%
        86%
    """

    if not text:
        return None

    cgpa = re.search(
        r"(?:cgpa|gpa)\s*[:\-]?\s*"
        r"\d+(?:\.\d+)?(?:\s*/\s*\d+)?",
        text,
        re.IGNORECASE
    )

    if cgpa:
        return cgpa.group(0).strip()

    percentage = re.search(
        r"\b\d{1,3}(?:\.\d+)?\s*%",
        text
    )

    if percentage:
        return percentage.group(0)

    return None


def extract_technologies(text):
    """
    Extract known technologies from a piece of text.
    """

    if not text:
        return []

    found = []

    text_lower = text.lower()

    for category_skills in SKILL_CATEGORIES.values():

        for skill in category_skills:

            escaped_skill = re.escape(skill)

            pattern = rf"(?<![a-zA-Z0-9+#.]){escaped_skill}(?![a-zA-Z0-9+#.])"

            if re.search(
                pattern,
                text_lower
            ):
                found.append(skill)

    return sorted(set(found))


# =========================================================
# CONTACT INFORMATION
# =========================================================

def extract_email(text):

    match = re.search(
        EMAIL_PATTERN,
        text
    )

    return match.group(0) if match else None


def extract_phone(text):

    match = re.search(
        PHONE_PATTERN,
        text
    )

    return match.group(0) if match else None


def extract_linkedin(text):

    match = re.search(
        LINKEDIN_PATTERN,
        text,
        re.IGNORECASE
    )

    return match.group(0) if match else None


def extract_github(text):

    match = re.search(
        GITHUB_PATTERN,
        text,
        re.IGNORECASE
    )

    return match.group(0) if match else None


def extract_name(text):
    """
    Extract candidate name.

    First attempts to derive the name from the email,
    then checks the first few lines,
    then uses spaCy as a fallback.
    """

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    email = extract_email(text)

    # -----------------------------------------------------
    # Email based name extraction
    # -----------------------------------------------------

    if email:

        username = email.split("@")[0]

        username = re.sub(
            r"\d+",
            "",
            username
        )

        parts = re.split(
            r"[._-]+",
            username
        )

        name_parts = []

        for part in parts:

            if part.isalpha():
                name_parts.append(
                    part.capitalize()
                )

        if 2 <= len(name_parts) <= 3:

            return " ".join(
                name_parts
            )

    # -----------------------------------------------------
    # First lines
    # -----------------------------------------------------

    invalid_names = {
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "computer science",
        "data science",
        "software developer",
        "software engineer",
        "web developer",
        "resume",
        "curriculum vitae",
        "skills",
        "education",
        "experience",
        "projects",
        "certifications",
        "python",
        "java",
        "javascript",
        "c++",
        "c#",
        "sql",
        "html",
        "css",
        "flask",
        "django",
        "react",
        "bootstrap",
        "github",
        "linkedin"
    }

    for line in lines[:10]:

        lower = line.lower()

        if lower in invalid_names:
            continue

        if "@" in line:
            continue

        if "linkedin.com" in lower:
            continue

        if "github.com" in lower:
            continue

        if re.search(
            PHONE_PATTERN,
            line
        ):
            continue

        words = line.split()

        if 2 <= len(words) <= 4:

            if all(
                re.match(
                    r"^[A-Za-z][A-Za-z.'-]*$",
                    word
                )
                for word in words
            ):
                return line

    # -----------------------------------------------------
    # spaCy fallback
    # -----------------------------------------------------

    doc = nlp(
        "\n".join(lines[:20])
    )

    for entity in doc.ents:

        if entity.label_ != "PERSON":
            continue

        name = entity.text.strip()

        if name.lower() in invalid_names:
            continue

        if len(name.split()) > 4:
            continue

        return name

    return None


# =========================================================
# SECTION EXTRACTION
# =========================================================

def extract_sections(text):
    """
    Split resume into sections.

    Handles numbered headings such as:

        1. EDUCATION
        2. TECHNICAL SKILLS

    and normal headings.
    """

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    sections = {
        "header": []
    }

    current_section = "header"

    heading_lookup = {}

    for section, headings in SECTION_NAMES.items():

        for heading in headings:

            normalized = normalize_heading(
                heading
            )

            heading_lookup[normalized] = section

    for line in lines:

        normalized_line = normalize_heading(
            line
        )

        if normalized_line in heading_lookup:

            current_section = heading_lookup[
                normalized_line
            ]

            sections.setdefault(
                current_section,
                []
            )

        else:

            sections.setdefault(
                current_section,
                []
            ).append(line)

    return {
        key: "\n".join(value).strip()
        for key, value in sections.items()
    }


# =========================================================
# SKILLS
# =========================================================

def extract_skills(text):

    text_lower = text.lower()

    result = {}

    for category, skills in SKILL_CATEGORIES.items():

        found = []

        for skill in skills:

            pattern = (
                rf"(?<![a-zA-Z0-9+#.])"
                rf"{re.escape(skill)}"
                rf"(?![a-zA-Z0-9+#.])"
            )

            if re.search(
                pattern,
                text_lower
            ):
                found.append(skill)

        result[category] = sorted(
            set(found)
        )

    all_skills = []

    for skills in result.values():
        all_skills.extend(skills)

    result["all"] = sorted(
        set(all_skills)
    )

    return result


# =========================================================
# KEYWORDS
# =========================================================

def extract_keywords(text):

    if not text:
        return []

    doc = nlp(text)

    keywords = []

    for token in doc:

        if (
            token.pos_ in {"NOUN", "PROPN"}
            and not token.is_stop
            and len(token.text) > 2
            and token.is_alpha
        ):
            keywords.append(
                token.text.lower()
            )

    return sorted(
        set(keywords)
    )


# =========================================================
# EDUCATION
# =========================================================

def extract_education(text):

    if not text:
        return []

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    entries = []

    degree_pattern = re.compile(
        r"\b("
        r"BCA|B\.?Tech|BTech|B\.?E|"
        r"MCA|M\.?Tech|MBA|"
        r"B\.?Sc|M\.?Sc|"
        r"Bachelor|Master|PhD|"
        r"Diploma|10th|12th"
        r")\b",
        re.IGNORECASE
    )

    for index, line in enumerate(lines):

        if not degree_pattern.search(line):
            continue

        dates = extract_dates(line)

        cgpa = extract_percentage_or_cgpa(
            line
        )

        # -------------------------------------------------
        # Find university / college from next lines
        # -------------------------------------------------

        college = None

        for next_line in lines[
            index + 1:index + 3
        ]:

            lower = next_line.lower()

            if any(
                keyword in lower
                for keyword in [
                    "university",
                    "college",
                    "school",
                    "institute"
                ]
            ):
                college = next_line
                break

        # Sometimes CGPA is on the college line
        if college:

            if not cgpa:
                cgpa = extract_percentage_or_cgpa(
                    college
                )

            college = re.sub(
                r"\s*(?:cgpa|gpa)\s*[:\-]?"
                r"\s*\d+(?:\.\d+)?"
                r"(?:\s*/\s*\d+)?",
                "",
                college,
                flags=re.IGNORECASE
            ).strip()

        entries.append({
            "degree": line,
            "college_university": college,
            "cgpa_percentage": cgpa,
            "dates": dates
        })

    return entries


# =========================================================
# WORK EXPERIENCE
# =========================================================

def extract_experience(text):
    """
    Extract work experience from the Work Experience section.

    Extracts:
    - Job Title
    - Company
    - Duration
    - Responsibilities
    - Technologies Used
    """

    if not text:
        return []

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    entries = []

    # -----------------------------------------------------
    # Date pattern
    # Supports:
    # May 2026 - Jul 2026
    # May 2026 – Jul 2026
    # 2024 - 2026
    # 2025 - Present
    # -----------------------------------------------------

    month = (
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|"
        r"Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
        r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
        r"Nov(?:ember)?|Dec(?:ember)?)"
    )

    date_pattern = re.compile(
        rf"("
        rf"{month}\s+(?:19|20)\d{{2}}"
        rf"\s*[-–—]\s*"
        rf"(?:{month}\s+)?(?:19|20)\d{{2}}"
        rf"|"
        rf"(?:19|20)\d{{2}}"
        rf"\s*[-–—]\s*"
        rf"(?:19|20)\d{{2}}"
        rf"|"
        rf"(?:19|20)\d{{2}}"
        rf"\s*[-–—]\s*"
        rf"(?:present|current)"
        rf")",
        re.IGNORECASE
    )

    # -----------------------------------------------------
    # Go through every line
    # -----------------------------------------------------

    for index, line in enumerate(lines):

        match = date_pattern.search(line)

        if not match:
            continue

        date_text = match.group(0).strip()

        # -------------------------------------------------
        # Remove date from the line
        # -------------------------------------------------

        title_company = re.sub(
            re.escape(date_text),
            "",
            line,
            flags=re.IGNORECASE
        ).strip(
            " |:-–—"
        )

        # -------------------------------------------------
        # Remove a trailing "|" if present
        # -------------------------------------------------

        title_company = title_company.strip(
            " |"
        )

        # -------------------------------------------------
        # Split Job Title and Company
        #
        # Example:
        #
        # Backend Developer Intern –
        # TechNova Solutions
        # -------------------------------------------------

        job_title = title_company
        company = None

        role_parts = re.split(
            r"\s*[–—-]\s*",
            title_company,
            maxsplit=1
        )

        if len(role_parts) == 2:

            job_title = role_parts[0].strip()
            company = role_parts[1].strip()

        # -------------------------------------------------
        # If "|" separates title/company
        # -------------------------------------------------

        elif "|" in title_company:

            parts = [
                part.strip()
                for part in title_company.split("|")
                if part.strip()
            ]

            if len(parts) >= 2:

                job_title = parts[0]
                company = parts[1]

        # -------------------------------------------------
        # Read responsibilities
        # -------------------------------------------------

        responsibilities = []

        for next_line in lines[index + 1:index + 8]:

            # Stop if we reach another numbered section
            if re.match(
                r"^\d+\.\s+",
                next_line
            ):
                break

            # Stop at a recognized section heading
            normalized = normalize_heading(
                next_line
            )

            all_section_headings = []

            for heading_list in SECTION_NAMES.values():

                all_section_headings.extend(
                    normalize_heading(
                        heading
                    )
                    for heading in heading_list
                )

            if normalized in all_section_headings:
                break

            # Add bullet responsibilities
            if is_bullet(next_line):

                responsibilities.append(
                    remove_bullet(next_line)
                )

            # Also allow normal text lines after
            # the experience heading
            elif next_line and not date_pattern.search(
                next_line
            ):

                # Don't accidentally consume another
                # job/internship heading
                if (
                    "developer" not in next_line.lower()
                    and "engineer" not in next_line.lower()
                    and "intern" not in next_line.lower()
                    and "manager" not in next_line.lower()
                    and "analyst" not in next_line.lower()
                ):
                    responsibilities.append(
                        next_line
                    )

        # -------------------------------------------------
        # Detect technologies used
        # -------------------------------------------------

        responsibility_text = " ".join(
            responsibilities
        )

        technologies = extract_technologies(
            responsibility_text
        )

        # -------------------------------------------------
        # Save experience entry
        # -------------------------------------------------

        entries.append({

            "job_title": job_title,

            "company": company,

            "duration": date_text,

            "responsibilities": responsibilities,

            "technologies_used": technologies
        })

    return entries

# =========================================================
# INTERNSHIPS
# =========================================================

def extract_internships(text):

    if not text:
        return []

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    entries = []

    for index, line in enumerate(lines):

        if "intern" not in line.lower():
            continue

        dates = extract_dates(line)

        # Example:
        #
        # Python Development Intern – CodeSphere Labs |
        # Jan 2026 – Mar 2026

        parts = re.split(
            r"\s*[|]\s*",
            line
        )

        role_company = parts[0].strip()

        role_company = re.sub(
            r"\s*(?:Jan(?:uary)?|Feb(?:ruary)?|"
            r"Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|"
            r"Sep(?:tember)?|Oct(?:ober)?|"
            r"Nov(?:ember)?|Dec(?:ember)?)"
            r"\s+(?:19|20)\d{2}"
            r"(?:\s*[-–—]\s*"
            r"(?:[A-Za-z]+\s+)?(?:19|20)\d{2})?",
            "",
            role_company,
            flags=re.IGNORECASE
        ).strip(
            " -–—|"
        )

        role = role_company
        organization = None

        role_parts = re.split(
            r"\s+[–—-]\s+",
            role_company,
            maxsplit=1
        )

        if len(role_parts) == 2:

            role = role_parts[0].strip()
            organization = role_parts[1].strip()

        responsibilities = []

        for next_line in lines[
            index + 1:index + 8
        ]:

            if is_bullet(next_line):

                responsibilities.append(
                    remove_bullet(next_line)
                )

            elif re.match(
                r"^\d+\.",
                next_line
            ):
                break

        responsibility_text = " ".join(
            responsibilities
        )

        technologies = extract_technologies(
            responsibility_text
        )

        entries.append({
            "organization": organization,
            "role": role,
            "duration": dates,
            "responsibilities": responsibilities,
            "technologies_used": technologies
        })

    return entries


# =========================================================
# PROJECTS
# =========================================================

def extract_projects(text):
    """
    Extract multiple projects from the Projects section.

    Extracts:
    - Project Name
    - Description
    - Technologies Used
    - Role
    - GitHub / Live Project Link
    """

    if not text:
        return []

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    projects = []

    # -----------------------------------------------------
    # Helper: determine whether a line looks like
    # a project title.
    # -----------------------------------------------------

    def looks_like_project_title(line):

        lower = line.lower().strip()

        # Metadata lines are not project titles
        if (
            lower.startswith("technologies:")
            or lower.startswith("technology:")
            or lower.startswith("role:")
            or lower.startswith("github:")
            or lower.startswith("live:")
            or lower.startswith("description:")
            or lower.startswith("link:")
        ):
            return False

        # Contact / metadata lines are not project titles
        if (
            "@" in line
            or "linkedin.com" in lower
            or "github.com" in lower
            or re.search(
                PHONE_PATTERN,
                line
            )
        ):
            return False

        # A project title is normally short
        # compared with a description.
        words = line.split()

        if len(words) > 12:
            return False

        # A description normally contains sentence punctuation
        if line.endswith("."):
            return False

        return True

    # -----------------------------------------------------
    # Find projects
    # -----------------------------------------------------

    index = 0

    while index < len(lines):

        line = lines[index]

        # -------------------------------------------------
        # Skip numbered headings
        # -------------------------------------------------

        if re.match(
            r"^\d+\.\s+",
            line
        ):
            index += 1
            continue

        # -------------------------------------------------
        # Check if this can be a project title
        # -------------------------------------------------

        if not looks_like_project_title(line):

            index += 1
            continue

        # -------------------------------------------------
        # Check the following lines for project-related
        # information.
        # -------------------------------------------------

        look_ahead = " ".join(
            lines[index + 1:index + 8]
        ).lower()

        project_indicators = [
            "technologies:",
            "technology:",
            "role:",
            "github:",
            "github.com",
            "live:",
            "description:"
        ]

        if not any(
            indicator in look_ahead
            for indicator in project_indicators
        ):

            index += 1
            continue

        # -------------------------------------------------
        # We found a project
        # -------------------------------------------------

        project_name = line.strip()

        description_lines = []

        technologies = []

        role = None

        project_link = None

        j = index + 1

        while j < len(lines):

            current = lines[j]

            lower = current.lower()

            # -------------------------------------------------
            # Stop if another numbered section starts
            # -------------------------------------------------

            if re.match(
                r"^\d+\.\s+",
                current
            ):
                break

            # -------------------------------------------------
            # Detect another project title
            #
            # Example:
            #
            # Resumate - AI Resume Analyzer
            # ...
            #
            # Smart Traffic Analytics Platform
            # ...
            # -------------------------------------------------

            if (
                j > index + 1
                and looks_like_project_title(current)
            ):

                remaining = " ".join(
                    lines[j + 1:j + 8]
                ).lower()

                if any(
                    indicator in remaining
                    for indicator in project_indicators
                ):

                    break

            # -------------------------------------------------
            # Technologies
            # -------------------------------------------------

            if (
                lower.startswith("technologies:")
                or lower.startswith("technology:")
            ):

                tech_text = current.split(
                    ":",
                    1
                )[1].strip()

                technologies = extract_technologies(
                    tech_text
                )

            # -------------------------------------------------
            # Role
            # -------------------------------------------------

            elif lower.startswith("role:"):

                role = current.split(
                    ":",
                    1
                )[1].strip()

            # -------------------------------------------------
            # Description
            # -------------------------------------------------

            elif lower.startswith("description:"):

                description = current.split(
                    ":",
                    1
                )[1].strip()

                if description:

                    description_lines.append(
                        description
                    )

            # -------------------------------------------------
            # GitHub / Live link
            # -------------------------------------------------

            elif (
                "github:" in lower
                or "github.com" in lower
                or "live:" in lower
                or "live project" in lower
                or "link:" in lower
            ):

                github_match = re.search(
                    r"github\.com/[^\s|]+",
                    current,
                    re.IGNORECASE
                )

                if github_match:

                    project_link = (
                        github_match.group(0)
                    )

                else:

                    url_match = re.search(
                        URL_PATTERN,
                        current,
                        re.IGNORECASE
                    )

                    if url_match:

                        project_link = (
                            url_match.group(0)
                        )

            # -------------------------------------------------
            # Normal description
            # -------------------------------------------------

            else:

                description = remove_bullet(
                    current
                )

                if description:

                    description_lines.append(
                        description
                    )

            j += 1

        # -------------------------------------------------
        # Remove duplicate descriptions
        # -------------------------------------------------

        cleaned_description = []

        for description in description_lines:

            description = description.strip()

            if (
                description
                and description
                not in cleaned_description
            ):

                cleaned_description.append(
                    description
                )

        # -------------------------------------------------
        # Detect technologies from description if the
        # resume doesn't explicitly provide them.
        # -------------------------------------------------

        if not technologies:

            technologies = extract_technologies(
                " ".join(
                    cleaned_description
                )
            )

        # -------------------------------------------------
        # Save project
        # -------------------------------------------------

        projects.append({

            "project_name":
                project_name,

            "description":
                " ".join(
                    cleaned_description
                ).strip() or None,

            "technologies_used":
                technologies,

            "role":
                role,

            "github_live_link":
                project_link
        })

        # Continue from where this project ended
        index = j

    return projects

# =========================================================
# CERTIFICATIONS
# =========================================================

def extract_certifications(text):

    if not text:
        return []

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    certifications = []

    # Words that strongly indicate a certification
    certification_keywords = [
        "certification",
        "certified",
        "certificate",
        "course",
        "academy",
        "nptel",
        "coursera"
    ]

    for line in lines:

        lower = line.lower()

        if not any(
            keyword in lower
            for keyword in certification_keywords
        ):
            continue

        # Don't treat the section heading itself as a certificate
        if normalize_heading(line) in {
            "certifications",
            "certification",
            "certificates"
        }:
            continue

        year = extract_year(line)

        link_match = re.search(
            URL_PATTERN,
            line,
            re.IGNORECASE
        )

        # -------------------------------------------------
        # Try to split:
        #
        # Certification Name | Organization | 2026
        # -------------------------------------------------

        parts = [
            part.strip()
            for part in re.split(
                r"\s*[|]\s*",
                line
            )
            if part.strip()
        ]

        certification_name = parts[0] if parts else line
        organization = None

        if len(parts) >= 2:

            # If second part is only a year,
            # it is not the organization.
            if not re.fullmatch(
                r"(?:19|20)\d{2}",
                parts[1]
            ):
                organization = parts[1]

        certifications.append({
            "certification_name": certification_name,
            "issuing_organization": organization,
            "date_year": year,
            "credential_link": (
                link_match.group(0)
                if link_match
                else None
            )
        })

    return certifications


# =========================================================
# ACHIEVEMENTS
# =========================================================

def extract_achievements(text):

    if not text:
        return []

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    achievements = []

    for line in lines:

        lower = line.lower()

        category = None

        if (
            "hackathon" in lower
        ):
            category = "Hackathon"

        elif (
            "competition" in lower
            or "coding competition" in lower
        ):
            category = "Competition"

        elif (
            "award" in lower
            or "winner" in lower
            or "won" in lower
        ):
            category = "Award"

        elif (
            "scholarship" in lower
            or "academic" in lower
            or "merit" in lower
        ):
            category = "Academic Achievement"

        elif (
            "achievement" in lower
            or "finalist" in lower
            or "rank" in lower
            or "position" in lower
        ):
            category = "Achievement"

        if category:

            achievements.append({
                "category": category,
                "description": remove_bullet(line)
            })

    return achievements


# =========================================================
# SUMMARY ANALYSIS
# =========================================================

def analyze_summary(summary):

    if not summary:

        return {
            "summary": None,
            "quality": "Not Available",
            "keywords": [],
            "relevance": "Not Evaluated"
        }

    words = summary.split()

    keywords = extract_keywords(
        summary
    )

    if len(words) < 20:
        quality = "Needs Improvement"

    elif len(words) < 40:
        quality = "Good"

    else:
        quality = "Detailed"

    return {
        "summary": summary,
        "quality": quality,
        "keywords": keywords,
        "relevance": "Requires Job Description"
    }


# =========================================================
# MAIN RESUME ANALYZER
# =========================================================

def analyze_resume(
    text,
    job_description=None
):

    if not text or not text.strip():

        return {
            "success": False,
            "message": "Resume text is empty."
        }

    # -----------------------------------------------------
    # Extract sections
    # -----------------------------------------------------

    sections = extract_sections(
        text
    )

    # -----------------------------------------------------
    # Skills
    # -----------------------------------------------------

    skills = extract_skills(
        text
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    summary = analyze_summary(
        sections.get(
            "summary",
            ""
        )
    )

    # -----------------------------------------------------
    # Job description matching
    # -----------------------------------------------------

    relevance = "Not Evaluated"

    if job_description:

        resume_words = set(
            extract_keywords(text)
        )

        job_words = set(
            extract_keywords(
                job_description
            )
        )

        if job_words:

            matched = (
                resume_words
                .intersection(job_words)
            )

            relevance = {
                "matched_keywords": sorted(
                    matched
                ),
                "match_percentage": round(
                    (
                        len(matched)
                        / len(job_words)
                    ) * 100,
                    2
                )
            }

    summary["relevance"] = relevance

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return {

        "success": True,

        # =============================================
        # 1. CONTACT INFORMATION
        # =============================================

        "contact_information": {

            "name": extract_name(text),

            "email": extract_email(text),

            "phone": extract_phone(text),

            "linkedin": extract_linkedin(text),

            "github": extract_github(text)
        },

        # =============================================
        # 2. PROFESSIONAL SUMMARY
        # =============================================

        "professional_summary": summary,

        # =============================================
        # 3. EDUCATION
        # =============================================

        "education": extract_education(
            sections.get(
                "education",
                ""
            )
        ),

        # =============================================
        # 4. TECHNICAL SKILLS
        # =============================================

        "technical_skills": {

            "programming_languages":
                skills[
                    "programming_languages"
                ],

            "frameworks":
                skills[
                    "frameworks"
                ],

            "libraries":
                skills[
                    "libraries"
                ],

            "databases":
                skills[
                    "databases"
                ],

            "tools_and_technologies":
                skills[
                    "tools_and_technologies"
                ],

            "relevant_keywords":
                extract_keywords(
                    sections.get(
                        "skills",
                        ""
                    )
                )
        },

        # =============================================
        # 5. WORK EXPERIENCE
        # =============================================

        "work_experience":
            extract_experience(
                sections.get(
                    "experience",
                    ""
                )
            ),

        # =============================================
        # 6. INTERNSHIPS
        # =============================================

        "internships":
            extract_internships(
                sections.get(
                    "internships",
                    ""
                )
            ),

        # =============================================
        # 7. PROJECTS
        # =============================================

        "projects":
            extract_projects(
                sections.get(
                    "projects",
                    ""
                )
            ),

        # =============================================
        # 8. CERTIFICATIONS
        # =============================================

        "certifications":
            extract_certifications(
                sections.get(
                    "certifications",
                    ""
                )
            ),

        # =============================================
        # 9. ACHIEVEMENTS
        # =============================================

        "achievements":
            extract_achievements(
                sections.get(
                    "achievements",
                    ""
                )
            )
    }