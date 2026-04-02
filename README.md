# MCP Provider/Gateway/Target 接入注册模块

本实现已按要求改为 **仅基于 AgentRun SDK 封装能力**：

- Provider：`IdentityClient`
- Gateway：`MCPGatewayHttpService`
- Target：`MCPTargetHttpService`

不再以底层 `huaweicloudsdkagentarts` 编写业务层平行封装。

## 目录

```text
config/
  settings.py
domain/
  dto.py
  constants.py
  exceptions.py
services/
  provider_service.py
  gateway_service.py
  target_service.py
  mcp_registration_service.py
scripts/
  register_mcp.py   # 可选
```

## 统一入口

业务层只调用：

- `McpRegistrationService.ensure_mcp_registered()`

内部顺序：

1. 读取配置
2. `ProviderService.ensure_provider`
3. `GatewayService.ensure_gateway`
4. `TargetService.ensure_target`
5. `TargetService.wait_target_ready`

## 配置路径

统一使用：

- `agentarts.mcp.provider.*`
- `agentarts.mcp.gateway.*`
- `agentarts.mcp.target.*`

`eso` 只作为配置值，不作为路径。
