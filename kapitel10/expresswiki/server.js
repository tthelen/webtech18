
// builtin libraries
const fs = require('fs');  // file system access (node.js builtin)

// http framework
const express = require('express');  // express js framework (installed via npm)

const cookieParser = require('cookie-parser'); // middleware for parsing cookies
const bodyParser = require('body-parser');  // middleware for parsing request bodys
const accesslog = require('access-log'); // logging middleware

// authentication middleware (passport)
const expressSession = require('express-session');  // express session support
const passport = require('passport'); // authentication middleware
const Strategy = require('passport-local').Strategy;  // local authentication strategy for passport
const ensureLoggedIn = require('connect-ensure-login').ensureLoggedIn;  // redirect to login for actions that need auth

// templating engine
const mustacheExpress = require('mustache-express');  // mustache as template engine for express (installed via npm)

function markup(text) {

    // substitute < by &lt;
    text = text.replace(/</g, "&lt;");
    // substitute links: [[pagename]] -> <a href="/show/pagename">pagename</a>
    text = text.replace(/\[\[([a-zA-Z0-9]+)\]\]/g, "<a href='/show/$1'>$1</a>");
    // substitute headlines: !bang -> <h1>bang</h1>
    text = text.replace(/^!(.*)$/gm, "<h1>$1</h1>");
    // replace two ends of line with <p>
    text = text.replace(/\r?\n\r?\n/gm, "<p>");
    // replace one end of line with <br>
    text = text.replace(/\r?\n\r?\n/gm, "<br>");

    return text
}

function pagelist() {
    // use synchronous I/O to get page list - return list of strings
    return fs.readdirSync('./data');
}

// show wiki page
function show(req, res, next) {
      var page = req.params['page'] || 'main';
      var pages = pagelist();
      var username = req.user;
      fs.readFile('data/'+page, 'utf8', function (err, data) {
          if (err) return next(err);  // pass to next handler which is the error handler
          res.render('show.mustache', { 'text': markup(data), 'pagename': page, 'pages': pages, 'username': username});
      });
}

// show login page
function loginview(req, res, next) {
      var page = req.params['page'] || 'main';
      var pages = pagelist();
      res.render('login.mustache', { 'pagename': page, 'pages': pages });
}

// show wiki page for editing
function edit(req, res, next) {
    var page = req.params['page'] || 'main';
    var pages = pagelist();
    if (req.session.wikitext) {  // perhaps we have a saved text in the session to survive login
          res.render('edit.mustache', { 'text': req.session.wikitext, 'pagename': page, 'pages': pages });
          req.session.wikitext = undefined;
    } else {
        fs.readFile('data/' + page, 'utf8', function (err, data) {
            if (err) return next(err);
            res.render('edit.mustache', {'text': data, 'pagename': page, 'pages': pages});
        });
    }
}

// receive post request, save data and redirect to show
function save(req, res, next) {
      var page = req.params['page'] || 'main';
      var data = req.body.wikitext;
      req.session.wikitext = undefined;
      fs.writeFile('data/'+page, data, function (err, data) {
          if (err) return next(err);
          res.redirect('/show/'+page);
      });
}

function savewikitext(req, res, next) {
      if (req.session) {
          req.session.wikitext = req.body.wikitext;
      } else {
          console.log("Wäh! Keine Session")
      }
      next();
}

// setup und start express engine
var app = express();

app.engine('mustache', mustacheExpress());
app.set('views', './templates');
app.set('view engine', 'mustache');

// bodyParser middleware parses request bodies
app.use(bodyParser.urlencoded({ extended: true })); // enables parsing application/x-www-form-urlencoded

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

// serve static files from ./static as /static
app.use('/static', express.static('static'));


// configure authorization
app.use(require('express-session')({ secret: '0815secret', resave: false, saveUninitialized: false }));


passport.use(new Strategy(
  function(username, password, cb) {
    if (username=='admin' && password=='admin') {
        return cb(null, 'admin');
    } else {
        return cb(null, false);
    }
  }));


passport.serializeUser(function(user, cb) {
  cb(null, user);
});

passport.deserializeUser(function(id, cb) {
    cb(null, id);
});

// Initialize Passport and restore authentication state, if any, from the
// session.
app.use(passport.initialize());
app.use(passport.session());

// configure routes
app.get('/', show);
app.get('/show', show);
app.get('/show/:page(\\w+)', show);
app.get('/edit', ensureLoggedIn('/login'), edit);
app.get('/edit/:page(\\w+)', ensureLoggedIn('/login'), edit);
app.post('/save/:page(\\w+)', savewikitext, ensureLoggedIn('/login'), save);
app.get('/save/:page(\\w+)', function (req, res) { res.redirect('/edit/'+req.params['page']); });

// logging in an out
app.get('/login', loginview);
app.post('/login', passport.authenticate('local', { successReturnToOrRedirect: '/', failureRedirect: '/login' }));
app.get('/logout',
  function(req, res){
    req.logout();
    res.redirect('/');
});

// run the wiki app
app.listen(8080, function () { console.log('Wiki app listening on http://localhost:8080/'); });