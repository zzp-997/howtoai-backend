#!/bin/bash
# ============================================
# 数据库迁移脚本
# 用法: ./migrate.sh
# 会执行 sql/migrations/ 下所有未执行过的 SQL 文件
# ============================================

# 迁移记录表
docker exec -i howtoai-mysql mysql -u howtoai -pHowtoai2024 howtoai <<EOF
CREATE TABLE IF NOT EXISTS migration_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL UNIQUE,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF

# 执行迁移
MIGRATION_DIR="/opt/howtoai/sql/migrations"

for sql_file in $(ls $MIGRATION_DIR/*.sql 2>/dev/null | sort); do
    filename=$(basename "$sql_file")

    # 检查是否已执行
    executed=$(docker exec -i howtoai-mysql mysql -u howtoai -pHowtoai2024 howtoai -sN -e "SELECT COUNT(*) FROM migration_log WHERE filename='$filename';")

    if [ "$executed" -eq 0 ]; then
        echo "📤 执行迁移: $filename"
        docker exec -i howtoai-mysql mysql -u howtoai -pHowtoai2024 howtoai < "$sql_file"

        if [ $? -eq 0 ]; then
            docker exec -i howtoai-mysql mysql -u howtoai -pHowtoai2024 howtoai -e "INSERT INTO migration_log (filename) VALUES ('$filename');"
            echo "✅ $filename 执行成功"
        else
            echo "❌ $filename 执行失败"
            exit 1
        fi
    else
        echo "⏩ 跳过已执行: $filename"
    fi
done

echo "🎉 迁移完成"