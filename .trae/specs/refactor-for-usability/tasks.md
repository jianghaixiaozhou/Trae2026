# Tasks

- [x] Task 1: 重写配置系统 `config.py`
  - [x] 1.1: 新增 `MOCK_MODE` 环境变量控制（默认 true，确保开箱即用）
  - [x] 1.2: 新增各平台 API Key 可选配置（`DEEPSEEK_API_KEY`, `KIMI_API_KEY`, `DOUBAO_API_KEY`, `BAIDU_API_KEY`, `XUNFEI_API_KEY`）
  - [x] 1.3: 新增请求超时配置（`REQUEST_TIMEOUT`，默认 30 秒）
  - [x] 1.4: 新增模型元数据注册表（id, name, description, api_url, web_url）

- [x] Task 2: 重写适配器基类 `adapters/base.py`
  - [x] 2.1: 实现三层降级策略框架：`_call_api()` → `_call_web()` → `_mock_response()`
  - [x] 2.2: 统一 `chat()` 和 `chat_stream()` 方法，子类只需实现三层方法
  - [x] 2.3: 增加响应来源标记（api/web/mock）
  - [x] 2.4: 修复 `build_response` 和 `build_stream_chunk` 中 `id` 字段使用时间戳而非对象 id

- [x] Task 3: 重写各平台适配器
  - [x] 3.1: 重写 `adapters/doubao.py`：实现三层降级
  - [x] 3.2: 重写 `adapters/baidu.py`：实现三层降级
  - [x] 3.3: 重写 `adapters/xunfei.py`：实现三层降级
  - [x] 3.4: 重写 `adapters/kimi.py`：实现三层降级
  - [x] 3.5: 重写 `adapters/deepseek.py`：实现三层降级，优先使用免费 API
  - [x] 3.6: 重写 `adapters/__init__.py`：从配置注册表动态构建适配器映射

- [x] Task 4: 重写后端主服务 `main.py`
  - [x] 4.1: 增加结构化错误处理中间件，统一返回 `{error: {code, message, suggestion}}` 格式
  - [x] 4.2: 重写 `/v1/models` 接口，返回模型状态（available/unavailable/mock_only）
  - [x] 4.3: 重写 `/v1/chat/completions`，传递响应来源 header `X-Response-Source`
  - [x] 4.4: 增加请求超时控制
  - [x] 4.5: 移除未使用的 WebSocket 端点（当前不可用，避免误导）

- [x] Task 5: 重写前端界面 `static/index.html`
  - [x] 5.1: 修复 `addMessage` 函数：返回内容 div 而非外层 div，避免 `textContent +=` 覆盖模型标签
  - [x] 5.2: 修复流式响应解析：正确处理跨 chunk 的 SSE 数据拼接
  - [x] 5.3: 增加模型状态指示：从 `/v1/models` 获取状态，不可用模型标注灰色
  - [x] 5.4: 增加错误状态展示：区分网络错误、上游不可用、解析错误等
  - [x] 5.5: 增加响应来源标签：显示当前响应来自 API/Web/Mock
  - [x] 5.6: 增加清空对话按钮

- [x] Task 6: 端到端测试验证
  - [x] 6.1: 启动服务，验证 mock 模式下所有模型可正常对话
  - [x] 6.2: 验证前端流式逐字显示正常
  - [x] 6.3: 验证错误场景（无效模型、超时）返回结构化错误
  - [x] 6.4: 验证 `/v1/models` 返回正确状态

# Task Dependencies
- Task 2 depends on Task 1（基类需要读取配置）
- Task 3 depends on Task 2（适配器继承基类）
- Task 4 depends on Task 3（主服务使用适配器）
- Task 5 depends on Task 4（前端对接后端接口）
- Task 6 depends on Task 5（端到端测试需要前后端都就绪）
