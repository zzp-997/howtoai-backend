# Approval Chain

## ADDED Requirements

### Requirement: Admin can create approval chain
The system SHALL allow administrators to create approval chains with multiple nodes.

#### Scenario: Create approval chain with single node
- **WHEN** admin creates an approval chain with 1 node (role-based approver)
- **THEN** system creates approval_chain and associated approval_node with correct order

#### Scenario: Create approval chain with multiple nodes
- **WHEN** admin creates an approval chain with 3 nodes (role → department_head → manager)
- **THEN** system creates approval_chain and 3 approval_nodes with sequential node_order

### Requirement: Admin can update approval chain
The system SHALL allow administrators to update existing approval chains.

#### Scenario: Update chain name
- **WHEN** admin updates approval chain name
- **THEN** system updates approval_chain.name and approval_chain.updated_at

#### Scenario: Add node to existing chain
- **WHEN** admin adds a new node to existing chain with 2 nodes
- **THEN** system creates approval_node with node_order=3

### Requirement: Admin can delete approval chain
The system SHALL allow administrators to delete approval chains (cascade deletes nodes).

#### Scenario: Delete chain with nodes
- **WHEN** admin deletes approval chain with 3 nodes
- **THEN** system deletes approval_chain and all associated approval_nodes (CASCADE)

### Requirement: Admin can list approval chains
The system SHALL allow administrators to list all approval chains with pagination.

#### Scenario: List all chains
- **WHEN** admin requests list of approval chains
- **THEN** system returns paginated list of chains with their nodes

#### Scenario: Filter chains by business_type
- **WHEN** admin requests chains filtered by business_type='leave'
- **THEN** system returns only chains with matching business_type

### Requirement: Admin can enable/disable approval chain
The system SHALL allow administrators to enable or disable approval chains.

#### Scenario: Disable chain
- **WHEN** admin sets is_enabled=False for an approval chain
- **THEN** system updates approval_chain.is_enabled and chain cannot be used for new requests

#### Scenario: Enable chain
- **WHEN** admin sets is_enabled=True for an approval chain
- **THEN** system updates approval_chain.is_enabled and chain can be used for new requests
