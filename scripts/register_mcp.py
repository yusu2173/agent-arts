"""MCP 注册本地调试脚本（可选）。"""

from hw_agentrun_wrapper.services.identity.identity_client import IdentityClient
from hw_agentrun_wrapper.services.mcp_gateway_http import MCPGatewayHttpService
from hw_agentrun_wrapper.services.mcp_target_http import MCPTargetHttpService

from services import GatewayService, McpRegistrationService, ProviderService, TargetService


class ConfigManager:
    """请替换为项目中的真实配置管理器。"""

    def get_config(self, key: str):  # noqa: ANN001
        raise RuntimeError(f"请接入真实配置，key={key}")


def build_identity_client() -> IdentityClient:
    """请替换为真实 IdentityClient 初始化逻辑。"""
    raise RuntimeError("请初始化 IdentityClient")


def build_gateway_http_service() -> MCPGatewayHttpService:
    """请替换为真实 MCPGatewayHttpService 初始化逻辑。"""
    raise RuntimeError("请初始化 MCPGatewayHttpService")


def build_target_http_service() -> MCPTargetHttpService:
    """请替换为真实 MCPTargetHttpService 初始化逻辑。"""
    raise RuntimeError("请初始化 MCPTargetHttpService")


def main() -> None:
    config_manager = ConfigManager()

    provider_service = ProviderService(build_identity_client())
    gateway_service = GatewayService(build_gateway_http_service())
    target_service = TargetService(build_target_http_service())

    registration_service = McpRegistrationService(
        get_config=config_manager.get_config,
        provider_service=provider_service,
        gateway_service=gateway_service,
        target_service=target_service,
    )
    result = registration_service.ensure_mcp_registered()
    print(result)


if __name__ == "__main__":
    main()
