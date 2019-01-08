const path = require('path');  // node.js uses CommonJS modules

module.exports = {
  entry: './src/index.js',  // the entry point
  output: {
    filename: 'bundle.js',  // the output filename
    path: path.resolve(__dirname, 'dist')  // fully qualified path
  }
};
