$( document ).ready(function() {
    $("#join-room").show();
    $("#setup").hide();
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

function timer(message, status, fadeIn) {
    if (count <= 0) {
        $("#" + fadeIn).fadeIn();
        $("#status-text").html(status);

        $("#ready-button").fadeIn()
        $("#ready-button").html("Ready!")

        clearInterval(interval);
        return;
    }
    $("#status-text").html(message + " " + count);
    count = count - 1;
}

socket.on("start_round", function (data) {
    $("#ready-button").fadeOut()
    count = data["time"];
    interval = setInterval(timer, 1000, data["message"], data["state"]);
});

socket.on("start_setup", function (data) {
    $("#ready-button").fadeOut();
    $("#join-room").fadeOut();

    $("#role-name").html("You are a " + data['role'] + "!");
    $("#role-description").html(data['role_description']);

    count = data["time"];
    interval = setInterval(timer, 1000, data["message"], data["state"], "setup");
});

