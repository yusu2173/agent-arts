# MCP Gateway/Target 接入

当前实现已升级为 **AgentArts SDK Request/Model 对象调用**（不再走 dict body 调用）。

## Identity（AgentRun SDK）

使用 `IdentityClient`：

- `create_oauth2_credential_provider(name, vendor, client_id, client_secret, tenant_id=None, oauth_discovery=None)`

Provider 幂等策略：

- 先直接创建；
- 如果后端返回“已存在”类错误，则视为复用成功。

## AgentArts（AgentArts SDK）

使用 `AgentArtsClient` 核心方法（Request 对象入参）：

- `list_core_gateways(ListCoreGatewaysRequest)`
- `create_core_gateway(CreateCoreGatewayRequest)`
- `list_core_gateway_targets(ListCoreGatewayTargetsRequest)`
- `create_core_gateway_target(CreateCoreGatewayTargetRequest)`
- `update_core_gateway_target(UpdateCoreGatewayTargetRequest)`
- `show_core_gateway_target(ShowCoreGatewayTargetRequest)`

## 模型对齐

Builder 会实例化真实 SDK 模型：

- `CreateCoreGatewayRequestBody`
- `CreateCoreGatewayTargetRequestBody`
- `UpdateCoreGatewayTargetRequestBody`
- `CoreGatewayTargetConfiguration`
- `CoreGatewayMcpServerTargetConfiguration`
- `CoreGatewayCredentialProviderConfiguration`
- `CoreGatewayCredentialProvider`
- `CoreGatewayOAuthCredentialProvider`
- `CoreGatewayTag`

凭据绑定路径：

- `credential_provider_configuration.credential_provider_type = "oauth"`
- `credential_provider_configuration.credential_provider.oauth_credential_provider.provider_name`

HTTP MCP Target 字段：

- `target_configuration.mcp_server.endpoint`
- `target_configuration.mcp_server.server_type`（`sse` / `streamable_http`）

## 接线方式

传入：

1. `get_config`（通常是 `config_manager.get_config`）
2. 已初始化的 `IdentityClient`
3. 已初始化的 `AgentArtsClient`

然后调用 `McpRegistrationService.ensure_mcp_registered()`。
