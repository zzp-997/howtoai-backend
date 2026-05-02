-- =============================================
-- 极智协同 - 知识库、任务协作、数据统计迁移 SQL
-- 字段名使用 snake_case 风格
-- MySQL 8 语法
-- =============================================

-- 1. 知识分类表
CREATE TABLE IF NOT EXISTS knowledge_categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '分类名称',
    parent_id INT DEFAULT NULL COMMENT '父分类ID',
    level INT DEFAULT 1 COMMENT '层级',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_by INT COMMENT '创建人ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_parent_id (parent_id),
    INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识分类表';

-- 2. 知识文章表
CREATE TABLE IF NOT EXISTS knowledge_articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL COMMENT '文章标题',
    summary TEXT COMMENT '文章摘要',
    content TEXT COMMENT '文章内容',
    category_id INT COMMENT '分类ID',
    author_id INT COMMENT '作者ID',
    tags TEXT COMMENT '标签，JSON格式',
    view_count INT DEFAULT 0 COMMENT '阅读数',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    status VARCHAR(20) DEFAULT 'draft' COMMENT '状态: draft/published',
    published_at DATETIME COMMENT '发布时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category_id (category_id),
    INDEX idx_author_id (author_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识文章表';

-- 3. 知识文章点赞表
CREATE TABLE IF NOT EXISTS knowledge_article_likes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    article_id INT NOT NULL COMMENT '文章ID',
    user_id INT NOT NULL COMMENT '用户ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_article_id (article_id),
    INDEX idx_user_id (user_id),
    UNIQUE KEY uk_article_user (article_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识文章点赞表';

-- 4. 知识文章阅读记录表
CREATE TABLE IF NOT EXISTS knowledge_article_views (
    id INT PRIMARY KEY AUTO_INCREMENT,
    article_id INT NOT NULL COMMENT '文章ID',
    user_id INT NOT NULL COMMENT '用户ID',
    read_duration INT DEFAULT 0 COMMENT '阅读时长(秒)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_article_id (article_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识文章阅读记录表';

-- 5. 任务表
CREATE TABLE IF NOT EXISTS tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL COMMENT '任务标题',
    description TEXT COMMENT '任务描述',
    priority VARCHAR(20) DEFAULT 'medium' COMMENT '优先级: low/medium/high',
    status VARCHAR(20) DEFAULT 'todo' COMMENT '状态: todo/in_progress/done/closed',
    assignee_ids TEXT COMMENT '负责人ID列表，JSON格式',
    watcher_ids TEXT COMMENT '关注者ID列表，JSON格式',
    due_date VARCHAR(19) COMMENT '截止日期',
    parent_id INT DEFAULT NULL COMMENT '父任务ID',
    project_id INT DEFAULT NULL COMMENT '项目ID',
    tags TEXT COMMENT '标签，JSON格式',
    completed_at DATETIME COMMENT '完成时间',
    created_by INT COMMENT '创建人ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_parent_id (parent_id),
    INDEX idx_project_id (project_id),
    INDEX idx_status (status),
    INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务表';

-- 6. 子任务表
CREATE TABLE IF NOT EXISTS task_subtasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_id INT NOT NULL COMMENT '任务ID',
    title VARCHAR(200) NOT NULL COMMENT '子任务标题',
    completed TINYINT(1) DEFAULT FALSE COMMENT '是否完成',
    assignee_id INT COMMENT '负责人ID',
    due_date VARCHAR(10) COMMENT '截止日期',
    completed_at DATETIME COMMENT '完成时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id),
    INDEX idx_assignee_id (assignee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='子任务表';

-- 7. 任务评论表
CREATE TABLE IF NOT EXISTS task_comments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_id INT NOT NULL COMMENT '任务ID',
    user_id INT NOT NULL COMMENT '用户ID',
    content TEXT NOT NULL COMMENT '评论内容',
    mention_users TEXT COMMENT '@提及的用户ID，JSON格式',
    parent_id INT DEFAULT NULL COMMENT '父评论ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务评论表';

-- 8. 任务动态表
CREATE TABLE IF NOT EXISTS task_activities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_id INT NOT NULL COMMENT '任务ID',
    user_id INT NOT NULL COMMENT '用户ID',
    action_type VARCHAR(30) NOT NULL COMMENT '动作类型',
    action_detail TEXT COMMENT '动作详情，JSON格式',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务动态表';

-- 9. 数据统计导出记录表
CREATE TABLE IF NOT EXISTS stats_exports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    export_type VARCHAR(50) NOT NULL COMMENT '导出类型',
    date_from VARCHAR(10) COMMENT '开始日期',
    date_to VARCHAR(10) COMMENT '结束日期',
    format VARCHAR(10) DEFAULT 'xlsx' COMMENT '导出格式',
    file_path VARCHAR(500) COMMENT '文件路径',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_export_type (export_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据统计导出记录表';

-- =============================================
-- 完成
-- =============================================
