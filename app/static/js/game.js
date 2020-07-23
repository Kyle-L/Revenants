var socket = io.connect();

socket.on('connect', function () {
    socket.emit('join', {});
});

socket.on('notify_join', function (data) {
    document.getElementById('players').innerHTML += data['data'];
})








count = 0;

function start() {
    socket.emit('start', {});
}

function timer() {
    count = count - 1;
    if (count <= 0) {
        document.getElementById("timer").innerHTML = 'done';
        clearInterval(counter);
        return;
    }

    document.getElementById("timer").innerHTML = count;
}

socket.on('start_timer', function (data) {
    count = 10;
    setInterval(timer, data['time']);
});

