var states = ["lobby", "setup", "results", "round", "win"]
var interval
var count = 0
var socket = io.connect();

/**
 * When the document has fully loaded.
 */
$(document).ready(function () {
    // Fades in the lobby and hides all other states.
    $("#game").fadeIn();
    $("#ready-status").hide();
    states.forEach(element => {
        $("#" + element).hide();
    })
    $("#lobby").fadeIn();
});

/**
 * When the client recognizes it has connected to socketio.
 */
socket.on("connect", function () {
    // Joins the player to a room on connect.
    socket.emit("join", {});
});

/**
 * When the client recognizes it has disconnected from socketio.
 */
socket.on("disconnect", function () {
    // Leaves a room when the player disconnects.
    socket.emit("leave", {});
});

/**
 * When the player's list has been updated by the server. 
 */
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

/**
 * When the server indicates a player has readied up.
 */
socket.on("update_ready", function (data) {
    // Fades in and updates the ready-status text to show 
    // how many players are ready.
    $("#ready-status").fadeIn();
    $("#ready-status").html(data["players"])
});

socket.on("start_lobby", function (data) {
    fadeOutState();
    count = data["time"];
    interval = setInterval(timer, 100, data["message"], data["state_html"], data["state_name"], data["alive"]);
});

socket.on("start_setup", function (data) {
    $("#ready-button").fadeOut();

    $("#role-name").html("You are " + data['name'] + "! A " + data['age'] + " year old " + data['role'] + "!");
    $("#role-description").html(data['role_description']);

    fadeOutState();
    count = data["time"];
    interval = setInterval(timer, 100, data["message"], data["state_html"], data["state_name"], data["alive"]);
});

socket.on("start_round", function (data) {
    // Add round radio boxes.
    $("#round-radio").fadeIn();

    if (data["alive"]) {
        var list = "";
        list += '<label class="radio-container">' + data["players_names"][0] + '<input type="radio" name="radio" checked="checked" value="' + data["players_ids"][0] + '"><span class="checkmark"></span></label>';
        data["players_names"].forEach((element, index) => {
            if (index < 1) return;
            list += '<label class="radio-container">' + element + '<input type="radio" name="radio" value="' + data["players_ids"][index] + '"><span class="checkmark"></span></label>';
        });
        $("#round-radio").html(list);
        $("#round-text").html(data["role_action"]);
    } else {
        $("#round-text").html("Sorry, ghost unfortunately can't affect the living. :(");
        $("#round-radio").html("");
    }

    // Start the timer.
    fadeOutState();
    count = data["time"];
    interval = setInterval(timer, 100, data["message"], data["state_html"], data["state_name"], data["alive"]);
});

socket.on("start_results", function (data) {
    // Empties the result lists.
    $("#results-text-general").html();
    $("#results-text-private").html();
    
    // Display the result bullet points if any results exist.
    if (data['results_general'] != null && data['results_general'].length > 0) {
        $("#results-header-general").show();
        $("#results-text-general").show();
        data['results_general'].forEach(element => {
            $("#results-text-general").append("<li>" + element + "</li>")
        })
    } else {
        $("#results-header-general").hide();
        $("#results-text-general").hide();
    }

    if (data['results_private'] != null && data['results_private'].length > 0) {
        $("#results-header-private").show();
        $("#results-text-private").show();
        data['results_private'].forEach(element => {
            $("#results-text-private").append("<li>" + element + "</li>")
        })
    } else {
        $("#results-header-private").hide();
        $("#results-text-private").hide();
    }

    // Start the timer to change states.
    fadeOutState();
    count = data["time"];
    interval = setInterval(timer, 100, data["message"], data["state_html"], data["state_name"], data["alive"]);
});

socket.on("start_win", function (data) {
    // Update the win message.
    $("#win-description").html(data["win_message"]);

    // Show the player list with roles and survival status.
    $("#win-list").html();
    data['players'].forEach(element => {
        $("#win-list").append("<li>" + element + "</li>")
    })

    // Start the timer to change states.
    fadeOutState();
    count = data["time"];
    interval = setInterval(timer, 100, data["message"], data["state_html"], data["state_name"], true);
});

function fadeOutState() {
    $("#ready-button").fadeOut();
    $("#ready-status").fadeOut();
    states.forEach(element => {
        $("#" + element).fadeOut();
    });
}

function setState(state, stateStatus, alive) {
    $("#status-text").html(stateStatus);
    if (alive) {
        $("#ready-button").html("I am ready!");
        $("#ready-button").fadeIn();
    }
    states.forEach(element => {
        if (element === state) {
            $("#" + state).fadeIn()
        }
    });
}


function ready() {
    if ($("#ready-button").html() == "I am ready!") {
        $("#ready-button").html("I am not ready!");
        $("#round-radio").fadeOut();
    } else {
        $("#ready-button").html("I am ready!")
        $("#round-radio").fadeIn();
    }

    socket.emit("ready", { "chosen_player": $('input[name="radio"]:checked').val() });
}

function timer(message, state, stateName, alive) {
    if (count <= 0) {
        setState(state, stateName, alive)
        clearInterval(interval);
        return;
    }
    $("#status-text").html(message + " " + count);
    count = (count - 0.1).toFixed(1);
}

