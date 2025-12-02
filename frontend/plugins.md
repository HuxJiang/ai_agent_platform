# 前端插件页面设计文档

## 1. 页面布局设计

### 1.1 整体布局

- 保持与现有页面一致的导航栏和侧边栏结构
- 主内容区分为三个部分：

  1. **插件列表区域**（左侧，占60%）
  2. **插件详情/关联管理区域**（右侧，占40%）

### 1.2 插件列表区域

- 顶部操作栏：
  - 搜索框（按插件名称搜索）
  - 筛选按钮（我的插件/系统插件/全部）
  - "创建插件"按钮
- 插件卡片列表：
  - 显示插件名称、描述、状态（激活/未激活）
  - 显示是否为系统插件标识
  - 每个插件卡片操作按钮：编辑、删除、查看关联

### 1.3 插件详情/关联管理区域

- 默认状态：显示提示信息"选择一个插件查看详情"
- 选中插件后显示：
  - 插件基本信息（名称、描述、UUID、创建时间等）
  - 智能体关联列表（显示关联的智能体及启用状态、优先级）
  - 操作按钮：编辑插件、管理关联

## 2. 功能模块设计

### 2.1 插件列表管理

**功能点：**

- 加载插件列表（区分用户插件和系统插件）
- 搜索和筛选
- 创建新插件
- 编辑插件
- 删除插件（系统插件不可删除）
- 激活/停用插件

**交互流程：**

1. 页面加载时调用获取插件列表API
2. 用户可切换筛选条件查看不同类型插件
3. 点击"创建插件"打开创建弹窗
4. 点击插件卡片，右侧显示详情和关联信息
5. 点击编辑/删除按钮执行相应操作

### 2.2 插件创建/编辑

**功能点：**

- 表单字段：插件名称、描述、OpenAPI规范文件上传
- 表单验证：必填字段、JSON格式验证、OpenAPI规范验证
- 支持编辑已有插件

**交互流程：**

1. 点击"创建插件"打开弹窗
2. 填写基本信息（名称、描述）
3. 上传OpenAPI规范JSON文件
4. 前端验证JSON格式和OpenAPI规范结构
5. 提交创建请求
6. 成功后刷新插件列表

**弹窗设计：**

- 标题：创建插件/编辑插件
- 表单字段：
  - 插件名称（必填，文本输入）
  - 插件描述（可选，文本域）
  - OpenAPI规范（必填，文件上传，限制.json文件）
  - 上传文件后显示文件名和文件大小
- 按钮：取消、确认

### 2.3 插件与智能体关联管理

**功能点：**

- 查看插件关联的智能体列表
- 为插件添加智能体关联
- 启用/禁用关联
- 设置优先级
- 移除关联

**交互流程：**

1. 在插件详情区域显示关联的智能体列表
2. 点击"添加关联"打开智能体选择弹窗
3. 选择智能体后设置优先级和启用状态
4. 在关联列表中可切换启用/禁用状态
5. 可编辑优先级（数字输入）
6. 可移除关联

**关联列表项显示：**

- 智能体名称
- 启用状态开关
- 优先级输入框
- 删除按钮

### 2.4 在智能体编辑页面管理插件关联

**功能点：**

- 在智能体编辑页面添加插件关联管理区域
- 显示已关联的插件列表
- 可以添加/移除插件关联
- 设置启用状态和优先级

**交互流程：**

1. 在AgentEditView中添加"插件关联"区域
2. 显示当前智能体已关联的插件列表
3. 点击"添加插件"打开插件选择弹窗
4. 选择插件并设置优先级和启用状态
5. 在列表中可切换启用状态和编辑优先级

## 3. 状态管理

### 3.1 数据状态

- `plugins`: 插件列表数组
- `selectedPlugin`: 当前选中的插件对象
- `filterType`: 筛选类型（all/my/system）
- `searchKeyword`: 搜索关键词
- `agentList`: 智能体列表（用于关联管理）
- `loading`: 加载状态
- `error`: 错误信息

### 3.2 UI状态

- `showCreateModal`: 显示创建插件弹窗
- `showEditModal`: 显示编辑插件弹窗
- `showAgentSelectModal`: 显示智能体选择弹窗
- `editingPlugin`: 正在编辑的插件对象

## 4. API接口定义

### 4.1 插件管理API

#### 4.1.1 获取插件列表

**端点:** `GET /api/plugin/list`

**查询参数:**

- `page` (可选): 页码，默认1
- `limit` (可选): 每页数量，默认20
- `type` (可选): 筛选类型，all/my/system
- `search` (可选): 搜索关键词

**响应:**

```json
{
  "code": 200,
  "message": "获取插件列表成功",
  "data": {
    "plugins": [
      {
        "id": 1,
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "name": "天气查询服务",
        "description": "提供天气查询功能的API服务",
        "is_active": 1,
        "is_system": 0,
        "user_id": 5,
        "created_at": "2025-01-20T10:00:00",
        "updated_at": "2025-01-20T10:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 10,
      "pages": 1
    }
  },
  "timestamp": 1640995200000
}
```

#### 4.1.2 创建插件

