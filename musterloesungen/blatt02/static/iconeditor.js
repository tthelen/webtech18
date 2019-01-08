/**
 * Created by Tobias Thelen 2015-2018
 * Public Domain
 */


/* Global mode variables */
var mode = 'paint';  // other values: 'fill', 'erase'

/*
 * create_table()
 *
 * create the main input table with 16x16 cells
 * register click events for all cells
 */
function create_table() {

    var tablediv=document.getElementById('icon-table'); // place inside #icon-table div
    var table = document.createElement("table");  // make a new table element
    table.className = "icon-table";
    tablediv.appendChild(table);  // place it inside the div
    for (var i = 0; i < 16; i++) {  // 16 rows
        var tr = document.createElement("tr");
        table.appendChild(tr);
        for (var j = 0; j < 16; j++) {  // 16 cells in each row
            var td = document.createElement("td");
            td.className = "icon-pixel";
            td.id="pixel-"+ i + "-" + j;  // systematic ids for the cells pixel-<row>-<cell>
            td.style.backgroundColor = "rgb(255,255,255)"; // no dash - css attribute name becomes camelCase
            td.addEventListener("mouseover", setpixel);
            td.addEventListener("click", setpixel);  // same event listener for all cells
            tr.appendChild(td);
        }
    }
}

/*
 * create_color_picker()
 *
 * creates the color picker table
 */
function create_color_picker() {
    var tablediv = document.getElementById('color-picker');
    var table = document.createElement("table");
    table.className = "color-picker-table";
    tablediv.appendChild(table);
    var tr;
    var count = 0;
    var step = 63;  // red, green, and blue have 256 values.
                    // three for loops step through these values, so for step=63 we have 5*5*5=125 color cells
    for (var r=0; r < 256; r += step) {
        for (var g=0; g < 256; g += step) {
            for (var b = 0; b < 256; b += step) {
                if (count++ % 24 === 0) {  // new row after 24 color cells
                    tr = document.createElement("tr");
                    table.appendChild(tr);
                }
                var td = document.createElement("td");
                td.className = "picker-pixel";
                td.style.backgroundColor = "rgb("+r+","+g+","+b+")";
                td.addEventListener("click", choosecolor);  // the callback function will look a the background color
                tr.appendChild(td);
            }
        }
    }
}

/*
 * choosecolor(event)
 *
 * Click event callback for color chooser. Set current color to clicked element's background color.
 */
function choosecolor(event) {
    var currentColor=document.getElementById("current-color");
    currentColor.style.backgroundColor = this.style.backgroundColor;
}

/* click callback for fill brush tool */
function choose_mode_fill(event) {
    mode = 'fill';
    document.getElementById('icon-table').classList.remove('mode-paint');
    document.getElementById('icon-table').classList.remove('mode-erase');
    document.getElementById('icon-table').classList.add('mode-fill');
    mode_indicator();
}

/* click callback for erase tool */
function choose_mode_paint(event) {
    mode = 'paint';
    document.getElementById('icon-table').classList.remove('mode-fill');
    document.getElementById('icon-table').classList.remove('mode-erase');
    document.getElementById('icon-table').classList.add('mode-paint');
    mode_indicator();
}

/* click callback for erase tool */
function choose_mode_erase(event) {
    mode = 'erase';
    document.getElementById('icon-table').classList.remove('mode-fill');
    document.getElementById('icon-table').classList.remove('mode-paint');
    document.getElementById('icon-table').classList.add('mode-erase');
    mode_indicator();
}

