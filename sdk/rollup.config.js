import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import typescript from '@rollup/plugin-typescript';

const config = [
  // CommonJS build
  {
    input: 'src/index.ts',
    output: {
      file: 'dist/cjs/index.js',
      format: 'cjs',
      sourcemap: true,
    },
    plugins: [
      resolve(),
      commonjs(),
      typescript({
        tsconfig: './tsconfig.json',
        declaration: false,
        outDir: 'dist/cjs',
      }),
    ],
    external: ['fs', 'path', 'os'],
  },
  // ESM build
  {
    input: 'src/index.ts',
    output: {
      file: 'dist/esm/index.js',
      format: 'esm',
      sourcemap: true,
    },
    plugins: [
      resolve(),
      commonjs(),
      typescript({
        tsconfig: './tsconfig.json',
        declaration: false,
        outDir: 'dist/esm',
      }),
    ],
    external: ['fs', 'path', 'os'],
  },
  // Browser build - UMD format for browser compatibility
  {
    input: 'src/browser/index.ts',
    output: {
      file: 'dist/browser/apitoolbox.js',
      format: 'umd',
      name: 'ApiToolBox',
      sourcemap: true,
    },
    plugins: [
      resolve({
        browser: true,
        preferBuiltins: false,
      }),
      commonjs(),
      typescript({
        tsconfig: './tsconfig.json',
        declaration: false,
        outDir: 'dist/browser',
      }),
    ],
    // No external dependencies for browser build - bundle everything
    external: [],
  },
  // Browser build - ES modules for modern browsers
  {
    input: 'src/browser/index.ts',
    output: {
      file: 'dist/browser/apitoolbox.esm.js',
      format: 'esm',
      sourcemap: true,
    },
    plugins: [
      resolve({
        browser: true,
        preferBuiltins: false,
      }),
      commonjs(),
      typescript({
        tsconfig: './tsconfig.json',
        declaration: false,
        outDir: 'dist/browser',
      }),
    ],
    // No external dependencies for browser build - bundle everything
    external: [],
  },
];

export default config;
