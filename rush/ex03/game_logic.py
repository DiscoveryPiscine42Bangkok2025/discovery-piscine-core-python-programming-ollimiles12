def is_in_check(grid, color):
    """
    Returns True if the king of the given color is currently in check.
    color is 'w' for white or 'b' for black.
    """
    # Find the king
    king_char = 'K' if color == 'w' else 'k'
    king_pos = None
    for r in range(8):
        for c in range(8):
            if grid[r][c] == king_char:
                king_pos = (r, c)
                break

    if king_pos is None:
        return False  # no king found (shouldn't happen in a real game)

    kr, kc = king_pos
    enemy_color = 'b' if color == 'w' else 'w'

    # Check if any enemy piece attacks the king square
    # Pawns
    if color == 'w':
        # Enemy black pawns attack downward (increasing row)
        for pr, pc in [(kr - 1, kc - 1), (kr - 1, kc + 1)]:
            if 0 <= pr < 8 and 0 <= pc < 8 and grid[pr][pc] == 'p':
                return True
    else:
        # Enemy white pawns attack upward (decreasing row)
        for pr, pc in [(kr + 1, kc - 1), (kr + 1, kc + 1)]:
            if 0 <= pr < 8 and 0 <= pc < 8 and grid[pr][pc] == 'P':
                return True

    # Knights
    knight_char = 'n' if enemy_color == 'b' else 'N'
    for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
        nr, nc = kr + dr, kc + dc
        if 0 <= nr < 8 and 0 <= nc < 8 and grid[nr][nc] == knight_char:
            return True

    # Bishops / Queens (diagonal)
    bishop_char = 'b' if enemy_color == 'b' else 'B'
    queen_char  = 'q' if enemy_color == 'b' else 'Q'
    for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
        r, c = kr + dr, kc + dc
        while 0 <= r < 8 and 0 <= c < 8:
            if grid[r][c] != '.':
                if grid[r][c] in (bishop_char, queen_char):
                    return True
                break
            r += dr
            c += dc

    # Rooks / Queens (straight lines)
    rook_char = 'r' if enemy_color == 'b' else 'R'
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        r, c = kr + dr, kc + dc
        while 0 <= r < 8 and 0 <= c < 8:
            if grid[r][c] != '.':
                if grid[r][c] in (rook_char, queen_char):
                    return True
                break
            r += dr
            c += dc

    # Enemy King (to prevent kings from being adjacent)
    enemy_king = 'k' if enemy_color == 'b' else 'K'
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = kr + dr, kc + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and grid[nr][nc] == enemy_king:
                return True

    return False


