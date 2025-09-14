import baseConfig from '@opendocs/eslint-config/next.js'

/** @type {import("eslint").Linter.Config} */
export default [
  // Config for config files (no TypeScript project parsing)
  {
    files: ['*.config.js', '*.config.ts', 'eslint.config.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    rules: {
      'prettier/prettier': 'off',
    },
  },
  // Main config for source files
  {
    ...baseConfig[0],
    ignores: [
      'node_modules/',
      '.next/**/*',
      'out/**/*',
      'dist/**/*',
      'build/**/*',
      'coverage/**/*',
      'eslint.config.js',
    ],
  },
]