function mode_indicator() {
    var e;

    // remove all active mode css
    document.getElementById('icon-table').classList.remove('mode-fill');
    document.getElementById('icon-table').classList.remove('mode-paint');
    document.getElementById('icon-table').classList.remove('mode-erase');
    e = document.getElementsByClassName('icon-mode-fill');
    for (var i=0; i<e.length; i++) { e[i].classList.remove('activemode'); }
    e = document.getElementsByClassName('icon-mode-paint');
    for (var i=0; i<e.length; i++) { e[i].classList.remove('activemode'); }
    e = document.getElementsByClassName('icon-mode-erase');
    for (var i=0; i<e.length; i++) { e[i].classList.remove('activemode'); }

    // set active mode css
    e = document.getElementsByClassName('icon-mode-'+mode);
    for (var i=0; i<e.length; i++) { e[i].classList.add('activemode'); }
    document.getElementById('icon-table').classList.add('mode-'+mode);

    set_mode_cookie();
}

function register_mode_icons() {
    mode_from_cookie();
    var paint = document.getElementsByClassName('icon-mode-paint');
    for (var i = 0; i < paint.length; i++) {
        paint[i].addEventListener('click', choose_mode_paint);
    }
    var fill = document.getElementsByClassName('icon-mode-fill');
    for (var i = 0; i < fill.length; i++) {
        fill[i].addEventListener('click', choose_mode_fill);
    }
    var erase = document.getElementsByClassName('icon-mode-erase');
    for (var i = 0; i < erase.length; i++) {
        erase[i].addEventListener('click', choose_mode_erase);
    }
    mode_indicator();
}

/*
 * mode_from_cookies()
 *
 * Parse document.cookie and determine if the iconeditor_mode cookie is set.
 * If yes, set global mode accoardingly.
 */
function mode_from_cookie() {
    var cookies = document.cookie.split(";");
    for (var i=0; i<cookies.length; i++) {
        if (cookies[i].trim().indexOf("iconeditor_mode=")==0) {
            mode = cookies[i].split("=")[1];
        }
    }
}

/*
 * set_mode_cookie()
 *
 * Sets a cookie indicating current mode.
 */
function set_mode_cookie() {
    document.cookie = "iconeditor_mode="+mode;
}

/*
 * setpixel(event)
 *
 * Click event callback for main cell table. Set background color to current color.
 */
function setpixel(event) {
    if (event.target.id.match(/pixel-([0-9]+)-([0-9]+)/i)) {
        // only draw if we are on the draw table
        // and mouseover and left mouse button is pressed or click
        if ((event.type == "mouseover" && event.buttons==1) || (event.type == "click")) {
            if (mode=='fill') {
                if (event.type=="click") return fillpixel(event);  // only fill on click
            } else {
                var currentColor="#ffffff";  // erase color
                if (mode=="paint") {
                    currentColor = document.getElementById("current-color").style.backgroundColor;
                }
                event.target.style.backgroundColor = currentColor;
                preview();
            }
        }
    };
}

/* flood fill from clicked cell

   non-recursive implementation with to queues:
   1. tovisit: all pixels that we have to check
   2. visited: all pixels that we already checked

   the algorithm starts at the clicked pixel and add it to tovisit

   while tovisit is not empty:

       remove first element from tovisit and add it to visited

       if it has the same color than the clicked pixel
             and is not in visited or tovisit:
          fill it in the desired color
          add all neighbors to tovisit

 */
