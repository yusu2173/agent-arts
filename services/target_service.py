from __future__ import annotations

import time
from typing import Any

from hw_agentrun_wrapper.services.mcp_target_http import MCPTargetHttpService

from domain.constants import TARGET_STATUS_FAILED, TARGET_STATUS_READY
from domain.dto import TargetConfig, TargetInfo
from domain.exceptions import TargetEnsureError, TargetNotReadyError


class TargetService:
    """基于 AgentRun MCPTargetHttpService 的 Target 管理服务。"""

    def __init__(self, target_http_service: MCPTargetHttpService):
        self.target_http_service = target_http_service

    def ensure_target(self, gateway_id: str, config: TargetConfig) -> TargetInfo:
        existing = self.get_target_by_name(gateway_id, config.target_name)
        if existing is None:
            return self.create_target(gateway_id, config)
        if self._target_differs(existing.raw, config):
            return self.update_target(gateway_id, existing.target_id, config)
        return TargetInfo(
            target_id=existing.target_id,
            target_name=existing.target_name,
            target_status=existing.target_status,
            endpoint=existing.endpoint,
            server_type=existing.server_type,
            reused=True,
            raw=existing.raw,
        )

    def get_target_by_name(self, gateway_id: str, target_name: str) -> TargetInfo | None:
        try:
            targets = self.target_http_service.list_mcp_gateway_targets(gateway_id=gateway_id)
        except Exception as exc:  # noqa: BLE001
            raise TargetEnsureError(f"查询 target 失败: {exc}") from exc

        for item in (targets or []):
            name = _safe_get(item, "name")
            if name == target_name:
                return TargetInfo(
                    target_id=_safe_get(item, "id") or _safe_get(item, "target_id"),
                    target_name=name,
                    target_status=_safe_get(item, "status") or "unknown",
                    endpoint=_extract_endpoint(item),
                    server_type=_extract_server_type(item),
                    reused=True,
                    raw=item,
                )
        return None

    def create_target(self, gateway_id: str, config: TargetConfig) -> TargetInfo:
        try:
            response = self.target_http_service.create_mcp_gateway_target(
                gateway_id=gateway_id,
                name=config.target_name,
                description=config.description,
                endpoint=config.endpoint,
                server_type=config.server_type,
                provider_name=config.provider_name,
                grant_type=config.grant_type,
                scopes=config.scopes,
            )
        except Exception as exc:  # noqa: BLE001
            raise TargetEnsureError(f"创建 target 失败: {exc}") from exc

        return TargetInfo(
            target_id=_safe_get(response, "id") or _safe_get(response, "target_id"),
            target_name=_safe_get(response, "name") or config.target_name,
            target_status=_safe_get(response, "status") or "creating",
            endpoint=config.endpoint,
            server_type=config.server_type,
            reused=False,
            raw=response,
        )

    def update_target(self, gateway_id: str, target_id: str, config: TargetConfig) -> TargetInfo:
        try:
            response = self.target_http_service.update_mcp_gateway_target(
                gateway_id=gateway_id,
                target_id=target_id,
                name=config.target_name,
                description=config.description,
                endpoint=config.endpoint,
                server_type=config.server_type,
                provider_name=config.provider_name,
                grant_type=config.grant_type,
                scopes=config.scopes,
            )
        except Exception as exc:  # noqa: BLE001
            raise TargetEnsureError(f"更新 target 失败: {exc}") from exc

        return TargetInfo(
            target_id=_safe_get(response, "id") or _safe_get(response, "target_id") or target_id,
            target_name=_safe_get(response, "name") or config.target_name,
            target_status=_safe_get(response, "status") or "updating",
            endpoint=config.endpoint,
            server_type=config.server_type,
            reused=True,
            raw=response,
        )

    def wait_target_ready(
        self,
        gateway_id: str,
        target_id: str,
        max_attempts: int = 20,
        interval_seconds: float = 3.0,
    ) -> TargetInfo:
        for _ in range(max_attempts):
            try:
                response = self.target_http_service.get_mcp_gateway_target(gateway_id=gateway_id, target_id=target_id)
            except Exception as exc:  # noqa: BLE001
                raise TargetEnsureError(f"查询 target 详情失败: {exc}") from exc

            status = _safe_get(response, "status") or "unknown"
            if status == TARGET_STATUS_READY:
                return TargetInfo(
                    target_id=_safe_get(response, "id") or _safe_get(response, "target_id") or target_id,
                    target_name=_safe_get(response, "name") or "",
                    target_status=status,
                    endpoint=_extract_endpoint(response),
                    server_type=_extract_server_type(response),
                    reused=False,
                    raw=response,
                )
            if status == TARGET_STATUS_FAILED:
                raise TargetNotReadyError(f"target 进入失败状态: {target_id}")
            time.sleep(interval_seconds)

        raise TargetNotReadyError(f"target 等待 ready 超时: {target_id}")

    def _target_differs(self, current: Any, desired: TargetConfig) -> bool:
        current_endpoint = (_extract_endpoint(current) or "").rstrip("/")
        desired_endpoint = desired.endpoint.rstrip("/")
        current_server_type = _extract_server_type(current)
        current_provider_name = _extract_provider_name(current)
        current_grant_type = _extract_grant_type(current)
        return any(
            [
                current_endpoint != desired_endpoint,
                current_server_type != desired.server_type,
                current_provider_name != desired.provider_name,
                current_grant_type != desired.grant_type,
            ]
        )


def _extract_endpoint(data: Any) -> str:
    return _dig(data, "target_configuration", "mcp_server", "endpoint") or _dig(data, "endpoint") or ""


def _extract_server_type(data: Any) -> str:
    return _dig(data, "target_configuration", "mcp_server", "server_type") or _dig(data, "server_type") or ""


def _extract_provider_name(data: Any) -> str:
    return (
        _dig(
            data,
            "credential_provider_configuration",
            "credential_provider",
            "oauth_credential_provider",
            "provider_name",
        )
        or _dig(data, "provider_name")
        or ""
    )


def _extract_grant_type(data: Any) -> str:
    return (
        _dig(
            data,
            "credential_provider_configuration",
            "credential_provider",
            "oauth_credential_provider",
            "grant_type",
        )
        or _dig(data, "grant_type")
        or ""
    )


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
