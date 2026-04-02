from __future__ import annotations

from typing import Any

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
            return ProviderInfo(
                provider_name=existing.provider_name,
                provider_id=existing.provider_id,
                reused=True,
                raw=existing.raw,
            )
        return self.create_provider(config)

    def get_provider_by_name(self, provider_name: str) -> ProviderInfo | None:
        try:
            providers = self.identity_client.list_credential_providers()
        except Exception as exc:  # noqa: BLE001
            raise ProviderEnsureError(f"查询 provider 失败: {exc}") from exc

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
                vendor=config.vendor,
                client_id=config.client_id,
                client_secret=config.client_secret,
                discovery_url=config.discovery_url,
                token_endpoint=config.token_endpoint,
                authorization_endpoint=config.authorization_endpoint,
                issuer=config.issuer,
                kms_key_id=config.kms_key_id,
                region=config.region,
            )
        except TypeError:
            # 兼容部分版本的参数名 oauth_discovery
            try:
                response = self.identity_client.create_oauth2_credential_provider(
                    name=config.provider_name,
                    vendor=config.vendor,
                    client_id=config.client_id,
                    client_secret=config.client_secret,
                    oauth_discovery=config.discovery_url,
                )
            except Exception as exc:  # noqa: BLE001
                raise ProviderEnsureError(f"创建 provider 失败: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            raise ProviderEnsureError(f"创建 provider 失败: {exc}") from exc

        return ProviderInfo(
            provider_name=config.provider_name,
            provider_id=_safe_get(response, "id") or _safe_get(response, "provider_id"),
            reused=False,
            raw=response,
        )


def _safe_get(data: Any, key: str) -> Any:
    if isinstance(data, dict):
        return data.get(key)
    return getattr(data, key, None)
