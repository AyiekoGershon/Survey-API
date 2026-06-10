-- Sky Survey Database Schema
-- Create database
CREATE DATABASE IF NOT EXISTS sky_survey_db;
USE sky_survey_db;

-- Surveys Table
CREATE TABLE surveys (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_active (is_active),
    INDEX idx_created_at (created_at)
);

-- Questions Table
CREATE TABLE questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    survey_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    type ENUM('short_text', 'long_text', 'email', 'single_choice', 'multiple_choice', 'file') NOT NULL,
    text VARCHAR(500) NOT NULL,
    description TEXT,
    required BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    file_properties JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE,
    INDEX idx_survey_id (survey_id),
    INDEX idx_sort_order (sort_order),
    UNIQUE KEY unique_survey_question (survey_id, name)
);

-- Options Table (for choice questions)
CREATE TABLE options (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question_id INT NOT NULL,
    option_value VARCHAR(255) NOT NULL,
    option_label VARCHAR(255) NOT NULL,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_question_id (question_id),
    INDEX idx_sort_order (sort_order)
);

-- Responses Table
CREATE TABLE responses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    survey_id INT NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE,
    INDEX idx_survey_id (survey_id),
    INDEX idx_user_email (user_email),
    INDEX idx_submitted_at (submitted_at)
);

-- Answer Texts Table (for text-based questions)
CREATE TABLE answer_texts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    response_id INT NOT NULL,
    question_id INT NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_response_id (response_id),
    INDEX idx_question_id (question_id),
    UNIQUE KEY unique_response_question (response_id, question_id)
);

-- Answer Choices Table (for choice-based questions)
CREATE TABLE answer_choices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    response_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_values JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_response_id (response_id),
    INDEX idx_question_id (question_id),
    UNIQUE KEY unique_response_question (response_id, question_id)
);

-- Certificates Table (for file uploads)
CREATE TABLE certificates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    response_id INT NOT NULL,
    filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE,
    INDEX idx_response_id (response_id),
    INDEX idx_uploaded_at (uploaded_at)
);

-- Create indexes for common queries
CREATE INDEX idx_responses_survey_email ON responses(survey_id, user_email);
CREATE INDEX idx_questions_type ON questions(type);
