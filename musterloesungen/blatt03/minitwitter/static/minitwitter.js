// prevent namespace pollution -> encapsulate code
(function () {

    // read csrf token form cookie, for regex see
    // https://stackoverflow.com/questions/5639346/what-is-the-shortest-function-for-reading-a-cookie-by-name-in-javascript
    function csrf_token() {
        return document.cookie.match('(^|;)\\s*csrf_token\\s*=\\s*([^;]+)').pop()
    }

    // make ajax call and replace content of an element with response
    // selector: css selector (for querySeletor)
    // url
    // method: 'GET' or 'POST' (post will always use application/x-www-form-urlencoded as content type)
    // body
    function replac(selector, method, url, body) {
        xhr = new XMLHttpRequest();
        xhr.open(method, url);
        xhr.onload = function() {
            if (xhr.status === 200) {
                document.querySelector(selector).innerHTML = xhr.responseText;
            } else {
                console.log('Request failed.  Returned status of ' + xhr.status);
            }
        };
        if (method=='POST') {
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            body = "csrf_token="+encodeURIComponent(csrf_token())+"&"+body; // add csrf token to post request
        }
        xhr.send(body);
    }

    document.addEventListener("DOMContentLoaded", function(event) {

        // which page are we on?
        if (window.location.href.match(/useradmin/)) {
            // user management
            document.addEventListener("click", function (event) {
                if (event.target.dataset.delusername) {
                    let u = event.target.dataset.delusername;
                    xhr = new XMLHttpRequest();
                    xhr.open('POST', '/useradmin/delete/' + encodeURIComponent(u)+'?ajax=1');
                    xhr.onload = function () {
                        if (xhr.status === 200) {
                            let e = document.getElementById('row-del-' + u);
                            e.parentNode.removeChild(e);
                        }
                    };
                    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                    xhr.send("csrf_token="+encodeURIComponent(csrf_token()));  // send csrf_token parameter as body
                }
            });
        } else if (window.location.href.match(/login/)) {
            // login page
        } else {
            // tweeting page

            // autorefresh after 5 seconds
            window.setInterval(function () { replac('#content-row', 'GET', '/?ajax=1'); }, 5000);

            document.getElementById('theform').addEventListener('submit', function (event) {
                event.preventDefault();
                replac('#content-row', 'POST', '/?ajax=1', 'status='+encodeURIComponent(document.getElementById('status').value));
            });
        }
    });
})();