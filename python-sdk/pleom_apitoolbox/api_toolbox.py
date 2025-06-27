"""Main ApiToolBox class for the Python SDK"""

from typing import List, Dict, Any, Optional
from .types import ToolName, ApiToolBoxConfig
from .services import ServiceManager

class ApiToolBox:
    """Main ApiToolBox class for managing API services and tools"""
    
    def __init__(self, config: Optional[ApiToolBoxConfig] = None):
        """
        Initialize ApiToolBox instance
        
        Args:
            config: Configuration object for ApiToolBox (optional)
        """
        self.config = config or ApiToolBoxConfig()
        self.service_manager = ServiceManager()
    
    def get_services(self) -> List[ToolName]:
        """
        Get the list of services currently connected to this ApiToolBox instance
        
        Returns:
            Array of top-level service names
        """
        return self.service_manager.get_services()
    
    async def list_tools(self, model: str = 'gemini', filter_tools: bool = True) -> List[Dict[str, Any]]:
        """
        Get all loaded tools from connected services
        
        Args:
            model: The model format to use: 'openai', 'gemini', or 'claude' (default: 'gemini')
            filter_tools: Whether to filter and format tools (default: True). If False, returns raw tools array.
            
        Returns:
            Array of tools formatted according to the specified model standard, or raw tools if filter is False
        """
        return self.service_manager.list_tools(model, filter_tools)
    
    def find_tool_by_id(self, id_tool: str) -> Optional[Dict[str, Any]]:
        """
        Find a tool by its idTool (camelCase identifier)
        
        Args:
            id_tool: The camelCase tool identifier (e.g., "vercelRetrieveAListOfProjects")
            
        Returns:
            The complete tool object or None if not found
        """
        return self.service_manager.find_tool_by_id(id_tool)
    
    async def load_services(self, services: List[ToolName], force_download: bool = False):
        """
        Download and connect specified services to this ApiToolBox instance
        
        Args:
            services: Array of service names to load (e.g., 'vercel', 'vercel/access-groups')
            force_download: Optional flag to force re-download (defaults to False)
        """
        await self.service_manager.load_services(services, force_download)
    
    def unload_service(self, service_name: str):
        """
        Disconnect a service from the current ApiToolBox instance
        This does not delete the service files from disk
        
        Args:
            service_name: The name of the service to unload
        """
        self.service_manager.unload_service(service_name) 