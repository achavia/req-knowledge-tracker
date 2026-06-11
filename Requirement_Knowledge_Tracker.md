# Requirement Knowledge Tracker

## Overview

Requirement Knowledge Tracker is a Python-based web application designed to preserve requirement history and improve requirement traceability across a project lifecycle.

Project Managers often send requirement changes through email. A single email may contain multiple requirements affecting different modules, pages, or business processes.

Instead of creating one Trello card per email, the system decomposes the email into individual requirements and creates separate Trello cards while maintaining relationships between related requirements.

The primary goal is to help developers understand previous adjustments made to the same feature before implementing new changes.

---

# Problem Statement

Requirement changes are often communicated through emails such as:

Subject:
Project B Items 05/06/2026

Body:

RSS Page
- Add status filter
- Update export format

Accommodation Page
- Add dismiss button

User Management
- Add lock account feature

A single email contains multiple independent requirements.

Creating one Trello card per email causes several problems:

- Requirement history becomes difficult to track.
- Different features become mixed together.
- Developers may miss previous changes to the same feature.
- Business knowledge becomes fragmented.

---

# Goals

## Primary Goal

Provide requirement traceability across multiple requirement changes.

## Secondary Goals

- Decompose large emails into individual requirements.
- Create one Trello card per requirement.
- Identify related requirements automatically.
- Maintain requirement history.
- Improve developer awareness of previous adjustments.

---

# MVP Features

## Email Input

User provides:

- Email Subject
- Email Body
- Attachments

Supported attachments:

- PDF
- DOCX
- TXT
- PNG
- JPG

## Requirement Decomposition

The system analyzes the email body and identifies separate requirements.

## Requirement Relationship Tracking

The system identifies whether a requirement belongs to an existing feature group.

Example:

Requirement Group: RSS

Related Requirements:

- RSS - Add status filter
- RSS - Add approval workflow
- RSS - Add notification support

## Trello Card Generation

One Trello card is created for each requirement.

## Attachment Support

Attachments are uploaded directly to Trello.

---

# Workflow

Paste Email Subject
→ Paste Email Body
→ Upload Attachments
→ Requirement Decomposition
→ Requirement Group Detection
→ Find Related Requirements
→ Create Trello Cards
→ Attach Requirement History

---

# AI Usage

The AI is NOT used for summarization.

The AI is used for:

- Requirement decomposition
- Feature identification
- Requirement grouping
- Relationship detection

The original email content is preserved without modification.

---

# Technology Stack

Backend:
- Python 3.12+
- FastAPI

Frontend:
- HTML
- Bootstrap
- Jinja2

Database:
- SQLite (MVP)

Project Management:
- Trello API

Deployment:
- Vercel

---

# Success Criteria

- One email can generate multiple Trello cards.
- Related requirements are detected accurately.
- Requirement history is visible from Trello.
- Developers can identify previous feature adjustments easily.
- Original email content is preserved.
- Attachments are uploaded successfully.
