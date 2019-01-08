/*
    main.js
     Demonstrating drawbacks of classical javascript loading with script tags

    Web-Technologien
    Tobias Thelen, 2017
    Public Domain
 */

document.addEventListener("DOMContentLoaded", function () {
    var my_state = 'main';

    util_func();  // call a function from util.js

    alert("My state is "+my_state);
});
