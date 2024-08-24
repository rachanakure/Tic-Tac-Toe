let board = [];
let player = 'X';
let playerName = '';
let gameEnd = false;

$(document).ready(function() {
    // Bind the start game button to the startGame function
    $('#startGameButton').on('click', startGame);
});

async function startGame() {
    gameEnd = false;
    playerName = $('#playerName').val();
    
    if (playerName === '') {
        $('.error').text('Enter a Name').css('padding', '5px');
        return;
    }
    
    $('.input_container').hide();

    try {
        // Use Axios to make a POST request to start the game
        const response = await axios.post('/start_game', { name: playerName });
        board = response.data.board;
        console.log(board);
        $('#message').text(response.data.message);
        renderBoard();
    } catch (error) {
        console.error('Error starting game:', error);
    }
}

function renderBoard() {
    $('.cell').each(function(index) {
        $(this).text(board[index]);
        $(this).off('click').on('click', function() {
            makeMove(index);
        });
    });
}

async function makeMove(position) {
    if (gameEnd) {
        return;
    }
    
    console.log(position);

    try {
        const response = await axios.post('/move', {
            board: board,
            position: position,
            player: player,
            name: playerName
        });

        board = response.data.board;
        console.log(response.data);
        $('#message').text(response.data.message);

        if (response.data.winner) {
            gameEnd = true;
            updateLeaderboard();
            setTimeout(() => {
                startGame();

            }, 2000);
        }

        renderBoard();
    } catch (error) {
        console.error('Error making move:', error);
    }
}

async function updateLeaderboard() {
    try {
        const response = await axios.get('/leaderboard');
        const leaderboardList = $('#leaderboardList');
        leaderboardList.empty();
        response.data.leaderboard.forEach(user => {
            leaderboardList.append(`<li>${user[0]}: ${user[1]} wins</li>`);
        });
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
    }
}
