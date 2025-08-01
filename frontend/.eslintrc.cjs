module.exports = {
  env: {
    browser: true,
    es2023: true
  },
  extends: ['eslint:recommended'],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    semi: ['error', 'never'],
    indent: ['error', 2]
  }
}
