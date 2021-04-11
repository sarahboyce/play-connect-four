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
            if (response.is_users_turn || response.is_game_over) {
                window.location.reload();
            } else {
                setTimeout(checkUsersTurn, 5000);
            }
        }
    });
}
