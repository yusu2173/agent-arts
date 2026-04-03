# MCP Provider/Gateway/Target 接入注册模块

本实现仅基于 AgentRun SDK 封装能力：

- Provider：`IdentityClient`
- Gateway：`MCPGatewayHttpService`
- Target：`MCPTargetHttpService`

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
  register.py        # 推荐入口
  register_mcp.py    # 兼容入口
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

## Identity 区域与鉴权说明

1. 如果本地 AgentIdentity SDK 仅支持 `ap-southeast-4`，请配置：
   - `agentarts.mcp.provider.identity_region=ap-southeast-4`
2. `scripts/register.py` 会显式注入 AK/SK/PROJECT_ID 构建底层 `AgentIdentityClient`，避免触发 metadata 凭证链异常：
   - `agentarts.ak`
   - `agentarts.sk`
   - `agentarts.project_id`
   或同名环境变量：
   - `HUAWEICLOUD_SDK_AK`
   - `HUAWEICLOUD_SDK_SK`
   - `HUAWEICLOUD_SDK_PROJECT_ID`
