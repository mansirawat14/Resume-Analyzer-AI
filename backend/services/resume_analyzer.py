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

    education = []

    date_pattern = re.compile(
        r"\b(?:19|20)\d{2}\s*[-–—]\s*(?:19|20)\d{2}\b"
        r"|\b(?:19|20)\d{2}\b",
        re.IGNORECASE
    )

    cgpa_pattern = re.compile(
        r"(?:CGPA|GPA)"
        r"\s*[:\-]?\s*[\d.]+"
        r"(?:\s*/\s*[\d.]+)?",
        re.IGNORECASE
    )

    percentage_pattern = re.compile(
        r"(?:Percentage|Percent)"
        r"\s*[:\-]?\s*[\d.]+\s*%?",
        re.IGNORECASE
    )

    degree_keywords = [
        "bca",
        "bachelor",
        "b.tech",
        "btech",
        "b.e",
        "be ",
        "mca",
        "master",
        "m.tech",
        "mtech",
        "mba",
        "b.sc",
        "bsc",
        "m.sc",
        "msc",
        "b.com",
        "bcom",
        "m.com",
        "mcom",
        "phd",
        "diploma"
    ]

    index = 0

    while index < len(lines):

        line = lines[index]

        lower = line.lower()

        # --------------------------------------------------
        # Find degree
        # --------------------------------------------------

        is_degree = any(
            keyword in lower
            for keyword in degree_keywords
        )

        if not is_degree:
            index += 1
            continue

        # --------------------------------------------------
        # DEGREE
        # --------------------------------------------------

        degree = date_pattern.sub(
            "",
            line
        )

        degree = cgpa_pattern.sub(
            "",
            degree
        )

        degree = percentage_pattern.sub(
            "",
            degree
        )

        degree = re.sub(
            r"\s+",
            " ",
            degree
        ).strip()

        # --------------------------------------------------
        # DATES
        # --------------------------------------------------

        dates = date_pattern.findall(line)

        # --------------------------------------------------
        # COLLEGE / UNIVERSITY
        # --------------------------------------------------

        college_university = None

        # Look at the next few lines
        for j in range(
            index + 1,
            min(index + 4, len(lines))
        ):

            nearby = lines[j]

            nearby_lower = nearby.lower()

            # Skip another degree
            if any(
                keyword in nearby_lower
                for keyword in degree_keywords
            ):
                break

            # Remove CGPA / percentage from the line
            college_candidate = cgpa_pattern.sub(
                "",
                nearby
            )

            college_candidate = percentage_pattern.sub(
                "",
                college_candidate
            )

            # Remove dates
            college_candidate = date_pattern.sub(
                "",
                college_candidate
            )

            college_candidate = re.sub(
                r"\s+",
                " ",
                college_candidate
            ).strip()

            if college_candidate:

                college_university = (
                    college_candidate
                )

                break

        # --------------------------------------------------
        # CGPA / PERCENTAGE
        # --------------------------------------------------

        cgpa_percentage = None

        # Search current + nearby lines
        for j in range(
            index,
            min(index + 4, len(lines))
        ):

            nearby = lines[j]

            cgpa_match = cgpa_pattern.search(
                nearby
            )

            if cgpa_match:

                cgpa_percentage = (
                    cgpa_match.group(0)
                )

                break

            percentage_match = (
                percentage_pattern.search(
                    nearby
                )
            )

            if percentage_match:

                cgpa_percentage = (
                    percentage_match.group(0)
                )

                break

        # --------------------------------------------------
        # Remove duplicate dates
        # --------------------------------------------------

        dates = list(
            dict.fromkeys(dates)
        )

        # --------------------------------------------------
        # SAVE EDUCATION
        # --------------------------------------------------

        education.append({

            "degree": degree or None,

            "college_university":
                college_university,

            "cgpa_percentage":
                cgpa_percentage,

            "dates":
                dates

        })

        index += 1

    return education

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

    internships = []

    # Matches:
    # Jan 2026 – Mar 2026
    # May 2026 - Jul 2026
    # 2025 - 2026
    # 2026
    date_pattern = re.compile(
        r"(?:"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\s+\d{4}"
        r"\s*[-–—]\s*"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\s+\d{4}"
        r"|"
        r"\b(?:19|20)\d{2}"
        r"\s*[-–—]\s*"
        r"(?:19|20)\d{2}\b"
        r")",
        re.IGNORECASE
    )

    index = 0

    while index < len(lines):

        line = lines[index]

        lower = line.lower()

        # --------------------------------------------------
        # Find internship entry
        # --------------------------------------------------

        if "intern" not in lower:

            index += 1
            continue

        # --------------------------------------------------
        # ROLE
        # --------------------------------------------------

        role = line

        # --------------------------------------------------
        # Find organization and duration
        # --------------------------------------------------

        organization = None
        duration = None

        date_match = date_pattern.search(line)

        if date_match:

            duration = date_match.group(0)

            # Text before duration
            before_date = line[
                :date_match.start()
            ].strip()

            # Remove separators
            before_date = before_date.rstrip(
                "|-–—"
            ).strip()

            # Try:
            # Python Development Intern – CodeSphere Labs
            role_org_parts = re.split(
                r"\s*[-|–—]\s*",
                before_date,
                maxsplit=1
            )

            if len(role_org_parts) == 2:

                role = role_org_parts[0].strip()

                organization = (
                    role_org_parts[1].strip()
                )

        # --------------------------------------------------
        # If organization wasn't found on same line,
        # look at next few lines
        # --------------------------------------------------

        if organization is None:

            for j in range(
                index + 1,
                min(index + 3, len(lines))
            ):

                nearby = lines[j]

                if date_pattern.search(nearby):
                    continue

                if (
                    "intern" not in
                    nearby.lower()
                ):

                    organization = nearby
                    break

        # --------------------------------------------------
        # If duration wasn't found on same line,
        # search nearby lines
        # --------------------------------------------------

        if duration is None:

            for j in range(
                index,
                min(index + 4, len(lines))
            ):

                nearby = lines[j]

                match = date_pattern.search(
                    nearby
                )

                if match:

                    duration = match.group(0)

                    break

        # --------------------------------------------------
        # RESPONSIBILITIES
        # --------------------------------------------------

        responsibilities = []

        for j in range(
            index + 1,
            min(index + 8, len(lines))
        ):

            current = lines[j]

            lower_current = current.lower()

            # Stop at another section
            if re.match(
                r"^\d+\.\s*",
                current
            ):
                break

            # Skip organization/date information
            if (
                date_pattern.search(current)
                and not is_bullet(current)
            ):
                continue

            # Stop at next internship
            if (
                "intern" in lower_current
                and j != index + 1
            ):
                break

            # Responsibility bullet
            if is_bullet(current):

                responsibilities.append(
                    remove_bullet(current)
                )

        # --------------------------------------------------
        # TECHNOLOGIES
        # --------------------------------------------------

        responsibility_text = " ".join(
            responsibilities
        )

        technologies = extract_technologies(
            responsibility_text
        )

        # --------------------------------------------------
        # SAVE INTERNSHIP
        # --------------------------------------------------

        internships.append({

            "organization":
                organization,

            "role":
                role,

            "duration":
                duration,

            "responsibilities":
                responsibilities,

            "technologies_used":
                technologies

        })

        index += 1

    return internships

