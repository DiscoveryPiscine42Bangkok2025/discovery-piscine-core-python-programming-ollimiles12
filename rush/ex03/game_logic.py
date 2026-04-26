def make_move(board_str, from_pos, to_pos):
    # board_str is 8 lines of 8 characters, from_pos and to_pos are dicts with 'r' and 'c' (0-indexed)
    rows = board_str.split('\n')
    grid = [list(row) for row in rows]
    
    fr, fc = from_pos['r'], from_pos['c']
    tr, tc = to_pos['r'], to_pos['c']
    
    if 0 <= fr < len(grid) and 0 <= fc < len(grid[0]) and 0 <= tr < len(grid) and 0 <= tc < len(grid[0]):
        piece = grid[fr][fc]
        grid[fr][fc] = '.'
        grid[tr][tc] = piece

    return "\n".join("".join(row) for row in grid)

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
