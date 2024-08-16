let board = [];
let player = 'X';
let playerName = '';

function startGame() {
    playerName = document.getElementById('playerName').value;
    fetch('/start_game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: playerName })
    })
    .then(response => response.json())
    .then(data => {
        board = data.board;
        document.getElementById('message').innerText = data.message;
        renderBoard();
    });
}

function renderBoard() {
    const boardDiv = document.getElementById('board');
    boardDiv.innerHTML = '';
    board.forEach((cell, index) => {
        const cellDiv = document.createElement('div');
        cellDiv.classList.add('cell');
        cellDiv.innerText = cell ? cell : '';
        if (!cell && !document.getElementById('message').innerText.includes("wins") && 
            !document.getElementById('message').innerText.includes("draw")) {
            cellDiv.onclick = () => makeMove(index);
        }
        boardDiv.appendChild(cellDiv);
    });
}

function makeMove(position) {
    fetch('/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ board: board, position: position, player: player, name: playerName })
    })
    .then(response => response.json())
    .then(data => {
        board = data.board;
        document.getElementById('message').innerText = data.message;
        if (data.winner) {
            updateLeaderboard();
        }
        renderBoard(); // Always render the board to reflect the latest state
    });
}

function updateLeaderboard() {
    fetch('/leaderboard')
    .then(response => response.json())
    .then(data => {
        const leaderboardList = document.getElementById('leaderboardList');
        leaderboardList.innerHTML = '';
        data.leaderboard.forEach(user => {
            const li = document.createElement('li');
            li.innerText = `${user[0]}: ${user[1]} wins`;
            leaderboardList.appendChild(li);
        });
    });
}
