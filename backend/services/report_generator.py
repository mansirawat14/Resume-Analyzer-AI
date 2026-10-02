from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


# ============================================================
# RESUMATE BRAND
# ============================================================

NAVY = HexColor("#0B1020")
PURPLE = HexColor("#6366F1")
VIOLET = HexColor("#8B5CF6")
PINK = HexColor("#EC4899")
CYAN = HexColor("#06B6D4")
GREEN = HexColor("#10B981")
ORANGE = HexColor("#F59E0B")
RED = HexColor("#EF4444")

WHITE = colors.white
TEXT = HexColor("#172033")
TEXT_SECONDARY = HexColor("#475569")
TEXT_MUTED = HexColor("#64748B")
BORDER = HexColor("#E2E8F0")
PAGE_BG = HexColor("#F8FAFC")

PURPLE_BG = HexColor("#F1F0FF")
PINK_BG = HexColor("#FDF2F8")
CYAN_BG = HexColor("#ECFEFF")
GREEN_BG = HexColor("#ECFDF5")
ORANGE_BG = HexColor("#FFF7ED")
RED_BG = HexColor("#FEF2F2")


# ============================================================
# SAFE DATA HELPERS
# ============================================================

def safe_text(value, default=""):
    if value is None:
        return default

    if isinstance(value, str):
        return value.strip()

    return str(value)


def list_values(items, key=None):
    """
    Supports both:
        [{"strength": "..."}]
    and:
        ["..."]
    """
    result = []

    for item in items or []:
        if isinstance(item, dict):
            value = item.get(key, "") if key else ""
        else:
            value = item

        value = safe_text(value)

        if value:
            result.append(value)

    return result


def first_non_empty(data, *keys, default=""):
    for key in keys:
        value = data.get(key)

        if value not in (None, ""):
            return safe_text(value)

    return default


# ============================================================
# PAGE DECORATION
# ============================================================

def draw_cover(canvas, doc):
    """Premium ResuMate cover page."""

    canvas.saveState()

    width, height = A4

    # White background
    canvas.setFillColor(WHITE)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)

    # Top-left brand icon
    canvas.setFillColor(PURPLE)
    canvas.roundRect(
        18 * mm,
        height - 25 * mm,
        10 * mm,
        10 * mm,
        2 * mm,
        fill=1,
        stroke=0,
    )

    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(
        23 * mm,
        height - 21.6 * mm,
        "R",
    )

    # Brand
    canvas.setFillColor(TEXT)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(
        31 * mm,
        height - 20.5 * mm,
        "RESUMATE",
    )

    # Top-right label
    canvas.setFillColor(TEXT_MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(
        width - 18 * mm,
        height - 18 * mm,
        "AI Resume Analysis Report",
    )

    # Subtle divider
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.6)
    canvas.line(
        18 * mm,
        height - 30 * mm,
        width - 18 * mm,
        height - 30 * mm,
    )

    # Decorative soft waves / blobs
    canvas.setFillColor(HexColor("#F0EAFE"))

    path = canvas.beginPath()
    path.moveTo(width * 0.43, 0)
    path.curveTo(
        width * 0.62,
        25 * mm,
        width * 0.76,
        17 * mm,
        width,
        55 * mm,
    )
    path.lineTo(width, 0)
    path.close()
    canvas.drawPath(path, fill=1, stroke=0)

    canvas.setFillColor(HexColor("#E5D8FF"))

    path = canvas.beginPath()
    path.moveTo(width * 0.55, 0)
    path.curveTo(
        width * 0.70,
        17 * mm,
        width * 0.86,
        25 * mm,
        width,
        75 * mm,
    )
    path.lineTo(width, 0)
    path.close()
    canvas.drawPath(path, fill=1, stroke=0)

    canvas.setFillColor(HexColor("#F7DDF0"))

    path = canvas.beginPath()
    path.moveTo(width * 0.70, 0)
    path.curveTo(
        width * 0.82,
        15 * mm,
        width * 0.92,
        35 * mm,
        width,
        42 * mm,
    )
    path.lineTo(width, 0)
    path.close()
    canvas.drawPath(path, fill=1, stroke=0)

    # Purple mini accent
    canvas.setFillColor(PURPLE)
    canvas.roundRect(
        18 * mm,
        55 * mm,
        15 * mm,
        1.2 * mm,
        0.6 * mm,
        fill=1,
        stroke=0,
    )

    # Footer
    canvas.setFillColor(PURPLE)
    canvas.roundRect(
        18 * mm,
        12 * mm,
        6 * mm,
        6 * mm,
        1.3 * mm,
        fill=1,
        stroke=0,
    )

    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 5)
    canvas.drawCentredString(
        21 * mm,
        14 * mm,
        "R",
    )

    canvas.setFillColor(TEXT)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(
        27 * mm,
        14 * mm,
        "RESUMATE",
    )

    canvas.restoreState()


