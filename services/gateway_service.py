from __future__ import annotations

from typing import Any

from hw_agentrun_wrapper.services.mcp_gateway_http import MCPGatewayHttpService

from domain.dto import GatewayConfig, GatewayInfo
from domain.exceptions import GatewayEnsureError


class GatewayService:
    """基于 AgentRun MCPGatewayHttpService 的 Gateway 管理服务。"""

    def __init__(self, gateway_http_service: MCPGatewayHttpService):
        self.gateway_http_service = gateway_http_service

    def ensure_gateway(self, config: GatewayConfig) -> GatewayInfo:
        existing = self.get_gateway_by_name(config.gateway_name)
        if existing is not None:
            return existing
        return self.create_gateway(config)

    def get_gateway_by_name(self, gateway_name: str) -> GatewayInfo | None:
        try:
            resp = self.gateway_http_service.list_mcp_gateways(name=gateway_name, limit=50, offset=0)
        except Exception as exc:  # noqa: BLE001
            raise GatewayEnsureError(f"查询 gateway 失败: {exc}") from exc

        gateways = _safe_get(resp, "gateways") or resp or []
        for item in gateways:
            name = _safe_get(item, "name")
            if name == gateway_name:
                return GatewayInfo(
                    gateway_id=_safe_get(item, "gateway_id") or _safe_get(item, "id"),
                    gateway_name=name,
                    region=_safe_get(item, "region") or "",
                    reused=True,
                    raw=item,
                )
        return None

    def create_gateway(self, config: GatewayConfig) -> GatewayInfo:
        try:
            resp = self.gateway_http_service.create_mcp_gateway(
                name=config.gateway_name,
                description=config.description,
            )
        except Exception as exc:  # noqa: BLE001
            raise GatewayEnsureError(f"创建 gateway 失败: {exc}") from exc

        return GatewayInfo(
            gateway_id=_safe_get(resp, "gateway_id") or _safe_get(resp, "id"),
            gateway_name=_safe_get(resp, "name") or config.gateway_name,
            region=_safe_get(resp, "region") or config.region,
            reused=False,
            raw=resp,
        )


def _safe_get(data: Any, key: str) -> Any:
    if isinstance(data, dict):
        return data.get(key)
    return getattr(data, key, None)
