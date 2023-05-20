module.exports = [
  {
    path: "/api",
    rule: {
      target: "http://127.0.0.1:6060/api",
      changeOrigin: false,
      pathRewrite: { "^/api": "" },
    },
  },
];
