var states = ["lobby", "setup", "results", "round", "end"]
var interval
var count = 0
var socket = io.connect();

$(document).ready(function () {
    $("#ready-status").hide();
    states.forEach(element => {
        $("#" + element).hide();
    })
    $("#lobby").show();
});

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
        var newCell = newRow.insertCell(0);
        var newText = document.createTextNode(element);
        newCell.appendChild(newText);
    });
})

socket.on("update_done", function (data) {
    $("#ready-status").fadeIn();
    $("#ready-status").html(data["players"])
})

socket.on("start_round", function (data) {
    // Found out last state.
    $("#ready-button").fadeOut();
    $("#ready-status").fadeOut();
    states.forEach(element => {
        $("#" + element).fadeOut();
    })

    // Add round radio boxes.
    var list = ''
    data["players"].forEach(element => {
        list += '<label class="radio-container">' + element +'<input type="radio" checked="checked" name="radio"><span class="checkmark"></span></label>';
    });
    $("#" + data["state_html"]).html(list);

    // Start the timer.
    count = data["time"];
    interval = setInterval(timer, 100, data["message"], data["state_html"], data["state_name"]);
});

socket.on("start_setup", function (data) {
    $("#ready-button").fadeOut();
    $("#lobby").fadeOut();

    $("#role-name").html("You are a " + data['role'] + "!");
    $("#role-description").html(data['role_description']);

    count = data["time"];
    interval = setInterval(timer, 100, data["message"], data["state_html"], data["state_name"]);
});

socket.on("results", function (data) {
    // Found out last state.
    $("#ready-button").fadeOut();
    $("#ready-status").fadeOut();
    states.forEach(element => {
        $("#" + element).fadeOut();
    })

    $("round-results")

    // Start the timer.
    count = data["time"];
    interval = setInterval(timer, 100, data["message"], data["state_html"], data["state_name"]);
});

function setState(state, stateStatus) {
    $("#status-text").html(stateStatus);
    $("#ready-button").html("I am ready!");
    $("#ready-button").fadeIn();
    states.forEach(element => {
        if (element === state) {
            $("#" + state).fadeIn()
        }
    });
}


function ready() {
    if ($("#ready-button").html() == "I am ready!") {
        $("#ready-button").html("I am not ready!")
    } else {
        $("#ready-button").html("I am ready!")
    }

    socket.emit("ready", {});
}

function timer(message, state, stateName) {
    if (count <= 0) {
        setState(state, stateName)
        clearInterval(interval);
        return;
    }
    $("#status-text").html(message + " " + count);
    count = (count - 0.1).toFixed(1);
}

