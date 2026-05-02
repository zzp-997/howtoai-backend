# Feedback Module

## ADDED Requirements

### Requirement: User can submit feedback
The system SHALL allow users to submit feedback or suggestions.

#### Scenario: Submit feedback
- **WHEN** user submits feedback with title, content, and category
- **THEN** system creates feedback record with status='submitted' and created_at=now

### Requirement: User can query own feedback
The system SHALL allow users to query their submitted feedback with pagination.

#### Scenario: Query own feedback
- **WHEN** user queries their feedback
- **THEN** system returns paginated list of user's feedback ordered by created_at desc

#### Scenario: Query feedback by status
- **WHEN** user queries feedback filtered by status='replied'
- **THEN** system returns only feedback with matching status

### Requirement: Admin can list all feedback
The system SHALL allow administrators to query all feedback with pagination and filters.

#### Scenario: Admin queries all feedback
- **WHEN** admin queries all feedback
- **THEN** system returns paginated list of all feedback ordered by created_at desc

#### Scenario: Admin filters feedback by category
- **WHEN** admin queries feedback filtered by category='suggestion'
- **THEN** system returns only feedback with matching category

### Requirement: Admin can reply to feedback
The system SHALL allow administrators to reply to user feedback.

#### Scenario: Reply to feedback
- **WHEN** admin submits reply to feedback
- **THEN** system updates feedback with admin_reply, replied_at, and status='replied'

### Requirement: User can query feedback detail
The system SHALL allow users to query feedback detail by ID.

#### Scenario: Query feedback detail
- **WHEN** user queries feedback by id
- **THEN** system returns feedback detail if user is the owner, or error if not
