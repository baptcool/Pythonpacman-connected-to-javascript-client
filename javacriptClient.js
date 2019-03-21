#!/usr/bin/env node
var WebSocketClient = require('websocket').client;
 
var client = new WebSocketClient();
 
client.on('connectFailed', function(error) {
    console.log('Connect Error: ' + error.toString());
});
 
client.on('connect', function(connection) {
    console.log('WebSocket Client Connected');



    connection.on('error', function(error) {
        console.log("Connection Error: " + error.toString());
    });
    connection.on('close', function() {
        console.log('echo-protocol Connection Closed');
    });
    connection.on('message', function(message) {
        if (message.type === 'utf8') {
            console.log("Received: '" + message.utf8Data + "'");
        }
    });
    

    function sleep(milliseconds) {
        var start = new Date().getTime();
        for (var i = 0; i < 1e7; i++) {
          if ((new Date().getTime() - start) > milliseconds){
            break;
          }
        }
      }

    function sendNumber() {
	console.log('sendNumber - begining');
        if (connection.connected) {

            // code send string to the python server
            nb = 0
            while(true){
                switch(nb){
                    case 0:
                        connection.sendUTF("U");
                        break
                    case 1:
                        connection.sendUTF("R");
                        break
                    case 2:
                        connection.sendUTF("R'");
                        break
                }
                
                sleep(5000);    
                nb++;
            }
            // code 
            
            
            
        }
	console.log("sendNumber - end ")
    }
    sendNumber();

	
    console.log("client on connect - end")
});
 
client.connect('ws://localhost:8765/');

