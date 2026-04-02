from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class ProviderConfig:
    provider_name: str
    vendor: str
    client_id: str
    client_secret: str
    discovery_url: Optional[str] = None
    token_endpoint: Optional[str] = None
    authorization_endpoint: Optional[str] = None
    issuer: Optional[str] = None
    kms_key_id: Optional[str] = None
    region: str = ""


@dataclass(slots=True)
class GatewayConfig:
    gateway_name: str
    description: Optional[str] = None
    region: str = ""


@dataclass(slots=True)
class TargetConfig:
    target_name: str
    description: Optional[str]
    endpoint: str
    server_type: str
    grant_type: str
    scopes: list[str] = field(default_factory=list)
    provider_name: str = ""


@dataclass(slots=True)
class ProviderInfo:
    provider_name: str
    provider_id: Optional[str]
    reused: bool
    raw: Any = None


@dataclass(slots=True)
class GatewayInfo:
    gateway_id: str
    gateway_name: str
    region: str
    reused: bool
    raw: Any = None


@dataclass(slots=True)
class TargetInfo:
    target_id: str
    target_name: str
    target_status: str
    endpoint: str
    server_type: str
    reused: bool
    raw: Any = None


@dataclass(slots=True)
class McpRegistrationResult:
    provider_name: str
    provider_id: Optional[str]
    gateway_id: str
    gateway_name: str
    target_id: str
    target_name: str
    target_status: str
    reused_provider: bool
    reused_gateway: bool
    reused_target: bool