def draw_report_page(canvas, doc):
    """Header/footer for all report pages after the cover."""

    canvas.saveState()

    width, height = A4

    canvas.setFillColor(PAGE_BG)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)

    # Header
    canvas.setFillColor(PURPLE)
    canvas.roundRect(
        18 * mm,
        height - 20 * mm,
        7 * mm,
        7 * mm,
        1.5 * mm,
        fill=1,
        stroke=0,
    )

    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 5)
    canvas.drawCentredString(
        21.5 * mm,
        height - 17.5 * mm,
        "R",
    )

    canvas.setFillColor(TEXT)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(
        28 * mm,
        height - 17.2 * mm,
        "RESUMATE",
    )

    canvas.setFillColor(TEXT_MUTED)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawRightString(
        width - 18 * mm,
        height - 17.2 * mm,
        "AI Resume Analysis Report",
    )

    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(
        18 * mm,
        height - 23 * mm,
        width - 18 * mm,
        height - 23 * mm,
    )

    # Footer
    canvas.line(
        18 * mm,
        13 * mm,
        width - 18 * mm,
        13 * mm,
    )

    canvas.setFillColor(TEXT_MUTED)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(
        18 * mm,
        8 * mm,
        "RESUMATE • AI Resume Analyzer",
    )

    canvas.drawRightString(
        width - 18 * mm,
        8 * mm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


# ============================================================
# STYLES
# ============================================================

def make_styles():
    return {
        "cover_title": ParagraphStyle(
            "CoverTitle",
            fontName="Helvetica-Bold",
            fontSize=31,
            leading=34,
            textColor=TEXT,
            alignment=TA_LEFT,
        ),
        "cover_title_accent": ParagraphStyle(
            "CoverAccent",
            fontName="Helvetica-Bold",
            fontSize=31,
            leading=34,
            textColor=PURPLE,
            alignment=TA_LEFT,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=TEXT_SECONDARY,
        ),
        "cover_meta": ParagraphStyle(
            "CoverMeta",
            fontName="Helvetica",
            fontSize=8,
            leading=12,
            textColor=TEXT_SECONDARY,
        ),
        "page_title": ParagraphStyle(
            "PageTitle",
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=25,
            textColor=TEXT,
        ),
        "page_subtitle": ParagraphStyle(
            "PageSubtitle",
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=TEXT_MUTED,
        ),
        "section_title": ParagraphStyle(
            "SectionTitle",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=TEXT,
        ),
        "section_subtitle": ParagraphStyle(
            "SectionSubtitle",
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=TEXT_MUTED,
        ),
        "body": ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=TEXT_SECONDARY,
        ),
        "body_small": ParagraphStyle(
            "BodySmall",
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=TEXT_SECONDARY,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=TEXT_SECONDARY,
        ),
        "metric_title": ParagraphStyle(
            "MetricTitle",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=TEXT_MUTED,
        ),
        "metric_value": ParagraphStyle(
            "MetricValue",
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=21,
        ),
        "metric_subtitle": ParagraphStyle(
            "MetricSubtitle",
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=TEXT_MUTED,
        ),
    }


# ============================================================
# CARD BUILDERS
# ============================================================

