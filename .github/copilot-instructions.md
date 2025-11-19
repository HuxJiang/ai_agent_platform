## 快速背景（大局观）
- 本仓库为 AI Agent 平台参考实现，包含后端（Spring Boot）、前端（Vite + Vue 3）和小程序示例。
- 后端负责 Agent 管理、模型接入与对外 HTTP API；前端为管理控制台的轻量示例（无需后端即可预览）。

## 主要组件与边界
- 后端：`backend/` —— Spring Boot 服务（Java 21、Spring Boot 3.x）。入口：`ProjectApplication.java`。
  - 配置：`backend/src/main/resources/application.yml`（数据库、JWT 默认值、MyBatis 设置）。
  - 安全：`backend/src/main/java/com/example/project/config/SecurityConfig.java`（开发阶段 `anyRequest().permitAll()`，注意生产需改回严格策略）。
  - JWT 工具：`common/utils/JwtUtil.java`（从 Authorization: Bearer header、query 参数读取 token）。
  - 管理员种子：`common/utils/AdminSeeder.java`（通过 JdbcTemplate 写 `admin` 表，注意表结构要求）。
  - 统一返回：`common/api/ApiResponse.java` + `common/api/ResultCode.java`（成功 code=0；错误通常用非 0）。
  - 异常处理：`common/exceptions/GlobalExceptionHandler.java`（将所有异常转换为 ApiResponse），自定义业务异常为 `BusinessException`。

- 前端：`frontend/` —— Vite + Vue3。入口：`frontend/src/main.js`，示例视图：`frontend/src/views/TestView.vue`。

## 构建 / 运行 / 测试（快速可复制命令，Windows PowerShell）
- 启动后端（开发）：在 `backend` 目录运行：

  ```powershell
  cd backend
  .\mvnw.cmd spring-boot:run
  ```

- 打包后端（生成 jar）：

  ```powershell
  cd backend
  .\mvnw.cmd -DskipTests package
  ```

- 运行后端测试：

  ```powershell
  cd backend
  .\mvnw.cmd test
  ```

- 启动前端（开发预览）：在 `frontend` 目录：

  ```powershell
  cd frontend
  npm install
  npm run dev
  ```

## 项目约定与可被复用的模式（给 AI agent 的具体提示）
- 统一响应：所有 Controller/Service 的对外接口应遵循 `ApiResponse<T>` 格式（见 `common/api/ApiResponse.java`）。生成或检查返回值时优先使用 `ApiResponse.ok(...)` / `ApiResponse.fail(...)`。
- 异常处理：抛出业务错误请使用 `BusinessException`（会被 `GlobalExceptionHandler` 捕获并包装成 ApiResponse）；不要直接返回堆栈信息。
- 身份/鉴权：代码中使用 JWT（`JwtUtil`）；agent 生成或解析用户信息时请遵循该工具的行为（Authorization header 优先，备用 query 参数 token）。
- 密码与加密：项目使用 Spring 的 `PasswordEncoder`（`SecurityConfig.passwordEncoder()` 返回 BCrypt）。如果要插入管理员请用 `AdminSeeder.insertAdmin(...)`，不要直接写明文到 DB。
- 数据访问：MyBatis-Plus 被用于 ORM（mapper 路径在 `application.yml` 中配置为 `classpath:mapper/*.xml`）。实体包约定为 `com.example.project.module.*.entity`。

## 外部依赖与集成点（注意事项）
- 数据库：`application.yml` 默认连接到 MySQL `jdbc:mysql://localhost:3306/physical_health_agent_db`，仓库包含默认密码（请在生产/协作前移除或覆盖）。优先使用环境变量覆盖：
  - JWT_SECRET: 覆盖 `jwt.secret`。
  - Spring datasource: `SPRING_DATASOURCE_URL`, `SPRING_DATASOURCE_USERNAME`, `SPRING_DATASOURCE_PASSWORD`。
- API 文档：已集成 springdoc（`/doc.html` 或 `/swagger-ui.html`），这些路由在 `SecurityConfig` 中被白名单允许访问。

## 典型改动点与审查要点（给 PR 检查的 AI agent）
- 配置变更：若修改 `application.yml`，请确保敏感信息不被提交（用占位或 env var）。
- 安全变更：若修改 `SecurityConfig`，确认生产环境下不要保留 `anyRequest().permitAll()`。
- 新增 API：新 Controller 应返回 `ApiResponse`，并在必要时添加异常处理或参数校验注解（`@Valid`），错误信息由 `GlobalExceptionHandler` 统一输出。

## 参考文件（快速跳转）
- 后端入口：`backend/src/main/java/com/example/project/ProjectApplication.java`
- 全局异常：`backend/src/main/java/com/example/project/common/exceptions/GlobalExceptionHandler.java`
- 统一响应：`backend/src/main/java/com/example/project/common/api/ApiResponse.java`
- JWT 工具：`backend/src/main/java/com/example/project/common/utils/JwtUtil.java`
- 管理员种子：`backend/src/main/java/com/example/project/common/utils/AdminSeeder.java`
- 安全配置：`backend/src/main/java/com/example/project/config/SecurityConfig.java`
- 前端入口：`frontend/src/main.js`，视图示例：`frontend/src/views/TestView.vue`

---
如果你想让我把某些地方改得更详细（例如：补充常见 Controller 模板、添加本地 Docker Compose 配置示例，或把敏感配置迁移指南写成脚本），告诉我你想先看哪块，我会迭代更新这个文件。
