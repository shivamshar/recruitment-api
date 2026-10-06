# Recruitment API

A production-style Recruitment / Applicant Tracking System backend built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT authentication, Pytest, and Docker.

The purpose of this project is not just to build a working API, but to understand backend architecture, relational databases, authentication, authorization, testing, migrations, deployment, and production-style development practices.

---

# Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT Authentication
- Pytest
- Docker / Docker Compose
- Redis — planned
- Background Jobs — planned
- GitHub Actions — planned
- Render — planned

---

# User Roles

The application currently supports three roles:

- Candidate
- Recruiter
- Admin

Roles are implemented using a Python Enum and stored in PostgreSQL.

### Candidate

Candidates can:

- Register through the public user registration endpoint
- Login
- View their authenticated user information
- Apply to jobs
- Submit an optional cover letter
- Be prevented from applying to the same job more than once

### Recruiter

Recruiters can:

- Login using JWT authentication
- Access recruiter-only routes
- Create a company
- Be associated with one company
- Create jobs for their company
- View applications submitted to jobs they created
- Update application statuses

Recruiter accounts cannot currently be created through public registration. They are created by an Admin.

### Admin

Admins can:

- Login
- Access admin-only routes
- Create recruiter accounts

The first admin account is created using a bootstrap script rather than through a public API endpoint.

---

# Project Structure

The application is separated into routers and backend modules roughly like:

```text
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── oauth2.py
├── utils.py
└── routers/
    ├── users.py
    ├── auth.py
    ├── admin.py
    ├── companies.py
    ├── jobs.py
    └── applications.py

scripts/
└── create_admin.py

tests/
├── conftest.py
├── test_users.py
├── test_login.py
├── test_jobs.py
└── test_applications.py
```

---

# Database

PostgreSQL is used as the main relational database.

The development PostgreSQL instance runs through Docker.

A separate PostgreSQL container/database is used for Pytest so that tests never modify development data.

Current core database entities include:

- Users
- Companies
- Jobs
- Applications

Interviews are the next entity being implemented.

---

# Users

The `users` table currently stores information such as:

```text
id
email
username
password
role
company_id
created_at
```

Passwords are never stored as plaintext.

Passwords are hashed using `pwdlib`.

Public account registration automatically creates a user with the:

```text
CANDIDATE
```

role.

Users cannot assign themselves recruiter or admin privileges through public registration.

Duplicate email addresses and usernames are rejected.

---

# Authentication

Authentication is implemented using JWT access tokens.

The login flow works as follows:

```text
User submits email/password
        ↓
Password is verified against stored hash
        ↓
JWT access token is generated
        ↓
Token is returned to client
        ↓
Client sends token using Authorization header
```

Protected routes expect:

```http
Authorization: Bearer <access_token>
```

The JWT contains the user identity and has an expiration time.

JWT configuration such as the secret key, algorithm, and expiry duration is stored in environment variables rather than hardcoded in the application.

---

# Current User

A reusable authentication dependency retrieves the logged-in user.

The flow is:

```text
Bearer token
↓
verify_access_token()
↓
extract user ID
↓
query users table
↓
return authenticated User
```

A `/users/me` endpoint can return information about the currently authenticated user.

---

# Role-Based Authorization

A reusable `required_role()` dependency is implemented.

This allows routes to specify which roles are permitted.

Example concept:

```text
required_role(RECRUITER)
```

The authorization layer distinguishes between:

```text
401 Unauthorized
```

when authentication is missing or invalid,

and:

```text
403 Forbidden
```

when the user is authenticated but does not have permission to perform an action.

---

# Admin Bootstrap

The first admin cannot be created through a public endpoint.

A one-time script exists:

```text
scripts/create_admin.py
```

This script:

- Takes admin credentials
- Hashes the password
- Creates a User
- Assigns the ADMIN role
- Stores the account in PostgreSQL

The script is run using:

```bash
python -m scripts.create_admin
```

---

# Admin Features

An authenticated admin can create recruiter accounts.

The recruiter creation route:

