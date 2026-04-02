from __future__ import annotations

from collections.abc import Callable

from config.settings import load_gateway_config, load_provider_config, load_target_config
from domain.dto import McpRegistrationResult
from services.gateway_service import GatewayService
from services.provider_service import ProviderService
from services.target_service import TargetService


class McpRegistrationService:
    """MCP 注册统一入口服务。"""

    def __init__(
        self,
        get_config: Callable[[str], object],
        provider_service: ProviderService,
        gateway_service: GatewayService,
        target_service: TargetService,
    ):
        self.get_config = get_config
        self.provider_service = provider_service
        self.gateway_service = gateway_service
        self.target_service = target_service

    def ensure_mcp_registered(self) -> McpRegistrationResult:
        provider_config = load_provider_config(self.get_config)
        gateway_config = load_gateway_config(self.get_config)
        target_config = load_target_config(self.get_config, provider_name=provider_config.provider_name)

        provider_info = self.provider_service.ensure_provider(provider_config)
        gateway_info = self.gateway_service.ensure_gateway(gateway_config)
        target_info = self.target_service.ensure_target(gateway_info.gateway_id, target_config)
        ready_target = self.target_service.wait_target_ready(gateway_info.gateway_id, target_info.target_id)

        return McpRegistrationResult(
            provider_name=provider_info.provider_name,
            provider_id=provider_info.provider_id,
            gateway_id=gateway_info.gateway_id,
            gateway_name=gateway_info.gateway_name,
            target_id=ready_target.target_id,
            target_name=ready_target.target_name,
            target_status=ready_target.target_status,
            reused_provider=provider_info.reused,
            reused_gateway=gateway_info.reused,
            reused_target=target_info.reused,
        )
