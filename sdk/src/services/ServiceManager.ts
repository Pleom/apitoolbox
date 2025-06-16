import { ToolName, ServicePage, ServiceTool } from '../types';
import * as fs from 'fs';
import * as path from 'path';
import { ServiceDownloader } from './ServiceDownloader';

export class ServiceManager {
  private connectedServices: Set<string> = new Set();
  private serviceDownloader: ServiceDownloader;
  private tools: any[] = []; // Array to store all loaded tools

  constructor() {
    this.serviceDownloader = new ServiceDownloader();
    this.initializeConnectedServices();
  }

  /**
   * Converts a service name and tool name to camelCase format
   * @param serviceName - The service name (e.g., 'vercel')
   * @param toolName - The tool name (e.g., 'Update an access group')
   * @returns Formatted camelCase string (e.g., 'vercelUpdateAnAccessGroup')
   */
  private toCamelCase(serviceName: string, toolName: string): string {
    // Remove special characters and split into words
    const cleanServiceName = serviceName.replace(/[^a-zA-Z0-9]/g, ' ').trim();
    const cleanToolName = toolName.replace(/[^a-zA-Z0-9]/g, ' ').trim();

    // Split into words and filter out empty strings
    const serviceWords = cleanServiceName
      .split(/\s+/)
      .filter((word) => word.length > 0);
    const toolWords = cleanToolName
      .split(/\s+/)
      .filter((word) => word.length > 0);

    // Combine all words
    const allWords = [...serviceWords, ...toolWords];

    // Convert to camelCase
    return allWords
      .map((word, index) => {
        if (index === 0) {
          return word.toLowerCase();
        }
        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
      })
      .join('');
  }

  /**
   * Scans the .apitoolbox directory and populates the initial list of connected services.
   */
  private initializeConnectedServices(): void {
    this.connectedServices = new Set();
    this.tools = [];
  }

  /**
   * Gets the list of services currently connected to this ApiToolBox instance.
   * @returns Array of top-level service names.
   */
  public getServices(): ToolName[] {
    return Array.from(this.connectedServices);
  }

  /**
   * Gets all loaded tools from connected services.
   * @returns Array of all tools with their full definitions.
   */
  public getTools(): any[] {
    return [...this.tools]; // Return a copy to prevent external modification
  }

  /**
   * Finds a tool by its idTool (camelCase identifier)
   * @param idTool - The camelCase tool identifier (e.g., "vercelRetrieveAListOfProjects")
   * @returns The complete tool object or undefined if not found
   */
  public findToolById(idTool: string): any | undefined {
    return this.tools.find((tool) => tool.idTool === idTool);
  }

  /**
   * Gets filtered and formatted tools for API consumption.
   * @param model - The model format to use: 'openai', 'gemini', or 'claude' (default: 'gemini')
   * @returns Array of tools formatted according to the specified model standard.
   */
  public listTools(model: 'openai' | 'gemini' | 'claude' = 'gemini'): any[] {
    const baseTools = this.tools.map((tool) => {
      // Build the result object in the correct order
      const result: any = {};

      // Always start with name and description
      result.name = tool.idTool;
      result.description = tool.description;

      // Format parameters object
      const parametersObj: any = {};
      if (tool.parameters && Object.keys(tool.parameters).length > 0) {
        parametersObj.parameters = tool.parameters;
      }
      if (tool.body && Object.keys(tool.body).length > 0) {
        parametersObj.body = tool.body;
      }

      // Add parameters if it has content (maintaining order)
      if (Object.keys(parametersObj).length > 0) {
        result.parameters = {
          type: 'object',
          ...parametersObj,
        };
      }

      // Add response last if it exists
      if (tool.response) {
        result.response = tool.response;
      }

      return result;
    });

    // Format according to model standard
    switch (model) {
      case 'openai':
        return baseTools.map((tool) => ({
          type: 'function',
          function: tool,
        }));

      case 'claude':
        return baseTools.map((tool) => {
          const claudeTool: any = {};

          // Maintain order: name, description, input_schema, response
          claudeTool.name = tool.name;
          claudeTool.description = tool.description;

          if (tool.parameters) {
            claudeTool.input_schema = tool.parameters;
          }

          if (tool.response) {
            claudeTool.response = tool.response;
          }

          return claudeTool;
        });

      case 'gemini':
      default:
        return baseTools;
    }
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
    const apitoolboxDir = path.join(process.cwd(), '.apitoolbox');
    if (!fs.existsSync(apitoolboxDir)) {
      fs.mkdirSync(apitoolboxDir, { recursive: true });
    }

    // Clear existing tools and reload all services to ensure consistency
    this.tools = [];

    for (const service of services) {
      const wasSuccessful = await this.processServicePath(
        service,
        apitoolboxDir,
        force_download
      );
      if (wasSuccessful) {
        const baseServiceName = service.split('/')[0];
        this.connectedServices.add(baseServiceName);
      }
    }

    // Load tools from all connected services
    for (const serviceName of this.connectedServices) {
      await this.loadToolsFromService(serviceName, apitoolboxDir);
    }
  }

