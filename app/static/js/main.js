var socket = io.connect('https://' + document.domain + ':' + location.port);

socket.on('connect', function() {
    socket.emit('joined', {});
});

socket.on('notify_join', function(data) {
    document.getElementById('players').innerHTML += '<il>' + test + '</il>';
})

function send(){
    socket.emit('status', {message : $('form textarea').val()});
}