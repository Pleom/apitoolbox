"""Service manager for loading and managing API services"""

import os
import json
import re
from typing import List, Set, Dict, Any, Optional
from ..types import ToolName, ServicePage, ServiceTool
from .service_downloader import ServiceDownloader

class ServiceManager:
    """Manages loading and organization of API services"""
    
    def __init__(self):
        self.connected_services: Set[str] = set()
        self.service_downloader = ServiceDownloader()
        self.tools: List[Dict[str, Any]] = []
        self._initialize_connected_services()
    
    def _to_camel_case(self, service_name: str, tool_name: str) -> str:
        """
        Convert service name and tool name to camelCase format
        
        Args:
            service_name: The service name (e.g., 'vercel')
            tool_name: The tool name (e.g., 'Update an access group')
            
        Returns:
            Formatted camelCase string (e.g., 'vercelUpdateAnAccessGroup')
        """
        # Remove special characters and split into words
        clean_service_name = re.sub(r'[^a-zA-Z0-9]', ' ', service_name).strip()
        clean_tool_name = re.sub(r'[^a-zA-Z0-9]', ' ', tool_name).strip()
        
        # Split into words and filter out empty strings
        service_words = [word for word in clean_service_name.split() if word]
        tool_words = [word for word in clean_tool_name.split() if word]
        
        # Combine all words
        all_words = service_words + tool_words
        
        # Convert to camelCase
        result = ""
        for i, word in enumerate(all_words):
            if i == 0:
                result += word.lower()
            else:
                result += word.capitalize()
        
        return result
    
    def _initialize_connected_services(self):
        """Initialize the connected services set"""
        self.connected_services = set()
        self.tools = []
    
    def get_services(self) -> List[ToolName]:
        """
        Get the list of services currently connected to this ApiToolBox instance
        
        Returns:
            Array of top-level service names
        """
        return list(self.connected_services)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get all loaded tools from connected services
        
        Returns:
            Array of all tools with their full definitions
        """
        return self.tools.copy()  # Return a copy to prevent external modification
    
    def find_tool_by_id(self, id_tool: str) -> Optional[Dict[str, Any]]:
        """
        Find a tool by its idTool (camelCase identifier)
        
        Args:
            id_tool: The camelCase tool identifier (e.g., "vercelRetrieveAListOfProjects")
            
        Returns:
            The complete tool object or None if not found
        """
        for tool in self.tools:
            if tool.get('idTool') == id_tool:
                return tool
        return None
    
    def list_tools(self, model: str = 'gemini', filter_tools: bool = True) -> List[Dict[str, Any]]:
        """
        Get filtered and formatted tools for API consumption
        
        Args:
            model: The model format to use: 'openai', 'gemini', or 'claude' (default: 'gemini')
            filter_tools: Whether to filter and format tools (default: True). If False, returns raw tools array.
            
        Returns:
            Array of tools formatted according to the specified model standard, or raw tools if filter is False
        """
        # If filter is False, return raw tools array
        if not filter_tools:
            return self.tools.copy()
        
        base_tools = []
        for tool in self.tools:
            # Build the result object in the correct order
            result = {}
            
            # Always start with name and description
            result['name'] = tool.get('idTool', '')
            result['description'] = tool.get('description', '')
            
            # Format parameters object
            parameters_obj = {}
            if tool.get('parameters') and tool['parameters']:
                parameters_obj['parameters'] = tool['parameters']
            if tool.get('body') and tool['body']:
                parameters_obj['body'] = tool['body']
            
            # Add parameters if it has content
            if parameters_obj:
                result['parameters'] = {
                    'type': 'object',
                    **parameters_obj
                }
            
            # Add response last if it exists
            if tool.get('response'):
                result['response'] = tool['response']
            
            base_tools.append(result)
        
        # Format according to model standard
        if model == 'openai':
            return [{'type': 'function', 'function': tool} for tool in base_tools]
        elif model == 'claude':
            claude_tools = []
            for tool in base_tools:
                claude_tool = {
                    'name': tool['name'],
                    'description': tool['description']
                }
                if tool.get('parameters'):
                    claude_tool['input_schema'] = tool['parameters']
                if tool.get('response'):
                    claude_tool['response'] = tool['response']
                claude_tools.append(claude_tool)
            return claude_tools
        else:  # gemini (default)
            return base_tools
    
    async def load_services(self, services: List[ToolName], force_download: bool = False):
        """
        Download and connect specified services to this ApiToolBox instance
        
        Args:
            services: Array of service names to load (e.g., 'vercel', 'vercel/access-groups')
            force_download: Optional flag to force re-download (defaults to False)
        """
        apitoolbox_dir = os.path.join(os.getcwd(), '.apitoolbox')
        os.makedirs(apitoolbox_dir, exist_ok=True)
        
        # Clear existing tools and reload all services to ensure consistency
        self.tools = []
        
        for service in services:
            was_successful = await self._process_service_path(service, apitoolbox_dir, force_download)
            if was_successful:
                base_service_name = service.split('/')[0]
                self.connected_services.add(base_service_name)
        
        # Load tools from all connected services
        for service_name in self.connected_services:
            await self._load_tools_from_service(service_name, apitoolbox_dir)
    
    def unload_service(self, service_name: str):
        """
        Disconnect a service from the current ApiToolBox instance
        This does not delete the service files from disk
        
        Args:
            service_name: The name of the service to unload
        """
        self.connected_services.discard(service_name)
        # Remove tools from this service
        self.tools = [tool for tool in self.tools if tool.get('serviceName') != service_name]
    
    async def _load_tools_from_service(self, service_name: str, base_dir: str):
        """Load tools from a specific service directory"""
        service_dir = os.path.join(base_dir, service_name)
        if os.path.exists(service_dir):
            await self._load_tools_from_directory(service_dir, service_name)
    
    async def _load_tools_from_directory(self, dir_path: str, service_name: str):
        """Load tools from a directory containing service definitions"""
        try:
            # First, check if there's a page.json file in this directory
            page_json_path = os.path.join(dir_path, 'page.json')
            if os.path.exists(page_json_path):
                try:
                    with open(page_json_path, 'r', encoding='utf-8') as f:
                        page_data = json.load(f)
                        
                    # Load tools from the page data
                    if 'tools' in page_data:
                        for tool_data in page_data['tools']:
                            # Skip tool groups (they only have a name property)
                            is_tool_group = len(tool_data.keys()) == 1 and 'name' in tool_data
                            if not is_tool_group:
                                # This is an actual tool, add it to our tools list
                                tool_data['serviceName'] = service_name
                                
                                # Generate idTool if not present
                                if 'idTool' not in tool_data:
                                    tool_name = tool_data.get('name', '')
                                    tool_data['idTool'] = self._to_camel_case(service_name, tool_name)
                                
                                self.tools.append(tool_data.copy())
                except json.JSONDecodeError as e:
                    print(f"Error parsing page file {page_json_path}: {e}")
                except Exception as e:
                    print(f"Error loading page file {page_json_path}: {e}")
            
            # Recursively process subdirectories
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isdir(item_path):
                    await self._load_tools_from_directory(item_path, service_name)
                    
        except Exception as e:
            print(f"Error loading tools from directory {dir_path}: {e}")
    
    async def _process_service_path(self, service_path: str, base_dir: str, force_download: bool) -> bool:
        """Process a service path (either full service or specific tool group)"""
        path_parts = service_path.split('/')
        base_service_name = path_parts[0]
        
        if len(path_parts) == 1:
            # Full service
            return await self._process_service(base_service_name, base_dir, force_download)
        else:
            # Specific tool group
            return await self._process_specific_tool_group(path_parts, base_dir, force_download)
    
    async def _process_specific_tool_group(self, path_parts: List[str], base_dir: str, force_download: bool) -> bool:
        """Process a specific tool group within a service"""
        base_service_name = path_parts[0]
        tool_group_path = path_parts[1:]
        service_dir = os.path.join(base_dir, base_service_name)
        service_page_path = os.path.join(service_dir, 'page.json')
        
        os.makedirs(service_dir, exist_ok=True)
        
        # Download base service page if it doesn't exist
        if not os.path.exists(service_page_path):
            service_page = await self.service_downloader.download_service_page(base_service_name)
            if service_page:
                with open(service_page_path, 'w', encoding='utf-8') as f:
                    json.dump(service_page, f, indent=2)
        
        # Download the specific tool group
        url_path = '/'.join([base_service_name] + tool_group_path)
        tool_group_page = await self.service_downloader.download_service_page(url_path)
        
        if not tool_group_page:
            print(f"Warning: Tool group {url_path} not found")
            return False
        
        # Create directory structure for tool group
        tool_group_dir = os.path.join(service_dir, *tool_group_path)
        os.makedirs(tool_group_dir, exist_ok=True)
        tool_group_page_path = os.path.join(tool_group_dir, 'page.json')
        
        with open(tool_group_page_path, 'w', encoding='utf-8') as f:
            json.dump(tool_group_page, f, indent=2)
        
        # Process all tools in the tool group
        if 'tools' in tool_group_page:
            for tool in tool_group_page['tools']:
                await self._process_tool(url_path, tool, tool_group_dir)
        
        return True
    
    async def _process_service(self, service_name: str, base_dir: str, force_download: bool) -> bool:
        """Process a complete service"""
        service_dir = os.path.join(base_dir, service_name)
        service_page_path = os.path.join(service_dir, 'page.json')
        
        # Check if service exists and handle force download
        if os.path.exists(service_dir) and force_download:
            should_redownload = await self._check_version_mismatch(service_name, service_page_path)
            if should_redownload:
                import shutil
                shutil.rmtree(service_dir, ignore_errors=True)
                self.connected_services.discard(service_name)
            else:
                await self._ensure_all_tool_groups_downloaded(service_name, service_dir)
                return True
        elif os.path.exists(service_dir) and not force_download:
            await self._ensure_all_tool_groups_downloaded(service_name, service_dir)
            return True
        
        # Download the service page
        service_page = await self.service_downloader.download_service_page(service_name)
        
        if not service_page:
            print(f"Warning: Service {service_name} not found")
            return False
        
        # Create service directory and save page
        os.makedirs(service_dir, exist_ok=True)
        with open(service_page_path, 'w', encoding='utf-8') as f:
            json.dump(service_page, f, indent=2)
        
        # Process all tools in the service
        if 'tools' in service_page:
            for tool in service_page['tools']:
                await self._process_tool(service_name, tool, service_dir)
        
        return True
    
    async def _ensure_all_tool_groups_downloaded(self, service_name: str, service_dir: str):
        """Ensure all tool groups for a service are downloaded"""
        service_page_path = os.path.join(service_dir, 'page.json')
        if not os.path.exists(service_page_path):
            return
        
        try:
            with open(service_page_path, 'r', encoding='utf-8') as f:
                service_page = json.load(f)
                
            if 'tools' in service_page:
                for tool in service_page['tools']:
                    await self._ensure_tool_group_downloaded(service_name, tool, service_dir)
        except Exception as e:
            print(f"Error checking tool groups for {service_name}: {e}")
    
    async def _ensure_tool_group_downloaded(self, service_path: str, tool: Dict[str, Any], current_dir: str):
        """Ensure a specific tool group is downloaded"""
        # Check if this is a tool group (has only name property)
        is_tool_group = len(tool.keys()) == 1 and 'name' in tool
        if not is_tool_group:
            return
        
        tool_group_dir = os.path.join(current_dir, tool['name'])
        tool_group_page_path = os.path.join(tool_group_dir, 'page.json')
        
        if not os.path.exists(tool_group_dir) or not os.path.exists(tool_group_page_path):
            # Download missing tool group
            url_path = f"{service_path}/{tool['name']}"
            print(f"Downloading missing tool group: {url_path}")
            tool_group_page = await self.service_downloader.download_service_page(url_path)
            
            if tool_group_page:
                os.makedirs(tool_group_dir, exist_ok=True)
                with open(tool_group_page_path, 'w', encoding='utf-8') as f:
                    json.dump(tool_group_page, f, indent=2)
                    
                if 'tools' in tool_group_page:
                    for sub_tool in tool_group_page['tools']:
                        await self._process_tool(url_path, sub_tool, tool_group_dir)
        else:
            # Tool group exists, check if sub-tool groups need downloading
            try:
                with open(tool_group_page_path, 'r', encoding='utf-8') as f:
                    tool_group_page = json.load(f)
                    
                if 'tools' in tool_group_page:
                    for sub_tool in tool_group_page['tools']:
                        new_service_path = f"{service_path}/{tool['name']}"
                        await self._ensure_tool_group_downloaded(new_service_path, sub_tool, tool_group_dir)
            except Exception as e:
                print(f"Error reading tool group page {tool_group_page_path}: {e}")
    
    async def _process_tool(self, service_name: str, tool: Dict[str, Any], service_dir: str):
        """Process a tool, downloading tool groups recursively if needed"""
        # Check if this is a tool group (has only name property)
        is_tool_group = len(tool.keys()) == 1 and 'name' in tool
        
        if is_tool_group:
            # This is a tool group, download it recursively
            tool_group_dir = os.path.join(service_dir, tool['name'])
            url_path = f"{service_name}/{tool['name']}"
            tool_group_page = await self.service_downloader.download_service_page(url_path)
            
            if tool_group_page:
                os.makedirs(tool_group_dir, exist_ok=True)
                tool_group_page_path = os.path.join(tool_group_dir, 'page.json')
                with open(tool_group_page_path, 'w', encoding='utf-8') as f:
                    json.dump(tool_group_page, f, indent=2)
                
                # Recursively process tools in the tool group
                if 'tools' in tool_group_page:
                    for sub_tool in tool_group_page['tools']:
                        await self._process_tool(url_path, sub_tool, tool_group_dir)
        # Note: Individual tools are NOT saved as separate files
        # They remain as part of the tools array in the page.json files
    
    async def _check_version_mismatch(self, service_name: str, local_page_path: str) -> bool:
        """Check if local service version differs from remote version"""
        try:
            with open(local_page_path, 'r', encoding='utf-8') as f:
                local_page = json.load(f)
                
            remote_page = await self.service_downloader.download_service_page(service_name)
            
            if remote_page and 'version' in local_page and 'version' in remote_page:
                return local_page['version'] != remote_page['version']
            
            return False
        except Exception:
            # If we can't read the local page or fetch remote, assume we need to redownload
            return True 