# =========================================================
# PROJECTS
# =========================================================

def extract_projects(text):

    if not text:
        return []

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    projects = []

    index = 0

    while index < len(lines):

        line = lines[index]
        lower_line = line.lower()

        # --------------------------------------------------
        # Skip numbered section headings
        # --------------------------------------------------

        if re.match(r"^\d+\.\s*", line):

            index += 1
            continue

        # --------------------------------------------------
        # Skip metadata lines
        # These should never become project names
        # --------------------------------------------------

        if (
            lower_line.startswith("role:")
            or lower_line.startswith("github:")
            or lower_line.startswith("github link:")
            or lower_line.startswith("live:")
            or lower_line.startswith("live link:")
            or lower_line.startswith("link:")
            or lower_line.startswith("technologies:")
            or lower_line.startswith("technology:")
        ):

            index += 1
            continue

        # --------------------------------------------------
        # Find Technologies line belonging to this project
        # --------------------------------------------------

        tech_index = None

        for look_ahead in range(
            index + 1,
            min(index + 8, len(lines))
        ):

            check_line = lines[look_ahead].lower()

            if (
                check_line.startswith("technologies:")
                or check_line.startswith("technology:")
            ):

                tech_index = look_ahead
                break

            # Do not cross another numbered section
            if re.match(
                r"^\d+\.\s*",
                lines[look_ahead]
            ):

                break

        # --------------------------------------------------
        # If no Technologies line was found,
        # this is probably not a project
        # --------------------------------------------------

        if tech_index is None:

            index += 1
            continue

        # --------------------------------------------------
        # PROJECT NAME
        # --------------------------------------------------

        project_name = line

        description_lines = []

        technologies = []

        role = None

        project_link = None

        # --------------------------------------------------
        # DESCRIPTION
        # Everything between project name and Technologies
        # --------------------------------------------------

        for j in range(
            index + 1,
            tech_index
        ):

            current = lines[j]

            if current:
                description_lines.append(
                    remove_bullet(current)
                )

        # --------------------------------------------------
        # TECHNOLOGIES
        # --------------------------------------------------

        tech_line = lines[tech_index]

        tech_text = tech_line.split(
            ":",
            1
        )[1].strip()

        technologies = extract_technologies(
            tech_text
        )

        # --------------------------------------------------
        # ROLE / GITHUB / LIVE LINK
        # --------------------------------------------------

        j = tech_index + 1

        while j < len(lines):

            current = lines[j]

            # Stop at next numbered section
            if re.match(
                r"^\d+\.\s*",
                current
            ):
                break

            lower = current.lower()

            # --------------------------------------------------
            # ROLE
            # --------------------------------------------------

            if lower.startswith("role:"):

                role_text = current.split(
                    ":",
                    1
                )[1].strip()

                # Find GitHub URL inside role line
                github_match = re.search(
                    r"(?:https?://)?(?:www\.)?github\.com/[^\s|]+",
                    role_text,
                    re.IGNORECASE
                )

                if github_match:

                    project_link = (
                        github_match.group(0)
                        .rstrip(".,)")
                    )

                    # Remove URL from role
                    role = re.sub(
                        re.escape(
                            github_match.group(0)
                        ),
                        "",
                        role_text,
                        flags=re.IGNORECASE
                    )

                    # Remove "GitHub:"
                    role = re.sub(
                        r"github\s*:\s*",
                        "",
                        role,
                        flags=re.IGNORECASE
                    )

                    # Remove extra separators
                    role = role.replace(
                        "|",
                        ""
                    ).strip()

                else:

                    role = role_text

            # --------------------------------------------------
            # GITHUB
            # --------------------------------------------------

            elif (
                lower.startswith("github:")
                or lower.startswith("github link:")
            ):

                url_match = re.search(
                    r"(?:https?://)?(?:www\.)?github\.com/[^\s]+",
                    current,
                    re.IGNORECASE
                )

                if url_match:

                    project_link = (
                        url_match.group(0)
                        .rstrip(".,)")
                    )

            # --------------------------------------------------
            # LIVE PROJECT / OTHER LINK
            # --------------------------------------------------

            elif (
                lower.startswith("live:")
                or lower.startswith("live link:")
                or lower.startswith("link:")
            ):

                url_match = re.search(
                    r"https?://[^\s]+|www\.[^\s]+|github\.com/[^\s]+",
                    current,
                    re.IGNORECASE
                )

                if url_match:

                    project_link = (
                        url_match.group(0)
                        .rstrip(".,)")
                    )

            # --------------------------------------------------
            # Check if another project is beginning
            # --------------------------------------------------

            else:

                if (
                    j + 1 < len(lines)
                    and (
                        lines[j + 1]
                        .lower()
                        .startswith("technologies:")
                        or
                        lines[j + 1]
                        .lower()
                        .startswith("technology:")
                    )
                ):
                    break

            j += 1

        # --------------------------------------------------
        # SAVE PROJECT
        # --------------------------------------------------

        projects.append({

            "project_name": project_name,

            "description": (
                " ".join(
                    description_lines
                ).strip()
                or None
            ),

            "technologies_used": technologies,

            "role": role,

            "github_live_link": project_link
        })

        # Continue searching for next project
        index = tech_index + 1

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

