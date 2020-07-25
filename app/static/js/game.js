$( document ).ready(function() {
    $("#join-room").show();
    $("#round-1").hide();
});

var socket = io.connect();

socket.on("connect", function () {
    socket.emit("join", {});
});

socket.on("disconnect", function () {
    socket.emit("leave", {});
});

socket.on("update_players", function (data) {
    var list = document.getElementById("players");
    list.innerHTML = "";
    
    data["players"].forEach(element => {
        var newRow = list.insertRow();
        var newCell  = newRow.insertCell(0);
        var newText  = document.createTextNode(element);
        newCell.appendChild(newText);
    });
})








count = 0;

function ready() {
    if ($("#ready-button").html() == "Ready!") {
        $("#ready-button").html("Not ready!")
    } else {
        $("#ready-button").html("Ready!")
    }

    socket.emit("ready", {});
}

var interval

function timer(message) {
    if (count <= 0) {
        $("#join-room").fadeOut();
        $("#round-1").delay(1000).fadeIn();
        clearInterval(interval);
        return;
    }
    $("#status-text").html(message + " " + count);
    count = count - 1;
}

socket.on("start_timer", function (data) {
    count = data["time"];
    interval = setInterval(timer, 1000, data["message"]);
});

