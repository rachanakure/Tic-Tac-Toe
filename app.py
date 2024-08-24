from flask import Flask, request, jsonify, render_template
import sqlite3
import random
import numpy as np

app = Flask(__name__)

# Define board configurations
array = np.array([
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8]
])
Tarray = array.T
diagonals = [np.diag(array), np.diag(np.fliplr(array))]

# Initialize SQLite database
def init_db():
    with sqlite3.connect('tictactoe.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY, 
                        name TEXT, 
                        wins INTEGER, 
                        losses INTEGER, 
                        draws INTEGER)''')
        conn.commit()

init_db()


# Helper function to get or create user
def get_or_create_user(name):
    with sqlite3.connect('tictactoe.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE name=?', (name,))
        user = c.fetchone()
        if not user:
            c.execute('INSERT INTO users (name, wins, losses, draws) VALUES (?, 0, 0, 0)', (name,))
            conn.commit()
            c.execute('SELECT * FROM users WHERE name=?', (name,))
            user = c.fetchone()
    return user



@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.json
    player_name = data.get('name')
    board = [None] * 9
    return jsonify({"board": board, "message": f"Game started for {player_name}!"})



def check_winner(board, player):

    for row in array:
        if board[row[0]] == board[row[1]] == board[row[2]] == player:
            return True
    for col in Tarray:
        if board[col[0]] == board[col[1]] == board[col[2]] == player:
            return True
    for dia in diagonals:
        if board[dia[0]] == board[dia[1]] == board[dia[2]] == player:
            return True
        
    if None not in board:
        return 'draw'
    return False

def get_best_move(board, player):
    opponent = 'O' if player == 'X' else 'X'
    
    #  Check if AI can win in the next move
    for i in range(9):
        if board[i] is None:
            board[i] = player 
            if check_winner(board, player):
                board[i] = None
                return i
            board[i] = None
    
    #  Block opponent's winning move
    for i in range(9):
        if board[i] is None:
            board[i] = opponent
            # if check_winner(board, opponent):
            if check_winner(board, opponent) and (random.choice([True, False])):
                board[i] = None
                return i
        
            board[i] = None
    
    #  Prefer center if available
    if board[4] is None:
        return 4
    
    #  Prefer corners if available
    corners = [0, 2, 6, 8]
    available_corners = [i for i in corners if board[i] is None]
    if available_corners:
        return random.choice(available_corners)
    
    # . Prefer edges if available
    edges = [1, 3, 5, 7]
    available_edges = [i for i in edges if board[i] is None]
    if available_edges:
        return random.choice(available_edges)
    
    #. Random move if no other options
    available_moves = [i for i in range(9) if board[i] is None]
    if available_moves:
        return random.choice(available_moves)
    
    return None

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    board = data['board']
    position = data['position']
    player = data['player']
    user_name = data['name']

    if board[position] is None:
        board[position] = player
        winner = check_winner(board, player)
        print('--------->', winner)
        
        with sqlite3.connect('tictactoe.db') as conn:
            c = conn.cursor()
            if winner:
                if winner == 'draw':
                    c.execute('UPDATE users SET draws = draws + 1 WHERE name = ?', (user_name,))
                    message = "It's a draw!" 
                elif winner and player == 'X':
                    c.execute('UPDATE users SET wins = wins + 1 WHERE name = ?', (user_name,))
                    message = "You win!"
                elif winner and player == 'O':
                    c.execute('UPDATE users SET losses = losses + 1 WHERE name = ?', (user_name,))
                    message = "AI wins!"
                    
                conn.commit()
                return jsonify({"board": board, "winner": winner, "message": message})
            else:
                # AI move with heuristic
                ai_move = get_best_move(board, 'O')
                
                if ai_move is not None:
                    board[ai_move] = 'O'
                    winner = check_winner(board, 'O')
                    
                    if winner:
                        c.execute('UPDATE users SET losses = losses + 1 WHERE name = ?', (user_name,))
                        message = "AI wins!"
                        conn.commit()
                        return jsonify({"board": board, "winner": 'O', "message": message})
                    elif None not in board:
                        c.execute('UPDATE users SET draws = draws + 1 WHERE name = ?', (user_name,))
                        message = "It's a draw!"
                        conn.commit()
                        return jsonify({"board": board, "winner": 'Draw', "message": message})
                
                return jsonify({"board": board, "winner": None, "message": "Next move"})
    else:
        return jsonify({"board": board, "winner": None, "message": "Invalid move"})



@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    with sqlite3.connect('tictactoe.db') as conn:
        c = conn.cursor()
        c.execute('SELECT name, wins FROM users ORDER BY wins DESC LIMIT 10')
        leaderboard = c.fetchall()
        print(leaderboard)
    return jsonify({"leaderboard": leaderboard})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