def is_valid_move(grid, fr, fc, tr, tc, turn, en_passant_target=None):
    """
    Checks if moving from (fr,fc) to (tr,tc) is legal for the current turn.
    en_passant_target: the square a pawn can capture en passant, e.g. (row, col) or None.
    Returns (True/False, message).
    """
    piece = grid[fr][fc]
    target = grid[tr][tc]

    if piece == '.':
        return False, "No piece selected."

    is_white = piece.isupper()
    if (turn == 'w' and not is_white) or (turn == 'b' and is_white):
        return False, "It's not your turn!"

    # Can't capture your own piece
    if target != '.':
        target_is_white = target.isupper()
        if is_white == target_is_white:
            return False, "Cannot capture your own piece!"

    p = piece.lower()
    dr = tr - fr
    dc = tc - fc

    move_ok = False

    # --- Pawn ---
    if p == 'p':
        direction = -1 if is_white else 1
        start_row = 6 if is_white else 1

        # Move forward 1
        if dc == 0 and dr == direction and target == '.':
            move_ok = True
        # Move forward 2 from starting row
        elif dc == 0 and dr == 2 * direction and fr == start_row and target == '.' and grid[fr + direction][fc] == '.':
            move_ok = True
        # Normal diagonal capture
        elif abs(dc) == 1 and dr == direction and target != '.':
            move_ok = True
        # En passant capture
        elif abs(dc) == 1 and dr == direction and en_passant_target == (tr, tc) and target == '.':
            move_ok = True
        else:
            return False, "Invalid Pawn move."

    # --- Knight ---
    elif p == 'n':
        if (abs(dr) == 2 and abs(dc) == 1) or (abs(dr) == 1 and abs(dc) == 2):
            move_ok = True
        else:
            return False, "Invalid Knight move."

    # --- Bishop ---
    elif p == 'b':
        if abs(dr) == abs(dc):
            step_r = 1 if dr > 0 else -1
            step_c = 1 if dc > 0 else -1
            r, c = fr + step_r, fc + step_c
            while r != tr and c != tc:
                if grid[r][c] != '.':
                    return False, "Bishop blocked."
                r += step_r
                c += step_c
            move_ok = True
        else:
            return False, "Invalid Bishop move."

    # --- Rook ---
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
            move_ok = True
        else:
            return False, "Invalid Rook move."

    # --- Queen ---
    elif p == 'q':
        if abs(dr) == abs(dc) or dr == 0 or dc == 0:
            step_r = (1 if dr > 0 else -1) if dr != 0 else 0
            step_c = (1 if dc > 0 else -1) if dc != 0 else 0
            r, c = fr + step_r, fc + step_c
            while r != tr or c != tc:
                if grid[r][c] != '.':
                    return False, "Queen blocked."
                r += step_r
                c += step_c
            move_ok = True
        else:
            return False, "Invalid Queen move."

    # --- King ---
    elif p == 'k':
        if abs(dr) <= 1 and abs(dc) <= 1:
            move_ok = True
        else:
            return False, "Invalid King move."

    if not move_ok:
        return False, "Unknown piece."

    # After any move, make sure our own king is NOT in check
    # Simulate the move on a copy of the board
    temp_grid = [row[:] for row in grid]
    # Handle en passant capture removal
    if p == 'p' and abs(dc) == 1 and target == '.' and en_passant_target == (tr, tc):
        # Remove the captured pawn
        captured_row = fr  # the captured pawn is on the same row as the moving pawn
        temp_grid[captured_row][tc] = '.'
    temp_grid[tr][tc] = piece
    temp_grid[fr][fc] = '.'

    color = 'w' if is_white else 'b'
    if is_in_check(temp_grid, color):
        return False, "That move leaves your king in check!"

    return True, ""


def can_castle(grid, turn, side, castling_rights):
    """
    Check if castling is legal.
    side: 'k' (kingside) or 'q' (queenside).
    castling_rights: dict like {'wk': True, 'wq': True, 'bk': True, 'bq': True}
    Returns True or False.
    """
    color = turn
    right_key = color + side  # e.g. 'wk', 'bq'

    if not castling_rights.get(right_key, False):
        return False

    row = 7 if color == 'w' else 0

    if side == 'k':  # kingside
        # Squares between king and rook must be empty
        if grid[row][5] != '.' or grid[row][6] != '.':
            return False
        # King must not be in check, and must not pass through check
        for col in [4, 5, 6]:
            temp = [r[:] for r in grid]
            # Simulate king on each square
            king_char = 'K' if color == 'w' else 'k'
            # Move king temporarily
            temp[row][4] = '.'
            temp[row][col] = king_char
            if is_in_check(temp, color):
                return False
    else:  # queenside
        if grid[row][3] != '.' or grid[row][2] != '.' or grid[row][1] != '.':
            return False
        for col in [4, 3, 2]:
            temp = [r[:] for r in grid]
            king_char = 'K' if color == 'w' else 'k'
            temp[row][4] = '.'
            temp[row][col] = king_char
            if is_in_check(temp, color):
                return False

    return True


