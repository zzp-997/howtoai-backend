# Audit Service Async

## ADDED Requirements

### Requirement: Login can be logged asynchronously
The system SHALL record login attempts asynchronously without blocking the login API response.

#### Scenario: Successful login logged
- **WHEN** user logs in successfully
- **THEN** system records login log with status='success', user_id, ip_address, and timestamp asynchronously

#### Scenario: Failed login logged
- **WHEN** user login fails due to wrong password
- **THEN** system records login log with status='failed', user_id, ip_address, and failure_reason asynchronously

### Requirement: Operations can be logged asynchronously
The system SHALL record user operations asynchronously.

#### Scenario: Logout logged
- **WHEN** user logs out
- **THEN** system records operation log with action='logout' asynchronously

#### Scenario: Password change logged
- **WHEN** user changes password
- **THEN** system records operation log with action='password_change' asynchronously

### Requirement: Audit service uses async database session
The system SHALL use SQLAlchemy async session for all audit logging operations.

#### Scenario: Async session used for login log
- **WHEN** audit service logs a login attempt
- **THEN** it uses async session with `await db.execute()` and `await db.commit()`

#### Scenario: Async session used for operation log
- **WHEN** audit service logs an operation
- **THEN** it uses async session with `await db.execute()` and `await db.commit()`
