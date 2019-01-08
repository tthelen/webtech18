import $ from 'jquery';
import io from 'socket.io-client';  // the socket.io client
import {sprintf} from 'sprintf-js';  // library with sprintf-string formatting function
import './style.css';

$(document).ready(function(){
	// connect to webSocket
	var socket = io.connect();

	// incoming message
    // register event handler for 'chat' events
	socket.on('chat', function (data) {
		var now = new Date(data.time);
		// construct html string for chat message and add to #content list
		$('#content').append(
            sprintf("<li>[%02d:%02d:%02d] <b>%s: </b> <span>%s</span></li>",
                now.getHours(), now.getMinutes(), now.getSeconds(),
                data.name  || '', data.text));
		// scroll down (broken)
		$('body').scrollTop($('body')[0].scrollHeight);
	});

	// send a message (submit handler for html form)
	$('#sendform').submit(function (event) {
	    // send (emit) a 'chat' event to server
		socket.emit('chat', { name: $('#name').val(), text: $('#text').val() });
		$('#text').val('');
	    event.preventDefault();
    });

	// refresh number of chatters every second via ajax
    // this could of course be done via websockets / counting connects and disconnects as well,
    // but this is to demonstrate how to use websockets and ajax together
	window.setInterval(function () { $('#numclients').load('/numclients'); }, 5000);

});