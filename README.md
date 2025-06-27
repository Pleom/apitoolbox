[![npm version](https://img.shields.io/npm/v/apitoolbox.svg)](https://www.npmjs.com/package/apitoolbox)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# API Tool Box

> Stateless API Mapping Context for LLM Tooling

**🌐 Browse Services:** Visit [apitoolbox.dev/services](https://apitoolbox.dev/services) to see all available API services and their tools.

## Better than MCP? 🔧

API Tool Box tools are **direct API mappings** that convert service APIs into LLM-compatible tool definitions. Each tool represents a specific API endpoint with proper parameter validation and response schemas.

**Example:** Check out [apitoolbox.dev/services/vercel/access-groups](https://apitoolbox.dev/services/vercel/access-groups) to see what Vercel access group tools look like - they're simply structured API mappings.

### 🤖 Programmatic Tool Generation

Tools can be generated automatically using Open API specifications, web scrapers, and API documentation parsers. Generation utilities can be found at [apitoolbox-scraper](https://github.com/Pleom/apitoolbox-scraper) which extracts API definitions and converts them into ATB tool format.

## Why API Tool Box vs MCP? 🥊

| Feature                | API Tool Box ✅                               | MCP ❌                                       |
|------------------------|----------------------------------------------|----------------------------------------------|
| **Architecture**       | Stateless - no servers required               | Stateful - requires multiple running servers |
| **Language Agnostic**  | ✅ Run from any language, use the same tools  | ❌ Tied to a specific runtime                |
| **Execution Model**    | Pure API requests                             | Executes arbitrary code                      |
| **Multi-user Support** | ✅ Single server supports multiple users/SaaS | ❌ Complex server management per user        |
| **Service Ecosystem**  | ✅ Centralized monorepo for all services      | ❌ Disconnected repositories                 |
| **Scalability**        | ✅ Lightweight, scales horizontally           | ❌ Heavy resource requirements               |
| **Security**           | ✅ No code execution, API-only                | ❌ Code execution security concerns          |

**🎯 Goal:** Build a comprehensive monorepo of all service integrations, creating a single source of truth for LLMs to connect to any API.

## Installation

```typescript
import { ApiToolBox, User, ToolCallError } from "apitoolbox";Add commentMore actions

async function main() {
  // Create an ApiToolBox instance
  const atb = new ApiToolBox();

  // Load services (downloads and connects service definitions)Add commentMore actions
  await atb.loadServices(["vercel"]);
  
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

### Browser Version

For browser usage, import the script directly from `apitoolbox.dev/dist.js`:

**Client-Side Execution Benefits:** This approach executes API calls directly from the user's browser, enhancing security by keeping credentials client-side and eliminating server-side rate limiting issues that occur when multiple users share the same server IP address.

```html
<html>
  <body>
    <!-- Load the ApiToolBox browser SDK -->
    <script src="https://apitoolbox.dev/dist.js"></script>

    <script>
      // Tool schema (get this from your backend using findToolById)
      const vercelTool = {};

      // Configure credentials
      const credentials = [
        {
          name: 'vercel',
          config: { Authorization: 'Bearer YOUR_API_KEY' },
        },
      ];

              async function callTool() {
        try {
          const userClient = new ApiToolBox.UserClient(credentials);
          const result = await userClient.callTool(vercelTool, {
            parameters: {},
            body: {},
          });
              console.log('Status:', result.status);
    console.log('Data:', result.data);
    
    if (result.status === 200) {
      console.log('Success:', result.data);
    } else {
      console.log('API Error:', result.status, result.data);
    }
        } catch (error) {
          console.error('Error:', error);
        }
      }

      window.addEventListener('load', callTool);
    </script>
  </body>
</html>
```

**Backend Integration:** Use `atb.findToolById()` in your backend to get the complete tool schema and send it to your client, which can then execute the API request directly in the browser.

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
await atb.loadServices(['vercel/access-groups', 'vercel/projects']);
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

We welcome contributions to API Tool Box! Please see our [Contributing Guidelines](CONTRIBUTING.md) for detailed information on how to get started, development workflow, coding standards, and how to submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: royce@pleom.com
- 🐛 Issues: [GitHub Issues](https://github.com/pleom/apitoolbox/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/pleom/apitoolbox/discussions)
