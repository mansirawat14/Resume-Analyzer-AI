import subprocess
from datetime import datetime
import os

DB_NAME = "resumate_db"
DB_USER = "root"


def backup_database():
    backup_folder = os.path.dirname(os.path.abspath(__file__))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(
        backup_folder,
        f"{DB_NAME}_backup_{timestamp}.sql"
    )

    command = [
        "mysqldump",
        "-u", DB_USER,
        "-p",
        DB_NAME
    ]

    with open(backup_file, "w") as file:
        subprocess.run(command, stdout=file, check=True)

    print(f"Backup created: {backup_file}")


if __name__ == "__main__":
    backup_database()