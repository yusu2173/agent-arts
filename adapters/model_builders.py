from __future__ import annotations

from typing import Any

from huaweicloudsdkagentarts.v1.model.core_gateway_credential_provider import CoreGatewayCredentialProvider
from huaweicloudsdkagentarts.v1.model.core_gateway_credential_provider_configuration import (
    CoreGatewayCredentialProviderConfiguration,
)
from huaweicloudsdkagentarts.v1.model.core_gateway_mcp_server_target_configuration import (
    CoreGatewayMcpServerTargetConfiguration,
)
from huaweicloudsdkagentarts.v1.model.core_gateway_oauth_credential_provider import CoreGatewayOAuthCredentialProvider
from huaweicloudsdkagentarts.v1.model.core_gateway_tag import CoreGatewayTag
from huaweicloudsdkagentarts.v1.model.core_gateway_target_configuration import CoreGatewayTargetConfiguration
from huaweicloudsdkagentarts.v1.model.create_core_gateway_request import CreateCoreGatewayRequest
from huaweicloudsdkagentarts.v1.model.create_core_gateway_request_body import CreateCoreGatewayRequestBody
from huaweicloudsdkagentarts.v1.model.create_core_gateway_target_request import CreateCoreGatewayTargetRequest
from huaweicloudsdkagentarts.v1.model.create_core_gateway_target_request_body import (
    CreateCoreGatewayTargetRequestBody,
)
from huaweicloudsdkagentarts.v1.model.list_core_gateways_request import ListCoreGatewaysRequest
from huaweicloudsdkagentarts.v1.model.list_core_gateway_targets_request import ListCoreGatewayTargetsRequest
from huaweicloudsdkagentarts.v1.model.show_core_gateway_target_request import ShowCoreGatewayTargetRequest
from huaweicloudsdkagentarts.v1.model.update_core_gateway_target_request import UpdateCoreGatewayTargetRequest
from huaweicloudsdkagentarts.v1.model.update_core_gateway_target_request_body import (
    UpdateCoreGatewayTargetRequestBody,
)

from domain.dto import GatewayConfig, OAuth2ProviderConfig, TargetConfig


def build_oauth2_provider_payload(config: OAuth2ProviderConfig) -> dict[str, Any]:
    payload = {
        "name": config.provider_name,
        "vendor": config.vendor,
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "tenant_id": config.tenant_id,
        "oauth_discovery": config.oauth_discovery,
    }
    return {k: v for k, v in payload.items() if v is not None}


def build_create_core_gateway_request(config: GatewayConfig) -> CreateCoreGatewayRequest:
    body = CreateCoreGatewayRequestBody(
        name=config.gateway_name,
        description=config.gateway_description,
        protocol_type=config.protocol_type,
        authorizer_type=config.authorizer_type,
        agency_name=config.agency_name,
        agent_gateway_id=config.agent_gateway_id,
        tags=_build_gateway_tags(config.tags),
    )
    return CreateCoreGatewayRequest(body=body)


def build_list_core_gateways_request(name: str, limit: int = 100, offset: int = 0) -> ListCoreGatewaysRequest:
    return ListCoreGatewaysRequest(name=name, limit=limit, offset=offset)


def build_list_core_gateway_targets_request(
    gateway_id: str, limit: int = 100, offset: int = 0
) -> ListCoreGatewayTargetsRequest:
    return ListCoreGatewayTargetsRequest(gateway_id=gateway_id, limit=limit, offset=offset)


def build_show_core_gateway_target_request(gateway_id: str, target_id: str) -> ShowCoreGatewayTargetRequest:
    return ShowCoreGatewayTargetRequest(gateway_id=gateway_id, target_id=target_id)


def build_create_core_gateway_target_request(
    gateway_id: str, config: TargetConfig
) -> CreateCoreGatewayTargetRequest:
    body = _build_core_gateway_target_body(CreateCoreGatewayTargetRequestBody, config)
    return CreateCoreGatewayTargetRequest(gateway_id=gateway_id, body=body)


def build_update_core_gateway_target_request(
    gateway_id: str, target_id: str, config: TargetConfig
) -> UpdateCoreGatewayTargetRequest:
    body = _build_core_gateway_target_body(UpdateCoreGatewayTargetRequestBody, config)
    return UpdateCoreGatewayTargetRequest(gateway_id=gateway_id, target_id=target_id, body=body)


def _build_core_gateway_target_body(body_cls: type, config: TargetConfig) -> Any:
    mcp_server = CoreGatewayMcpServerTargetConfiguration(
        endpoint=config.endpoint,
        server_type=config.server_type,
    )
    target_configuration = CoreGatewayTargetConfiguration(mcp_server=mcp_server)

    oauth_credential_provider = CoreGatewayOAuthCredentialProvider(
        provider_name=config.provider_name,
        grant_type=config.grant_type,
        scopes=config.scopes or None,
        custom_parameters=config.custom_parameters or None,
    )
    credential_provider = CoreGatewayCredentialProvider(
        oauth_credential_provider=oauth_credential_provider,
    )
    credential_provider_configuration = CoreGatewayCredentialProviderConfiguration(
        credential_provider_type="oauth",
        credential_provider=credential_provider,
    )

    return body_cls(
        name=config.target_name,
        description=config.target_description,
        target_configuration=target_configuration,
        credential_provider_configuration=credential_provider_configuration,
    )


def _build_gateway_tags(raw_tags: list[str]) -> list[CoreGatewayTag] | None:
    if not raw_tags:
        return None
    tag_models: list[CoreGatewayTag] = []
    for raw in raw_tags:
        if "=" in raw:
            key, value = raw.split("=", 1)
        else:
            key, value = raw, ""
        tag_models.append(CoreGatewayTag(key=key.strip(), value=value.strip()))
    return tag_models
