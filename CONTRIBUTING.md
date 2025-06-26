# Contributing to API Tool Box

We welcome contributions to API Tool Box! This project consists of a TypeScript SDK and Python server components. Please follow these guidelines to ensure a smooth contribution process.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/Pleom/apitoolbox.git
   cd apitoolbox
   ```

3. **Set up the development environment**:

   **For SDK Development:**
   ```bash
   cd sdk
   npm install
   ```

   **For Server Development:**
   ```bash
   cd tools/server
   pip install -r requirements.txt
   ```

## 📋 Development Workflow

### SDK Development (TypeScript)

The SDK is located in the `sdk/` directory and includes:

- **Build the project:**
  ```bash
  npm run build
  ```

- **Run tests:**
  ```bash
  npm test
  npm run test:watch    # Watch mode
  npm run test:coverage # With coverage
  ```

- **Development mode:**
  ```bash
  npm run dev  # Watch mode with automatic rebuilds
  ```

- **Code quality:**
  ```bash
  npm run lint          # Check linting
  npm run lint:fix      # Fix linting issues
  npm run format        # Format code
  npm run format:check  # Check formatting
  ```

### Server Development (Python)

The server component is in `tools/server/` and provides service definitions and metadata.

- **Run the server:**
  ```bash
  cd tools/server
  python app.py
  ```


## 📝 Pull Request Guidelines

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards:
   - Write clear, documented code
   - Follow existing code style

3. **Test your changes:**
   ```bash
   # SDK testing
   cd sdk && npm test
   
   # Manual testing
   npm run build
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new service integration for XYZ"
   ```
   
   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `test:` for tests
   - `refactor:` for refactoring

5. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub.

## 🏗️ Project Structure

```
apitoolbox/
├── sdk/                    # TypeScript SDK
│   ├── src/
│   │   ├── __tests__/      # Jest tests
│   │   ├── browser/        # Browser-specific code
│   │   ├── services/       # Service management
│   │   ├── user/           # User context
│   │   └── types.ts        # Type definitions
│   ├── package.json
│   └── tsconfig.json
└── tools/
    └── server/             # Python server
        ├── app.py          # Main server application
        └── requirements.txt
```

## 🐛 Reporting Issues

When reporting issues, please include:

1. **Environment details:**
   - Node.js/Python version
   - Operating system
   - Browser (if applicable)

2. **Steps to reproduce**
3. **Expected vs actual behavior**
4. **Minimal code example**
5. **Error messages/logs**

## 💬 Getting Help

- **Questions:** Use [GitHub Discussions](https://github.com/Pleom/apitoolbox/discussions)
- **Bugs:** Create an [issue](https://github.com/Pleom/apitoolbox/issues)
- **Email:** royce@pleom.com

## 📄 License

By contributing to API Tool Box, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You

Thank you for considering contributing to API Tool Box! Your contributions help make this project better for everyone. 