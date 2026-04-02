class McpRegistrationError(Exception):
    """MCP 注册基础异常。"""


class ProviderEnsureError(McpRegistrationError):
    """Provider 查询/创建/更新失败。"""


class GatewayEnsureError(McpRegistrationError):
    """Gateway 查询/创建失败。"""


class TargetEnsureError(McpRegistrationError):
    """Target 查询/创建/更新失败。"""


class TargetNotReadyError(McpRegistrationError):
    """Target 未达到就绪状态。"""


class InvalidMcpConfigError(McpRegistrationError):
    """MCP 配置非法。"""
