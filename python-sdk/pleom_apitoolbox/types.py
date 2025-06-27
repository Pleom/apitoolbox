"""Type definitions for ApiToolBox"""

from typing import Dict, Any, List, Optional

ToolName = str

class ApiToolBoxConfig:
    """Configuration class for ApiToolBox"""
    def __init__(self):
        pass

class Tool:
    """Represents a tool definition"""
    def __init__(self, name: ToolName, version: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.version = version
        self.config = config or {}

class ServiceTool:
    """Represents a service tool"""
    def __init__(self, name: str):
        self.name = name

class ServicePage:
    """Represents a service page with tools"""
    def __init__(self, name: str, version: str, tools: List[ServiceTool]):
        self.name = name
        self.version = version
        self.tools = tools 