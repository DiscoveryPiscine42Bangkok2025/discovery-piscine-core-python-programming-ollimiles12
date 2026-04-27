from flask import Flask, render_template, request, jsonify
from clock import ChessClock
import chess_game
import chess
import chess.engine
import os

STOCKFISH_PATH = os.path.join(os.path.dirname(__file__), "stockfish_extracted", "stockfish", "stockfish-windows-x86-64.exe")

app = Flask(__name__)

clock = ChessClock(seconds_p1=600, seconds_p2=600)

SYMBOL_TO_CHAR = {
    # White pieces  
    '♚': 'K', '♛': 'Q', '♜': 'R', '♝': 'B', '♞': 'N', '♟': 'P',
    # Black pieces 
    '♔': 'k', '♕': 'q', '♖': 'r', '♗': 'b', '♘': 'n', '♙': 'p',
    '.': '.',
}

CHAR_TO_SYMBOL = {
    # White (uppercase) 
    'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟',
    # Black (lowercase)
    'k': '♔', 'q': '♕', 'r': '♖', 'b': '♗', 'n': '♘', 'p': '♙',
    '.': '.',
}


def board_str_to_matrix(board_str: str):
    """Convert the JS board string to chess_game's 2-D list."""
    lines = board_str.strip().split('\n')
    return [[CHAR_TO_SYMBOL.get(ch, '.') for ch in line] for line in lines]


def matrix_to_board_str(matrix) -> str:
    """Convert chess_game's 2-D list back to the JS board string."""
    rows = []
    for row in matrix:
        rows.append(''.join(SYMBOL_TO_CHAR.get(cell, '.') for cell in row))
    return '\n'.join(rows)


def generate_fen(board_matrix, turn, castling_rights, en_passant_target):
    fen_rows = []
    for row in board_matrix:
        empty_count = 0
        fen_row = ""
        for cell in row:
            if cell == '.':
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += SYMBOL_TO_CHAR[cell]
        if empty_count > 0:
            fen_row += str(empty_count)
        fen_rows.append(fen_row)
    fen_board = "/".join(fen_rows)

    fen_castling = ""
    if castling_rights.get('wk', True): fen_castling += "K"
    if castling_rights.get('wq', True): fen_castling += "Q"
    if castling_rights.get('bk', True): fen_castling += "k"
    if castling_rights.get('bq', True): fen_castling += "q"
    if not fen_castling:
        fen_castling = "-"

    if en_passant_target:
        r, c = en_passant_target['r'], en_passant_target['c']
        ep_row = r + 1 if turn == 'b' else r - 1
        fen_ep = f"{chr(ord('a') + c)}{8 - ep_row}"
    else:
        fen_ep = "-"

    return f"{fen_board} {turn} {fen_castling} {fen_ep} 0 1"


def load_state(board_str, turn, en_passant_target, castling_rights):
    """Push frontend state into chess_game module globals."""
    chess_game.board = board_str_to_matrix(board_str)
    chess_game.current_turn = 'white' if turn == 'w' else 'black'

    # en_passant_target from JS: {"r": row, "c": col} or null
    if en_passant_target and isinstance(en_passant_target, dict):
        chess_game.en_passant_target = (en_passant_target['r'], en_passant_target['c'])
    else:
        chess_game.en_passant_target = None

    cr = castling_rights or {}
    # Derive moved flags from the combined castling-rights flags.
    # wk = can castle kingside = king AND h-rook not moved
    # wq = can castle queenside = king AND a-rook not moved
    # So: king moved only if NEITHER side can castle.
    chess_game.moved_pieces = {
        'white_king':   not (cr.get('wk', True) or cr.get('wq', True)),
        'white_rook_a': not cr.get('wq', True),
        'white_rook_h': not cr.get('wk', True),
        'black_king':   not (cr.get('bk', True) or cr.get('bq', True)),
        'black_rook_a': not cr.get('bq', True),
        'black_rook_h': not cr.get('bk', True),
    }


