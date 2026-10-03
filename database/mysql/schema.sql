CREATE DATABASE IF NOT EXISTS resumate_db;

USE resumate_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255),
    name VARCHAR(100),
    email VARCHAR(150),
    phone VARCHAR(30),
    linkedin VARCHAR(255),
    github VARCHAR(255),
    education TEXT,
    skills TEXT,
    experience TEXT,
    projects TEXT,
    certifications TEXT,
    achievements TEXT,
    resume_text LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_title VARCHAR(150),
    company_name VARCHAR(150),
    required_skills TEXT,
    qualification TEXT,
    experience_required VARCHAR(100),
    job_description LONGTEXT,
    location VARCHAR(150),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resume_id INT NOT NULL,
    job_id INT NULL,
    resume_score FLOAT DEFAULT 0,
    ats_score FLOAT DEFAULT 0,
    job_match FLOAT DEFAULT 0,
    resume_health FLOAT DEFAULT 0,
    matched_skills TEXT,
    missing_skills TEXT,
    suggestions TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
        ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
        ON DELETE SET NULL
);