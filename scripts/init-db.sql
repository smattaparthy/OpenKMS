-- OpenKMS Database Initialization Script
-- This script initializes the PostgreSQL database with schema matching SQLAlchemy models

-- Enable uuid-ossp extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types matching the SQLAlchemy models
CREATE TYPE user_role AS ENUM ('EMPLOYEE', 'KNOWLEDGE_MANAGER', 'ADMIN');
CREATE TYPE training_category AS ENUM ('TECHNICAL', 'SOFT_SKILLS', 'COMPLIANCE', 'LEADERSHIP', 'SAFETY');
CREATE TYPE training_level AS ENUM ('BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT');
CREATE TYPE training_status AS ENUM ('DRAFT', 'PUBLISHED', 'CANCELLED', 'COMPLETED');
CREATE TYPE registration_status AS ENUM ('PENDING', 'CONFIRMED', 'WAITLISTED', 'CANCELLED');
CREATE TYPE attendance_status AS ENUM ('PRESENT', 'ABSENT', 'TARDY', 'EARLY_DEPARTURE', 'EXCUSED_ABSENCE');

-- Create users table (matching User SQLAlchemy model)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'EMPLOYEE',
    is_active BOOLEAN NOT NULL DEFAULT true,
    office_location VARCHAR(50),
    department VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create trainings table (matching Training SQLAlchemy model)
CREATE TABLE trainings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category training_category NOT NULL,
    level training_level NOT NULL DEFAULT 'BEGINNER',
    status training_status NOT NULL DEFAULT 'DRAFT',
    location VARCHAR(100) NOT NULL,
    max_participants INTEGER NOT NULL DEFAULT 30,
    current_participants INTEGER NOT NULL DEFAULT 0,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    duration_hours FLOAT NOT NULL,
    credits_required INTEGER NOT NULL DEFAULT 1,
    cost FLOAT NOT NULL DEFAULT 0.0,
    instructor VARCHAR(100),
    prerequisites TEXT,
    learning_objectives TEXT,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create registrations table (matching Registration SQLAlchemy model)
CREATE TABLE registrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    training_id UUID NOT NULL REFERENCES trainings(id),
    status registration_status NOT NULL DEFAULT 'PENDING',
    registration_date TIMESTAMP NOT NULL DEFAULT NOW(),
    confirmed_date TIMESTAMP,
    cancelled_date TIMESTAMP,
    cancellation_reason VARCHAR(500),
    notes VARCHAR(1000),
    special_requirements VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create attendance table (matching Attendance SQLAlchemy model)
CREATE TABLE attendance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    training_id UUID NOT NULL REFERENCES trainings(id),
    registration_id UUID REFERENCES registrations(id),
    status attendance_status NOT NULL,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    hours_attended FLOAT,
    recorded_by UUID REFERENCES users(id),
    notes VARCHAR(1000),
    credits_earned FLOAT NOT NULL DEFAULT 0.0,
    certificate_issued BOOLEAN NOT NULL DEFAULT false,
    certificate_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Insert sample users (passwords are 'password123' for all)
-- In production, use proper password hashing and secure authentication
INSERT INTO users (
    id, username, email, full_name, hashed_password, role, is_active,
    office_location, department, created_at, updated_at
) VALUES
(
    '550e8400-e29b-41d4-a716-446655440000',
    'admin',
    'admin@openkms.com',
    'System Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeZeUfkZMBs9kYZP6', -- password123
    'ADMIN',
    true,
    'Main Office',
    'IT',
    NOW(),
    NOW()
),
(
    '550e8400-e29b-41d4-a716-446655440001',
    'manager',
    'manager@openkms.com',
    'Knowledge Manager',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeZeUfkZMBs9kYZP6', -- password123
    'KNOWLEDGE_MANAGER',
    true,
    'Main Office',
    'Knowledge Management',
    NOW(),
    NOW()
),
(
    '550e8400-e29b-41d4-a716-446655440002',
    'employee',
    'employee@openkms.com',
    'Regular Employee',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeZeUfkZMBs9kYZP6', -- password123
    'EMPLOYEE',
    true,
    'Remote',
    'Operations',
    NOW(),
    NOW()
);

-- Insert sample training programs
INSERT INTO trainings (
    id, title, description, category, level, status, location, max_participants,
    current_participants, start_date, end_date, duration_hours, credits_required,
    cost, instructor, prerequisites, learning_objectives, created_by,
    created_at, updated_at
) VALUES
(
    '550e8400-e29b-41d4-a716-446655440010',
    'Introduction to Knowledge Management',
    'Learn the fundamentals of knowledge management systems and best practices',
    'TECHNICAL', 'BEGINNER', 'PUBLISHED', 'Conference Room A', 25, 0,
    NOW() + INTERVAL '7 days', NOW() + INTERVAL '7 days 4 hours', 4.0, 1, 0.0,
    'System Administrator', 'None', 'Understand KM principles and tools',
    '550e8400-e29b-41d4-a716-446655440000', NOW(), NOW()
),
(
    '550e8400-e29b-41d4-a716-446655440011',
    'Advanced Knowledge Capture Techniques',
    'Advanced methods for capturing and organizing organizational knowledge',
    'TECHNICAL', 'ADVANCED', 'DRAFT', 'Virtual', 15, 0,
    NOW() + INTERVAL '14 days', NOW() + INTERVAL '14 days 6 hours', 6.0, 2, 50.0,
    'Knowledge Manager', 'Basic KM knowledge required', 'Master advanced knowledge capture methods',
    '550e8400-e29b-41d4-a716-446655440001', NOW(), NOW()
),
(
    '550e8400-e29b-41d4-a716-446655440012',
    'Safety Protocols and Procedures',
    'Essential safety training for all employees',
    'SAFETY', 'BEGINNER', 'PUBLISHED', 'Training Facility', 30, 0,
    NOW() + INTERVAL '3 days', NOW() + INTERVAL '3 days 2 hours', 2.0, 1, 0.0,
    'Safety Officer', 'None', 'Understand and apply safety protocols',
    '550e8400-e29b-41d4-a716-446655440000', NOW(), NOW()
);

-- Insert sample registrations
INSERT INTO registrations (
    id, user_id, training_id, status, registration_date, notes, created_at, updated_at
) VALUES
(
    '550e8400-e29b-41d4-a716-446655440100',
    '550e8400-e29b-41d4-a716-446655440001',
    '550e8400-e29b-41d4-a716-446655440010',
    'CONFIRMED',
    NOW(),
    'Looking forward to this training',
    NOW(),
    NOW()
),
(
    '550e8400-e29b-41d4-a716-446655440101',
    '550e8400-e29b-41d4-a716-446655440002',
    '550e8400-e29b-41d4-a716-446655440012',
    'PENDING',
    NOW(),
    'Required safety training',
    NOW(),
    NOW()
);