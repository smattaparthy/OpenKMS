-- OpenKMS Database Initialization Script
-- This script initializes the PostgreSQL database with basic schema and sample data

-- Enable uuid-ossp extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types for various fields
CREATE TYPE user_role AS ENUM ('EMPLOYEE', 'MANAGER', 'ADMIN');
CREATE TYPE training_status AS ENUM ('DRAFT', 'PUBLISHED', 'ACTIVE', 'COMPLETED', 'CANCELLED');
CREATE TYPE training_type AS ENUM ('ONLINE', 'IN_PERSON', 'HYBRID');
CREATE TYPE registration_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED');

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
        'Headquarters',
        'IT',
        NOW(),
        NOW()
    ),
    (
        '550e8400-e29b-41d4-a716-446655440001',
        'michael',
        'michael.knowledge@openkms.com',
        'Michael Knowledge Manager',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeZeUfkZMBs9kYZP6', -- password123
        'MANAGER',
        true,
        'Headquarters',
        'Knowledge Management',
        NOW(),
        NOW()
    ),
    (
        '550e8400-e29b-41d4-a716-446655440002',
        'emma',
        'emma.employee@openkms.com',
        'Emma Employee',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeZeUfkZMBs9kYZP6', -- password123
        'EMPLOYEE',
        true,
        'Branch Office',
        'Marketing',
        NOW(),
        NOW()
    );

-- Insert sample training programs
INSERT INTO training_programs (
    id, title, description, content, trainer_name, duration_minutes,
    max_participants, training_type, status, created_at, updated_at
) VALUES
    (
        '550e8400-e29b-41d4-a716-446655440010',
        'Introduction to Knowledge Management',
        'Learn the fundamentals of knowledge management systems and best practices',
        'This comprehensive course covers the basics of knowledge management, including documentation standards, information architecture, and collaborative knowledge sharing.',
        'Michael Knowledge',
        180,
        25,
        'ONLINE',
        'PUBLISHED',
        NOW(),
        NOW()
    ),
    (
        '550e8400-e29b-41d4-a716-446655440011',
        'Advanced Document Management',
        'Master advanced document management techniques and version control',
        'Advanced techniques for managing large document repositories, including version control, metadata management, and automated categorization.',
        'Sarah Expert',
        240,
        15,
        'IN_PERSON',
        'PUBLISHED',
        NOW(),
        NOW()
    ),
    (
        '550e8400-e29b-41d4-a716-446655440012',
        'Remote Team Collaboration',
        'Best practices for knowledge sharing in distributed teams',
        'Learn effective strategies for knowledge sharing among remote teams, using modern collaboration tools and methodologies.',
        'David Remote',
        120,
        30,
        'HYBRID',
        'DRAFT',
        NOW(),
        NOW()
    );

-- Insert sample training schedules
INSERT INTO training_schedules (
    id, training_program_id, start_time, end_time, location, is_online_meeting_url,
    meeting_url, status, created_at, updated_at
) VALUES
    (
        '550e8400-e29b-41d4-a716-446655440020',
        '550e8400-e29b-41d4-a716-446655440010',
        '2024-01-15 09:00:00',
        '2024-01-15 12:00:00',
        'Conference Room A',
        false,
        NULL,
        'ACTIVE',
        NOW(),
        NOW()
    ),
    (
        '550e8400-e29b-41d4-a716-446655440021',
        '550e8400-e29b-41d4-a716-446655440011',
        '2024-01-22 14:00:00',
        '2024-01-22 18:00:00',
        'Training Center',
        false,
        NULL,
        'PUBLISHED',
        NOW(),
        NOW()
    ),
    (
        '550e8400-e29b-41d4-a716-446655440022',
        '550e8400-e29b-41d4-a716-446655440012',
        '2024-01-25 10:00:00',
        '2024-01-25 12:00:00',
        'Virtual Classroom',
        true,
        'https://meet.openkms.com/team-collaboration',
        'DRAFT',
        NOW(),
        NOW()
    );

-- Insert sample training registrations
INSERT INTO training_registrations (
    id, training_schedule_id, user_id, status, notes, created_at, updated_at
) VALUES
    (
        '550e8400-e29b-41d4-a716-446655440030',
        '550e8400-e29b-41d4-a716-446655440020',
        '550e8400-e29b-41d4-a716-446655440002',
        'APPROVED',
        'Looking forward to learning about knowledge management basics',
        NOW(),
        NOW()
    ),
    (
        '550e8400-e29b-41d4-a716-446655440031',
        '550e8400-e29b-41d4-a716-446655440021',
        '550e8400-e29b-41d4-a716-446655440001',
        'PENDING',
        'Need approval from line manager',
        NOW(),
        NOW()
    ),
    (
        '550e8400-e29b-41d4-a716-446655440032',
        '550e8400-e29b-41d4-a716-446655440020',
        '550e8400-e29b-41d4-a716-446655440001',
        'APPROVED',
        'Will help assess training quality',
        NOW(),
        NOW()
    );

-- Insert sample training materials
INSERT INTO training_materials (
    id, training_program_id, title, description, file_url, file_type, file_size,
    created_at, updated_at
) VALUES
    (
        '550e8400-e29b-41d4-a716-446655440040',
        '550e8400-e29b-41d4-a716-446655440010',
        'Knowledge Management Guide',
        'Comprehensive guide to knowledge management principles',
        'materials/km-guide.pdf',
        'PDF',
        2048000,
        NOW(),
        NOW()
    ),
    (
        '550e8400-e29b-41d4-a716-446655440041',
        '550e8400-e29b-41d4-a716-446655440010',
        'Best Practices Checklist',
        'Checklist for knowledge management best practices',
        'materials/best-practices.pdf',
        'PDF',
        512000,
        NOW(),
        NOW()
    );

-- Insert sample knowledge articles
INSERT INTO knowledge_articles (
    id, title, content, category, tags, author_id, view_count,
    is_published, created_at, updated_at
) VALUES
    (
        '550e8400-e29b-41d4-a716-446655440050',
        'Getting Started with OpenKMS',
        'Welcome to OpenKMS! This guide will help you understand how to use the system effectively.',
        'Best Practices',
        '["getting-started", "guide", "tutorial"]',
        '550e8400-e29b-41d4-a716-446655440000',
        150,
        true,
        NOW(),
        NOW()
    ),
    (
        '550e8400-e29b-41d4-a716-446655440051',
        'Document Management Best Practices',
        'Learn how to effectively manage documents in OpenKMS with proper organization and version control.',
        'Documentation',
        '["document-management", "best-practices", "organization"]',
        '550e8400-e29b-41d4-a716-446655440001',
        89,
        true,
        NOW(),
        NOW()
    ),
    (
        '550e8400-e29b-41d4-a716-446655440052',
        'Team Collaboration Strategies',
        'Effective strategies for knowledge sharing and collaboration in distributed teams.',
        'Collaboration',
        '["collaboration", "teams", "remote-work"]',
        '550e8400-e29b-41d4-a716-446655440001',
        67,
        true,
        NOW(),
        NOW()
    );

-- Grant proper permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO openkms;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO openkms;