-- 安全模块扩展字段迁移
-- 添加 login_fail_count, locked_until, password_changed_at, password_history 字段

-- 添加 login_fail_count 字段 (连续登录失败次数)
ALTER TABLE users ADD COLUMN IF NOT EXISTS login_fail_count INT DEFAULT 0 COMMENT '连续登录失败次数';

-- 添加 locked_until 字段 (账户锁定截止时间)
ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until DATETIME COMMENT '账户锁定截止时间';

-- 添加 password_changed_at 字段 (密码最后修改时间)
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at DATETIME COMMENT '密码最后修改时间';

-- 添加 password_history 字段 (历史密码哈希列表)
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_history JSON COMMENT '历史密码哈希列表';
