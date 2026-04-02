from collections.abc import Callable

from domain.constants import (
    MCP_ALLOWED_SERVER_TYPES,
    MCP_SERVER_TYPE_STREAMABLE_HTTP,
    OAUTH_GRANT_TYPE_CLIENT_CREDENTIALS,
    OAUTH_VENDOR_CUSTOM,
)
from domain.dto import GatewayConfig, OAuth2ProviderConfig, TargetConfig
from domain.exceptions import InvalidMcpConfigError


def _read(get_config: Callable[[str], object], key: str, default: object = None) -> object:
    value = get_config(key)
    return default if value is None else value


def load_oauth2_provider_config(get_config: Callable[[str], object]) -> OAuth2ProviderConfig:
    discovery = _as_optional_str(_read(get_config, "agentarts.mcp.provider.discovery_url"))
    config = OAuth2ProviderConfig(
        provider_name=str(_read(get_config, "agentarts.mcp.provider.name", "eso-oauth2-provider")),
        vendor=str(_read(get_config, "agentarts.mcp.provider.vendor", OAUTH_VENDOR_CUSTOM)),
        client_id=str(_read(get_config, "agentarts.mcp.provider.client_id", "")),
        client_secret=str(_read(get_config, "agentarts.mcp.provider.client_secret", "")),
        tenant_id=_as_optional_str(_read(get_config, "agentarts.mcp.provider.tenant_id")),
        oauth_discovery=_as_optional_str(_read(get_config, "agentarts.mcp.provider.oauth_discovery")) or discovery,
        discovery_url=discovery,
        token_endpoint=_as_optional_str(_read(get_config, "agentarts.mcp.provider.token_endpoint")),
        authorization_endpoint=_as_optional_str(_read(get_config, "agentarts.mcp.provider.authorization_endpoint")),
        issuer=_as_optional_str(_read(get_config, "agentarts.mcp.provider.issuer")),
        region=str(_read(get_config, "agentarts.mcp.provider.region", "")),
        kms_key_id=_as_optional_str(_read(get_config, "agentarts.mcp.provider.kms_key_id")),
    )
    _validate_provider_config(config)
    return config


def load_gateway_config(get_config: Callable[[str], object]) -> GatewayConfig:
    raw_tags = _read(get_config, "agentarts.mcp.gateway.tags", [])
    tags = [str(tag) for tag in (raw_tags or [])]
    config = GatewayConfig(
        gateway_name=str(_read(get_config, "agentarts.mcp.gateway.name", "eso-mcp-gateway")),
        protocol_type=str(_read(get_config, "agentarts.mcp.gateway.protocol_type", "mcp")),
        gateway_description=_as_optional_str(_read(get_config, "agentarts.mcp.gateway.description")),
        authorizer_type=_as_optional_str(_read(get_config, "agentarts.mcp.gateway.authorizer_type")),
        agency_name=_as_optional_str(_read(get_config, "agentarts.mcp.gateway.agency_name")),
        agent_gateway_id=_as_optional_str(_read(get_config, "agentarts.mcp.gateway.agent_gateway_id")),
        tags=tags,
        region=str(_read(get_config, "agentarts.mcp.gateway.region", "")),
    )
    _validate_gateway_config(config)
    return config


def load_target_config(get_config: Callable[[str], object]) -> TargetConfig:
    server_type = str(_read(get_config, "agentarts.mcp.target.server_type", MCP_SERVER_TYPE_STREAMABLE_HTTP))
    raw_scopes = _read(get_config, "agentarts.mcp.target.scopes", [])
    raw_parameters = _read(get_config, "agentarts.mcp.target.custom_parameters", {})
    target = TargetConfig(
        target_name=str(_read(get_config, "agentarts.mcp.target.name", "eso-mcp-target")),
        target_description=_as_optional_str(_read(get_config, "agentarts.mcp.target.description")),
        endpoint=str(_read(get_config, "agentarts.mcp.target.endpoint", "")),
        server_type=server_type,
        provider_name=str(_read(get_config, "agentarts.mcp.provider.name", "eso-oauth2-provider")),
        grant_type=str(_read(get_config, "agentarts.mcp.target.grant_type", OAUTH_GRANT_TYPE_CLIENT_CREDENTIALS)),
        scopes=[str(item) for item in (raw_scopes or [])],
        custom_parameters={str(k): str(v) for k, v in (raw_parameters or {}).items()},
    )
    _validate_target_config(target)
    return target


def _validate_provider_config(config: OAuth2ProviderConfig) -> None:
    if not config.provider_name:
        raise InvalidMcpConfigError("agentarts.mcp.provider.name 不能为空")
    if not config.client_id:
        raise InvalidMcpConfigError("agentarts.mcp.provider.client_id 不能为空")
    if not config.client_secret:
        raise InvalidMcpConfigError("agentarts.mcp.provider.client_secret 不能为空")
    if not config.region:
        raise InvalidMcpConfigError("agentarts.mcp.provider.region 不能为空")


def _validate_gateway_config(config: GatewayConfig) -> None:
    if not config.gateway_name:
        raise InvalidMcpConfigError("agentarts.mcp.gateway.name 不能为空")
    if config.protocol_type != "mcp":
        raise InvalidMcpConfigError("agentarts.mcp.gateway.protocol_type 仅支持 mcp")


def _validate_target_config(config: TargetConfig) -> None:
    if not config.target_name:
        raise InvalidMcpConfigError("agentarts.mcp.target.name 不能为空")
    if not config.endpoint:
        raise InvalidMcpConfigError("agentarts.mcp.target.endpoint 不能为空")
    if not config.provider_name:
        raise InvalidMcpConfigError("agentarts.mcp.provider.name 不能为空")
    if config.server_type not in MCP_ALLOWED_SERVER_TYPES:
        raise InvalidMcpConfigError(
            f"invalid server_type={config.server_type}, allowed={sorted(MCP_ALLOWED_SERVER_TYPES)}"
        )


def _as_optional_str(value: object) -> str | None:
    if value is None:
        return None
    string_value = str(value).strip()
    return string_value or None
