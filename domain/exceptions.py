class McpRegistrationError(Exception):
    """MCP 注册领域基础异常。"""


class InvalidMcpConfigError(McpRegistrationError):
    """MCP 配置不合法。"""


class ProviderEnsureError(McpRegistrationError):
    """Provider 创建/复用流程失败。"""


class GatewayEnsureError(McpRegistrationError):
    """Gateway 创建/复用流程失败。"""


class TargetEnsureError(McpRegistrationError):
    """Target 创建/更新/查询流程失败。"""


class TargetNotReadyError(McpRegistrationError):
    """Target 未在预期时间内进入就绪状态。"""
