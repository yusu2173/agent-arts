from __future__ import annotations

from typing import Any

from domain.dto import OAuth2ProviderConfig, ProviderInfo
from domain.exceptions import ProviderEnsureError


class IdentityProviderAdapter:
    """Identity 适配层，使用 AgentRun SDK 的 IdentityClient。"""

    def __init__(self, identity_client: Any):
        self.identity_client = identity_client

    def ensure_oauth2_provider(self, config: OAuth2ProviderConfig) -> ProviderInfo:
        try:
            response = self.identity_client.create_oauth2_credential_provider(
                name=config.provider_name,
                vendor=config.vendor,
                client_id=config.client_id,
                client_secret=config.client_secret,
                tenant_id=config.tenant_id,
                oauth_discovery=config.oauth_discovery,
            )
            provider_id = _safe_get(response, "id") or _safe_get(response, "provider_id")
            return ProviderInfo(name=config.provider_name, provider_id=provider_id, reused=False, raw=response)
        except Exception as exc:  # noqa: BLE001
            if _is_already_exists_error(exc):
                return ProviderInfo(name=config.provider_name, provider_id=None, reused=True, raw=None)
            raise ProviderEnsureError(f"create_oauth2_credential_provider 失败: {exc}") from exc


def _safe_get(data: Any, key: str) -> Any:
    if isinstance(data, dict):
        return data.get(key)
    return getattr(data, key, None)


def _is_already_exists_error(exc: Exception) -> bool:
    text = str(exc).lower()
    keywords = ["already exists", "already_exist", "409", "conflict", "duplicate"]
    return any(word in text for word in keywords)
