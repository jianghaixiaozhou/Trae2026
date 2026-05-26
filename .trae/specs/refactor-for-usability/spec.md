# 免费大模型中转服务可用性重构 Spec

## Why
当前项目请求总是失败，前端存在流式响应解析 bug，适配器架构混乱（部分尝试调不存在的 API 再降级为 mock，部分直接 mock），没有真正可用的免费模型接入方式。需要重构使系统真正可用。

## What Changes
- **BREAKING**: 重写适配器架构，统一为「真实请求 → 降级 mock」的可靠模式
- **BREAKING**: 重写前端聊天界面，修复流式响应解析 bug 和消息渲染 bug
- 重写后端主服务，增加模型健康探测、请求超时控制、结构化错误响应
- 新增配置系统，支持通过环境变量配置各平台的免费 API Key（可选）和 mock 模式开关
- 新增 DeepSeek 适配器使用其公开免费 API 端点（无需 API Key 的 chat.deepseek.com 网页端逆向）
- 新增统一的错误处理中间件，返回结构化错误信息而非让前端收到模糊的"请求失败"

## Impact
- Affected code: `main.py`, `config.py`, `adapters/` 全部文件, `static/index.html`
- Affected specs: 无（首次规范）

## ADDED Requirements

### Requirement: 统一适配器架构
系统 SHALL 为每个模型适配器实现统一的三层降级策略：1) 真实 API 请求 → 2) 网页端逆向请求 → 3) 本地 mock 响应。每一层失败后自动降级到下一层，且响应中必须标记来源层级。

#### Scenario: 真实 API 可用
- **WHEN** 适配器配置了有效的 API Key 且目标服务可达
- **THEN** 使用真实 API 获取响应，响应 header 中标记 `X-Response-Source: api`

#### Scenario: API 不可用但网页端可达
- **WHEN** 适配器未配置 API Key 或 API 请求失败，但目标平台网页端可达
- **THEN** 通过模拟网页请求获取响应，响应 header 中标记 `X-Response-Source: web`

#### Scenario: 全部不可用降级为 mock
- **WHEN** 真实 API 和网页端均不可用
- **THEN** 返回本地 mock 响应，响应 header 中标记 `X-Response-Source: mock`，响应内容开头标注 `[模拟响应]`

### Requirement: 前端流式响应正确解析
系统 SHALL 正确解析 SSE 流式响应，逐字显示 AI 回复内容。

#### Scenario: 流式响应正常接收
- **WHEN** 用户发送消息，后端返回 SSE 流式响应
- **THEN** 前端逐字追加显示内容，不覆盖模型标签，不丢失字符

#### Scenario: 流式响应中断
- **WHEN** 流式响应中途断开
- **THEN** 前端显示已接收的内容，并附加「响应中断」提示，不显示"请求失败"

### Requirement: 结构化错误响应
系统 SHALL 在所有错误场景下返回结构化的 JSON 错误响应，包含错误码、错误描述和建议操作。

#### Scenario: 模型不支持
- **WHEN** 请求的 model 参数不在支持列表中
- **THEN** 返回 HTTP 400，body 为 `{"error": {"code": "UNSUPPORTED_MODEL", "message": "不支持的模型: xxx", "suggestion": "可用模型: doubao, baidu, xunfei, kimi, deepseek"}}`

#### Scenario: 上游服务不可用
- **WHEN** 目标模型平台请求超时或连接失败
- **THEN** 返回 HTTP 502，body 为 `{"error": {"code": "UPSTREAM_ERROR", "message": "xxx服务暂时不可用", "suggestion": "请稍后重试或切换其他模型"}}`

### Requirement: 模型健康探测
系统 SHALL 提供 `/v1/models` 接口返回每个模型的可用状态，包括是否可达和响应来源层级。

#### Scenario: 查询模型列表
- **WHEN** 用户请求 GET /v1/models
- **THEN** 返回每个模型的 id、name、description、status（available/unavailable/mock_only）

### Requirement: 配置系统
系统 SHALL 支持通过环境变量和 .env 文件配置各平台参数，包括 API Key（可选）、mock 模式开关、请求超时时间。

#### Scenario: 配置 mock 模式
- **WHEN** 环境变量 `MOCK_MODE=true`
- **THEN** 所有适配器跳过真实请求，直接返回 mock 响应

#### Scenario: 配置 API Key
- **WHEN** 环境变量 `DEEPSEEK_API_KEY=sk-xxx`
- **THEN** DeepSeek 适配器使用该 Key 调用真实 API

### Requirement: 前端聊天界面修复
系统 SHALL 提供可用的聊天界面，修复消息渲染 bug，增加错误状态展示和模型状态指示。

#### Scenario: 发送消息
- **WHEN** 用户输入消息并点击发送
- **THEN** 用户消息显示在右侧，AI 回复逐字流式显示在左侧，模型标签不被覆盖

#### Scenario: 模型状态指示
- **WHEN** 模型选择器中某个模型当前不可用
- **THEN** 该选项显示灰色并标注「不可用」

## MODIFIED Requirements
（无已有需求需要修改，此为首次规范）

## REMOVED Requirements
（无已有需求需要移除）
