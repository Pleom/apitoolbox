import { ToolName, ApiToolBoxConfig } from './types';
import { ServiceManager } from './services';

export class ApiToolBox {
  private config: ApiToolBoxConfig;
  private serviceManager: ServiceManager;

  constructor(config: ApiToolBoxConfig = {}) {
    this.config = config;
    this.serviceManager = new ServiceManager();
  }

  /**
   * Gets the list of services currently connected to this ApiToolBox instance.
   * @returns Array of top-level service names.
   */
  public getServices(): ToolName[] {
    return this.serviceManager.getServices();
  }

  /**
   * Gets all loaded tools from connected services.
   * @param model - The model format to use: 'openai', 'gemini', or 'claude' (default: 'gemini')
   * @returns Array of tools formatted according to the specified model standard.
   */
  public async listTools(
    model: 'openai' | 'gemini' | 'claude' = 'gemini'
  ): Promise<any[]> {
    return this.serviceManager.listTools(model);
  }

  /**
   * Finds a tool by its idTool (camelCase identifier)
   * @param idTool - The camelCase tool identifier (e.g., "vercelRetrieveAListOfProjects")
   * @returns The complete tool object or undefined if not found
   */
  public findToolById(idTool: string): any | undefined {
    return this.serviceManager.findToolById(idTool);
  }

  /**
   * Downloads and connects specified services to this ApiToolBox instance.
   * @param services - Array of service names to load (e.g., 'vercel', 'vercel/access-groups').
   * @param force_download - Optional flag to force re-download (defaults to false).
   */
  public async loadServices(
    services: ToolName[],
    force_download: boolean = false
  ): Promise<void> {
    return this.serviceManager.loadServices(services, force_download);
  }

  /**
   * Disconnects a service from the current ApiToolBox instance.
   * This does not delete the service files from disk.
   * @param serviceName - The name of the service to unload.
   */
  public unloadService(serviceName: string): void {
    this.serviceManager.unloadService(serviceName);
  }
}
