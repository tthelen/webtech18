/*
    util2.js
     Demonstrating drawbacks of classical javascript loading with script tags

    Web-Technologien
    Tobias Thelen, 2017
    Public Domain
 */

var util2 = (function () {
    var my_state = 'util2';

    return {
        funky: function () {
            document.body.style.backgroundColor = 'red';
        }
    }
}());
