"""MCP 注册脚本（推荐入口）。"""

from hw_agentrun_wrapper.services.identity.identity_client import IdentityClient
from hw_agentrun_wrapper.services.mcp_gateway_http import MCPGatewayHttpService
from hw_agentrun_wrapper.services.mcp_target_http import MCPTargetHttpService

from services import GatewayService, McpRegistrationService, ProviderService, TargetService


class ConfigManager:
    """请替换为项目真实配置对象。"""

    def get_config(self, key: str):  # noqa: ANN001
        raise RuntimeError(f"请实现配置读取，key={key}")


def build_identity_client(config_manager: ConfigManager) -> IdentityClient:
    region = config_manager.get_config("agentarts.mcp.provider.region")
    return IdentityClient(region=region)


def build_gateway_http_service(config_manager: ConfigManager) -> MCPGatewayHttpService:
    region = config_manager.get_config("agentarts.mcp.gateway.region")
    return MCPGatewayHttpService(region_name=region)


def build_target_http_service(config_manager: ConfigManager) -> MCPTargetHttpService:
    region = config_manager.get_config("agentarts.mcp.gateway.region")
    return MCPTargetHttpService(region_name=region)


def main() -> None:
    config_manager = ConfigManager()

    provider_service = ProviderService(build_identity_client(config_manager))
    gateway_service = GatewayService(build_gateway_http_service(config_manager))
    target_service = TargetService(build_target_http_service(config_manager))

    registration_service = McpRegistrationService(
        get_config=config_manager.get_config,
        provider_service=provider_service,
        gateway_service=gateway_service,
        target_service=target_service,
    )
    print(registration_service.ensure_mcp_registered())


if __name__ == "__main__":
    main()
