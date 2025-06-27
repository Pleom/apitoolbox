"""Service downloader for fetching service definitions"""

import os
import json
import asyncio
import aiohttp
import ssl
from typing import Optional, Dict, Any

class ServiceDownloader:
    """Downloads service definitions from remote sources"""
    
    def __init__(self):
        self.base_url = "https://apitoolbox.dev" 
    
    async def download_service_page(self, service_path: str) -> Optional[Dict[str, Any]]:
        """
        Download a service page from the API
        
        Args:
            service_path: The service path (e.g., 'vercel' or 'vercel/access-groups')
            
        Returns:
            Service page data as dictionary or None if not found
        """
        service_url = f"{self.base_url}/services/{service_path}.json"
        return await self._download_json(service_url)
    
    
    async def download_service(self, service_name: str, force_download: bool = False) -> Optional[Dict[str, Any]]:
        """
        Download a service definition (legacy method for backward compatibility)
        
        Args:
            service_name: Name of the service to download
            force_download: Whether to force re-download
            
        Returns:
            Service definition as dictionary or None if failed
        """
        return await self.download_service_page(service_name)
    
    async def download_tool_group(self, service_name: str, tool_group: str) -> Optional[Dict[str, Any]]:
        """
        Download a specific tool group for a service
        
        Args:
            service_name: Name of the service
            tool_group: Name of the tool group
            
        Returns:
            Tool group definition or None if failed
        """
        service_path = f"{service_name}/{tool_group}"
        return await self.download_service_page(service_path)
    
    async def _download_json(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Download and parse JSON from URL with proper error handling
        
        Args:
            url: URL to download from
            
        Returns:
            Parsed JSON data or None if failed
        """
        try:
            # Create SSL context that doesn't verify certificates (for development)
            # In production, you should use proper certificate verification
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create connector with SSL context and timeout
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        # Don't warn for 404s like the TypeScript version
                        return None
                    else:
                        print(f"Failed to download {url}: HTTP {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            print(f"Request timeout for {url}")
            return None
        except aiohttp.ClientError as e:
            print(f"Request error for {url}: {e}")
            return None
        except Exception as e:
            print(f"Error downloading from {url}: {e}")
            return None 