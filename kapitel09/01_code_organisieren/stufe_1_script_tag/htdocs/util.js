/*
    util.js
     Demonstrating drawbacks of classical javascript loading with script tags

    Web-Technologien
    Tobias Thelen, 2017
    Public Domain
 */


var my_state="util";

function util_func() {
    console.log("I'm util_func and working. My state is "+my_state);

    var script = document.createElement("script");
    script.src="util2.js";
    document.head.appendChild(script);
    script.onload = function () { funky(); };
}
