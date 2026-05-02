# Approval Request

## ADDED Requirements

### Requirement: User can submit approval request
The system SHALL allow users to submit approval requests for configured business types.

#### Scenario: Submit request with valid chain
- **WHEN** user submits approval request for business_type with active approval chain
- **THEN** system creates approval_request with status='pending' and current_node pointing to first node

#### Scenario: Submit request without chain
- **WHEN** user submits approval request for business_type without approval chain
- **THEN** system returns error indicating no approval chain configured

### Requirement: Approver can approve request
The system SHALL allow designated approvers to approve pending requests.

#### Scenario: Approve single request
- **WHEN** approver approves a pending request
- **THEN** system creates approval_record with action='approve', updates request status and current_node

#### Scenario: Approve last node completes request
- **WHEN** approver approves a request whose current_node is the last node
- **THEN** system sets request status='approved' and completed_at=now

### Requirement: Approver can reject request
The system SHALL allow designated approvers to reject pending requests.

#### Scenario: Reject request
- **WHEN** approver rejects a pending request
- **THEN** system creates approval_record with action='reject', sets request status='rejected' and completed_at=now

### Requirement: User can batch approve requests
The system SHALL allow approvers to approve multiple requests at once.

#### Scenario: Batch approve
- **WHEN** approver batch approves 5 pending requests
- **THEN** system creates approval_records for each and updates all request statuses

#### Scenario: Batch approve with partial failures
- **WHEN** approver batch approves 5 requests but 1 is not approvable (wrong status)
- **THEN** system processes 4 successfully and returns failure for the 5th

### Requirement: User can query own requests
The system SHALL allow users to query their own approval requests with pagination.

#### Scenario: Query own pending requests
- **WHEN** user queries their pending requests
- **THEN** system returns paginated list of user's pending requests

#### Scenario: Query own requests with status filter
- **WHEN** user queries their requests filtered by status='approved'
- **THEN** system returns only user's approved requests
