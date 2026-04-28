def checkmate(p):
    rows = p.split('\n')
    grid = [list(row) for row in rows]

    row_lengths = [len(row) for row in grid]
    if len(set(row_lengths)) != 1 or len(grid) != row_lengths[0]:
        print("Error")
        return False

    n = len(grid)
    king = None
    queens = []
    bishops = []
    pawns = []
    rooks = []

    for x in range(n):
        for y in range(n):
            cell = grid[x][y]
            if cell == 'R':
                rooks.append((x, y))
            elif cell == 'P':
                pawns.append((x, y))
            elif cell == 'B':
                bishops.append((x, y))
            elif cell == 'Q':
                queens.append((x, y))
            elif cell == 'K':
                if king is None:
                    king = (x, y)
                else:
                    print("Error")
                    return False

    if king is None:
        print("Error")
        return False

    for px, py in pawns:
        if (px - 1, py - 1) == king or (px - 1, py + 1) == king:
            print("Success")
            return True

    for bx, by in bishops:
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            for i in range(1, n):
                nx, ny = bx + dx * i, by + dy * i
                if not (0 <= nx < n and 0 <= ny < n):
                    break
                if (nx, ny) == king:
                    print("Success")
                    return True
                if grid[nx][ny] != '.':
                    break

    for rx, ry in rooks:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            for i in range(1, n):
                nx, ny = rx + dx * i, ry + dy * i
                if not (0 <= nx < n and 0 <= ny < n):
                    break
                if (nx, ny) == king:
                    print("Success")
                    return True
                if grid[nx][ny] != '.':
                    break 

    for qx, qy in queens:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            for i in range(1, n):
                nx, ny = qx + dx * i, qy + dy * i
                if not (0 <= nx < n and 0 <= ny < n):
                    break
                if (nx, ny) == king:
                    print("Success")
                    return True
                if grid[nx][ny] != '.':
                    break 

    print("Fail")
    return False

def best_move(p):
    rows = p.split('\n')
    grid = [list(row) for row in rows]

    pieces = []
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            if grid[x][y] in ["Q", "R", "B", "P"]:
                pieces.append((grid[x][y], x, y))

    for piece, x, y in pieces:
        for nx in range(len(grid)):
            for ny in range(len(grid[nx])):
                if grid[nx][ny] == ".":
                    new_grid = [row[:] for row in grid]
                    new_grid[nx][ny] = piece
                    new_grid[x][y] = "."

                    new_board = "\n".join("".join(row) for row in new_grid)

                    if checkmate(new_board):
                        print("Best move:")
                        print(piece, "from", (x, y), "to", (nx, ny))
                        return

    print("No move")