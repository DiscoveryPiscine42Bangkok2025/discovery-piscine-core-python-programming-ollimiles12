from flask import Flask, render_template, request, jsonify
from checkmate import checkmate, best_move
from game_logic import make_move, init_board
import io
import sys

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/checkmate", methods=["POST"])
def api_checkmate():
    """Check if the given board state is checkmate."""
    data = request.get_json()
    board = data.get("board", "")

    # Capture printed output from checkmate()
    captured = io.StringIO()
    sys.stdout = captured
    result = checkmate(board)
    sys.stdout = sys.__stdout__

    return jsonify({
        "checkmate": result,
        "message": captured.getvalue().strip()
    })

@app.route("/api/best_move", methods=["POST"])
def api_best_move():
    """Find the best move on the given board."""
    data = request.get_json()
    board = data.get("board", "")

    captured = io.StringIO()
    sys.stdout = captured
    best_move(board)
    sys.stdout = sys.__stdout__

    output = captured.getvalue().strip()
    return jsonify({"result": output})

@app.route("/api/move", methods=["POST"])
def api_move():
    data = request.get_json()
    board = data.get("board", "")
    from_pos = data.get("from")
    to_pos = data.get("to")
    turn = data.get("turn", "w")
    
    valid, new_turn, new_board, msg = make_move(board, from_pos, to_pos, turn)
    return jsonify({
        "valid": valid,
        "board": new_board,
        "turn": new_turn,
        "message": msg
    })

if __name__ == "__main__":
    app.run(debug=True)