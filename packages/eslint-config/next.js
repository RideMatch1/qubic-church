import { resolve } from 'node:path'

const project = resolve(process.cwd(), 'tsconfig.json')

/** @type {import("eslint").Linter.Config} */
export default [
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      parser: (await import('@typescript-eslint/parser')).default,
      parserOptions: {
        project,
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        React: 'readonly',
        JSX: 'readonly',
      },
    },
    plugins: {
      '@typescript-eslint': (await import('@typescript-eslint/eslint-plugin')).default,
      prettier: (await import('eslint-plugin-prettier')).default,
      'only-warn': (await import('eslint-plugin-only-warn')).default,
      '@next/next': (await import('@next/eslint-plugin-next')).default,
    },
    rules: {
      'prettier/prettier': [
        'error',
        {
          semi: false,
          singleQuote: true,
          tabWidth: 2,
          useTabs: false,
          trailingComma: 'es5',
        },
      ],
      '@next/next/no-html-link-for-pages': 'off',
      'no-duplicate-imports': 'error',
      'eslint-plugin-import/no-unassigned-import': 'off',
    },
    settings: {
      'import/resolver': {
        typescript: {
          project,
        },
      },
    },
  },
]
