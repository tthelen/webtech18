const path = require('path');  // node.js uses CommonJS modules

module.exports = {
  entry: './clientsrc/client.js',  // the entry point
  output: {
    filename: 'bundle.js',  // the output filename
    path: path.resolve(__dirname, 'public')  // fully qualified path
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [ 'style-loader', 'css-loader' ]
      }
    ]
  }
};
