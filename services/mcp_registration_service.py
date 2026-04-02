import uuid
from collections.abc import Callable

from config.settings import load_gateway_config, load_oauth2_provider_config, load_target_config
from domain.dto import RegistrationResult


class McpRegistrationService:
    def __init__(
        self,
        get_config: Callable[[str], object],
        identity_provider_adapter,
        mcp_gateway_adapter,
    ):
        self.get_config = get_config
        self.identity_provider_adapter = identity_provider_adapter
        self.mcp_gateway_adapter = mcp_gateway_adapter

    def ensure_mcp_registered(self) -> RegistrationResult:
        provider_config = load_oauth2_provider_config(self.get_config)
        gateway_config = load_gateway_config(self.get_config)
        target_config = load_target_config(self.get_config)

        provider = self.identity_provider_adapter.ensure_oauth2_provider(provider_config)
        gateway = self.mcp_gateway_adapter.ensure_gateway(gateway_config)
        target = self.mcp_gateway_adapter.ensure_target(gateway.gateway_id, target_config)
        ready_target = self.mcp_gateway_adapter.wait_target_ready(gateway.gateway_id, target.target_id)

        return RegistrationResult(
            provider_name=provider.name,
            provider_id=provider.provider_id,
            gateway_id=gateway.gateway_id,
            gateway_name=gateway.gateway_name,
            target_id=ready_target.target_id,
            target_name=ready_target.target_name,
            target_status=ready_target.status,
            endpoint=ready_target.endpoint,
            server_type=ready_target.server_type,
            region=gateway.region,
            reused_provider=provider.reused,
            reused_gateway=gateway.reused,
            reused_target=target.reused,
            operation_trace_id=str(uuid.uuid4()),
        )
