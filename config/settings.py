from collections.abc import Callable

from domain.constants import (
    DEFAULT_PROVIDER_VENDOR,
    DEFAULT_TARGET_GRANT_TYPE,
    DEFAULT_TARGET_SERVER_TYPE,
    TARGET_SERVER_TYPES,
)
from domain.dto import GatewayConfig, ProviderConfig, TargetConfig
from domain.exceptions import InvalidMcpConfigError


def load_provider_config(get_config: Callable[[str], object]) -> ProviderConfig:
    config = ProviderConfig(
        provider_name=str(_read(get_config, "agentarts.mcp.provider.name", "eso-oauth2-provider")),
        vendor=str(_read(get_config, "agentarts.mcp.provider.vendor", DEFAULT_PROVIDER_VENDOR)),
        client_id=str(_read(get_config, "agentarts.mcp.provider.client_id", "")),
        client_secret=str(_read(get_config, "agentarts.mcp.provider.client_secret", "")),
        discovery_url=_optional(_read(get_config, "agentarts.mcp.provider.discovery_url")),
        token_endpoint=_optional(_read(get_config, "agentarts.mcp.provider.token_endpoint")),
        authorization_endpoint=_optional(_read(get_config, "agentarts.mcp.provider.authorization_endpoint")),
        issuer=_optional(_read(get_config, "agentarts.mcp.provider.issuer")),
        kms_key_id=_optional(_read(get_config, "agentarts.mcp.provider.kms_key_id")),
        region=str(_read(get_config, "agentarts.mcp.provider.region", "")),
    )
    if not config.provider_name or not config.client_id or not config.client_secret:
        raise InvalidMcpConfigError("provider 配置缺少必填项")
    return config


def load_gateway_config(get_config: Callable[[str], object]) -> GatewayConfig:
    config = GatewayConfig(
        gateway_name=str(_read(get_config, "agentarts.mcp.gateway.name", "eso-mcp-gateway")),
        description=_optional(_read(get_config, "agentarts.mcp.gateway.description")),
        region=str(_read(get_config, "agentarts.mcp.gateway.region", "")),
    )
    if not config.gateway_name:
        raise InvalidMcpConfigError("gateway.name 不能为空")
    return config


def load_target_config(get_config: Callable[[str], object], provider_name: str) -> TargetConfig:
    raw_scopes = _read(get_config, "agentarts.mcp.target.scopes", [])
    config = TargetConfig(
        target_name=str(_read(get_config, "agentarts.mcp.target.name", "eso-mcp-target")),
        description=_optional(_read(get_config, "agentarts.mcp.target.description")),
        endpoint=str(_read(get_config, "agentarts.mcp.target.endpoint", "")),
        server_type=str(_read(get_config, "agentarts.mcp.target.server_type", DEFAULT_TARGET_SERVER_TYPE)),
        grant_type=str(_read(get_config, "agentarts.mcp.target.grant_type", DEFAULT_TARGET_GRANT_TYPE)),
        scopes=[str(i) for i in (raw_scopes or [])],
        provider_name=provider_name,
    )
    if not config.target_name or not config.endpoint:
        raise InvalidMcpConfigError("target 配置缺少必填项")
    if config.server_type not in TARGET_SERVER_TYPES:
        raise InvalidMcpConfigError(f"target.server_type 仅支持: {sorted(TARGET_SERVER_TYPES)}")
    return config


def _read(get_config: Callable[[str], object], key: str, default: object = None) -> object:
    value = get_config(key)
    return default if value is None else value


def _optional(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
