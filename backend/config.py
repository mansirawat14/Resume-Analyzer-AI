import os


class Config:
    # Resumate configuration
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "resumate-development-key"
    )

    # Resume upload settings
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "uploads"
    )

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    ALLOWED_EXTENSIONS = {
        "pdf",
        "docx",
        "txt"
    }
