var http = require("http");
var accesslog = require("access-log");

http.createServer(function (req, res) {
  res.writeHeader(200, {"Content-Type": "text/plain"});
  res.write("Hello World\n");
  accesslog(req,res);
  res.end();
}).listen(8080);

console.log("Server running at http://127.0.0.1:8080/");