# ============================================================
# RESUME SCORE
# ============================================================

def calculate_resume_score(resume_data):
    """
    Calculate overall resume score out of 100.
    """

    score = 0

    # --------------------------------------------------------
    # 1. Contact Information - 10 points
    # --------------------------------------------------------

    contact = resume_data.get(
        "contact_information",
        {}
    )

    contact_fields = [
        "name",
        "email",
        "phone",
        "linkedin",
        "github"
    ]

    filled_contacts = sum(
        1
        for field in contact_fields
        if contact.get(field)
    )

    score += min(
        filled_contacts * 2,
        10
    )

    # --------------------------------------------------------
    # 2. Professional Summary - 10 points
    # --------------------------------------------------------

    summary = resume_data.get(
        "professional_summary",
        {}
    )

    summary_text = summary.get(
        "summary"
    )

    if summary_text:

        word_count = len(
            summary_text.split()
        )

        if word_count >= 20:
            score += 10

        elif word_count >= 10:
            score += 7

        else:
            score += 4

    # --------------------------------------------------------
    # 3. Education - 10 points
    # --------------------------------------------------------

    education = resume_data.get(
        "education",
        []
    )

    if education:
        score += 10

    # --------------------------------------------------------
    # 4. Technical Skills - 20 points
    # --------------------------------------------------------

    skills = resume_data.get(
        "technical_skills",
        {}
    )

    skill_categories = [
        "programming_languages",
        "frameworks",
        "libraries",
        "databases",
        "tools_and_technologies"
    ]

    skill_count = 0

    for category in skill_categories:

        skill_count += len(
            skills.get(
                category,
                []
            )
        )

    if skill_count >= 15:
        score += 20

    elif skill_count >= 10:
        score += 16

    elif skill_count >= 5:
        score += 12

    elif skill_count > 0:
        score += 7

    # --------------------------------------------------------
    # 5. Work Experience - 15 points
    # --------------------------------------------------------

    if resume_data.get(
        "work_experience"
    ):
        score += 15

    # --------------------------------------------------------
    # 6. Internships - 10 points
    # --------------------------------------------------------

    if resume_data.get(
        "internships"
    ):
        score += 10

    # --------------------------------------------------------
    # 7. Projects - 10 points
    # --------------------------------------------------------

    projects = resume_data.get(
        "projects",
        []
    )

    if len(projects) >= 2:
        score += 10

    elif len(projects) == 1:
        score += 7

    # --------------------------------------------------------
    # 8. Certifications - 5 points
    # --------------------------------------------------------

    if resume_data.get(
        "certifications"
    ):
        score += 5

    # --------------------------------------------------------
    # 9. Achievements - 5 points
    # --------------------------------------------------------

    if resume_data.get(
        "achievements"
    ):
        score += 5

    return min(
        score,
        100
    )


