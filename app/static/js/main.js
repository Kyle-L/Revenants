var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('status', function(data) {
    document.getElementById('test').innerHTML += "Someone clicked the button, ";
})

function send(){
    socket.emit('status', {message : $('form textarea').val()});
}