**端点:** `POST /api/plugin/create`

**请求体:** `multipart/form-data`

- `name`: 插件名称（必填）
- `description`: 插件描述（可选）
- `openapi_file`: OpenAPI规范JSON文件（必填）

**响应:**

```json
{
  "code": 200,
  "message": "创建插件成功",
  "data": {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000"
  },
  "timestamp": 1640995200000
}
```

#### 4.1.3 获取插件详情

**端点:** `GET /api/plugin/{pluginId}`

**响应:**

```json
{
  "code": 200,
  "message": "获取插件详情成功",
  "data": {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "天气查询服务",
    "description": "提供天气查询功能的API服务",
    "openapi_spec": {...},
    "is_active": 1,
    "is_system": 0,
    "user_id": 5,
    "created_at": "2025-01-20T10:00:00",
    "updated_at": "2025-01-20T10:00:00"
  },
  "timestamp": 1640995200000
}
```

#### 4.1.4 更新插件

**端点:** `PUT /api/plugin/{pluginId}`

**请求体:** `multipart/form-data`

- `name`: 插件名称（可选）
- `description`: 插件描述（可选）
- `openapi_file`: OpenAPI规范JSON文件（可选）
- `is_active`: 是否激活（可选，0或1）

**响应:**

```json
{
  "code": 200,
  "message": "更新插件成功",
  "timestamp": 1640995200000
}
```

#### 4.1.5 删除插件

**端点:** `DELETE /api/plugin/{pluginId}`

**响应:**

```json
{
  "code": 200,
  "message": "删除插件成功",
  "timestamp": 1640995200000
}
```

### 4.2 插件与智能体关联API

#### 4.2.1 获取插件的智能体关联列表

**端点:** `GET /api/plugin/{pluginId}/agents`

**响应:**

```json
{
  "code": 200,
  "message": "获取关联列表成功",
  "data": {
    "associations": [
      {
        "id": 1,
        "agent_id": 5,
        "agent_name": "智能助手",
        "plugin_id": 1,
        "is_enabled": 1,
        "priority": 0,
        "created_at": "2025-01-20T10:00:00"
      }
    ]
  },
  "timestamp": 1640995200000
}
```

#### 4.2.2 创建插件与智能体关联

**端点:** `POST /api/plugin/{pluginId}/agent`

**请求体:**

```json
{
  "agent_id": 5,
  "is_enabled": 1,
  "priority": 0
}
```

**响应:**

```json
{
  "code": 200,
  "message": "创建关联成功",
  "data": {
    "id": 1
  },
  "timestamp": 1640995200000
}
```

#### 4.2.3 更新插件与智能体关联

**端点:** `PUT /api/plugin/{pluginId}/agent/{associationId}`

**请求体:**

```json
{
  "is_enabled": 1,
  "priority": 5
}
```

**响应:**

```json
{
  "code": 200,
  "message": "更新关联成功",
  "timestamp": 1640995200000
}
```

#### 4.2.4 删除插件与智能体关联

**端点:** `DELETE /api/plugin/{pluginId}/agent/{associationId}`

**响应:**

```json
{
  "code": 200,
  "message": "删除关联成功",
  "timestamp": 1640995200000
}
```

#### 4.2.5 获取智能体的插件关联列表

**端点:** `GET /api/agent/{agentId}/plugins`

**响应:**

```json
{
  "code": 200,
  "message": "获取关联列表成功",
  "data": {
    "associations": [
      {
        "id": 1,
        "agent_id": 5,
        "plugin_id": 1,
        "plugin_name": "天气查询服务",
        "plugin_uuid": "550e8400-e29b-41d4-a716-446655440000",
        "is_enabled": 1,
        "priority": 0,
        "created_at": "2025-01-20T10:00:00"
      }
    ]
  },
  "timestamp": 1640995200000
}
```

#### 4.2.6 为智能体添加插件关联

**端点:** `POST /api/agent/{agentId}/plugin`

**请求体:**

```json
{
  "plugin_id": 1,
  "is_enabled": 1,
  "priority": 0
}
```

**响应:**

```json
{
  "code": 200,
  "message": "创建关联成功",
  "data": {
    "id": 1
  },
  "timestamp": 1640995200000
}
```

## 5. 前端实现文件清单

### 5.1 需要创建/修改的文件

1. **`frontend/src/views/PluginsView.vue`** - 插件管理主页面（修改）
2. **`frontend/src/utils/plugin.js`** - 插件相关API工具（新建）
3. **`frontend/src/utils/api.js`** - 导出插件API（修改）
4. **`frontend/src/views/AgentEditView.vue`** - 添加插件关联管理区域（修改）

### 5.2 关键实现要点

- 文件上传使用 `FormData` 和 `multipart/form-data`
- OpenAPI规范文件验证（JSON格式、OpenAPI 3.0结构）
- 关联管理的双向操作（从插件页面和智能体页面）
- 优先级和启用状态的实时更新

## 6. 错误处理

- API调用失败显示错误提示
- JSON文件格式错误提示
- OpenAPI规范验证失败提示
- 系统插件删除限制提示

