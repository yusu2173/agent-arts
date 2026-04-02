"""MCP 注册本地调试脚本。"""

from adapters.identity_provider_adapter import IdentityProviderAdapter
from adapters.mcp_gateway_adapter import McpGatewayAdapter
from services.mcp_registration_service import McpRegistrationService


class ConfigManager:
    """请替换为项目内真实配置管理器。"""

    def get_config(self, key: str):  # noqa: ANN001
        raise RuntimeError(f"请接入真实 config_manager，key={key}")


def build_identity_client():
    """请替换为真实 IdentityClient 初始化逻辑。"""
    raise RuntimeError("请初始化 IdentityClient")


def build_agentarts_client():
    """请替换为真实 AgentArtsClient 初始化逻辑。"""
    raise RuntimeError("请初始化 AgentArtsClient")


def main() -> None:
    config_manager = ConfigManager()
    service = McpRegistrationService(
        get_config=config_manager.get_config,
        identity_provider_adapter=IdentityProviderAdapter(build_identity_client()),
        mcp_gateway_adapter=McpGatewayAdapter(build_agentarts_client()),
    )
    result = service.ensure_mcp_registered()
    print(result)


if __name__ == "__main__":
    main()