def metric_card(title, value, subtitle, accent, bg, styles):
    value_style = ParagraphStyle(
        "MetricValueCustom",
        parent=styles["metric_value"],
        textColor=accent,
    )

    content = [
        Paragraph(title.upper(), styles["metric_title"]),
        Spacer(1, 2),
        Paragraph(value, value_style),
        Spacer(1, 1),
        Paragraph(subtitle, styles["metric_subtitle"]),
    ]

    table = Table(
        [[content]],
        colWidths=[40 * mm],
        rowHeights=[31 * mm],
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )

    return table


def bullet_table(items, accent, styles, empty_text="No items available."):
    if not items:
        return Table(
            [[Paragraph(empty_text, styles["body_small"])]],
            colWidths=[155 * mm],
        )

    rows = []

    for item in items:
        dot = Paragraph(
            "●",
            ParagraphStyle(
                "Dot",
                parent=styles["body"],
                fontSize=7,
                textColor=accent,
                alignment=TA_CENTER,
            ),
        )

        rows.append([
            dot,
            Paragraph(safe_text(item), styles["bullet"]),
        ])

    table = Table(
        rows,
        colWidths=[6 * mm, 149 * mm],
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 1 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )

    return table


def section_card(title, subtitle, body, accent, styles):
    """
    A single-column card.

    Important: keep every row to ONE cell. The previous version used
    two cells in the title row while declaring only one column width,
    which caused the PDF content to shift/crop horizontally.
    """

    title_block = [
        Paragraph(
            title,
            styles["section_title"],
        ),
        Spacer(1, 1.5 * mm),
        Paragraph(
            subtitle,
            styles["section_subtitle"],
        ),
    ]

    table = Table(
        [
            [title_block],
            [body],
        ],
        colWidths=[168 * mm],
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), WHITE),
            ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
            ("LINEBEFORE", (0, 0), (0, -1), 3.5, accent),

            ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),

            ("TOPPADDING", (0, 0), (-1, 0), 4 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 2.5 * mm),

            ("TOPPADDING", (0, 1), (-1, 1), 2 * mm),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 5 * mm),

            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )

    return table


# ============================================================
# PROFILE SNAPSHOT
# ============================================================

