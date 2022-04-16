module.exports = [
  {
    path: "/api",
    rule: {
      target: "http://localhost:6060/api",
      pathRewrite: { "^/api": "" },
    },
  },
];
