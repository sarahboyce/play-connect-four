let $script = $('#gameDetailScript');
let checkTurn = $script.data("check-turn");
let checkTurnURL = $script.data("check-turn-url");

if (checkTurn) {
    checkUsersTurn();
}

$('th.play-row').on('click', function(){
    let url = $(this).data("url");
    window.location.href = url;
})

function checkUsersTurn() {
    $.ajax({
        url: checkTurnURL,
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            console.log("checking")
            if (response.is_users_turn) {
                window.location.reload();
            } else {
                setTimeout(checkUsersTurn, 5000);
            }
        }
    });
}