def profile_snapshot(section_analysis, styles):
    rows = []

    if isinstance(section_analysis, dict):
        iterable = section_analysis.items()
    elif isinstance(section_analysis, list):
        iterable = []

        for item in section_analysis:
            if isinstance(item, dict):
                name = (
                    item.get("section")
                    or item.get("name")
                    or item.get("title")
                    or "Section"
                )
                iterable.append((name, item))
    else:
        iterable = []

    for name, item in iterable:
        if isinstance(item, dict):
            status = (
                item.get("status")
                or item.get("rating")
                or item.get("quality")
                or item.get("message")
                or "Present"
            )
        else:
            status = safe_text(item, "Present")

        name_text = safe_text(name, "Section")
        status_text = safe_text(status, "Present")

        status_color = GREEN

        lower = status_text.lower()

        if any(word in lower for word in ["improve", "weak", "missing", "poor"]):
            status_color = ORANGE

        rows.append([
            Paragraph(name_text, styles["body_small"]),
            Paragraph(
                f'<font color="{status_color.hexval()}">●</font> '
                f'{status_text}',
                styles["body_small"],
            ),
        ])

    if not rows:
        rows = [[
            Paragraph(
                "Section analysis will appear here after analysis.",
                styles["body_small"],
            ),
            "",
        ]]

    table = Table(
        rows,
        colWidths=[95 * mm, 60 * mm],
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 0.35, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 1 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 1 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2.2 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ])
    )

    return table


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_resume_report(analysis_data):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=32 * mm,
        bottomMargin=18 * mm,
        title="ResuMate - AI Resume Analysis Report",
        author="ResuMate",
    )

    styles = make_styles()

    # --------------------------------------------------------
    # Extract real analysis values
    # --------------------------------------------------------

    resume_score = analysis_data.get("resume_score", 0)
    ats_score = analysis_data.get("ats_score", 0)

    resume_health = analysis_data.get("resume_health") or {}

    health_score = resume_health.get("score", 0)
    health_status = resume_health.get("health", "N/A")

    job_match = analysis_data.get("job_match") or {}

    match_percentage = job_match.get("match_percentage")

    issues = list_values(
        analysis_data.get("issues", []),
        "issue",
    )

    strengths = list_values(
        analysis_data.get("top_strengths", []),
        "strength",
    )

    suggestions = list_values(
        analysis_data.get("ai_suggestions", []),
        "suggestion",
    )

    matched_skills = [
        safe_text(x)
        for x in job_match.get("matched_skills", [])
        if safe_text(x)
    ]

    missing_skills = [
        safe_text(x)
        for x in job_match.get("missing_skills", [])
        if safe_text(x)
    ]

    section_analysis = (
        analysis_data.get("section_analysis")
        or {}
    )

    # Flexible support for candidate metadata
    candidate_name = first_non_empty(
        analysis_data,
        "candidate_name",
        "name",
        "full_name",
        default="Candidate",
    )

    target_role = first_non_empty(
        analysis_data,
        "target_role",
        "job_title",
        "role",
        default="Not Specified",
    )

    generated_date = datetime.now().strftime(
        "%d %B %Y"
    )

    # Optional summary
    ai_summary = first_non_empty(
        analysis_data,
        "ai_summary",
        "summary",
        default="Your resume analysis has been completed. "
                "Review the scores, strengths, issues, and "
                "suggestions in this report.",
    )

    story = []

    # ========================================================
    # PAGE 1 — COVER
    # ========================================================

    story.append(Spacer(1, 28 * mm))

    story.append(
        Paragraph(
            "AI RESUME",
            styles["cover_title"],
        )
    )

    story.append(
        Paragraph(
            "ANALYSIS REPORT",
            styles["cover_title_accent"],
        )
    )

    story.append(Spacer(1, 7 * mm))

    story.append(
        Paragraph(
            "Your Resume. Smarter Insights.",
            ParagraphStyle(
                "CoverTagline",
                fontName="Helvetica-Bold",
                fontSize=16,
                leading=20,
                textColor=TEXT,
            ),
        )
    )

    story.append(Spacer(1, 2 * mm))

    story.append(
        Paragraph(
            "Get AI-powered insights into your resume, "
            "understand its strengths, and identify areas "
            "for improvement.",
            styles["cover_subtitle"],
        )
    )

    story.append(Spacer(1, 18 * mm))

    meta_data = [
        [
            Paragraph(
                "<b>Candidate Name</b>",
                styles["cover_meta"],
            ),
            Paragraph(
                safe_text(candidate_name),
                styles["cover_meta"],
            ),
        ],
        [
            Paragraph(
                "<b>Report Generated</b>",
                styles["cover_meta"],
            ),
            Paragraph(
                generated_date,
                styles["cover_meta"],
            ),
        ],
        [
            Paragraph(
                "<b>Target Role</b>",
                styles["cover_meta"],
            ),
            Paragraph(
                safe_text(target_role),
                styles["cover_meta"],
            ),
        ],
    ]

    meta_table = Table(
        meta_data,
        colWidths=[40 * mm, 75 * mm],
        hAlign="LEFT",
    )

    meta_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("LINEBELOW", (0, 0), (-1, -1), 0.35, BORDER),
        ])
    )

    story.append(meta_table)

    story.append(PageBreak())

    # ========================================================
    # PAGE 2 — RESUME OVERVIEW
    # ========================================================

    story.append(
        Paragraph(
            "1. Resume Overview",
            styles["page_title"],
        )
    )

    story.append(
        Paragraph(
            "A quick summary of your resume analysis.",
            styles["page_subtitle"],
        )
    )

    story.append(Spacer(1, 7 * mm))

    job_display = (
        f"{match_percentage}%"
        if match_percentage is not None
        else "N/A"
    )

    cards = Table(
        [[
            metric_card(
                "Resume Score",
                f"{resume_score}/100",
                "Overall Score",
                PURPLE,
                PURPLE_BG,
                styles,
            ),
            metric_card(
                "ATS Score",
                f"{ats_score}/100",
                "ATS Compatibility",
                PINK,
                PINK_BG,
                styles,
            ),
            metric_card(
                "Resume Health",
                f"{health_score}/100",
                safe_text(health_status, "N/A"),
                GREEN,
                GREEN_BG,
                styles,
            ),
            metric_card(
                "Job Match",
                job_display,
                "Target Role Match",
                CYAN,
                CYAN_BG,
                styles,
            ),
        ]],
        colWidths=[
            42 * mm,
            42 * mm,
            42 * mm,
            42 * mm,
        ],
    )

    cards.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 1 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 1 * mm),
        ])
    )

    story.append(cards)
    story.append(Spacer(1, 7 * mm))

    # AI Summary
    story.append(
        section_card(
            "✦  AI Summary",
            "A concise overview of the completed analysis.",
            Paragraph(
                safe_text(ai_summary),
                styles["body"],
            ),
            PURPLE,
            styles,
        )
    )

    story.append(Spacer(1, 7 * mm))

    # Profile Snapshot
    story.append(
        section_card(
            "Profile Snapshot",
            "Detected resume sections and their current status.",
            profile_snapshot(
                section_analysis,
                styles,
            ),
            GREEN,
            styles,
        )
    )

    story.append(PageBreak())

    # ========================================================
    # PAGE 3 — RESUME INSIGHTS
    # ========================================================

    story.append(
        Paragraph(
            "2. Resume Insights",
            styles["page_title"],
        )
    )

    story.append(
        Paragraph(
            "Strengths, issues, and recommendations from your analysis.",
            styles["page_subtitle"],
        )
    )

    story.append(Spacer(1, 7 * mm))

    story.append(
        section_card(
            "Top Strengths",
            "High-impact positive factors identified in your resume.",
            bullet_table(
                strengths,
                GREEN,
                styles,
                "No strengths were returned by the analysis.",
            ),
            GREEN,
            styles,
        )
    )

    story.append(Spacer(1, 7 * mm))

    story.append(
        section_card(
            "Issues Found",
            "Areas that may need attention or improvement.",
            bullet_table(
                issues,
                ORANGE,
                styles,
                "No issues were found.",
            ),
            ORANGE,
            styles,
        )
    )

    story.append(Spacer(1, 7 * mm))

    story.append(
        section_card(
            "AI Suggestions",
            "Actionable recommendations based on the analysis.",
            bullet_table(
                suggestions,
                PURPLE,
                styles,
                "No AI suggestions were returned.",
            ),
            PURPLE,
            styles,
        )
    )

    story.append(PageBreak())

    # ========================================================
    # PAGE 4 — JOB MATCH & SKILLS
    # ========================================================

    story.append(
        Paragraph(
            "3. Job Match & Skills",
            styles["page_title"],
        )
    )

    story.append(
        Paragraph(
            "Resume compatibility and detected skills.",
            styles["page_subtitle"],
        )
    )

    story.append(Spacer(1, 7 * mm))

    job_match_text = (
        f"<b>Job Match Score:</b> "
        f'<font color="{PINK.hexval()}">'
        f"{job_display}"
        f"</font>"
        if match_percentage is not None
        else
        "<b>Job Match:</b> No job description has been analyzed yet."
    )

    story.append(
        section_card(
            "Job Match",
            "How closely your resume matches the selected role.",
            Paragraph(
                job_match_text,
                styles["body"],
            ),
            PINK,
            styles,
        )
    )

    story.append(Spacer(1, 7 * mm))

    story.append(
        section_card(
            "Matching Skills",
            "Skills detected in both the resume and job description.",
            bullet_table(
                matched_skills,
                GREEN,
                styles,
                "No matching skills available.",
            ),
            GREEN,
            styles,
        )
    )

    if missing_skills:
        story.append(Spacer(1, 7 * mm))

        story.append(
            section_card(
                "Missing Skills",
                "Skills detected in the job description but not in the resume.",
                bullet_table(
                    missing_skills,
                    RED,
                    styles,
                    "No missing skills detected.",
                ),
                RED,
                styles,
            )
        )

    # ========================================================
    # BUILD
    # ========================================================

    def first_page(canvas, doc):
        draw_cover(canvas, doc)

    def later_pages(canvas, doc):
        draw_report_page(canvas, doc)

    doc.build(
        story,
        onFirstPage=first_page,
        onLaterPages=later_pages,
    )

    buffer.seek(0)

    return buffer
