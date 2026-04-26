def is_valid_move(grid, fr, fc, tr, tc, turn):
    piece = grid[fr][fc]
    target = grid[tr][tc]

    # Empty square check
    if piece == '.':
        return False, "No piece selected."

    # Turn verification
    is_white = piece.isupper()
    if (turn == 'w' and not is_white) or (turn == 'b' and is_white):
        return False, "It's not your turn!"

    # Friendly fire check
    if target != '.':
        target_is_white = target.isupper()
        if is_white == target_is_white:
            return False, "Cannot capture your own piece!"

    p = piece.lower()
    dr = tr - fr
    dc = tc - fc

    # Pawn Logic
    if p == 'p':
        direction = -1 if is_white else 1
        start_row = 6 if is_white else 1

        # Move forward 1
        if dc == 0 and dr == direction and target == '.':
            return True, ""
        # Move forward 2 from start
        if dc == 0 and dr == 2 * direction and fr == start_row and target == '.' and grid[fr + direction][fc] == '.':
            return True, ""
        # Capture diagonally
        if abs(dc) == 1 and dr == direction and target != '.':
            return True, ""
        return False, "Invalid Pawn move."

    # Knight Logic
    elif p == 'n':
        if (abs(dr) == 2 and abs(dc) == 1) or (abs(dr) == 1 and abs(dc) == 2):
            return True, ""
        return False, "Invalid Knight move."

    # Bishop Logic
    elif p == 'b':
        if abs(dr) == abs(dc):
            # Check for blocking pieces
            step_r = 1 if dr > 0 else -1
            step_c = 1 if dc > 0 else -1
            r, c = fr + step_r, fc + step_c
            while r != tr and c != tc:
                if grid[r][c] != '.':
                    return False, "Bishop blocked."
                r += step_r
                c += step_c
            return True, ""
        return False, "Invalid Bishop move."

    # Rook Logic
    elif p == 'r':
        if dr == 0 or dc == 0:
            step_r = (1 if dr > 0 else -1) if dr != 0 else 0
            step_c = (1 if dc > 0 else -1) if dc != 0 else 0
            r, c = fr + step_r, fc + step_c
            while r != tr or c != tc:
                if grid[r][c] != '.':
                    return False, "Rook blocked."
                r += step_r
                c += step_c
            return True, ""
        return False, "Invalid Rook move."

    # Queen Logic
    elif p == 'q':
        # Queen is Rook + Bishop
        if abs(dr) == abs(dc) or dr == 0 or dc == 0:
            step_r = (1 if dr > 0 else -1) if dr != 0 else 0
            step_c = (1 if dc > 0 else -1) if dc != 0 else 0
            r, c = fr + step_r, fc + step_c
            while r != tr or c != tc:
                if grid[r][c] != '.':
                    return False, "Queen blocked."
                r += step_r
                c += step_c
            return True, ""
        return False, "Invalid Queen move."

    # King Logic
    elif p == 'k':
        if abs(dr) <= 1 and abs(dc) <= 1:
            return True, ""
        return False, "Invalid King move."

    return False, "Unknown piece."


def make_move(board_str, from_pos, to_pos, turn):
    rows = board_str.split('\n')
    grid = [list(row) for row in rows]
    
    fr, fc = from_pos['r'], from_pos['c']
    tr, tc = to_pos['r'], to_pos['c']
    
    if 0 <= fr < 8 and 0 <= fc < 8 and 0 <= tr < 8 and 0 <= tc < 8:
        valid, msg = is_valid_move(grid, fr, fc, tr, tc, turn)
        if not valid:
            return False, turn, board_str, msg
            
        # Move piece
        piece = grid[fr][fc]
        grid[fr][fc] = '.'
        grid[tr][tc] = piece

        # Basic Promotion logic for Pawn (auto-promote to Queen to keep it simple)
        if piece.lower() == 'p':
            if (piece.isupper() and tr == 0) or (piece.islower() and tr == 7):
                grid[tr][tc] = 'Q' if piece.isupper() else 'q'

        new_turn = 'b' if turn == 'w' else 'w'
        new_board = "\n".join("".join(row) for row in grid)
        return True, new_turn, new_board, ""
    
    return False, turn, board_str, "Out of bounds."


def init_board():
    return (
        "rnbqkbnr\n"
        "pppppppp\n"
        "........\n"
        "........\n"
        "........\n"
        "........\n"
        "PPPPPPPP\n"
        "RNBQKBNR"
    )
