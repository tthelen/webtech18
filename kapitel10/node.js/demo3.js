var fs = require('fs');

fs.readdir('.', function (err, files) {
   console.log(files);
});

console.log("Now I will read the file list...");
