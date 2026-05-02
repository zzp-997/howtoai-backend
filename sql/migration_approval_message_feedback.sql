-- =============================================
-- 极智协同 - 审批模块、消息中心、意见反馈建表 SQL
-- 字段名使用 snake_case 风格
-- MySQL 8 语法
-- =============================================

-- 1. 审批链配置表
CREATE TABLE IF NOT EXISTS approval_chains (
    id INT AUTO_INCREMENT PRIMARY KEY,
    business_type VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_enabled TINYINT(1) DEFAULT 1,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_approval_chains_business_type ON approval_chains(business_type);
CREATE INDEX idx_approval_chains_is_enabled ON approval_chains(is_enabled);

-- 2. 审批节点表
CREATE TABLE IF NOT EXISTS approval_nodes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chain_id INT NOT NULL,
    node_order INT NOT NULL,
    node_type VARCHAR(20) NOT NULL COMMENT 'role/user/department_head',
    node_value TEXT NOT NULL,
    approval_mode VARCHAR(10) NOT NULL COMMENT 'or/and',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chain_id) REFERENCES approval_chains(id) ON DELETE CASCADE
);

CREATE INDEX idx_approval_nodes_chain_id ON approval_nodes(chain_id);

-- 3. 审批申请记录表
CREATE TABLE IF NOT EXISTS approval_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_no VARCHAR(50) NOT NULL UNIQUE,
    business_type VARCHAR(50) NOT NULL,
    chain_id INT,
    applicant_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content JSON,
    attachments JSON,
    current_node_id INT,
    current_approver_id INT,
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/approved/rejected',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (chain_id) REFERENCES approval_chains(id),
    FOREIGN KEY (current_node_id) REFERENCES approval_nodes(id)
);

CREATE INDEX idx_approval_requests_request_no ON approval_requests(request_no);
CREATE INDEX idx_approval_requests_business_type ON approval_requests(business_type);
CREATE INDEX idx_approval_requests_applicant_id ON approval_requests(applicant_id);
CREATE INDEX idx_approval_requests_current_approver_id ON approval_requests(current_approver_id);
CREATE INDEX idx_approval_requests_status ON approval_requests(status);

-- 4. 审批记录表
CREATE TABLE IF NOT EXISTS approval_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    node_id INT NOT NULL,
    approver_id INT NOT NULL,
    approver_name VARCHAR(100),
    action VARCHAR(20) NOT NULL COMMENT 'approve/reject',
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES approval_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (node_id) REFERENCES approval_nodes(id)
);

CREATE INDEX idx_approval_records_request_id ON approval_records(request_id);
CREATE INDEX idx_approval_records_approver_id ON approval_records(approver_id);

-- 5. 催办记录表
CREATE TABLE IF NOT EXISTS approval_reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    requester_id INT NOT NULL,
    reminder_count INT DEFAULT 1,
    last_reminded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES approval_requests(id) ON DELETE CASCADE
);

CREATE INDEX idx_approval_reminders_request_id ON approval_reminders(request_id);
CREATE INDEX idx_approval_reminders_requester_id ON approval_reminders(requester_id);

-- 6. 消息表
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type VARCHAR(20) NOT NULL COMMENT 'approval/system/task',
    title VARCHAR(200) NOT NULL,
    content TEXT,
    related_type VARCHAR(50) COMMENT '关联类型',
    related_id INT COMMENT '关联ID',
    is_read TINYINT(1) DEFAULT 0,
    read_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_type ON messages(type);
CREATE INDEX idx_messages_related_type ON messages(related_type);
CREATE INDEX idx_messages_related_id ON messages(related_id);
CREATE INDEX idx_messages_is_read ON messages(is_read);

-- 7. 意见反馈表
CREATE TABLE IF NOT EXISTS feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    feedback_no VARCHAR(50) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    user_name VARCHAR(100),
    type VARCHAR(20) NOT NULL COMMENT 'suggestion/bug/optimization/other',
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    images JSON COMMENT '图片列表',
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/processing/replied/closed',
    handler_id INT COMMENT '处理人ID',
    handler_name VARCHAR(100) COMMENT '处理人姓名',
    reply_content TEXT COMMENT '回复内容',
    replied_at TIMESTAMP NULL COMMENT '回复时间',
    closed_at TIMESTAMP NULL COMMENT '关闭时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedbacks_feedback_no ON feedbacks(feedback_no);
CREATE INDEX idx_feedbacks_user_id ON feedbacks(user_id);
CREATE INDEX idx_feedbacks_type ON feedbacks(type);
CREATE INDEX idx_feedbacks_status ON feedbacks(status);
CREATE INDEX idx_feedbacks_handler_id ON feedbacks(handler_id);

-- =============================================
-- 完成
-- =============================================
