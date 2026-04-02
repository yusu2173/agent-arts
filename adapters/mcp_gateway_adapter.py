from __future__ import annotations

import time
from dataclasses import replace
from typing import Any

from huaweicloudsdkagentarts.v1 import AgentArtsClient

from adapters.model_builders import (
    build_create_core_gateway_request,
    build_create_core_gateway_target_request,
    build_list_core_gateways_request,
    build_list_core_gateway_targets_request,
    build_show_core_gateway_target_request,
    build_update_core_gateway_target_request,
)
from domain.constants import TARGET_STATUS_FAILED, TARGET_STATUS_READY
from domain.dto import GatewayConfig, GatewayInfo, TargetConfig, TargetInfo
from domain.exceptions import GatewayEnsureError, TargetEnsureError, TargetNotReadyError


class McpGatewayAdapter:
    """AgentArts Core Gateway/Target 适配层（仅使用 SDK Request Model 调用）。"""

    def __init__(self, agentarts_client: AgentArtsClient):
        self.client = agentarts_client

    def ensure_gateway(self, config: GatewayConfig) -> GatewayInfo:
        existing = self.get_gateway_by_name(config.gateway_name)
        if existing is not None:
            return replace(existing, reused=True)
        return self.create_gateway(config)

    def get_gateway_by_name(self, name: str) -> GatewayInfo | None:
        request = build_list_core_gateways_request(name)
        try:
            response = self.client.list_core_gateways(request)
        except Exception as exc:  # noqa: BLE001
            raise GatewayEnsureError(f"list_core_gateways 失败: {exc}") from exc

        gateways = self._extract_collection(response, ["core_gateways", "gateways", "data", "items"])
        for item in gateways:
            if (_safe_get(item, "name") or "") == name:
                return GatewayInfo(
                    gateway_id=_safe_get(item, "id") or _safe_get(item, "gateway_id"),
                    gateway_name=name,
                    region=_safe_get(item, "region") or "",
                    raw=item,
                )
        return None

    def create_gateway(self, config: GatewayConfig) -> GatewayInfo:
        request = build_create_core_gateway_request(config)
        try:
            response = self.client.create_core_gateway(request)
        except Exception as exc:  # noqa: BLE001
            raise GatewayEnsureError(f"create_core_gateway 失败: {exc}") from exc

        payload = self._extract_payload(response)
        return GatewayInfo(
            gateway_id=_safe_get(payload, "id") or _safe_get(payload, "gateway_id"),
            gateway_name=_safe_get(payload, "name") or config.gateway_name,
            region=_safe_get(payload, "region") or config.region,
            raw=payload,
        )

    def ensure_target(self, gateway_id: str, config: TargetConfig) -> TargetInfo:
        existing = self.get_target_by_name(gateway_id, config.target_name)
        if existing is None:
            return self.create_target(gateway_id, config)

        if self._target_differs(existing.raw, config):
            return self.update_target(gateway_id, existing.target_id, config)

        return replace(existing, reused=True)

    def get_target_by_name(self, gateway_id: str, name: str) -> TargetInfo | None:
        request = build_list_core_gateway_targets_request(gateway_id)
        try:
            response = self.client.list_core_gateway_targets(request)
        except Exception as exc:  # noqa: BLE001
            raise TargetEnsureError(f"list_core_gateway_targets 失败: {exc}") from exc

        targets = self._extract_collection(response, ["core_gateway_targets", "targets", "data", "items"])
        for target in targets:
            if (_safe_get(target, "name") or "") == name:
                return TargetInfo(
                    target_id=_safe_get(target, "id") or _safe_get(target, "target_id"),
                    target_name=name,
                    endpoint=self._extract_endpoint(target),
                    server_type=self._extract_server_type(target),
                    status=_safe_get(target, "status") or "unknown",
                    raw=target,
                )
        return None

    def create_target(self, gateway_id: str, config: TargetConfig) -> TargetInfo:
        request = build_create_core_gateway_target_request(gateway_id, config)
        try:
            response = self.client.create_core_gateway_target(request)
        except Exception as exc:  # noqa: BLE001
            raise TargetEnsureError(f"create_core_gateway_target 失败: {exc}") from exc

        payload = self._extract_payload(response)
        return TargetInfo(
            target_id=_safe_get(payload, "id") or _safe_get(payload, "target_id"),
            target_name=_safe_get(payload, "name") or config.target_name,
            endpoint=config.endpoint,
            server_type=config.server_type,
            status=_safe_get(payload, "status") or "creating",
            raw=payload,
        )

    def update_target(self, gateway_id: str, target_id: str, config: TargetConfig) -> TargetInfo:
        request = build_update_core_gateway_target_request(gateway_id, target_id, config)
        try:
            response = self.client.update_core_gateway_target(request)
        except Exception as exc:  # noqa: BLE001
            raise TargetEnsureError(f"update_core_gateway_target 失败: {exc}") from exc

        payload = self._extract_payload(response)
        return TargetInfo(
            target_id=_safe_get(payload, "id") or _safe_get(payload, "target_id") or target_id,
            target_name=_safe_get(payload, "name") or config.target_name,
            endpoint=config.endpoint,
            server_type=config.server_type,
            status=_safe_get(payload, "status") or "updating",
            reused=True,
            raw=payload,
        )

    def wait_target_ready(
        self,
        gateway_id: str,
        target_id: str,
        max_attempts: int = 10,
        initial_interval_seconds: float = 2.0,
        max_interval_seconds: float = 60.0,
    ) -> TargetInfo:
        interval = initial_interval_seconds
        for attempt in range(1, max_attempts + 1):
            target = self._get_target_by_id(gateway_id, target_id)
            if target.status == TARGET_STATUS_READY:
                return target
            if target.status == TARGET_STATUS_FAILED:
                raise TargetNotReadyError(f"target 进入失败状态, target_id={target_id}")

            if attempt < max_attempts:
                time.sleep(interval)
                interval = min(interval * 2, max_interval_seconds)

        raise TargetNotReadyError(f"target 就绪超时, target_id={target_id}, attempts={max_attempts}")

    def _get_target_by_id(self, gateway_id: str, target_id: str) -> TargetInfo:
        request = build_show_core_gateway_target_request(gateway_id, target_id)
        try:
            response = self.client.show_core_gateway_target(request)
        except Exception as exc:  # noqa: BLE001
            raise TargetEnsureError(f"show_core_gateway_target 失败: {exc}") from exc

        payload = self._extract_payload(response)
        return TargetInfo(
            target_id=_safe_get(payload, "id") or _safe_get(payload, "target_id") or target_id,
            target_name=_safe_get(payload, "name") or "",
            endpoint=self._extract_endpoint(payload),
            server_type=self._extract_server_type(payload),
            status=_safe_get(payload, "status") or "unknown",
            raw=payload,
        )

    def _target_differs(self, current: Any, desired: TargetConfig) -> bool:
        current_endpoint = (self._extract_endpoint(current) or "").rstrip("/")
        desired_endpoint = desired.endpoint.rstrip("/")
        current_server_type = self._extract_server_type(current)
        current_provider_name = self._extract_provider_name(current)
        current_grant_type = self._extract_grant_type(current)
        current_scopes = sorted(self._extract_scopes(current))
        desired_scopes = sorted(desired.scopes)
        current_params = dict(sorted(self._extract_custom_parameters(current).items()))
        desired_params = dict(sorted(desired.custom_parameters.items()))

        return any(
            [
                current_endpoint != desired_endpoint,
                current_server_type != desired.server_type,
                current_provider_name != desired.provider_name,
                current_grant_type != desired.grant_type,
                current_scopes != desired_scopes,
                current_params != desired_params,
            ]
        )

    def _extract_endpoint(self, data: Any) -> str:
        return (
            _dig(data, "target_configuration", "mcp_server", "endpoint")
            or _dig(data, "mcp_server", "endpoint")
            or ""
        )

    def _extract_server_type(self, data: Any) -> str:
        return (
            _dig(data, "target_configuration", "mcp_server", "server_type")
            or _dig(data, "mcp_server", "server_type")
            or ""
        )

    def _extract_provider_name(self, data: Any) -> str:
        return (
            _dig(
                data,
                "credential_provider_configuration",
                "credential_provider",
                "oauth_credential_provider",
                "provider_name",
            )
            or ""
        )

    def _extract_grant_type(self, data: Any) -> str:
        return (
            _dig(
                data,
                "credential_provider_configuration",
                "credential_provider",
                "oauth_credential_provider",
                "grant_type",
            )
            or ""
        )

    def _extract_scopes(self, data: Any) -> list[str]:
        scopes = _dig(
            data,
            "credential_provider_configuration",
            "credential_provider",
            "oauth_credential_provider",
            "scopes",
        )
        return list(scopes or [])

    def _extract_custom_parameters(self, data: Any) -> dict[str, str]:
        params = _dig(
            data,
            "credential_provider_configuration",
            "credential_provider",
            "oauth_credential_provider",
            "custom_parameters",
        )
        return dict(params or {})

    def _extract_payload(self, response: Any) -> Any:
        if response is None:
            return None
        for key in ["core_gateway", "gateway", "core_gateway_target", "target", "data"]:
            value = _safe_get(response, key)
            if value is not None:
                return value
        return response

    def _extract_collection(self, response: Any, keys: list[str]) -> list[Any]:
        if response is None:
            return []
        for key in keys:
            value = _safe_get(response, key)
            if value is not None:
                return list(value)
        if isinstance(response, list):
            return response
        return []


def _safe_get(data: Any, key: str) -> Any:
    if isinstance(data, dict):
        return data.get(key)
    return getattr(data, key, None)


def _dig(data: Any, *keys: str) -> Any:
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            current = getattr(current, key, None)
        if current is None:
            return None
    return current