# ============================================================
# ATS SCORE
# ============================================================

def calculate_ats_score(resume_data):
    """
    Calculate ATS-style score out of 100.
    """

    score = 0

    # --------------------------------------------------------
    # 1. Contact Information - 15 points
    # --------------------------------------------------------

    contact = resume_data.get(
        "contact_information",
        {}
    )

    contact_fields = [
        "name",
        "email",
        "phone",
        "linkedin",
        "github"
    ]

    filled_contacts = sum(
        1
        for field in contact_fields
        if contact.get(field)
    )

    score += min(
        filled_contacts * 3,
        15
    )

    # --------------------------------------------------------
    # 2. Professional Summary - 10 points
    # --------------------------------------------------------

    summary = resume_data.get(
        "professional_summary",
        {}
    )

    if summary.get("summary"):
        score += 10

    # --------------------------------------------------------
    # 3. Education - 10 points
    # --------------------------------------------------------

    if resume_data.get(
        "education"
    ):
        score += 10

    # --------------------------------------------------------
    # 4. Technical Skills - 25 points
    # --------------------------------------------------------

    skills = resume_data.get(
        "technical_skills",
        {}
    )

    skill_categories = [
        "programming_languages",
        "frameworks",
        "libraries",
        "databases",
        "tools_and_technologies"
    ]

    total_skills = 0

    for category in skill_categories:

        total_skills += len(
            skills.get(
                category,
                []
            )
        )

    if total_skills >= 15:
        score += 25

    elif total_skills >= 10:
        score += 20

    elif total_skills >= 5:
        score += 15

    elif total_skills > 0:
        score += 8

    # --------------------------------------------------------
    # 5. Work Experience - 15 points
    # --------------------------------------------------------

    if resume_data.get(
        "work_experience"
    ):
        score += 15

    # --------------------------------------------------------
    # 6. Projects - 10 points
    # --------------------------------------------------------

    if resume_data.get(
        "projects"
    ):
        score += 10

    # --------------------------------------------------------
    # 7. Certifications - 5 points
    # --------------------------------------------------------

    if resume_data.get(
        "certifications"
    ):
        score += 5

    # --------------------------------------------------------
    # 8. Achievements - 5 points
    # --------------------------------------------------------

    if resume_data.get(
        "achievements"
    ):
        score += 5

    return min(
        score,
        100
    )

