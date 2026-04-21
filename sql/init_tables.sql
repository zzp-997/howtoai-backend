-- =============================================
-- 极智协同 - MySQL 8 数据库建表 SQL
-- 字段名使用 snake_case 风格
-- =============================================

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    department VARCHAR(100),
    position VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    avatar VARCHAR(255),
    annual_leave_balance FLOAT DEFAULT 0,
    sick_leave_balance FLOAT DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);

-- 2. 会议室表
CREATE TABLE IF NOT EXISTS meeting_rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    capacity INT DEFAULT 10,
    location VARCHAR(200),
    equipment TEXT,
    description TEXT,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 预定记录表
CREATE TABLE IF NOT EXISTS reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    start_time VARCHAR(20) NOT NULL,
    end_time VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES meeting_rooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_reservations_room ON reservations(room_id);
CREATE INDEX idx_reservations_user ON reservations(user_id);

-- 4. 差旅申请表
CREATE TABLE IF NOT EXISTS trips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    destination VARCHAR(200) NOT NULL,
    reason TEXT,
    start_date VARCHAR(10) NOT NULL,
    end_date VARCHAR(10) NOT NULL,
    est_transport_fee FLOAT DEFAULT 0,
    est_accom_fee FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    approval_comment TEXT,
    approved_by INT,
    approved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

CREATE INDEX idx_trips_user ON trips(user_id);
CREATE INDEX idx_trips_status ON trips(status);

-- 5. 请假申请表
CREATE TABLE IF NOT EXISTS leaves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    leave_type VARCHAR(20) NOT NULL,
    start_date VARCHAR(10) NOT NULL,
    end_date VARCHAR(10) NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    approval_comment TEXT,
    approved_by INT,
    approved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

CREATE INDEX idx_leaves_user ON leaves(user_id);
CREATE INDEX idx_leaves_status ON leaves(status);

-- 6. 考勤打卡表
CREATE TABLE IF NOT EXISTS attendances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date VARCHAR(10) NOT NULL,
    check_in_time VARCHAR(10),
    check_out_time VARCHAR(10),
    is_late TINYINT(1) DEFAULT 0,
    is_early_leave TINYINT(1) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'normal',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_attendances_user ON attendances(user_id);
CREATE INDEX idx_attendances_date ON attendances(date);
CREATE UNIQUE INDEX idx_attendances_user_date ON attendances(user_id, date);

-- 7. 补卡申请表
CREATE TABLE IF NOT EXISTS make_up_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date VARCHAR(10) NOT NULL,
    type VARCHAR(20) NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    approved_by INT,
    approved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

CREATE INDEX idx_makeup_user ON make_up_requests(user_id);

-- 8. 考勤配置表
CREATE TABLE IF NOT EXISTS attendance_config (
    `key` VARCHAR(50) PRIMARY KEY,
    value VARCHAR(100)
);

-- 9. 文档分类表
CREATE TABLE IF NOT EXISTS document_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. 文档表
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    file_size INT,
    file_type VARCHAR(50),
    upload_by INT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES document_categories(id),
    FOREIGN KEY (upload_by) REFERENCES users(id)
);

CREATE INDEX idx_documents_category ON documents(category_id);
CREATE INDEX idx_documents_upload ON documents(upload_by);

-- 11. 待办事项表
CREATE TABLE IF NOT EXISTS todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    task_date VARCHAR(10),
    due_date VARCHAR(10),
    status VARCHAR(20) DEFAULT 'pending',
    priority INT DEFAULT 2,
    related_type VARCHAR(50),
    related_id INT,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_todos_user ON todos(user_id);
CREATE INDEX idx_todos_status ON todos(status);

-- 12. 公告通知表
CREATE TABLE IF NOT EXISTS announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    summary VARCHAR(500),
    category VARCHAR(20) DEFAULT 'notice',
    category_label VARCHAR(50),
    is_top TINYINT(1) DEFAULT 0,
    is_remind TINYINT(1) DEFAULT 0,
    publish_time TIMESTAMP NULL,
    read_by TEXT,
    popup_shown TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_announcements_category ON announcements(category);

-- 13. 用户偏好设置表
CREATE TABLE IF NOT EXISTS user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'zh',
    notifications_enabled TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 14. 出差模板表
CREATE TABLE IF NOT EXISTS trip_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    destination VARCHAR(200),
    reason TEXT,
    est_transport_fee FLOAT DEFAULT 0,
    est_accom_fee FLOAT DEFAULT 0,
    use_count INT DEFAULT 0,
    last_used_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_trip_templates_user ON trip_templates(user_id);

-- 15. 城市配置表
CREATE TABLE IF NOT EXISTS city_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    province VARCHAR(100),
    transport_fee_base FLOAT DEFAULT 0,
    accom_fee_base FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. 节假日配置表
CREATE TABLE IF NOT EXISTS holiday_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    date VARCHAR(10) NOT NULL,
    type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 17. 文档查看日志表
CREATE TABLE IF NOT EXISTS document_view_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    user_id INT NOT NULL,
    view_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_doc_view_doc ON document_view_logs(document_id);
CREATE INDEX idx_doc_view_user ON document_view_logs(user_id);

-- 18. 搜索历史表
CREATE TABLE IF NOT EXISTS search_histories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    keyword VARCHAR(200) NOT NULL,
    search_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_search_user ON search_histories(user_id);

-- 19. 报销单表
CREATE TABLE IF NOT EXISTS expense_claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    trip_id INT,
    expenses TEXT,
    total_estimated FLOAT DEFAULT 0,
    total_actual FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    submitted_at TIMESTAMP NULL,
    approved_by INT,
    approved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (trip_id) REFERENCES trips(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

CREATE INDEX idx_expense_user ON expense_claims(user_id);
CREATE INDEX idx_expense_trip ON expense_claims(trip_id);

-- =============================================
-- 完成
-- =============================================
