"use strict";

const path = require("path");

module.exports = {
  // mode: 'development',
  entry: "./static/src/app.ts",
  context: path.resolve(__dirname),
  output: {
    path: path.resolve(__dirname, "static/js"),
    filename: "bundle.js",
  },
  module: {
    rules: [
      { test: /\.tsx?$/, use: "ts-loader", exclude: /node_modules/ },
      { test: /\.js$/, loader: "source-map-loader" },
    ],
  },
  resolve: {
    extensions: [".webpack.js", ".web.js", ".ts", ".tsx", ".js"],
  },
  devtool: "source-map",
  plugins: [],
};
