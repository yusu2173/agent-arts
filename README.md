# MCP Gateway/Target 接入

当前实现已按你的要求改为 **显式 SDK import + 显式 SDK model/request 调用**，不再使用动态反射加载类名。

## Identity（AgentRun SDK）

显式使用：

- `hw_agentrun_wrapper.services.identity.identity_client.IdentityClient`
- `create_oauth2_credential_provider(name, vendor, client_id, client_secret, tenant_id=None, oauth_discovery=None)`

Provider 幂等策略：

- 先直接创建；
- 如果后端返回“已存在”类错误，则视为复用成功。

## AgentArts（AgentArts SDK）

显式 import 并使用如下 request/model：

- `CreateCoreGatewayRequestBody` / `CreateCoreGatewayRequest`
- `ListCoreGatewaysRequest`
- `CreateCoreGatewayTargetRequestBody` / `CreateCoreGatewayTargetRequest`
- `UpdateCoreGatewayTargetRequestBody` / `UpdateCoreGatewayTargetRequest`
- `ListCoreGatewayTargetsRequest`
- `ShowCoreGatewayTargetRequest`
- `CoreGatewayTargetConfiguration`
- `CoreGatewayMcpServerTargetConfiguration`
- `CoreGatewayCredentialProviderConfiguration`
- `CoreGatewayCredentialProvider`
- `CoreGatewayOAuthCredentialProvider`
- `CoreGatewayTag`

Target 关键字段：

- `target_configuration.mcp_server.endpoint`
- `target_configuration.mcp_server.server_type`（`sse` / `streamable_http`）
- `credential_provider_configuration.credential_provider_type = "oauth"`
- `credential_provider_configuration.credential_provider.oauth_credential_provider.provider_name`

## 接线方式

传入：

1. `get_config`（通常是 `config_manager.get_config`）
2. 已初始化的 `IdentityClient`
3. 已初始化的 `AgentArtsClient`

然后调用 `McpRegistrationService.ensure_mcp_registered()`。
