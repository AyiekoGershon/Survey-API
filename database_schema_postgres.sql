-- Sky Survey Database Schema - PostgreSQL Version
-- Create database
CREATE DATABASE sky_survey_db;

-- Connect to the database (in psql, use: \c sky_survey_db)
-- For SQL file execution, ensure you're connected to sky_survey_db before running

-- Create ENUM type for question types
CREATE TYPE question_type AS ENUM (
    'short_text',
    'long_text',
    'email',
    'single_choice',
    'multiple_choice',
    'file'
);

-- Surveys Table
CREATE TABLE surveys (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create index on surveys
CREATE INDEX idx_surveys_active ON surveys(is_active);
CREATE INDEX idx_surveys_created_at ON surveys(created_at);

-- Questions Table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    survey_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    type question_type NOT NULL,
    text VARCHAR(500) NOT NULL,
    description TEXT,
    required BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    file_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE,
    CONSTRAINT unique_survey_question UNIQUE (survey_id, name)
);

-- Create indexes on questions
CREATE INDEX idx_questions_survey_id ON questions(survey_id);
CREATE INDEX idx_questions_sort_order ON questions(sort_order);
CREATE INDEX idx_questions_type ON questions(type);

-- Options Table (for choice questions)
CREATE TABLE options (
    id SERIAL PRIMARY KEY,
    question_id INT NOT NULL,
    option_value VARCHAR(255) NOT NULL,
    option_label VARCHAR(255) NOT NULL,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Create indexes on options
CREATE INDEX idx_options_question_id ON options(question_id);
CREATE INDEX idx_options_sort_order ON options(sort_order);

-- Responses Table
CREATE TABLE responses (
    id SERIAL PRIMARY KEY,
    survey_id INT NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE
);

-- Create indexes on responses
CREATE INDEX idx_responses_survey_id ON responses(survey_id);
CREATE INDEX idx_responses_user_email ON responses(user_email);
CREATE INDEX idx_responses_submitted_at ON responses(submitted_at);
CREATE INDEX idx_responses_survey_email ON responses(survey_id, user_email);

-- Answer Texts Table (for text-based questions)
CREATE TABLE answer_texts (
    id SERIAL PRIMARY KEY,
    response_id INT NOT NULL,
    question_id INT NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    CONSTRAINT unique_answer_text UNIQUE (response_id, question_id)
);

-- Create indexes on answer_texts
CREATE INDEX idx_answer_texts_response_id ON answer_texts(response_id);
CREATE INDEX idx_answer_texts_question_id ON answer_texts(question_id);

-- Answer Choices Table (for choice-based questions)
CREATE TABLE answer_choices (
    id SERIAL PRIMARY KEY,
    response_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_values JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    CONSTRAINT unique_answer_choice UNIQUE (response_id, question_id)
);

-- Create indexes on answer_choices
CREATE INDEX idx_answer_choices_response_id ON answer_choices(response_id);
CREATE INDEX idx_answer_choices_question_id ON answer_choices(question_id);

-- Certificates Table (for file uploads)
CREATE TABLE certificates (
    id SERIAL PRIMARY KEY,
    response_id INT NOT NULL,
    filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE
);

-- Create indexes on certificates
CREATE INDEX idx_certificates_response_id ON certificates(response_id);
CREATE INDEX idx_certificates_uploaded_at ON certificates(uploaded_at);

-- Create triggers for updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER surveys_update_timestamp
BEFORE UPDATE ON surveys
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER questions_update_timestamp
BEFORE UPDATE ON questions
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Grant permissions (optional, adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_user;
