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
        var newRow = list.insertRow();
        var newCell  = newRow.insertCell(0);
        var newText  = document.createTextNode(element);
        newCell.appendChild(newText);
    });
})








count = 0;

function ready() {
    var button = document.getElementById('ready-button');
    if (button.innerHTML == 'Ready!') {
        button.innerHTML = 'Unready!'
    } else {
        button.innerHTML = 'Ready!'
    }

    socket.emit('ready', {});
}

var interval

function timer(message) {
    count = count - 1;
    if (count <= 0) {
        document.getElementById("timer").innerHTML = 'done';
        clearInterval(interval);
        return;
    }

    document.getElementById("timer").innerHTML = message + ' ' + count;
}

socket.on('start_timer', function (data) {
    count = data['time'];
    interval = setInterval(timer, 1000, data['message']);
});

