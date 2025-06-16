export type ToolName = string;

export interface ApiToolBoxConfig {
  // Simplified config - removed version and debug
}

export interface Tool {
  name: ToolName;
  version?: string;
  config?: Record<string, any>;
}

// New interfaces for service page structure
export interface ServiceTool {
  name: string;
}

export interface ServicePage {
  name: string;
  version: string;
  tools: ServiceTool[];
}
