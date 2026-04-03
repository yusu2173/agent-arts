from __future__ import annotations

from typing import Any

from hw_agentrun_wrapper.identity.types import OAuth2Discovery, OAuth2Vendor
from hw_agentrun_wrapper.services.identity.identity_client import IdentityClient

from domain.dto import ProviderConfig, ProviderInfo
from domain.exceptions import ProviderEnsureError


class ProviderService:
    """基于 AgentRun IdentityClient 的 Provider 管理服务。"""

    def __init__(self, identity_client: IdentityClient):
        self.identity_client = identity_client

    def ensure_provider(self, config: ProviderConfig) -> ProviderInfo:
        existing = self.get_provider_by_name(config.provider_name)
        if existing is not None:
            return existing
        return self.create_provider(config)

    def get_provider_by_name(self, provider_name: str) -> ProviderInfo | None:
        """优先使用 SDK 的查询能力；若当前版本未暴露则返回 None 走创建路径。"""
        if hasattr(self.identity_client, "get_credential_provider"):
            try:
                item = self.identity_client.get_credential_provider(provider_name)
            except Exception as exc:  # noqa: BLE001
                raise ProviderEnsureError(f"查询 provider 失败: {exc}") from exc
            if item:
                return ProviderInfo(
                    provider_name=provider_name,
                    provider_id=_safe_get(item, "id") or _safe_get(item, "provider_id"),
                    reused=True,
                    raw=item,
                )

        if hasattr(self.identity_client, "list_credential_providers"):
            try:
                providers = self.identity_client.list_credential_providers()
            except Exception as exc:  # noqa: BLE001
                raise ProviderEnsureError(f"查询 provider 列表失败: {exc}") from exc
            for item in (providers or []):
                name = _safe_get(item, "name") or _safe_get(item, "provider_name")
                if name == provider_name:
                    return ProviderInfo(
                        provider_name=provider_name,
                        provider_id=_safe_get(item, "id") or _safe_get(item, "provider_id"),
                        reused=True,
                        raw=item,
                    )

        return None

    def create_provider(self, config: ProviderConfig) -> ProviderInfo:
        try:
            response = self.identity_client.create_oauth2_credential_provider(
                name=config.provider_name,
                vendor=_normalize_vendor(config.vendor),
                client_id=config.client_id,
                client_secret=config.client_secret,
                tenant_id=None,
                oauth_discovery=_build_oauth_discovery(config),
            )
        except Exception as exc:  # noqa: BLE001
            if _is_conflict_error(exc):
                return ProviderInfo(provider_name=config.provider_name, provider_id=None, reused=True, raw=None)
            raise ProviderEnsureError(f"创建 provider 失败: {exc}") from exc

        return ProviderInfo(
            provider_name=config.provider_name,
            provider_id=_safe_get(response, "id") or _safe_get(response, "provider_id"),
            reused=False,
            raw=response,
        )


def _build_oauth_discovery(config: ProviderConfig) -> OAuth2Discovery | None:
    """按当前 SDK 签名构建 OAuth2Discovery。

    当前签名：OAuth2Discovery(discovery_url=None, authorization_server_metadata=None)
    """
    metadata = {}
    if config.token_endpoint:
        metadata["token_endpoint"] = config.token_endpoint
    if config.authorization_endpoint:
        metadata["authorization_endpoint"] = config.authorization_endpoint
    if config.issuer:
        metadata["issuer"] = config.issuer

    if not config.discovery_url and not metadata:
        return None

    return OAuth2Discovery(
        discovery_url=config.discovery_url,
        authorization_server_metadata=metadata or None,
    )


def _normalize_vendor(vendor: str) -> str:
    if vendor.lower() == "custom":
        return OAuth2Vendor.CUSTOMOAUTH2
    return vendor


def _is_conflict_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(k in text for k in ["already", "conflict", "409", "exists"])


def _safe_get(data: Any, key: str) -> Any:
    if isinstance(data, dict):
        return data.get(key)
    return getattr(data, key, None)
