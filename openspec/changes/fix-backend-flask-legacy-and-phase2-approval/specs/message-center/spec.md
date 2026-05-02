# Message Center

## ADDED Requirements

### Requirement: System can create messages
The system SHALL create messages for users when approval events occur.

#### Scenario: Create message for approval requestor
- **WHEN** approval request status changes
- **THEN** system creates message for the request applicant with related_type='approval_request' and related_id=request_id

### Requirement: User can query messages
The system SHALL allow users to query their messages with pagination.

#### Scenario: Query own messages
- **WHEN** user queries their messages
- **THEN** system returns paginated list of user's messages ordered by created_at desc

#### Scenario: Query unread messages
- **WHEN** user queries messages filtered by is_read=False
- **THEN** system returns only unread messages

### Requirement: User can mark message as read
The system SHALL allow users to mark individual messages as read.

#### Scenario: Mark message as read
- **WHEN** user marks a message as read
- **THEN** system updates message.is_read=True and message.read_at=now

### Requirement: User can batch mark messages as read
The system SHALL allow users to mark all messages as read.

#### Scenario: Batch mark as read
- **WHEN** user marks all messages as read
- **THEN** system updates all user's unread messages with is_read=True and read_at=now

### Requirement: User can get unread count
The system SHALL return the count of unread messages for a user.

#### Scenario: Get unread count
- **WHEN** user requests unread message count
- **THEN** system returns count of messages where user_id matches and is_read=False