  /**
   * Disconnects a service from the current ApiToolBox instance.
   * This does not delete the service files from disk.
   * @param serviceName - The name of the service to unload.
   */
  public unloadService(serviceName: string): void {
    this.connectedServices.delete(serviceName);
    // Remove tools from this service
    this.tools = this.tools.filter(
      (tool) => !tool.serviceName || tool.serviceName !== serviceName
    );
  }

  /**
   * Recursively loads all tools from a service directory.
   */
  private async loadToolsFromService(
    serviceName: string,
    baseDir: string
  ): Promise<void> {
    const serviceDir = path.join(baseDir, serviceName);
    await this.loadToolsFromDirectory(serviceDir, serviceName);
  }

  /**
   * Recursively loads tools from a directory and its subdirectories.
   */
  private async loadToolsFromDirectory(
    dirPath: string,
    serviceName: string
  ): Promise<void> {
    const pageJsonPath = path.join(dirPath, 'page.json');

    if (!fs.existsSync(pageJsonPath)) {
      return;
    }

    try {
      const pageContent = fs.readFileSync(pageJsonPath, 'utf-8');
      const page: ServicePage = JSON.parse(pageContent);

      if (page.tools) {
        for (const tool of page.tools) {
          // Check if this is an actual tool (has more than just a name) or a tool group
          const isToolGroup = Object.keys(tool).length === 1 && tool.name;

          if (!isToolGroup) {
            // This is an actual tool, add it to our tools array
            const idTool = this.toCamelCase(serviceName, tool.name);
            const toolWithService = {
              ...tool,
              idTool: idTool,
              serviceName: serviceName,
              servicePath: path.relative(
                path.join(process.cwd(), '.apitoolbox'),
                dirPath
              ),
            };
            this.tools.push(toolWithService);
          } else {
            // This is a tool group, recursively load from its subdirectory
            const toolGroupDir = path.join(dirPath, tool.name);
            if (fs.existsSync(toolGroupDir)) {
              await this.loadToolsFromDirectory(toolGroupDir, serviceName);
            }
          }
        }
      }
    } catch (error) {
      console.warn(`Error loading tools from ${dirPath}:`, error);
    }
  }

  private async processServicePath(
    servicePath: string,
    baseDir: string,
    forceDownload: boolean
  ): Promise<boolean> {
    const pathParts = servicePath.split('/');
    const baseServiceName = pathParts[0];

    if (pathParts.length === 1) {
      return this.processService(baseServiceName, baseDir, forceDownload);
    } else {
      return this.processSpecificToolGroup(pathParts, baseDir, forceDownload);
    }
  }

  private async processSpecificToolGroup(
    pathParts: string[],
    baseDir: string,
    forceDownload: boolean
  ): Promise<boolean> {
    const baseServiceName = pathParts[0];
    const toolGroupPath = pathParts.slice(1);
    const serviceDir = path.join(baseDir, baseServiceName);
    const servicePagePath = path.join(serviceDir, 'page.json');

    fs.mkdirSync(serviceDir, { recursive: true });

    if (!fs.existsSync(servicePagePath)) {
      const servicePage =
        await this.serviceDownloader.downloadServicePage(baseServiceName);
      if (servicePage) {
        fs.writeFileSync(servicePagePath, JSON.stringify(servicePage, null, 2));
      }
    }

    const urlPath = path.join(baseServiceName, ...toolGroupPath);
    const toolGroupPage =
      await this.serviceDownloader.downloadServicePage(urlPath);

    if (!toolGroupPage) {
      console.warn(`Warning: Tool group ${urlPath} not found`);
      return false;
    }

    const toolGroupDir = path.join(serviceDir, ...toolGroupPath);
    fs.mkdirSync(toolGroupDir, { recursive: true });
    const toolGroupPagePath = path.join(toolGroupDir, 'page.json');
    fs.writeFileSync(toolGroupPagePath, JSON.stringify(toolGroupPage, null, 2));

    for (const tool of toolGroupPage.tools) {
      await this.processTool(urlPath, tool, toolGroupDir);
    }
    return true;
  }