def make_move(board_str, from_pos, to_pos, turn, en_passant_target=None, castling_rights=None):
    """
    Attempts to make a move. Returns:
    (valid, new_turn, new_board, message, new_en_passant_target, new_castling_rights)
    """
    rows = board_str.split('\n')
    grid = [list(row) for row in rows]

    if castling_rights is None:
        castling_rights = {'wk': True, 'wq': True, 'bk': True, 'bq': True}

    fr, fc = from_pos['r'], from_pos['c']
    tr, tc = to_pos['r'], to_pos['c']

    # Convert en_passant_target from dict to tuple if needed
    ep = None
    if en_passant_target:
        ep = (en_passant_target['r'], en_passant_target['c'])

    if not (0 <= fr < 8 and 0 <= fc < 8 and 0 <= tr < 8 and 0 <= tc < 8):
        return False, turn, board_str, "Out of bounds.", en_passant_target, castling_rights

    piece = grid[fr][fc]
    if piece == '.':
        return False, turn, board_str, "No piece there.", en_passant_target, castling_rights

    p = piece.lower()
    is_white = piece.isupper()
    color = 'w' if is_white else 'b'

    # --- Check for castling attempt ---
    # King moves 2 squares sideways = castling
    if p == 'k' and abs(tc - fc) == 2 and fr == tr:
        side = 'k' if tc > fc else 'q'
        if can_castle(grid, color, side, castling_rights):
            row = fr
            rook_char = 'R' if color == 'w' else 'r'
            king_char = 'K' if color == 'w' else 'k'
            if side == 'k':
                grid[row][4] = '.'
                grid[row][7] = '.'
                grid[row][6] = king_char
                grid[row][5] = rook_char
            else:
                grid[row][4] = '.'
                grid[row][0] = '.'
                grid[row][2] = king_char
                grid[row][3] = rook_char
            # Update castling rights — king moved
            new_cr = dict(castling_rights)
            new_cr[color + 'k'] = False
            new_cr[color + 'q'] = False
            new_turn = 'b' if turn == 'w' else 'w'
            new_board = "\n".join("".join(row) for row in grid)
            return True, new_turn, new_board, "", None, new_cr
        else:
            return False, turn, board_str, "Castling not allowed.", en_passant_target, castling_rights

    # --- Normal move validation ---
    valid, msg = is_valid_move(grid, fr, fc, tr, tc, turn, ep)
    if not valid:
        return False, turn, board_str, msg, en_passant_target, castling_rights

    # --- Apply the move ---
    new_ep = None  # reset en passant each turn

    # En passant capture: remove the captured pawn
    if p == 'p' and abs(tc - fc) == 1 and grid[tr][tc] == '.' and ep == (tr, tc):
        grid[fr][tc] = '.'  # remove captured pawn (same row as moving pawn, same column as destination)

    # Set en passant target if pawn moves 2 squares
    if p == 'p' and abs(tr - fr) == 2:
        new_ep = {'r': (fr + tr) // 2, 'c': fc}  # the skipped square

    grid[tr][tc] = piece
    grid[fr][fc] = '.'

    # Pawn promotion (auto-queen)
    if p == 'p':
        if is_white and tr == 0:
            grid[tr][tc] = 'Q'
        elif not is_white and tr == 7:
            grid[tr][tc] = 'q'

    # Update castling rights if king or rook moved
    new_cr = dict(castling_rights)
    if p == 'k':
        new_cr[color + 'k'] = False
        new_cr[color + 'q'] = False
    if p == 'r':
        if color == 'w':
            if fr == 7 and fc == 7: new_cr['wk'] = False
            if fr == 7 and fc == 0: new_cr['wq'] = False
        else:
            if fr == 0 and fc == 7: new_cr['bk'] = False
            if fr == 0 and fc == 0: new_cr['bq'] = False

    new_turn = 'b' if turn == 'w' else 'w'
    new_board = "\n".join("".join(row) for row in grid)
    return True, new_turn, new_board, "", new_ep, new_cr


def has_any_legal_move(board_str, turn, en_passant_target=None, castling_rights=None):
    """
    Returns True if the current player has at least one legal move.
    Used to detect checkmate and stalemate.
    """
    rows = board_str.split('\n')
    grid = [list(row) for row in rows]

    if castling_rights is None:
        castling_rights = {'wk': True, 'wq': True, 'bk': True, 'bq': True}

    ep = None
    if en_passant_target:
        ep = (en_passant_target['r'], en_passant_target['c'])

    for fr in range(8):
        for fc in range(8):
            piece = grid[fr][fc]
            if piece == '.':
                continue
            is_white = piece.isupper()
            if (turn == 'w' and not is_white) or (turn == 'b' and is_white):
                continue
            for tr in range(8):
                for tc in range(8):
                    valid, _ = is_valid_move(grid, fr, fc, tr, tc, turn, ep)
                    if valid:
                        return True
    return False


def get_game_status(board_str, turn, en_passant_target=None, castling_rights=None):
    """
    Returns the current game status:
    'check', 'checkmate', 'stalemate', or 'ongoing'
    """
    rows = board_str.split('\n')
    grid = [list(row) for row in rows]

    in_check = is_in_check(grid, turn)
    has_moves = has_any_legal_move(board_str, turn, en_passant_target, castling_rights)

    if in_check and not has_moves:
        return 'checkmate'
    elif not in_check and not has_moves:
        return 'stalemate'
    elif in_check:
        return 'check'
    else:
        return 'ongoing'


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
