module.exports = {
  'root': true,
  'env': {
    'node': true
  },
  extends: [
    'plugin:vue/essential',
    'eslint:recommended'
  ],
  'parserOptions': {
    'parser': 'babel-eslint'
  },
  plugins: [
    'vuetify'
  ],
  rules: {
    'semi': [
      'error',
      'never'
    ],
    'quotes': [
      'error',
      'single',
      {
        'avoidEscape': true,
        'allowTemplateLiterals': true
      }
    ],
    'space-before-function-paren': [
      'error',
      {
        'anonymous': 'always',
        'named': 'always',
        'asyncArrow': 'always'
      }
    ],
    'vue/no-unused-components': 1,
    'vue/no-unused-vars': 1,
    'vuetify/no-deprecated-classes': 'error',
    'vuetify/grid-unknown-attributes': 'error',
    'vuetify/no-legacy-grid': 'error',
  }
}
