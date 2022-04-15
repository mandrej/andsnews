module.exports = [
  {
    path: "/api",
    rule: {
      target: "http://localhost:6060/api",
      changeOrigin: true,
      pathRewrite: { "^/api": "" },
    },
  },
];
