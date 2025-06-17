export interface BrowserServiceConfig {
  name: string;
  config: {
    apiKey?: string;
    [key: string]: any;
  };
}

export class ToolCallError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ToolCallError';
  }
}

export class UserClient {
  private config: Record<string, any> = {};

  constructor(serviceConfigs: BrowserServiceConfig[] = []) {
    // Convert service configs to user config format
    for (const serviceConfig of serviceConfigs) {
      this.config[serviceConfig.name] = serviceConfig.config;
    }
  }

  /**
   * Calls a tool with the specified tool object and parameters
   * @param tool - The complete tool object (fetched externally)
   * @param parameters - Optional input parameters for the tool
   * @returns Promise that resolves with the API response
   */
  public async callTool(tool: any, parameters: any = {}): Promise<any> {
    if (!tool) {
      throw new ToolCallError('Tool object is required');
    }

    // Get service configuration
    const serviceConfig = this.config[tool.serviceName];
    if (!serviceConfig) {
      throw new ToolCallError(
        `No configuration found for service '${tool.serviceName}'`
      );
    }

    // Build headers
    const headers: Record<string, string> = {};
    if (tool.headers && Array.isArray(tool.headers)) {
      for (const header of tool.headers) {
        if (header.name && header.required) {
          if (serviceConfig[header.name]) {
            headers[header.name] = serviceConfig[header.name];
          } else {
            throw new ToolCallError(
              `Required header '${header.name}' not found in service configuration`
            );
          }
        }
      }
    }

    // Process endpoint and extract path parameters
    let endpoint = tool.endpoint;
    const pathParamRegex = /\{([^}]+)\}/g;
    const pathParams: string[] = [];
    let match;

    while ((match = pathParamRegex.exec(tool.endpoint)) !== null) {
      pathParams.push(match[1]);
    }

    // Replace path parameters in endpoint
    for (const pathParam of pathParams) {
      if (parameters.parameters && parameters.parameters[pathParam]) {
        endpoint = endpoint.replace(
          `{${pathParam}}`,
          parameters.parameters[pathParam]
        );
      } else {
        throw new ToolCallError(
          `Missing required path parameter: ${pathParam}`
        );
      }
    }

    // Build URL with query parameters
    const url = new URL(endpoint);
    if (parameters.parameters) {
      for (const [key, value] of Object.entries(parameters.parameters)) {
        // Skip path parameters as they're already used in endpoint
        if (!pathParams.includes(key)) {
          url.searchParams.set(key, String(value));
        }
      }
    }

    // Prepare fetch options
    const fetchOptions: RequestInit = {
      method: tool.method || 'GET',
      headers: headers,
    };

    // Add body if present
    if (parameters.body && Object.keys(parameters.body).length > 0) {
      if (typeof parameters.body === 'string') {
        fetchOptions.body = parameters.body;
      } else {
        fetchOptions.body = JSON.stringify(parameters.body);
        headers['Content-Type'] = 'application/json';
      }
    }

    try {
      const response = await fetch(url.toString(), fetchOptions);

      if (!response.ok) {
        throw new ToolCallError(
          `API request failed with status ${response.status}: ${response.statusText}`
        );
      }

      const responseData = await response.json();
      return responseData;
    } catch (error) {
      if (error instanceof ToolCallError) {
        throw error;
      }
      throw new ToolCallError(
        `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }

  /**
   * Gets the current configuration
   * @returns The user configuration object
   */
  public getConfig(): Record<string, any> {
    return { ...this.config };
  }

  /**
   * Updates the configuration with new values
   * @param newConfig - New configuration to merge
   */
  public updateConfig(newConfig: Record<string, any>): void {
    this.config = { ...this.config, ...newConfig };
  }
}
