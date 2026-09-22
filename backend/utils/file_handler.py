import os
from werkzeug.utils import secure_filename


def save_resume(file, upload_folder):
    """
    Save an uploaded resume to the specified upload folder.
    """

    filename = secure_filename(file.filename)

    # Create the upload folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)

    # Create the complete file path
    file_path = os.path.join(upload_folder, filename)

    # Save the uploaded file
    file.save(file_path)

    return filename
