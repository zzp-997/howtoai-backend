-- =============================================
-- 极智协同 - Supabase 数据库建表 SQL
-- 在 Supabase SQL Editor 中执行
-- 注意：用户数据由后端自动初始化
-- =============================================

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    department VARCHAR(100),
    position VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    avatar VARCHAR(255),
    "annualLeaveBalance" FLOAT DEFAULT 0,
    "sickLeaveBalance" FLOAT DEFAULT 0,
    "isActive" BOOLEAN DEFAULT TRUE,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- 2. 会议室表
CREATE TABLE IF NOT EXISTS meeting_rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    capacity INTEGER DEFAULT 10,
    location VARCHAR(200),
    equipment TEXT,
    description TEXT,
    "isActive" BOOLEAN DEFAULT TRUE,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 预定记录表
CREATE TABLE IF NOT EXISTS reservations (
    id SERIAL PRIMARY KEY,
    "roomId" INTEGER NOT NULL REFERENCES meeting_rooms(id),
    "userId" INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    "start" VARCHAR(20) NOT NULL,
    "end" VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed',
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reservations_room ON reservations("roomId");
CREATE INDEX IF NOT EXISTS idx_reservations_user ON reservations("userId");

-- 4. 差旅申请表
CREATE TABLE IF NOT EXISTS trips (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES users(id),
    destination VARCHAR(200) NOT NULL,
    reason TEXT,
    "startDate" VARCHAR(10) NOT NULL,
    "endDate" VARCHAR(10) NOT NULL,
    "estTransportFee" FLOAT DEFAULT 0,
    "estAccomFee" FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    "approvalComment" TEXT,
    "approvedBy" INTEGER REFERENCES users(id),
    "approvedAt" TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trips_user ON trips("userId");
CREATE INDEX IF NOT EXISTS idx_trips_status ON trips(status);

-- 5. 请假申请表
CREATE TABLE IF NOT EXISTS leaves (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES users(id),
    "leaveType" VARCHAR(20) NOT NULL,
    "startDate" VARCHAR(10) NOT NULL,
    "endDate" VARCHAR(10) NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    "approvalComment" TEXT,
    "approvedBy" INTEGER REFERENCES users(id),
    "approvedAt" TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_leaves_user ON leaves("userId");
CREATE INDEX IF NOT EXISTS idx_leaves_status ON leaves(status);

-- 6. 考勤打卡表
CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES users(id),
    date VARCHAR(10) NOT NULL,
    "checkInTime" VARCHAR(10),
    "checkOutTime" VARCHAR(10),
    "isLate" BOOLEAN DEFAULT FALSE,
    "isEarlyLeave" BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'normal',
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_attendances_user ON attendances("userId");
CREATE INDEX IF NOT EXISTS idx_attendances_date ON attendances(date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_attendances_user_date ON attendances("userId", date);

-- 7. 补卡申请表
CREATE TABLE IF NOT EXISTS make_up_requests (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES users(id),
    date VARCHAR(10) NOT NULL,
    type VARCHAR(20) NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    "approvedBy" INTEGER REFERENCES users(id),
    "approvedAt" TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_makeup_user ON make_up_requests("userId");

-- 8. 考勤配置表
CREATE TABLE IF NOT EXISTS attendance_config (
    key VARCHAR(50) PRIMARY KEY,
    value VARCHAR(100)
);

-- 9. 文档分类表
CREATE TABLE IF NOT EXISTS document_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. 文档表
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    "categoryId" INTEGER REFERENCES document_categories(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    "fileSize" INTEGER,
    "fileType" VARCHAR(50),
    "uploadBy" INTEGER REFERENCES users(id),
    tags TEXT,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_documents_category ON documents("categoryId");
CREATE INDEX IF NOT EXISTS idx_documents_upload ON documents("uploadBy");

-- 11. 待办事项表
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    "taskDate" VARCHAR(10),
    "dueDate" VARCHAR(10),
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 2,
    "relatedType" VARCHAR(50),
    "relatedId" INTEGER,
    "completedAt" TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_todos_user ON todos("userId");
CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status);

-- 12. 公告通知表
CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    summary VARCHAR(500),
    category VARCHAR(20) DEFAULT 'notice',
    "categoryLabel" VARCHAR(50),
    "isTop" BOOLEAN DEFAULT FALSE,
    "isRemind" BOOLEAN DEFAULT FALSE,
    "publishTime" TIMESTAMP,
    "readBy" TEXT,
    "popupShown" TEXT,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_announcements_category ON announcements(category);

-- 13. 用户偏好设置表
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL UNIQUE REFERENCES users(id),
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'zh',
    "notificationsEnabled" BOOLEAN DEFAULT TRUE,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. 出差模板表
CREATE TABLE IF NOT EXISTS trip_templates (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    destination VARCHAR(200),
    reason TEXT,
    "estTransportFee" FLOAT DEFAULT 0,
    "estAccomFee" FLOAT DEFAULT 0,
    "useCount" INTEGER DEFAULT 0,
    "lastUsedAt" TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trip_templates_user ON trip_templates("userId");

-- 15. 城市配置表
CREATE TABLE IF NOT EXISTS city_configs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    province VARCHAR(100),
    "transportFeeBase" FLOAT DEFAULT 0,
    "accomFeeBase" FLOAT DEFAULT 0,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. 节假日配置表
CREATE TABLE IF NOT EXISTS holiday_configs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    date VARCHAR(10) NOT NULL,
    type VARCHAR(20),
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 17. 文档查看日志表
CREATE TABLE IF NOT EXISTS document_view_logs (
    id SERIAL PRIMARY KEY,
    "documentId" INTEGER NOT NULL REFERENCES documents(id),
    "userId" INTEGER NOT NULL REFERENCES users(id),
    "viewTime" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_doc_view_doc ON document_view_logs("documentId");
CREATE INDEX IF NOT EXISTS idx_doc_view_user ON document_view_logs("userId");

-- 18. 搜索历史表
CREATE TABLE IF NOT EXISTS search_histories (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES users(id),
    keyword VARCHAR(200) NOT NULL,
    "searchType" VARCHAR(50),
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_search_user ON search_histories("userId");

-- 19. 报销单表
CREATE TABLE IF NOT EXISTS expense_claims (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES users(id),
    "tripId" INTEGER REFERENCES trips(id),
    expenses TEXT,
    "totalEstimated" FLOAT DEFAULT 0,
    "totalActual" FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    "submittedAt" TIMESTAMP,
    "approvedBy" INTEGER REFERENCES users(id),
    "approvedAt" TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_expense_user ON expense_claims("userId");
CREATE INDEX IF NOT EXISTS idx_expense_trip ON expense_claims("tripId");

-- =============================================
-- 完成
-- =============================================
-- 执行完成后，启动后端会自动创建测试用户
