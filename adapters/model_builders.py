from __future__ import annotations

import importlib
import re
from typing import Any

from domain.dto import GatewayConfig, OAuth2ProviderConfig, TargetConfig
from domain.exceptions import McpRegistrationError


class AgentArtsModelBuildError(McpRegistrationError):
    """当 AgentArts SDK 模型加载或实例化失败时抛出。"""


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


def build_create_core_gateway_request(config: GatewayConfig) -> Any:
    body = _new_model(
        "CreateCoreGatewayRequestBody",
        name=config.gateway_name,
        description=config.gateway_description,
        protocol_type=config.protocol_type,
        authorizer_type=config.authorizer_type,
        agency_name=config.agency_name,
        agent_gateway_id=config.agent_gateway_id,
        tags=_build_gateway_tags(config.tags),
    )
    return _new_model("CreateCoreGatewayRequest", body=body)


def build_list_core_gateways_request(name: str, limit: int = 100, offset: int = 0) -> Any:
    return _new_model("ListCoreGatewaysRequest", name=name, limit=limit, offset=offset)


def build_list_core_gateway_targets_request(gateway_id: str, limit: int = 100, offset: int = 0) -> Any:
    return _new_model("ListCoreGatewayTargetsRequest", gateway_id=gateway_id, limit=limit, offset=offset)


def build_show_core_gateway_target_request(gateway_id: str, target_id: str) -> Any:
    return _new_model("ShowCoreGatewayTargetRequest", gateway_id=gateway_id, target_id=target_id)


def build_create_core_gateway_target_request(gateway_id: str, config: TargetConfig) -> Any:
    body = _build_core_gateway_target_body("CreateCoreGatewayTargetRequestBody", config)
    return _new_model("CreateCoreGatewayTargetRequest", gateway_id=gateway_id, body=body)


def build_update_core_gateway_target_request(gateway_id: str, target_id: str, config: TargetConfig) -> Any:
    body = _build_core_gateway_target_body("UpdateCoreGatewayTargetRequestBody", config)
    return _new_model("UpdateCoreGatewayTargetRequest", gateway_id=gateway_id, target_id=target_id, body=body)


def _build_core_gateway_target_body(body_cls: str, config: TargetConfig) -> Any:
    mcp_server = _new_model(
        "CoreGatewayMcpServerTargetConfiguration",
        endpoint=config.endpoint,
        server_type=config.server_type,
    )
    target_configuration = _new_model("CoreGatewayTargetConfiguration", mcp_server=mcp_server)

    oauth_credential_provider = _new_model(
        "CoreGatewayOAuthCredentialProvider",
        provider_name=config.provider_name,
        grant_type=config.grant_type,
        scopes=config.scopes or None,
        custom_parameters=config.custom_parameters or None,
    )
    credential_provider = _new_model(
        "CoreGatewayCredentialProvider",
        oauth_credential_provider=oauth_credential_provider,
    )
    credential_provider_configuration = _new_model(
        "CoreGatewayCredentialProviderConfiguration",
        credential_provider_type="oauth",
        credential_provider=credential_provider,
    )

    return _new_model(
        body_cls,
        name=config.target_name,
        description=config.target_description,
        target_configuration=target_configuration,
        credential_provider_configuration=credential_provider_configuration,
    )


def _build_gateway_tags(raw_tags: list[str]) -> list[Any] | None:
    if not raw_tags:
        return None
    tag_models: list[Any] = []
    for raw in raw_tags:
        if "=" in raw:
            key, value = raw.split("=", 1)
        else:
            key, value = raw, ""
        tag_models.append(_new_model("CoreGatewayTag", key=key.strip(), value=value.strip()))
    return tag_models


def _new_model(class_name: str, **kwargs: Any) -> Any:
    cls = _load_model_class(class_name)
    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
    try:
        return cls(**filtered_kwargs)
    except Exception as exc:  # noqa: BLE001
        raise AgentArtsModelBuildError(
            f"实例化 {class_name} 失败，参数={list(filtered_kwargs.keys())}: {exc}"
        ) from exc


def _load_model_class(class_name: str) -> type:
    module_name = _camel_to_snake(class_name)
    full_module = f"huaweicloudsdkagentarts.v1.model.{module_name}"
    try:
        module = importlib.import_module(full_module)
        return getattr(module, class_name)
    except Exception as exc:  # noqa: BLE001
        raise AgentArtsModelBuildError(f"无法加载 AgentArts 模型 {class_name} ({full_module}): {exc}") from exc


def _camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
