const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const webpack = require('webpack');
const path = require('path');

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin(), // Visualize bundle sizes
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
      feather: 'feather-icons',
      bootstrap: ['bootstrap/dist/js/bootstrap.esm.js', 'default'],
    }),
  ],
  mode: 'production',
  entry: {
    base: './js/base.js',
    portfolio: './js/portfolio.js',
    admin: './js/admin.js',
    home: './js/home.js',
  },
  output: {
    filename: '[name].bundle.js', // Main bundles
    chunkFilename: '[id].bundle.js', // Split chunks
    path: path.resolve(__dirname, 'js/bundles'), // Output directory
    publicPath: "/static/js/bundles/", // Public path for dynamic imports 
  },
  // devtool: 'source-map',
  // optimization: {
  //   runtimeChunk: "single", // Ensure Webpack runtime is included
  //   splitChunks: {
  //     chunks: 'all', // Automatically extract shared code into separate files
  //   },
  // },
  module: {
    rules: [
      {
        test: /\.css$/i, // Matches .css files
        use: ['style-loader', 'css-loader'], // Loads and injects CSS into JavaScript
      },
    ],
  },
};
