-- 安全模块扩展字段迁移
-- 添加 login_fail_count, locked_until, password_changed_at, password_history 字段
-- MySQL 8.0 兼容版本

-- 添加 login_fail_count 字段 (连续登录失败次数)
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME = 'login_fail_count');
SET @sqlstmt := IF(@exist = 0, 'ALTER TABLE users ADD COLUMN login_fail_count INT DEFAULT 0 COMMENT ''连续登录失败次数''', 'SELECT ''Column login_fail_count already exists''');
PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 locked_until 字段 (账户锁定截止时间)
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME = 'locked_until');
SET @sqlstmt := IF(@exist = 0, 'ALTER TABLE users ADD COLUMN locked_until DATETIME COMMENT ''账户锁定截止时间''', 'SELECT ''Column locked_until already exists''');
PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 password_changed_at 字段 (密码最后修改时间)
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME = 'password_changed_at');
SET @sqlstmt := IF(@exist = 0, 'ALTER TABLE users ADD COLUMN password_changed_at DATETIME COMMENT ''密码最后修改时间''', 'SELECT ''Column password_changed_at already exists''');
PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 password_history 字段 (历史密码哈希列表)
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME = 'password_history');
SET @sqlstmt := IF(@exist = 0, 'ALTER TABLE users ADD COLUMN password_history JSON COMMENT ''历史密码哈希列表''', 'SELECT ''Column password_history already exists''');
PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
