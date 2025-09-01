module.exports = {
  root: true,
  env: {
    browser: true,
    es2023: true
  },
  extends: ['eslint:recommended', 'prettier'],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  overrides: [
    {
      files: ['*.svelte'],
      parser: 'svelte-eslint-parser',
      extends: ['plugin:svelte/recommended', 'prettier']
    }
  ],
  rules: {
    semi: ['error', 'never'],
    indent: ['error', 2]
  }
}
