# 极智协同 - FastAPI 后端

![Deploy](https://github.com/zzp-997/howtoai-backend/actions/workflows/deploy.yml/badge.svg)

基于 FastAPI + MySQL 的后端服务。

## 项目结构

```
howtoai-backend/
├── app/
│   ├── api/v1/                    # API 路由
│   │   ├── auth.py                # 认证接口
│   │   ├── meeting_rooms.py       # 会议室管理
│   │   ├── reservations.py        # 预定管理
│   │   ├── trips.py               # 差旅申请
│   │   ├── leaves.py              # 请假申请
│   │   ├── attendance.py          # 考勤打卡
│   │   ├── todos.py               # 待办事项
│   │   ├── announcements.py       # 公告通知
│   │   ├── documents.py           # 文档管理
│   │   └── expenses.py            # 报销单
│   ├── core/
│   │   ├── config.py              # 配置管理
│   │   ├── database.py            # 数据库连接
│   │   └── security.py            # JWT 认证
│   ├── models/
│   │   └── models.py              # 数据模型 (19张表)
│   ├── schemas/
│   │   ├── common.py              # 通用响应
│   │   ├── user.py                # 用户相关
│   │   ├── meeting_room.py        # 会议室
│   │   ├── reservation.py         # 预定
│   │   ├── trip.py                # 差旅
│   │   ├── leave.py               # 请假
│   │   ├── attendance.py          # 考勤
│   │   ├── todo.py                # 待办
│   │   ├── announcement.py        # 公告
│   │   ├── document.py            # 文档
│   │   └── expense.py             # 报销
│   ├── services/
│   │   ├── base.py                # 基础 CRUD 服务
│   │   ├── auth_service.py        # 认证服务
│   │   ├── meeting_room_service.py
│   │   ├── reservation_service.py
│   │   ├── trip_service.py
│   │   ├── leave_service.py
│   │   ├── attendance_service.py
│   │   ├── todo_service.py
│   │   ├── announcement_service.py
│   │   ├── document_service.py
│   │   └── expense_service.py
│   └── main.py                    # 应用入口
├── .env                           # 环境配置
├── requirements.txt               # 依赖
└── run.py                         # 启动脚本
```

## API 接口列表

### 认证 `/api/v1/auth`
| 接口 | 方法 | 说明 |
|------|------|------|
| `/login` | POST | 用户登录 |
| `/logout` | POST | 用户登出 |
| `/me` | GET | 获取当前用户信息 |

### 会议室 `/api/v1/meeting-rooms`
| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 获取会议室列表 |
| `/` | POST | 创建会议室 |
| `/{id}` | GET | 获取会议室详情 |
| `/{id}` | PUT | 更新会议室 |
| `/{id}` | DELETE | 删除会议室 |

### 预定 `/api/v1/reservations`
| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 获取预定列表 |
| `/my` | GET | 获取我的预定 |
| `/` | POST | 创建预定 |
| `/check-conflict` | POST | 检查冲突 |
| `/{id}` | PUT | 更新预定 |
| `/{id}` | DELETE | 取消预定 |

### 差旅申请 `/api/v1/trips`
| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 获取差旅列表 |
| `/pending` | GET | 待审批列表 |
| `/` | POST | 创建申请 |
| `/{id}` | PUT | 更新申请 |
| `/{id}/approve` | POST | 审批申请 |
| `/{id}` | DELETE | 删除申请 |

### 请假申请 `/api/v1/leaves`
| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 获取请假列表 |
| `/pending` | GET | 待审批列表 |
| `/` | POST | 创建申请 |
| `/{id}` | PUT | 更新申请 |
| `/{id}/approve` | POST | 审批申请 |
| `/{id}` | DELETE | 删除申请 |

### 考勤打卡 `/api/v1/attendance`
| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 获取考勤记录 |
| `/today` | GET | 今日考勤 |
| `/check-in` | POST | 上班打卡 |
| `/check-out` | POST | 下班打卡 |
| `/stats` | GET | 考勤统计 |
| `/makeup-requests` | GET | 补卡申请列表 |
| `/makeup-requests` | POST | 创建补卡申请 |

### 待办事项 `/api/v1/todos`
| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 获取待办列表 |
| `/upcoming` | GET | 即将到期 |
| `/count` | GET | 未完成数量 |
| `/` | POST | 创建待办 |
| `/{id}` | PUT | 更新待办 |
| `/{id}/toggle` | POST | 切换完成状态 |
| `/{id}` | DELETE | 删除待办 |

### 公告通知 `/api/v1/announcements`
| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 获取公告列表 |
| `/unread` | GET | 未读公告 |
| `/unread-count` | GET | 未读数量 |
| `/{id}` | GET | 获取详情 |
| `/{id}/read` | POST | 标记已读 |
| `/` | POST | 创建公告 |

### 文档管理 `/api/v1/documents`
| 接口 | 方法 | 说明 |
|------|------|------|
| `/categories` | GET | 获取分类 |
| `/` | GET | 获取文档列表 |
| `/` | POST | 上传文档 |
| `/{id}` | GET | 获取详情 |
| `/{id}` | DELETE | 删除文档 |

### 报销单 `/api/v1/expenses`
| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 获取报销单列表 |
| `/` | POST | 创建报销单 |
| `/{id}` | GET | 获取详情 |
| `/{id}` | PUT | 更新报销单 |
| `/{id}/submit` | POST | 提交报销单 |
| `/{id}/approve` | POST | 审批报销单 |
| `/{id}` | DELETE | 删除报销单 |

## 快速开始

### 1. 安装依赖

```bash
cd D:\coderzzp\howtoai-backend
pip install -r requirements.txt
```

### 2. 配置数据库

修改 `.env` 文件，设置 Supabase 数据库连接：

1. 登录 Supabase 控制台：https://supabase.com/dashboard
2. 进入项目 > Settings > Database
3. 复制 Connection string (URI)
4. 替换 `.env` 中的 `DATABASE_URL`

格式示例：
```
DATABASE_URL=postgresql+asyncpg://postgres.xxx:密码@aws-0-region.pooler.supabase.com:6543/postgres
```

### 3. 启动服务

```bash
python run.py
```

或使用 uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 前端对接

修改前端 `.env`:
```
VITE_API_URL=http://localhost:8000
```

## 数据库建表

在 Supabase SQL Editor 中执行建表语句，或让 Supabase 自动创建表结构。

## 部署

推荐使用 Railway、Render 或 Fly.io 部署 FastAPI 后端。