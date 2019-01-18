
// builtin libraries
const fs = require('fs');  // file system access (node.js builtin)
const path = require('path');  // path handling functions (node.js builtin)

// http framework
const express = require('express');  // express js framework (installed via npm)
const bodyParser = require('body-parser');  // middleware for parsing request bodys
const accesslog = require('access-log'); // logging middleware

// additional libraries
const uuidv4 = require('uuid/v4');  // for generating IDs via uuidv4()

// global constants
const datadir = './data';  // the directory that holds all the files
const url_base = 'http://localhost:8080'; // for constructing absolute urls

// -------------------------------------------
// helper functions
//

function construct_path(filename) {
    // Prevent path traversal attacks: Is resulting path below desired datadir in file system?
    var fn = path.normalize(path.resolve(datadir+'/'+filename));
    if (fn.startsWith(path.resolve(datadir))) {
        return fn
    } else {
        return false
    }
}

function absurl(path) {
    // Makes an absolute url from a path that may or may not start with /.
    if (!path.startsWith('/')) {
        path = '/' + path;
    }
    return url_base + path;
}

// -------------------------------------------
// Rest API functions
//

// READ files (collection)
function list_files (req, res, next) {
    // use synchronous I/O to get file list - return list of strings
    res.json({files:fs.readdirSync('./data').map(obj => {return absurl("files/"+obj)})});
}

// READ file (single)
function get_file(req, res, next) {
    // fetch file content and send json representation
    var filename = construct_path(req.params['id']);  // construct and check absolute filename
    if (filename && fs.existsSync(filename)) {  // does the file exist (synchronous I/O, could also be async)
        fs.readFile(filename, 'utf8', function (err, data) {
            if (err) return next(err);  // I/O error -> default handler
            res.json({  // construct and send json representation of file
                id: req.params['id'],
                url: absurl("files/" + req.params['id']),
                content: data
            });
        });
    } else {
        res.sendStatus(404);  // file not found or invalid filename
    }
}

// UPDATE or CREATE file
function put_file(req, res, next) {
    // write body content to file
    var filename = construct_path(req.params['id'] || undefined);
    if (req.body.content) {  // application/x-www-form-urlencoded
        fs.writeFile(filename, req.body.content, function (err, data) {
            if (err) return next(err);
            res.sendStatus(204);
        });
    } else {
        res.sendStatus(400);
    }
}

// CREATE FILE
// ... add ...

// DELETE FILE
// ... add ...

// -------------------------------------------
// express setup and route configuration
//

// setup und start express engine
var app = express();

// bodyParser middleware parses request bodies
app.use(bodyParser.urlencoded({extended: true}))  ; // enables body parsing of application/x-www-form-urlencoded

// logging middleware
app.use(function (req,res, next) {
   accesslog(req,res);
   next();
});

// error handling
app.use(function(err, req, res, next) {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

// configure routes

// serve static files from ./static as /static
app.use('/static', express.static('static'));

// rest api entry point: list all available types (only files here)
app.get('/', function (req, res, next) {
    res.json(['http://localhost:8080/files']);
});

// files routes
app.get('/files', list_files);  // GET collection
app.get('/files/:id([0-9A-Za-z-]+)', get_file);  // READ single file content
app.put('/files/:id([0-9A-Za-z-]+)', put_file);  // UPDATE single file content

// run the rest files app
app.listen(8080, function () { console.log('File rest app listening on http://localhost:8080/'); });