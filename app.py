from flask import Flask, request, jsonify, render_template
import sqlite3
import random

app = Flask(__name__, template_folder='.')

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('tictactoe.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY, 
                    name TEXT, 
                    wins INTEGER, 
                    losses INTEGER, 
                    draws INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# Helper function to get or create user
def get_or_create_user(name):
    conn = sqlite3.connect('tictactoe.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE name=?', (name,))
    user = c.fetchone()
    if not user:
        c.execute('INSERT INTO users (name, wins, losses, draws) VALUES (?, 0, 0, 0)', (name,))
        conn.commit()
        c.execute('SELECT * FROM users WHERE name=?', (name,))
        user = c.fetchone()
    conn.close()
    return user

# Game logic
def check_winner(board):
    # Rows, columns, and diagonals to check
    winning_combinations = [
        [board[0], board[1], board[2]],
        [board[3], board[4], board[5]],
        [board[6], board[7], board[8]],
        [board[0], board[3], board[6]],
        [board[1], board[4], board[7]],
        [board[2], board[5], board[8]],
        [board[0], board[4], board[8]],
        [board[2], board[4], board[6]],
    ]
    for combo in winning_combinations:
        if combo[0] == combo[1] == combo[2] and combo[0] is not None:
            return combo[0]
    if None not in board:
        return 'Draw'
    return None

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.json
    player_name = data.get('name')
    board = [None] * 9  # Example board setup
    return jsonify({"board": board, "message": f"Game started for {player_name}!"})


@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    board = data['board']
    position = data['position']
    player = data['player']
    user_name = data['name']
    
    if board[position] is None:
        board[position] = player
        winner = check_winner(board)
        
        conn = sqlite3.connect('tictactoe.db')
        c = conn.cursor()
        
        if winner:
            if winner == 'X':
                c.execute('UPDATE users SET wins = wins + 1 WHERE name = ?', (user_name,))
                message = "You win!"
            elif winner == 'O':
                c.execute('UPDATE users SET losses = losses + 1 WHERE name = ?', (user_name,))
                message = "AI wins!"
            else:
                c.execute('UPDATE users SET draws = draws + 1 WHERE name = ?', (user_name,))
                message = "It's a draw!"
                
            conn.commit()
            conn.close()
            
            return jsonify({"board": board, "winner": winner, "message": message})
        else:
            # AI makes a random move if the game is not yet won or drawn
            empty_positions = [i for i in range(9) if board[i] is None]
            if empty_positions:
                ai_move = random.choice(empty_positions)
                board[ai_move] = 'O'
                winner = check_winner(board)
                
                if winner:
                    if winner == 'O':
                        c.execute('UPDATE users SET losses = losses + 1 WHERE name = ?', (user_name,))
                        message = "AI wins!"
                    else:
                        c.execute('UPDATE users SET draws = draws + 1 WHERE name = ?', (user_name,))
                        message = "It's a draw!"
                    
                    conn.commit()
                    conn.close()
                    return jsonify({"board": board, "winner": winner, "message": message})
        
        conn.close()  # Ensure connection is closed if no winner yet
        return jsonify({"board": board, "winner": None, "message": "Next move"})
    else:
        return jsonify({"board": board, "winner": None, "message": "Invalid move"})

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    conn = sqlite3.connect('tictactoe.db')
    c = conn.cursor()
    c.execute('SELECT name, wins FROM users ORDER BY wins DESC limit 10')
    leaderboard = c.fetchall()
    conn.close()
    return jsonify({"leaderboard": leaderboard})

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)
