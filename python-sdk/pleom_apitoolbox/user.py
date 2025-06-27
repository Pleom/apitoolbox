"""User class for handling authenticated API calls"""

import aiohttp
import json
import ssl
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode
from .api_toolbox import ApiToolBox

# Type definitions
UserConfig = Dict[str, Dict[str, Any]]

class ServiceConfig:
    """Configuration for a specific service"""
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config

class ToolCallError(Exception):
    """Exception raised when a tool call fails"""
    def __init__(self, message: str):
        super().__init__(message)
        self.name = 'ToolCallError'

class User:
    """User class for making authenticated API calls"""
    
    def __init__(self, api_toolbox: ApiToolBox, service_configs: Optional[List[ServiceConfig]] = None):
        """
        Initialize User instance
        
        Args:
            api_toolbox: ApiToolBox instance
            service_configs: List of service configurations (optional)
        """
        self.api_toolbox = api_toolbox
        self.config: UserConfig = {}
        
        # Convert service configs to user config format
        if service_configs:
            for service_config in service_configs:
                self.config[service_config.name] = service_config.config
    
    async def call_tool(self, tool_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call a tool with the specified ID and parameters
        
        Args:
            tool_id: The camelCase tool identifier (e.g., "vercelRetrieveAListOfProjects")
            parameters: Optional input parameters for the tool
            
        Returns:
            Dictionary containing status and data
            
        Raises:
            ToolCallError: If tool is not found or call fails
        """
        if parameters is None:
            parameters = {}
            
        tool = self.api_toolbox.find_tool_by_id(tool_id)
        
        if not tool:
            raise ToolCallError(f"Tool '{tool_id}' not found")
        
        # Get service configuration
        service_name = tool.get('serviceName')
        if not service_name:
            raise ToolCallError(f"Tool '{tool_id}' has no service name")
            
        service_config = self.config.get(service_name)
        if not service_config:
            raise ToolCallError(f"No configuration found for service '{service_name}'")
        
        # Build headers
        headers = {}
        if tool.get('headers') and isinstance(tool['headers'], list):
            for header in tool['headers']:
                if isinstance(header, dict) and header.get('name') and header.get('required'):
                    header_name = header['name']
                    if header_name in service_config:
                        headers[header_name] = service_config[header_name]
                    else:
                        raise ToolCallError(f"Required header '{header_name}' not found in service configuration")
        
        # Process endpoint and extract path parameters
        endpoint = tool.get('endpoint', '')
        if not endpoint:
            raise ToolCallError(f"Tool '{tool_id}' has no endpoint")
            
        # Extract path parameters
        import re
        path_param_regex = r'\{([^}]+)\}'
        path_params = re.findall(path_param_regex, endpoint)
        
        # Replace path parameters in endpoint
        processed_endpoint = endpoint
        for path_param in path_params:
            param_value = None
            if parameters.get('parameters') and path_param in parameters['parameters']:
                param_value = parameters['parameters'][path_param]
            elif path_param in parameters:
                param_value = parameters[path_param]
            
            if param_value is not None:
                processed_endpoint = processed_endpoint.replace(f'{{{path_param}}}', str(param_value))
            else:
                raise ToolCallError(f"Missing required path parameter: {path_param}")
        
        # Build URL with query parameters
        base_url = processed_endpoint
        query_params = {}
        
        if parameters.get('parameters'):
            for key, value in parameters['parameters'].items():
                # Skip path parameters as they're already used in endpoint
                if key not in path_params:
                    query_params[key] = str(value)
        
        # Add query parameters to URL
        if query_params:
            separator = '&' if '?' in base_url else '?'
            base_url += separator + urlencode(query_params)
        
        # Prepare request options
        method = tool.get('method', 'GET').upper()
        
        # Prepare body
        body_data = None
        if parameters.get('body') and parameters['body']:
            body_data = parameters['body']
            if isinstance(body_data, dict):
                body_data = json.dumps(body_data)
                headers['Content-Type'] = 'application/json'
        
        try:
            # Create SSL context that doesn't verify certificates (for development)
            # In production, you should use proper certificate verification
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create connector with SSL context and timeout
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.request(
                    method=method,
                    url=base_url,
                    headers=headers,
                    data=body_data
                ) as response:
                    
                    response_data = None
                    try:
                        response_data = await response.json()
                    except:
                        try:
                            response_data = await response.text()
                        except:
                            response_data = None
                    
                    return {
                        'status': response.status,
                        'data': response_data
                    }
                    
        except Exception as error:
            raise ToolCallError(f"Network error: {str(error)}")
    
    async def validate_tool_call(self, tool_id: str, api_response: Any) -> bool:
        """
        Validate an API response against the tool's response schema
        
        Args:
            tool_id: The camelCase tool identifier
            api_response: The response from the API call
            
        Returns:
            Boolean indicating if the response matches the expected schema
            
        Raises:
            ToolCallError: If tool is not found
        """
        tool = self.api_toolbox.find_tool_by_id(tool_id)
        
        if not tool:
            raise ToolCallError(f"Tool '{tool_id}' not found")
        
        # If tool has no response schema, consider it valid
        response_schema = tool.get('response')
        if not response_schema or not response_schema.get('properties'):
            print('No response schema defined, returning True')
            return True
        
        # If API response is not an object, handle differently
        if not isinstance(api_response, dict):
            # For non-object responses, if tool expects an object, it's invalid
            if response_schema.get('type') == 'object':
                print('API response is not an object but schema expects object')
                return False
            # For other types, we'll consider it valid since we can't deeply validate primitive types easily
            return True
        
        # Use BFS to find the expected schema anywhere in the response
        return self._bfs_validate_schema(api_response, response_schema.get('properties', {}))
    
    def _bfs_validate_schema(self, response: Any, expected_properties: Dict[str, Any]) -> bool:
        """
        Use Breadth-First Search to validate schema at any level of the response
        
        Args:
            response: The API response object
            expected_properties: Expected properties schema
            
        Returns:
            Boolean indicating if validation passed
        """
        from collections import deque
        
        if not isinstance(response, dict):
            return False
        
        # Start BFS with the root object
        queue = deque([response])
        
        while queue:
            current_obj = queue.popleft()
            
            if not isinstance(current_obj, dict):
                continue
            
            # Check if current object matches the expected schema
            if self._validate_properties(current_obj, expected_properties):
                return True
            
            # Add child objects to queue for further exploration
            for value in current_obj.values():
                if isinstance(value, dict):
                    queue.append(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            queue.append(item)
        
        return False
    
    def _validate_properties(self, obj: Dict[str, Any], expected_properties: Dict[str, Any]) -> bool:
        """
        Validate properties of an object against expected schema
        
        Args:
            obj: Object to validate
            expected_properties: Expected properties schema
            
        Returns:
            Boolean indicating if validation passed
        """
        if not expected_properties:
            return True
        
        for prop_name, prop_schema in expected_properties.items():
            if prop_name in obj:
                if isinstance(prop_schema, dict) and 'type' in prop_schema:
                    expected_type = prop_schema['type']
                    if not self._validate_type(obj[prop_name], expected_type):
                        return False
        
        return True
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """
        Validate a value against an expected type
        
        Args:
            value: Value to validate
            expected_type: Expected type string
            
        Returns:
            Boolean indicating if type matches
        """
        type_mapping = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        expected_python_type = type_mapping.get(expected_type.lower())
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True  # Unknown type, assume valid
    
    def get_config(self) -> UserConfig:
        """
        Get the current user configuration
        
        Returns:
            Current user configuration
        """
        return self.config.copy()
    
    def update_config(self, new_config: UserConfig):
        """
        Update the user configuration
        
        Args:
            new_config: New configuration to set
        """
        self.config = new_config.copy()
    
    def get_api_toolbox(self) -> ApiToolBox:
        """
        Get the ApiToolBox instance
        
        Returns:
            The ApiToolBox instance
        """
        return self.api_toolbox 