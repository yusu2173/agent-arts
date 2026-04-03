"""MCP 注册脚本（推荐入口）。"""

import os

from huaweicloudsdkagentidentity.v1 import AgentIdentityClient
from huaweicloudsdkagentidentity.v1.region.agentidentity_region import AgentIdentityRegion
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.http.http_config import HttpConfig

from hw_agentrun_wrapper.services.identity.identity_client import IdentityClient
from hw_agentrun_wrapper.services.mcp_gateway_http import MCPGatewayHttpService
from hw_agentrun_wrapper.services.mcp_target_http import MCPTargetHttpService

from services import GatewayService, McpRegistrationService, ProviderService, TargetService


class ConfigManager:
    """请替换为项目真实配置对象。"""

    def get_config(self, key: str):  # noqa: ANN001
        raise RuntimeError(f"请实现配置读取，key={key}")


def build_identity_client(config_manager: ConfigManager) -> IdentityClient:
    """构建 IdentityClient。

    这里显式注入 AK/SK，避免 SDK 走 MetadataBasicCredentialProvider 导致本地环境异常。
    """
    identity_region = (
        config_manager.get_config("agentarts.mcp.provider.identity_region")
        or config_manager.get_config("agentarts.mcp.identity.region")
        or "ap-southeast-4"
    )

    ak = config_manager.get_config("agentarts.ak") or os.getenv("HUAWEICLOUD_SDK_AK")
    sk = config_manager.get_config("agentarts.sk") or os.getenv("HUAWEICLOUD_SDK_SK")
    project_id = config_manager.get_config("agentarts.project_id") or os.getenv("HUAWEICLOUD_SDK_PROJECT_ID")

    if not ak or not sk or not project_id:
        raise RuntimeError(
            "IdentityClient 初始化失败：缺少 AK/SK/PROJECT_ID。"
            "请配置 agentarts.ak、agentarts.sk、agentarts.project_id 或对应环境变量。"
        )

    sdk_region = AgentIdentityRegion.value_of(identity_region)
    credentials = BasicCredentials().with_ak(ak).with_sk(sk).with_project_id(project_id)
    http_config = HttpConfig(ignore_ssl_verification=True)
    low_level_client = (
        AgentIdentityClient.new_builder()
        .with_region(sdk_region)
        .with_credentials(credentials)
        .with_http_config(http_config)
        .build()
    )
    return IdentityClient(region=identity_region, client=low_level_client)


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
