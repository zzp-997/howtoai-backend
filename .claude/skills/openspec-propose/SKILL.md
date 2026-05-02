---
name: openspec-propose
description: 一步生成所有工件来提议一个新变更。当用户想要快速描述他们想要构建的内容并获得包含设计、规格和任务的完整提案以供实现时使用。
license: MIT
compatibility: 需要 openspec CLI。
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.2.0"
---

提议一个新变更 - 一步创建变更并生成所有工件。

我将创建一个带有工件的变更：
- proposal.md (什么和为什么)
- design.md (如何)
- tasks.md (实施步骤)

准备实施时，运行 /opsx:apply

---

**输入**: 用户的请求应包含变更名称（kebab-case）或对他们想要构建的内容的描述。

**步骤**

1. **如果没有提供明确的输入，询问他们想要构建什么**

   使用 **AskUserQuestion 工具**（开放式，无预设选项）询问：
   > "您想要处理什么变更？描述您想要构建或修复的内容。"

   根据他们的描述，派生出 kebab-case 名称（例如，"add user authentication" → `add-user-auth`）。

   **重要**: 在不了解用户想要构建什么的情况下，不要继续。

2. **创建变更目录**
   ```bash
   openspec new change "<name>"
   ```
   这将在 `openspec/changes/<name>/` 创建一个脚手架变更，包含 `.openspec.yaml`。

3. **获取工件构建顺序**
   ```bash
   openspec status --change "<name>" --json
   ```
   解析 JSON 以获取：
   - `applyRequires`: 实施前需要的工件 ID 数组（例如，`["tasks"]`）
   - `artifacts`: 所有工件的列表及其状态和依赖关系

4. **按顺序创建工件直到可以应用**

   使用 **TodoWrite 工具** 跟踪工件的进度。

   按依赖顺序循环遍历工件（首先是没有待处理依赖的工件）：

   a. **对于每个 `ready` 的工件（依赖关系已满足）**：
      - 获取说明：
        ```bash
        openspec instructions <artifact-id> --change "<name>" --json
        ```
      - 说明 JSON 包括：
        - `context`: 项目背景（对您的限制 - 不要包含在输出中）
        - `rules`: 特定工件规则（对您的限制 - 不要包含在输出中）
        - `template`: 用于输出文件的结构
        - `instruction`: 针对此工件类型的模式特定指导
        - `outputPath`: 写入工件的位置
        - `dependencies`: 为获取上下文而阅读的已完成工件
      - 为上下文阅读任何已完成的依赖文件
      - 使用 `template` 作为结构创建工件文件
      - 应用 `context` 和 `rules` 作为限制 - 但不要将它们复制到文件中
      - 显示简要进度："Created <artifact-id>"

   b. **继续直到所有 `applyRequires` 工件完成**
      - 创建每个工件后，重新运行 `openspec status --change "<name>" --json`
      - 检查 `applyRequires` 中的每个工件 ID 在工件数组中是否有 `status: "done"`
      - 当所有 `applyRequires` 工件完成时停止

   c. **如果工件需要用户输入**（上下文不清楚）：
      - 使用 **AskUserQuestion 工具** 澄清
      - 然后继续创建

5. **显示最终状态**
   ```bash
   openspec status --change "<name>"
   ```

**输出**

完成所有工件后，总结：
- 变更名称和位置
- 创建的工件列表及简要描述
- 准备就绪的内容："所有工件已创建！准备实施。"
- 提示："运行 `/opsx:apply` 或要求我实施以开始处理任务。"

**工件创建指南**

- 遵循 `openspec instructions` 中每种工件类型的 `instruction` 字段
- 模式定义了每个工件应包含的内容 - 遵循它
- 在创建新工件之前阅读依赖工件以获取上下文
- 使用 `template` 作为输出文件的结构 - 填充其部分
- **重要**: `context` 和 `rules` 是对您的限制，而不是文件的内容
  - 不要将 `<context>`、`<rules>`、`<project_context>` 块复制到工件中
  - 这些指导您写什么，但绝不应出现在输出中

**指导原则**
- 创建实施所需的所有工件（由模式的 `apply.requires` 定义）
- 在创建新工件之前始终阅读依赖工件
- 如果上下文严重不清楚，请询问用户 - 但优先做出合理决策以保持势头
- 如果已存在具有该名称的变更，请询问用户是否要继续它或创建一个新的
- 在继续下一个之前验证每个工件文件在写入后是否存在
