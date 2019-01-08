/*
    util.js
     Demonstrating drawbacks of classical javascript loading with script tags

    Web-Technologien
    Tobias Thelen, 2017
    Public Domain
 */

define(["util2"], function (util2) {
    var my_state = "util";

    return {
        util_func: function () {
            console.log("I'm util_func and working. My state is " + my_state);
            util2.funky();
        }
    }
});