function fillpixel(event) {

    var m = event.target.id.match(/pixel-([0-9]+)-([0-9]+)/i); // matchgroups m[1] and m[2] contain coordinates
    if (m) {  // if we clicked a pixel

        // val is a number 0 <= val <= 255, return an object with properties x and y for coordinates
        function to_coords(val) {
            return {'x': val % 16,
                    'y': Math.floor(val/16) };
        }

        // take coordinates and return a number 0 <= val <= 255 to represent coordinates as an integer
        function from_coords(x,y) {
            return x + y*16;
        }

        // return color at given pixel
        function color_at(x,y) {
            console.log("x="+x+", y="+y+", id=pixel-"+x+"-"+y);
            return document.getElementById("pixel-"+x+"-"+y).style.backgroundColor;
        }

        var visited=[];  // list of pixels we already finished looking at
        var tovisit=[];  // list of pixel that we have to look at yet
        var current_color = document.getElementById("current-color").style.backgroundColor;// current color element contains color
        var x = parseInt(m[1]); // must be explicitly converted, otherwise x+w in for loop would be concatenated string
        var y = parseInt(m[2]);
        var color = color_at(x,y);  // the color the pixel to be filled had before - we look for connected cells with this color

        tovisit.push(from_coords(x,y));

        while (tovisit.length) {  // while there are still pixels to look at
            var cur = tovisit.shift();  // pick the first pixel
            visited.push(cur);  // add it to the visited list (never visit again)
            var curx = to_coords(cur).x;
            var cury = to_coords(cur).y;
            if (color_at(curx, cury) == color) {
                // if this pixel has the same color as the first pixel clicked:
                // 1. we fill ist
                // 2. we add its neighbors to the tovisit list
                document.getElementById("pixel-" + curx + "-" + cury).style.backgroundColor = current_color;  // fill it
                // each cell has 4 neighbors: left, right, up, down
                var new_coords = [];
                if (curx>0) new_coords.push(from_coords(curx-1,cury));
                if (curx<15) new_coords.push(from_coords(curx+1, cury));
                if (cury<15) new_coords.push(from_coords(curx, cury+1));
                if (cury>0) new_coords.push(from_coords(curx, cury-1));

                // we check for each neighbor if it is in bounds and not visited yet -> add to tovisit list.
                for (var i = 0; i < new_coords.length; i++) {
                    var c = to_coords(new_coords[i]);
                    if (visited.indexOf(new_coords[i]) == -1 && tovisit.indexOf(new_coords[i]) == -1) {
                        tovisit.push(new_coords[i]);
                    }
                }
            }
        }
    }
    return preview(); // update preview
}

/*
 * preview()
 *
 * Set canvas pixels to pixels from main input table.
 */
function preview() {
    var canvas = document.getElementById('preview-canvas');
    var ctx = canvas.getContext("2d");  // we want a 2d canvas to draw on
    for (var i=0; i<16; i++) {  // 16 rows
        for (var j=0; j<16; j++) {  // 16 cells
            // fetch color from pixel-<row>-<cell> input cell
            ctx.fillStyle = document.getElementById("pixel-"+i+"-"+j).style.backgroundColor;
            ctx.fillRect(j,i,1,1);  // draw a 1x1 pixel rectangle (i.e. a pixel)
        }
    }
    // generate a data: url representing the image
    document.getElementById("save-icon").value = canvas.toDataURL();
}


/* load an icon from server generated icon list to preview canvas and pixel editor */
function load_icon(event) {

    // we need to do two steps:
    // 1. draw the image object to the canvas
    // 2. loop the canvas pixels and set pixel editor background colors

    var canvas = document.getElementById('preview-canvas');
    var ctx = canvas.getContext("2d");

    ctx.drawImage(event.target, 0, 0); // "event.target" is an Image object that can be drawn to the canvas
    for (var i=0; i<16; i++) { // loop through all the pixels
        for (var j=0; j<16; j++) {
            // getImageData returns a flat list with rgba (a=alpha) values
            // so rgba holds [r,g,b,a]
            var rgba = ctx.getImageData(j, i, 1, 1).data;
            // set backgroundColor property in editor table
            document.getElementById("pixel-"+i+"-"+j).style.backgroundColor = "rgb("+rgba[0]+","+rgba[1]+","+rgba[2]+")";
        }
    }
    document.getElementById("save-title").value = event.target.title;
}

/* add a click callback to every icon in server generated list of saved icons */
function register_iconlist_callback() {
    var icons = document.querySelectorAll(".icon-list-item img");
    for (var i=0; i<icons.length; i++) {
        icons[i].addEventListener("click", load_icon);
    }
}

// at start
window.addEventListener("DOMContentLoaded", function () {
    validate_init();  // init the validation library
    create_table();   // create main table
    create_color_picker();  // create color picker
    register_mode_icons(); // make mode indicator icons clickable
    register_iconlist_callback(); // make icons from server clickable
    preview();        // create first preview image
});

