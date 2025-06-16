# ApiToolBox SDK

[![npm version](https://img.shields.io/npm/v/apitoolbox.svg)](https://www.npmjs.com/package/apitoolbox)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Stateless API Mapping Context for LLM Tooling

ApiToolBox is a TypeScript SDK that provides a stateless API mapping context for Language Model (LLM) tooling.

## Installation

```bash
npm install apitoolbox
```

## Quick Start

```typescript
import { ApiToolBox, User, ToolCallError } from 'apitoolbox';

async function main() {
  // Create an ApiToolBox instance
  const atb = new ApiToolBox();

  // Load services (downloads and connects service definitions)
  await atb.loadServices(['vercel']);

  // List available tools
  const tools = await atb.listTools();
  console.log('Available tools:', tools);

  // Create a user with service configurations
  const user = new User(atb, [
    {
      name: 'vercel',
      config: {
        apiKey: 'Bearer YOUR_API_KEY_HERE',
      },
    },
  ]);

  try {
    // Call a specific tool
    const result = await user.callTool('vercelFindAProjectByIdOrName', {
      parameters: {
        idOrName: 'your-project-id',
      },
    });

    console.log('Result:', result);
  } catch (error) {
    if (error instanceof ToolCallError) {
      console.error('Tool call failed:', error.message);
    } else {
      console.error('Unexpected error:', error);
    }
  }
}

main();
```

## Core Classes

### ApiToolBox

The main class for managing services and tools.

```typescript
const atb = new ApiToolBox(config?: ApiToolBoxConfig);
```

#### Methods

- `loadServices(services: string[], force_download?: boolean): Promise<void>` - Load specified services
- `listTools(model?: 'openai' | 'gemini' | 'claude'): Promise<any[]>` - Get formatted tools for different LLM models
- `findToolById(idTool: string): any | undefined` - Find a specific tool by its camelCase ID
- `getServices(): string[]` - Get list of currently loaded services
- `unloadService(serviceName: string): void` - Disconnect a service

### User

The execution context for calling tools with authentication.

```typescript
const user = new User(apiToolBox: ApiToolBox, serviceConfigs?: ServiceConfig[]);
```

#### Methods

- `callTool(toolId: string, parameters?: any): Promise<any>` - Execute a tool with parameters
- `validateToolCall(toolId: string, apiResponse: any): Promise<boolean>` - Validate API response against tool schema
- `getConfig(): UserConfig` - Get current user configuration
- `updateConfig(newConfig: UserConfig): void` - Update user configuration

## Service Configuration

Configure services with API keys and other settings:

```typescript
const serviceConfigs = [
  {
    name: 'vercel',
    config: {
      apiKey: 'Bearer YOUR_VERCEL_TOKEN',
      // Additional service-specific config
    },
  },
  {
    name: 'github',
    config: {
      apiKey: 'Bearer YOUR_GITHUB_TOKEN',
      baseUrl: 'https://api.github.com', // Optional custom base URL
    },
  },
];

const user = new User(atb, serviceConfigs);
```

## Tool Formats

ApiToolBox supports multiple LLM tool formats:

### Gemini Format (Default)

```typescript
const tools = await atb.listTools('gemini');
// Returns tools in Gemini function calling format
```

### OpenAI Format

```typescript
const tools = await atb.listTools('openai');
// Returns tools wrapped in OpenAI function format:
// { type: 'function', function: { name, description, parameters } }
```

### Claude Format

```typescript
const tools = await atb.listTools('claude');
// Returns tools in Claude format with input_schema
```

## Error Handling

Use the `ToolCallError` class for proper error handling:

```typescript
try {
  const result = await user.callTool('toolName', { parameters: {} });
} catch (error) {
  if (error instanceof ToolCallError) {
    // Handle tool-specific errors
    console.error('Tool error:', error.message);
  } else {
    // Handle other errors
    console.error('Unexpected error:', error);
  }
}
```

## Advanced Usage

### Dynamic Service Loading

Load specific tool groups from services:

```typescript
// Load specific tool groups
await atb.loadServices([
  'vercel',
  'vercel/access-groups',
  'github/repositories',
]);
```

### Tool Discovery

Find and inspect tools:

```typescript
// List all tools
const allTools = await atb.listTools();

// Find a specific tool
const tool = atb.findToolById('vercelRetrieveAListOfProjects');

if (tool) {
  console.log('Tool description:', tool.description);
  console.log('Tool parameters:', tool.parameters);
  console.log('Tool response schema:', tool.response);
}
```

### Response Validation

Validate API responses against tool schemas:

```typescript
const result = await user.callTool('toolName', { parameters: {} });
const isValid = await user.validateToolCall('toolName', result);

if (!isValid) {
  console.warn("Response doesn't match expected schema");
}
```

## TypeScript Support

ApiToolBox provides comprehensive TypeScript types:

```typescript
import {
  ApiToolBox,
  User,
  UserConfig,
  ServiceConfig,
  ToolCallError,
  ToolName,
  ApiToolBoxConfig,
} from 'apitoolbox';
```

## Directory Structure

When you load services, ApiToolBox creates a `.apitoolbox` directory in your project root to cache service definitions:

```
your-project/
├── .apitoolbox/
│   ├── vercel/
│   │   ├── page.json
│   │   └── [tool-groups]/
│   └── [other-services]/
├── node_modules/
└── package.json
```

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our [GitHub repository](https://github.com/pleom/apitoolbox).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: royce@pleom.com
- 🐛 Issues: [GitHub Issues](https://github.com/pleom/apitoolbox/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/pleom/apitoolbox/discussions)