- Requires an Admin JWT
- Checks duplicate email
- Checks duplicate username
- Hashes the password
- Creates the user with the RECRUITER role

Candidates and recruiters cannot access this route.

---

# Companies

A Company model has been created.

Current company fields include:

```text
id
name
description
website
location
created_at
```

Users also contain:

```text
company_id
```

which references:

```text
companies.id
```

Current architecture intentionally keeps the relationship simple:

```text
One Recruiter → One Company
```

A recruiter can create a company and their `company_id` is automatically updated to reference the created company.

Duplicate company names are rejected.

---

# Jobs

A Job model has been implemented.

Current fields include:

```text
id
title
description
location
employment_type
company_id
created_by
created_at
```

Relationships:

```text
jobs.company_id → companies.id
jobs.created_by → users.id
```

A recruiter must belong to a company before creating a job.

When a recruiter creates a job:

```text
company_id = current_user.company_id
created_by = current_user.id
```

This prevents recruiters from manually choosing another company or pretending another recruiter created the job.

Job responses also include convenience information such as:

```text
company_name
recruiter_name
```

These values are obtained through SQLAlchemy relationships rather than duplicated as database columns.

---

# Applications

Candidates can apply to jobs.

Current Application fields include:

```text
id
candidate_id
job_id
status
cover_letter
created_at
```

Relationships:

```text
applications.candidate_id → users.id
applications.job_id → jobs.id
```

The same candidate cannot apply to the same job more than once.

This is protected both by application logic and a database-level unique constraint on:

```text
candidate_id + job_id
```

---

# Application Status

Application status is represented using an Enum.

Current statuses include:

```text
applied
screening
interview
offered
rejected
withdrawn
```

New applications automatically begin with:

```text
applied
```

Recruiters can update the status of applications belonging to jobs they created.

A recruiter cannot update applications belonging to another recruiter's jobs.

---

# Recruiter Application Management

Recruiters can retrieve applications for jobs they created.

The backend determines ownership using:

```text
current_user.id
        ↓
jobs.created_by
        ↓
applications.job_id
```

This means the recruiter does not need to manually provide every job ID.

The API can return information including:

```text
application ID
candidate ID
candidate username
job ID
job title
job location
application status
cover letter
```

---

# Response Schemas

Pydantic schemas are used to separate:

```text
Database model
API input
API output
```

For example:

```text
ApplicationCreate
```

defines what a candidate is allowed to send.

The candidate only sends:

```text
job_id
cover_letter
```

The backend determines trusted fields such as:

```text
candidate_id
status
```

from authentication and application logic.

`ApplicationOut` defines the API response contract and can include information combined from several database tables.

---

# Database Migrations

Alembic is configured and working.

Schema changes are created using:

```bash
alembic revision --autogenerate -m "migration description"
```

and applied using:

```bash
alembic upgrade head
```

Migrations have already been used for:

- Users
- Companies
- User → Company relationship
- Jobs
- Applications
- Foreign key constraints
- Unique constraints

Database migrations are manually inspected before being applied.

---

# Docker

PostgreSQL runs through Docker Compose.

The development database uses its own container and persistent volume.

A separate PostgreSQL container is used for automated tests.

Example architecture:

```text
FastAPI Development
        ↓
PostgreSQL Development DB

Pytest
        ↓
PostgreSQL Test DB
```

This prevents tests from modifying real development data.

---

# Testing

Pytest and FastAPI's `TestClient` are being used for automated testing.

A dedicated PostgreSQL test database is used.

FastAPI's normal `get_db` dependency is overridden during tests so API routes automatically use the test database.

The database is reset between tests using an automatic Pytest fixture.

---

# Tests Implemented

## User Tests

Tests currently cover:

- Successful user creation
- Duplicate email
- Duplicate username
- Password hashing
- Password verification
- Password not exposed in API responses
- Invalid registration data

---

## Authentication Tests

Tests cover:

- Successful login
- Incorrect password
- Invalid user
- JWT returned after login
- JWT belongs to correct user
- Current authenticated user
- Invalid/missing authentication