# ============================================================
# SUMMARY ANALYSIS
# ============================================================

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

    # Evaluate summary length
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

# ============================================================
# MAIN RESUME ANALYZER
# ============================================================

def analyze_resume(
    text,
    job_description=None
):

    # --------------------------------------------------------
    # Check resume text
    # --------------------------------------------------------

    if not text or not text.strip():

        return {
            "success": False,
            "message": "Resume text is empty."
        }

    # --------------------------------------------------------
    # 1. Extract sections
    # --------------------------------------------------------

    sections = extract_sections(
        text
    )

    # --------------------------------------------------------
    # 2. Extract skills
    # --------------------------------------------------------

    skills = extract_skills(
        text
    )

    # --------------------------------------------------------
    # 3. Analyze summary
    # --------------------------------------------------------

    summary = analyze_summary(
        sections.get(
            "summary",
            ""
        )
    )

    # --------------------------------------------------------
    # 4. Job description matching
    # --------------------------------------------------------

    relevance = "Not Evaluated"

    if job_description:

        resume_words = set(
            extract_keywords(
                text
            )
        )

        job_words = set(
            extract_keywords(
                job_description
            )
        )

        if job_words:

            matched = (
                resume_words
                .intersection(
                    job_words
                )
            )

            relevance = {

                "matched_keywords":
                    sorted(
                        matched
                    ),

                "match_percentage":
                    round(
                        (
                            len(matched)
                            /
                            len(job_words)
                        ) * 100,
                        2
                    )
            }

    summary["relevance"] = relevance

    # ========================================================
    # 5. BUILD FINAL RESULT
    # ========================================================

    result = {

        "success": True,

        # ====================================================
        # 1. CONTACT INFORMATION
        # ====================================================

        "contact_information": {

            "name":
                extract_name(
                    text
                ),

            "email":
                extract_email(
                    text
                ),

            "phone":
                extract_phone(
                    text
                ),

            "linkedin":
                extract_linkedin(
                    text
                ),

            "github":
                extract_github(
                    text
                )
        },

        # ====================================================
        # 2. PROFESSIONAL SUMMARY
        # ====================================================

        "professional_summary":
            summary,

        # ====================================================
        # 3. EDUCATION
        # ====================================================

        "education":
            extract_education(
                sections.get(
                    "education",
                    ""
                )
            ),

        # ====================================================
        # 4. TECHNICAL SKILLS
        # ====================================================

        "technical_skills": {

            "programming_languages":
                skills.get(
                    "programming_languages",
                    []
                ),

            "frameworks":
                skills.get(
                    "frameworks",
                    []
                ),

            "libraries":
                skills.get(
                    "libraries",
                    []
                ),

            "databases":
                skills.get(
                    "databases",
                    []
                ),

            "tools_and_technologies":
                skills.get(
                    "tools_and_technologies",
                    []
                ),

            "relevant_keywords":
                extract_keywords(
                    sections.get(
                        "skills",
                        ""
                    )
                )
        },

        # ====================================================
        # 5. WORK EXPERIENCE
        # ====================================================

        "work_experience":
            extract_experience(
                sections.get(
                    "experience",
                    ""
                )
            ),

        # ====================================================
        # 6. INTERNSHIPS
        # ====================================================

        "internships":
            extract_internships(
                sections.get(
                    "internships",
                    ""
                )
            ),

        # ====================================================
        # 7. PROJECTS
        # ====================================================

        "projects":
            extract_projects(
                sections.get(
                    "projects",
                    ""
                )
            ),

        # ====================================================
        # 8. CERTIFICATIONS
        # ====================================================

        "certifications":
            extract_certifications(
                sections.get(
                    "certifications",
                    ""
                )
            ),

        # ====================================================
        # 9. ACHIEVEMENTS
        # ====================================================

        "achievements":
            extract_achievements(
                sections.get(
                    "achievements",
                    ""
                )
            )
    }

    # ========================================================
    # 6. CALCULATE RESUME SCORE
    # ========================================================

    resume_score = calculate_resume_score(
        result
    )

    # ========================================================
    # 7. CALCULATE ATS SCORE
    # ========================================================

    ats_score = calculate_ats_score(
        result
    )

    # ========================================================
    # 8. ADD SCORES
    # ========================================================

    result["resume_score"] = (
        resume_score
    )

    result["ats_score"] = (
        ats_score
    )

    # ========================================================
    # 9. RETURN RESULT
    # ========================================================

    return result