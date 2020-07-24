var socket = io.connect();

socket.on('connect', function () {
    socket.emit('join', {});
});

socket.on('disconnect', function () {
    socket.emit('leave', {});
});

socket.on('update_players', function (data) {
    var list = document.getElementById('players');
    list.innerHTML = '';

    
    data['players'].forEach(element => {
        var entry = document.createElement('li');
        entry.appendChild(document.createTextNode(element));
        list.appendChild(entry);
    });

})








count = 0;

function start() {
    socket.emit('start', {});
}

function timer() {
    count = count - 1;
    if (count <= 0) {
        document.getElementById("timer").innerHTML = 'done';
        clearInterval(timer);
        return;
    }

    document.getElementById("timer").innerHTML = count;
}

socket.on('start_timer', function (data) {
    count = 10;
    clearInterval(timer);
    setInterval(timer, data['time']);
});