---

## Role Tests

Tests cover:

- Recruiter access to recruiter-only routes
- Candidate denied recruiter routes
- Admin role
- Candidate cannot create recruiters
- Recruiter cannot create recruiters
- Admin can create recruiters

---

## Company Tests

Tests cover:

- Recruiter can create a company
- Candidate cannot create a company
- Duplicate company names
- Recruiter's `company_id` updates after company creation

---

## Job Tests

Tests cover:

- Recruiter with a company can create a job
- Recruiter without a company cannot create a job
- Candidate cannot create a job
- Missing token is rejected
- Correct company is stored
- Correct recruiter is stored
- Company name is returned
- Recruiter name is returned

---

## Application Tests

Tests cover:

- Candidate can apply to a valid job
- Candidate cannot apply twice to the same job
- Invalid job ID returns an error
- Recruiter cannot apply as a candidate
- Authentication protection
- Correct candidate ID is stored
- Correct job ID is stored
- Default application status is stored
- Recruiter can fetch applications for jobs they created
- Recruiter cannot access another recruiter's applications
- Recruiter can update an application's status
- Recruiter cannot update applications belonging to another recruiter
- Updated application status persists in PostgreSQL

---

# Testing Fixtures

Reusable Pytest fixtures have been created for entities including:

```text
candidate_user
recruiter_user
admin_user
company
job
application
```

These fixtures allow tests to build predictable dependency chains such as:

```text
Recruiter
↓
Company
↓
Job
↓
Application
↓
Candidate
```

without repeating setup code in every test.

---

# Current API Flow

The backend currently supports the following end-to-end workflow:

```text
Bootstrap Admin
        ↓
Admin Login
        ↓
Admin Creates Recruiter
        ↓
Recruiter Login
        ↓
Recruiter Creates Company
        ↓
Recruiter Creates Job
        ↓
Candidate Registers
        ↓
Candidate Login
        ↓
Candidate Views/Chooses Job
        ↓
Candidate Applies
        ↓
Recruiter Views Applications
        ↓
Recruiter Updates Application Status
```

---

# Features Intentionally Deferred

## Application Status History

A separate application status history table was considered but intentionally deferred because the current project does not yet need a full audit trail.

The current application row stores only the latest status.

This can be added later if audit/history requirements become important.

---

# Next Feature: Interviews

The next entity to implement is Interviews.

Proposed fields:

```text
id
application_id
scheduled_at
interview_type
location_or_link
notes
created_by
created_at
```

Relationship:

```text
Application
     ↓
Interview
```

An application may eventually have multiple interview rounds.

Planned interview functionality:

- Recruiter schedules an interview
- Only recruiter responsible for the job can schedule it
- Interview is linked to an application
- Candidate can eventually view scheduled interviews
- Recruiter can update or cancel interview details
- Interview endpoints will have automated tests

---

# Remaining Backend Work

After Interviews, the major remaining work includes:

## Job Retrieval Improvements

- Get individual job
- Filtering jobs
- Search by title
- Search by location
- Filter by employment type
- Pagination
- Possibly company-based job filtering

---

## Candidate Features

Potential additions:

- View own applications
- View application status
- Withdraw an application
- View scheduled interviews
- Candidate profile information

---

## Recruiter Features

Potential additions:

- View jobs created by recruiter
- Edit job
- Close/delete job
- View applicants grouped by job
- Filter applications by status
- Schedule interviews
- Update/cancel interviews

---

## Admin Features

Potential additions:

- View users
- Create additional admins
- Disable users
- View companies
- Manage recruiter accounts
- Administrative statistics

---

# Redis

Redis has not yet been implemented.

Possible uses include:

- Caching frequently requested job listings
- Rate limiting
- Background task queues
- Temporary data
- Token/session-related features if needed

---

# Background Jobs

Background task processing is still planned.

Possible examples:

- Sending application confirmation emails
- Interview notification emails
- Recruiter notifications
- Scheduled reminders