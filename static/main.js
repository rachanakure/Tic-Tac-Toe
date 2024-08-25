let board = [];
let player = 'X';
let playerName = '';
let gameEnd = false;

let winsCount = 0, lossesCount = 0, drawsCount = 0;

let wins = $("#wins");
let losses = $("#losses");
let draws = $("#draws");

async function startGame() {
    wins.text(winsCount);
    losses.text(lossesCount);
    draws.text(drawsCount);
    
    console.log(winsCount, lossesCount, drawsCount);

    gameEnd = false;
    playerName = $('#playerName').val();

    if (playerName === '') {
        $('.error').text('Enter a Name').css('padding', '5px');
        return;
    }
    
    $('.input_container').hide();
    
    try {
        await getLeaderBoard(); 
        const response = await axios.post('/start_game', { name: playerName });
        board = response.data.board;
        console.log(board);
        $('#message').text(response.data.message);
        renderBoard();
    } catch (error) {
        console.error('Error starting game:', error);
        $('#message').text('Error starting game. Please try again.'); // Feedback for the user
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

        let result = response.data.winner;
        console.log("---> ", result);
        
        if (result) {
            if (result === 'draw') {
                drawsCount++;
                draws.text(drawsCount);
            } else if (result === 'O') {
                lossesCount++;
                losses.text(lossesCount);
            } else if (result) {
                winsCount++;
                wins.text(winsCount);
            }

            gameEnd = true;
            await updateLeaderboard(); 
            setTimeout(startGame, 2000);
        }

        renderBoard();
    } catch (error) {
        console.error('Error making move:', error);
        $('#message').text('Error making move. Please try again.'); // Feedback for the user
    }
}

async function updateLeaderboard() {
    try {
        const response = await axios.post('/updateLeaderboard', {
            userName: playerName,
            wins: winsCount,
            losses: lossesCount,
            draws: drawsCount
        });
        if (JSON.parse(response.data.status)) {
            await getLeaderBoard();
        }
    } catch (error) {
        console.error('Error updating leaderboard:', error);
    }
}

const getLeaderBoard = async function() {
    try {
        const response = await axios.get('/getLeaderBoard');
        const data = response.data;
        const leaderboardList = $('#leaderboardList');
        leaderboardList.empty();
        if (data.leaderboard.length !== 0) {
            data.leaderboard.forEach(user => {
                leaderboardList.append(`<li>${user[1]}: ${user[2]} wins, ${user[3]} losses, ${user[4]} draws</li>`);
            });
        }
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
        $('#message').text('Error loading leaderboard. Please try again.'); 
    }
};
