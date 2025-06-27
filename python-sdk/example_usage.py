
import asyncio
from pleom_apitoolbox import ApiToolBox, User, ServiceConfig

async def service_loading_example():
    """Example showing service loading (mock example)"""
    print("\n=== Service Loading Example ===")
    
    api_toolbox = ApiToolBox()
    
    await api_toolbox.load_services(['vercel'])

    service_configs = [
        ServiceConfig('vercel', {
            'Authorization': 'Bearer <token goes here>'
        })
    ]
    
    user = User(api_toolbox, service_configs)

    result = await user.call_tool('vercelGetProjects')
    

async def main():
    await service_loading_example()

if __name__ == "__main__":
    asyncio.run(main()) 