def get_game_status(new_turn_char):
    """Return 'checkmate' | 'stalemate' | 'check' | 'draw' | 'ongoing'."""
    color = 'white' if new_turn_char == 'w' else 'black'

    if chess_game.is_checkmate(color):
        return 'checkmate'
    if chess_game.check_50_moves() or chess_game.check_repeat() or chess_game.is_insufficient_material():
        return 'draw'

    all_moves = chess_game.get_all_valid_moves()
    if not all_moves:
        return 'stalemate'
    if chess_game.in_check(color):
        return 'check'

    return 'ongoing'


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/move", methods=["POST"])
def api_move():
    data = request.get_json()
    board_str        = data.get("board", "")
    from_pos         = data.get("from")          # {"r": int, "c": int}
    to_pos           = data.get("to")            # {"r": int, "c": int}
    turn             = data.get("turn", "w")     # "w" or "b"
    en_passant_target = data.get("en_passant_target", None)
    castling_rights  = data.get("castling_rights", {'wk': True, 'wq': True, 'bk': True, 'bq': True})
    promotion_piece  = data.get("promotion", None)  # optional: "Q","R","B","N"

    # --- Load state into chess_game globals ---
    load_state(board_str, turn, en_passant_target, castling_rights)

    sr, sc = from_pos['r'], from_pos['c']
    er, ec = to_pos['r'],   to_pos['c']

    # --- Validate move ---
    if not chess_game.valid_move(sr, sc, er, ec):
        # Check castling
        row = 7 if chess_game.current_turn == 'white' else 0
        is_castle = False
        castle_type = None
        if sr == row and sc == 4 and er == row:
            if ec == 6 and chess_game.can_castle('short'):
                castle_type = 'O-O'
                is_castle = True
            elif ec == 2 and chess_game.can_castle('long'):
                castle_type = 'O-O-O'
                is_castle = True

        if not is_castle:
            return jsonify({"valid": False, "board": board_str, "turn": turn,
                            "message": "Illegal move",
                            "en_passant_target": en_passant_target,
                            "castling_rights": castling_rights,
                            "status": "ongoing"})
    else:
        is_castle = False
        castle_type = None

    # --- Apply the move ---
    is_capture = chess_game.board[er][ec] != '.'
    piece = chess_game.board[sr][sc]
    is_pawn = piece in ('♟', '♙')

    # Clear en passant before this move; will be set again if needed
    chess_game.en_passant_target = None

    if is_castle:
        row = 7 if chess_game.current_turn == 'white' else 0
        if castle_type == 'O-O':
            chess_game.board[row][6], chess_game.board[row][4] = chess_game.board[row][4], '.'
            chess_game.board[row][5], chess_game.board[row][7] = chess_game.board[row][7], '.'
            chess_game.moved_pieces[f"{chess_game.current_turn}_rook_h"] = True
        else:
            chess_game.board[row][2], chess_game.board[row][4] = chess_game.board[row][4], '.'
            chess_game.board[row][3], chess_game.board[row][0] = chess_game.board[row][0], '.'
            chess_game.moved_pieces[f"{chess_game.current_turn}_rook_a"] = True
        chess_game.moved_pieces[f"{chess_game.current_turn}_king"] = True
        chess_game.halfmove_clock += 1
    else:
        # Track rook/king moves for castling rights
        if piece == '♚':
            chess_game.moved_pieces['white_king'] = True
        elif piece == '♔':
            chess_game.moved_pieces['black_king'] = True
        elif piece == '♜':
            if sr == 7 and sc == 0: chess_game.moved_pieces['white_rook_a'] = True
            if sr == 7 and sc == 7: chess_game.moved_pieces['white_rook_h'] = True
        elif piece == '♖':
            if sr == 0 and sc == 0: chess_game.moved_pieces['black_rook_a'] = True
            if sr == 0 and sc == 7: chess_game.moved_pieces['black_rook_h'] = True

        if is_pawn or is_capture:
            chess_game.halfmove_clock = 0
        else:
            chess_game.halfmove_clock += 1

        # En passant capture
        if is_pawn and abs(ec - sc) == 1 and chess_game.board[er][ec] == '.':
            chess_game.board[sr][ec] = '.'
            is_capture = True

        chess_game.board[er][ec], chess_game.board[sr][sc] = piece, '.'

        # Set en passant target on double pawn push
        if is_pawn and abs(er - sr) == 2:
            chess_game.en_passant_target = (er, ec)

        # Pawn promotion
        if is_pawn and (er == 0 or er == 7):
            promo = (promotion_piece or 'Q').upper()
            syms = {
                'white': {'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞'},
                'black': {'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘'}
            }
            chess_game.board[er][ec] = syms[chess_game.current_turn][promo]

    # --- Switch turn ---
    opp_color = 'black' if chess_game.current_turn == 'white' else 'white'
    new_turn_char = 'b' if chess_game.current_turn == 'white' else 'w'
    chess_game.current_turn = opp_color
    chess_game.record_position()

    # --- Build response ---
    new_board_str = matrix_to_board_str(chess_game.board)
    new_ep = None
    if chess_game.en_passant_target:
        new_ep = {'r': chess_game.en_passant_target[0], 'c': chess_game.en_passant_target[1]}

    new_cr = {
        'wk': not chess_game.moved_pieces['white_king'] and not chess_game.moved_pieces['white_rook_h'],
        'wq': not chess_game.moved_pieces['white_king'] and not chess_game.moved_pieces['white_rook_a'],
        'bk': not chess_game.moved_pieces['black_king'] and not chess_game.moved_pieces['black_rook_h'],
        'bq': not chess_game.moved_pieces['black_king'] and not chess_game.moved_pieces['black_rook_a'],
    }

    status = get_game_status(new_turn_char)
    clock.switch_turn()

    return jsonify({
        "valid": True,
        "board": new_board_str,
        "turn": new_turn_char,
        "message": "ok",
        "en_passant_target": new_ep,
        "castling_rights": new_cr,
        "status": status
    })


