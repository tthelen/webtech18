/*
    main.js
     require.js demonstration

    Web-Technologien
    Tobias Thelen, 2017
    Public Domain
 */

require(["util"], function (util) {
    var my_state = 'main';
    util.util_func();  // call a function from util.js
    alert("My state is " + my_state);
});

