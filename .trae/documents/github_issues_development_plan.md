# 基于 GitHub Issues 的开发计划

## 项目概述
基于 HKUDS/nanobot 项目中的开放 issues 进行开发，重点关注功能增强和性能优化。

## 当前开放的 Issues 分析

### 1. Issue #1645 - vLLM 会话亲和性路由和前缀缓存指导
**状态**: 开放
**优先级**: 高
**复杂度**: 中等

**问题描述**:
为分布式/自托管的 vLLM 使用添加会话亲和性路由和前缀缓存指导，以提高缓存局部性。

**技术要点**:
- vLLM 前缀缓存配置
- 会话感知路由
- LiteLLM 头部转发支持
- OpenAI Python SDK 的额外头部支持

**实施规则**:
- 仅在官方文档支持的情况下应用行为变更
- 为 vLLM 路径保留会话亲和性路由提示
- 不引入未文档化的 Azure/Codex 特定语义

**预期影响**:
使用 `--enable-prefix-caching` 和会话粘性路由配置的分布式 vLLM 部署应该看到更好的前缀缓存局部性和更稳定的延迟/成本。

### 2. PR #1646 - 传播 vLLM 缓存局部性的会话亲和性
**状态**: 开放 (PR)
**优先级**: 高
**复杂度**: 中等

**改进内容**:
- 为 provider 接口添加可选的 `session_id`
- `AgentLoop` 现在将会话密钥转发到 provider 聊天调用
- **LiteLLM provider**: 仅对 vLLM 路径注入稳定的 `x-session-affinity`
- **Custom provider**: 当 `session_id` 可用时，每个请求发送 `x-session-affinity`
- **Azure/Codex**: 不引入新的未文档化亲和性行为

**测试**:
- 添加了 `tests/test_session_affinity.py`
- 验证按会话的稳定/不同亲和性
- 验证头部合并行为
- 验证 `AgentLoop` 转发 `session_id`

### 3. PR #1644 - Telegram 群组策略 @提及配置
**状态**: 开放 (PR)
**优先级**: 中
**复杂度**: 低

**功能描述**:
为 Telegram 群组频道添加 `group_policy` @提及配置和架构支持。

**实施内容**:
- 在 schema.py 中添加 `group_policy` 到 `TelegramConfig` (open | mention)
- 更新 telegram 频道以尊重群组聊天的 `group_policy`

**使用示例**:
- 设置 `group_policy: "mention"` - bot 仅在 @提及时回复
- 设置 `group_policy: "open"` - bot 回复 telegram 群组中的所有消息

### 4. PR #1643 - ExecTool 交互式用户确认
**状态**: 开放 (PR)
**优先级**: 中
**复杂度**: 中等

**功能描述**:
为 ExecTool 添加交互式用户确认功能，提高安全性。

### 5. PR #1647 - Logo 透明背景
**状态**: 开放 (PR)
**优先级**: 低
**复杂度**: 低

**功能描述**:
为 logo 添加透明背景，便于在构建网关时使用。深色和浅色模式可以使用相同的 logo。

## 开发优先级和计划

### 第一阶段：高优先级功能 (1-2周)

#### 1.1 完成 Issue #1645 - vLLM 会话亲和性
**任务**:
1. 研究 vLLM 前缀缓存官方文档
2. 分析 LiteLLM provider 的头部转发机制
3. 实现 session_id 在 provider 接口中的传递
4. 为 vLLM 路径添加 `x-session-affinity` 头部注入
5. 更新文档，添加 vLLM 启动示例和粘性路由说明
6. 编写测试用例验证功能

**文件修改**:
- `nanobot/providers/litellm_provider.py` - 添加会话亲和性支持
- `nanobot/providers/custom_provider.py` - 添加头部转发
- `nanobot/agent/loop.py` - 传递 session_id 到 provider
- `tests/test_session_affinity.py` - 添加测试
- `README_CN.md` / `README.md` - 更新文档

#### 1.2 审查和合并 PR #1646
**任务**:
1. 代码审查 PR #1646
2. 运行测试验证功能
3. 提供反馈或合并 PR

### 第二阶段：中优先级功能 (1周)

#### 2.1 完成 PR #1644 - Telegram 群组策略
**任务**:
1. 在 `nanobot/config/schema.py` 中添加 `group_policy` 配置
2. 修改 `nanobot/channels/telegram.py` 实现群组策略逻辑
3. 更新文档说明配置选项
4. 测试不同群组策略下的行为

**文件修改**:
- `nanobot/config/schema.py` - 添加配置
- `nanobot/channels/telegram.py` - 实现逻辑
- `README_CN.md` / `README.md` - 更新文档

#### 2.2 完成 PR #1643 - ExecTool 交互式确认
**任务**:
1. 分析 ExecTool 的当前实现
2. 设计交互式确认机制
3. 实现用户确认逻辑
4. 更新安全配置选项
5. 测试确认功能

**文件修改**:
- `nanobot/agent/tools/exec.py` - 添加确认逻辑
- `nanobot/config/schema.py` - 添加配置选项
- `nanobot/agent/security_guard.py` - 集成安全检查
- `README_CN.md` / `README.md` - 更新文档

### 第三阶段：低优先级功能 (几天)

#### 3.1 完成 PR #1647 - Logo 透明背景
**任务**:
1. 处理现有 logo 图片
2. 添加透明背景
3. 测试在不同主题下的显示效果
4. 更新文档和资源文件

## 实施步骤

### 步骤 1: 环境准备
1. 确保本地开发环境已配置
2. 安装必要的依赖
3. 设置测试环境

### 步骤 2: 代码开发
1. 按优先级顺序实现各功能
2. 遵循现有代码风格和架构
3. 添加必要的测试
4. 更新相关文档

### 步骤 3: 测试验证
1. 运行单元测试
2. 进行集成测试
3. 验证功能完整性
4. 性能测试（特别是 vLLM 缓存功能）

### 步骤 4: 文档更新
1. 更新 README 文档
2. 添加配置示例
3. 更新 CHANGELOG
4. 提供使用指南

### 步骤 5: 提交和发布
1. 创建功能分支
2. 提交代码更改
3. 创建 Pull Request
4. 响应审查反馈
5. 合并到主分支

## 技术考虑

### vLLM 会话亲和性实现
- 使用官方文档支持的 API
- 保持向后兼容性
- 提供配置选项控制行为
- 添加详细的日志记录

### Telegram 群组策略
- 支持灵活的配置选项
- 保持现有功能不受影响
- 提供清晰的文档说明
- 测试不同场景下的行为

### ExecTool 交互确认
- 与现有安全系统集成
- 提供可配置的确认级别
- 支持自动化场景
- 记录确认操作到审计日志

## 风险和缓解措施

### 风险 1: vLLM API 变更
**缓解**: 仅使用官方文档支持的 API，定期检查更新

### 风险 2: 向后兼容性
**缓解**: 添加配置选项，默认行为保持不变

### 风险 3: 测试覆盖不足
**缓解**: 添加全面的测试用例，包括边界情况

### 风险 4: 文档不完整
**缓解**: 提供详细的配置示例和使用说明

## 成功标准

1. 所有高优先级功能成功实现并测试
2. 代码通过所有现有测试
3. 文档完整且准确
4. 功能性能符合预期
5. 无向后兼容性问题
6. 代码审查通过

## 时间估算

- 第一阶段: 1-2 周
- 第二阶段: 1 周
- 第三阶段: 几天
- 总计: 约 2-3 周

## 后续优化

1. 监控 vLLM 缓存性能改进
2. 收集用户反馈
3. 优化配置选项
4. 添加更多测试用例
5. 性能调优