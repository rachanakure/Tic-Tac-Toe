let board = [];
let player = 'X';
let playerName = '';
let gameEnd = false;

let winsCount=0, lossesCount=0, drawsCount=0;

let wins = $("#wins");
let losses = $("#losses");
let draws = $("#draws");


async function startGame() {
    wins.text(winsCount);
    losses.text(lossesCount);
    draws.text(drawsCount);
    
    console.log(winsCount, lossesCount, drawsCount)

    gameEnd = false;
    playerName = $('#playerName').val();
    await getLeaderBoard();
    
    if (playerName === '') {
        $('.error').text('Enter a Name').css('padding', '5px');
        return;
    }
    
    $('.input_container').hide();

    try {
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

        let result = response.data.winner;
        console.log("---> ",result);

        if (result == 'draw'){
            draws.text(drawsCount++);
        }
        else if(result=='O'){
            losses.text(lossesCount++);
        }
        else if(result){
            wins.text(winsCount++);
        }
        
        if(result){
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
        const response = await axios.post('/updateLeaderboard', {
            userName: playerName,
            wins: winsCount,
            losses: lossesCount,
            draws: drawsCount
        });
        const leaderboardList = $('#leaderboardList');
        leaderboardList.empty();
        response.data.leaderboard.forEach(user => {
            leaderboardList.append(`<li>${user[0]}: ${user[1]} wins</li>`);
        });
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
    }
}

const getLeaderBoard = async function(){
    const response = await axios.get('/getLeaderBoard');
    const data = response.data;
    console.log(data);

};
