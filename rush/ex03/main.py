from flask import Flask, render_template, request, jsonify
from game_logic import make_move, init_board, get_game_status
from clock import ChessClock

app = Flask(__name__)

# Single shared chess clock instance (server-side state)
clock = ChessClock(seconds_p1=600, seconds_p2=600)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/move", methods=["POST"])
def api_move():
    data = request.get_json()
    board = data.get("board", "")
    from_pos = data.get("from")
    to_pos = data.get("to")
    turn = data.get("turn", "w")
    en_passant_target = data.get("en_passant_target", None)
    castling_rights = data.get("castling_rights", {
        'wk': True, 'wq': True, 'bk': True, 'bq': True
    })

    valid, new_turn, new_board, msg, new_ep, new_cr = make_move(
        board, from_pos, to_pos, turn, en_passant_target, castling_rights
    )

    status = "ongoing"
    if valid:
        status = get_game_status(new_board, new_turn, new_ep, new_cr)
        # Switch the chess clock turn when a valid move is made
        clock.switch_turn()

    return jsonify({
        "valid": valid,
        "board": new_board,
        "turn": new_turn,
        "message": msg,
        "en_passant_target": new_ep,
        "castling_rights": new_cr,
        "status": status
    })


@app.route("/api/timer/state", methods=["GET"])
def timer_state():
    """Poll this every second to update the clock display."""
    return jsonify(clock.get_state())


@app.route("/api/timer/start", methods=["POST"])
def timer_start():
    clock.start()
    return jsonify(clock.get_state())


@app.route("/api/timer/stop", methods=["POST"])
def timer_stop():
    clock.stop()
    return jsonify(clock.get_state())


@app.route("/api/timer/reset", methods=["POST"])
def timer_reset():
    data = request.get_json(silent=True) or {}
    p1 = data.get("p1", 600)
    p2 = data.get("p2", 600)
    clock.reset(seconds_p1=p1, seconds_p2=p2)
    return jsonify(clock.get_state())


if __name__ == "__main__":
    app.run(debug=True)