---
name: find-agent
description: 快速查询和推荐合适的 AI 智能体。当用户需要：（1）寻找适合特定任务的智能体，（2）了解某个智能体的用途，（3）按领域/功能查找智能体，（4）询问"哪个智能体适合做X"时使用。
---

# 智能体查询

根据用户需求，快速推荐合适的智能体。

## 快速索引

| 需求 | 推荐智能体 |
|------|-----------|
| 代码审查 | `code-reviewer`, `security-engineer` |
| 架构设计 | `software-architect`, `backend-architect` |
| 前端开发 | `frontend-developer`, `ui-designer` |
| 后端开发 | `backend-architect`, `data-engineer` |
| 移动开发 | `mobile-app-builder` |
| 微信开发 | `wechat-mini-program-developer`, `feishu-integration-developer` |
| 数据库 | `database-optimizer` |
| DevOps | `devops-automator`, `sre` |
| 安全 | `security-engineer`, `threat-detection-engineer` |
| 测试 | `api-tester`, `accessibility-auditor`, `performance-benchmarker` |
| 内容营销 | `content-creator`, `social-media-strategist` |
| 短视频营销 | `douyin-strategist`, `tiktok-strategist`, `bilibili-content-strategist` |
| 电商运营 | `china-ecommerce-operator`, `cross-border-ecommerce-specialist` |
| 中国市场 | `china-market-localization-strategist`, `baidu-seo-specialist` |
| 私域运营 | `private-domain-operator`, `wechat-official-account-manager` |
| 财务管理 | `financial-analyst`, `bookkeeper-controller`, `tax-strategist` |
| 项目管理 | `project-shepherd`, `jira-workflow-steward` |
| 游戏开发 | `game-designer`, `unity-architect`, `godot-gameplay-scripter` |
| 法律合规 | `legal-compliance-checker`, `legal-document-review` |
| 招聘 HR | `recruitment-specialist`, `hr-onboarding` |
| 销售支持 | `sales-engineer`, `deal-strategist`, `outbound-strategist` |
| 文档生成 | `document-generator`, `technical-writer` |

## 分类目录

完整智能体列表参见 [AGENTS_INDEX.md](./references/AGENTS_INDEX.md)，包含以下分类：

- **Academic** — 学术研究（人类学、地理、历史、叙事学、心理学）
- **Design** — 设计（品牌、UI/UX、视觉叙事）
- **Engineering** — 工程开发（前端、后端、DevOps、安全等）
- **Finance** — 财务（会计、分析、税务、投资）
- **Game Development** — 游戏开发（Unity、Unreal、Godot、Roblox）
- **Marketing** — 市场营销（SEO、社交媒体、中国市场营销）
- **Paid Media** — 付费媒体（广告、程序化购买）
- **Product** — 产品管理
- **Project Management** — 项目管理
- **Sales** — 销售
- **Specialized** — 专业服务（法律、医疗、教育等）
- **Spatial Computing** — 空间计算（visionOS、XR）
- **Strategy** — 战略
- **Support** — 支持服务
- **Testing** — 测试

## 使用方法

1. 用户描述需求 → 查询索引表找到匹配智能体
2. 需要详细信息 → 读取 `C:\Users\991138\.claude\agents\<category>\<agent-name>.md`
3. 推荐多个智能体 → 按适用性排序并说明各自优势
