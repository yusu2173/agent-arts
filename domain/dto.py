from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class OAuth2ProviderConfig:
    provider_name: str
    vendor: str
    client_id: str
    client_secret: str
    region: str
    tenant_id: Optional[str] = None
    oauth_discovery: Optional[str] = None
    discovery_url: Optional[str] = None
    token_endpoint: Optional[str] = None
    authorization_endpoint: Optional[str] = None
    issuer: Optional[str] = None
    kms_key_id: Optional[str] = None


@dataclass(slots=True)
class GatewayConfig:
    gateway_name: str
    protocol_type: str = "mcp"
    gateway_description: Optional[str] = None
    authorizer_type: Optional[str] = None
    agency_name: Optional[str] = None
    agent_gateway_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    region: str = ""


@dataclass(slots=True)
class TargetConfig:
    target_name: str
    endpoint: str
    server_type: str
    provider_name: str
    grant_type: str
    target_description: Optional[str] = None
    scopes: list[str] = field(default_factory=list)
    custom_parameters: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderInfo:
    name: str
    provider_id: Optional[str] = None
    reused: bool = False
    raw: Any = None


@dataclass(slots=True)
class GatewayInfo:
    gateway_id: str
    gateway_name: str
    region: str
    reused: bool = False
    raw: Any = None


@dataclass(slots=True)
class TargetInfo:
    target_id: str
    target_name: str
    endpoint: str
    server_type: str
    status: str
    reused: bool = False
    raw: Any = None


@dataclass(slots=True)
class RegistrationResult:
    provider_name: str
    provider_id: Optional[str]
    gateway_id: str
    gateway_name: str
    target_id: str
    target_name: str
    target_status: str
    endpoint: str
    server_type: str
    region: str
    reused_provider: bool
    reused_gateway: bool
    reused_target: bool
    operation_trace_id: Optional[str] = None