  private async processService(
    serviceName: string,
    baseDir: string,
    forceDownload: boolean
  ): Promise<boolean> {
    const serviceDir = path.join(baseDir, serviceName);
    const servicePagePath = path.join(serviceDir, 'page.json');

    if (fs.existsSync(serviceDir) && forceDownload) {
      const shouldRedownload = await this.checkVersionMismatch(
        serviceName,
        servicePagePath
      );
      if (shouldRedownload) {
        fs.rmSync(serviceDir, { recursive: true, force: true });
        this.connectedServices.delete(serviceName);
      } else {
        await this.ensureAllToolGroupsDownloaded(serviceName, serviceDir);
        return true;
      }
    } else if (fs.existsSync(serviceDir) && !forceDownload) {
      await this.ensureAllToolGroupsDownloaded(serviceName, serviceDir);
      return true;
    }

    const servicePage =
      await this.serviceDownloader.downloadServicePage(serviceName);

    if (!servicePage) {
      console.warn(`Warning: Service ${serviceName} not found`);
      return false;
    }

    fs.mkdirSync(serviceDir, { recursive: true });
    fs.writeFileSync(servicePagePath, JSON.stringify(servicePage, null, 2));

    for (const tool of servicePage.tools) {
      await this.processTool(serviceName, tool, serviceDir);
    }
    return true;
  }

  private async ensureAllToolGroupsDownloaded(
    serviceName: string,
    serviceDir: string
  ): Promise<void> {
    const servicePagePath = path.join(serviceDir, 'page.json');
    if (!fs.existsSync(servicePagePath)) return;

    try {
      const servicePageContent = fs.readFileSync(servicePagePath, 'utf-8');
      const servicePage: ServicePage = JSON.parse(servicePageContent);
      for (const tool of servicePage.tools) {
        await this.ensureToolGroupDownloaded(serviceName, tool, serviceDir);
      }
    } catch (error) {
      console.warn(`Error checking tool groups for ${serviceName}:`, error);
    }
  }

  private async ensureToolGroupDownloaded(
    servicePath: string,
    tool: ServiceTool,
    currentDir: string
  ): Promise<void> {
    const isToolGroup = Object.keys(tool).length === 1 && tool.name;
    if (!isToolGroup) return;

    const toolGroupDir = path.join(currentDir, tool.name);
    const toolGroupPagePath = path.join(toolGroupDir, 'page.json');

    if (!fs.existsSync(toolGroupDir) || !fs.existsSync(toolGroupPagePath)) {
      const urlPath = path.join(servicePath, tool.name);
      console.log(`Downloading missing tool group: ${urlPath}`);
      const toolGroupPage =
        await this.serviceDownloader.downloadServicePage(urlPath);

      if (toolGroupPage) {
        fs.mkdirSync(toolGroupDir, { recursive: true });
        fs.writeFileSync(
          toolGroupPagePath,
          JSON.stringify(toolGroupPage, null, 2)
        );
        for (const subTool of toolGroupPage.tools) {
          await this.processTool(urlPath, subTool, toolGroupDir);
        }
      }
    } else {
      const toolGroupPageContent = fs.readFileSync(toolGroupPagePath, 'utf-8');
      const toolGroupPage: ServicePage = JSON.parse(toolGroupPageContent);
      for (const subTool of toolGroupPage.tools) {
        await this.ensureToolGroupDownloaded(
          path.join(servicePath, tool.name),
          subTool,
          toolGroupDir
        );
      }
    }
  }

  private async processTool(
    serviceName: string,
    tool: ServiceTool,
    serviceDir: string
  ): Promise<void> {
    const isToolGroup = Object.keys(tool).length === 1 && tool.name;
    if (isToolGroup) {
      const toolGroupDir = path.join(serviceDir, tool.name);
      const urlPath = path.join(serviceName, tool.name);
      const toolGroupPage =
        await this.serviceDownloader.downloadServicePage(urlPath);

      if (toolGroupPage) {
        fs.mkdirSync(toolGroupDir, { recursive: true });
        const toolGroupPagePath = path.join(toolGroupDir, 'page.json');
        fs.writeFileSync(
          toolGroupPagePath,
          JSON.stringify(toolGroupPage, null, 2)
        );
        for (const subTool of toolGroupPage.tools) {
          await this.processTool(urlPath, subTool, toolGroupDir);
        }
      }
    }
  }

  private async checkVersionMismatch(
    serviceName: string,
    localPagePath: string
  ): Promise<boolean> {
    try {
      const localPageContent = fs.readFileSync(localPagePath, 'utf-8');
      const localPage: ServicePage = JSON.parse(localPageContent);
      const remotePage =
        await this.serviceDownloader.downloadServicePage(serviceName);
      return remotePage ? localPage.version !== remotePage.version : false;
    } catch (error) {
      return true;
    }
  }
}