@app.route("/api/timer/state", methods=["GET"])
def timer_state():
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
    # Clear game history so stale repetition/50-move data doesn't leak across games
    chess_game.reset_history()
    return jsonify(clock.get_state())


@app.route("/api/bot_move", methods=["POST"])
def api_bot_move():
    data = request.get_json()
    elo = data.get("elo", 1500)
    fen = generate_fen(
        board_str_to_matrix(data.get("board", "")),
        data.get("turn", "w"),
        data.get("castling_rights", {}),
        data.get("en_passant_target")
    )

    print(f"[BOT] FEN: {fen}")

    try:
        board = chess.Board(fen)
    except Exception as e:
        print(f"[BOT] Invalid FEN: {e}")
        return jsonify({"error": f"Invalid FEN: {e}"}), 400

    # If no legal moves (checkmate/stalemate) don't bother asking Stockfish
    if not list(board.legal_moves):
        return jsonify({"error": "No legal moves"}), 400

    try:
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            # UCI_LimitStrength requires ELO >= 1320 for most Stockfish builds
            if elo >= 1320:
                engine.configure({"UCI_LimitStrength": True, "UCI_Elo": elo})
            else:
                engine.configure({"UCI_LimitStrength": True, "UCI_Elo": 1320,
                                   "Skill Level": max(0, int((elo - 100) / 40))})
            result = engine.play(board, chess.engine.Limit(time=0.15))
            if result.move:
                m = result.move
                print(f"[BOT] Move: {m}")
                return jsonify({
                    "from": {"r": 7 - chess.square_rank(m.from_square), "c": chess.square_file(m.from_square)},
                    "to": {"r": 7 - chess.square_rank(m.to_square), "c": chess.square_file(m.to_square)},
                    "promotion": chess.piece_symbol(m.promotion).upper() if m.promotion else None
                })
    except Exception as e:
        print(f"[BOT] Engine error: {e}")
        return jsonify({"error": str(e)}), 500
    return jsonify({"error": "No move"}), 400


if __name__ == "__main__":
    app.run(debug=True)