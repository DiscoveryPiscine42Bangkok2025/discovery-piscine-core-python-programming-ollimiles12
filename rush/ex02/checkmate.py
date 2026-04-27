def checkmate(p):
    rows = p.split('\n')
    grid = [list(row) for row in rows]
    n = len(grid)
    king = None
    queens = []
    bishops = []
    pawns = []
    rooks = []

    for x in range(len(grid)):
        for y in range(len(grid[x])):
            sector_value = grid[x][y]
            if sector_value == "R":
                rooks.append((x, y))
            elif sector_value == "P":
                pawns.append((x, y))
            elif sector_value == "B":
                bishops.append((x, y))
            elif sector_value == "Q":
                queens.append((x, y))
            elif sector_value == "K":
                if king is None:
                    king = (x, y)
                else:
                    print("Multiple Kings found")
                    return False

    if king is None:
        print("No King")
        return False

    for px, py in pawns:
        if (px - 1, py - 1) == king or (px - 1, py + 1) == king:
            print("Success")
            return True
        if (px + 1, py - 1) == king or (px + 1, py + 1) == king:
            print("Success")
            return True

    for bx, by in bishops:
        for i in range(1, n):
            if (bx - i, by - i) == king or (bx - i, by + i) == king or (bx + i, by - i) == king or (bx + i, by + i) == king:
                print("Success")
                return True  # fix #1

    for rx, ry in rooks:
        for i in range(1, n):
            if (rx, ry - i) == king or (rx, ry + i) == king or (rx - i, ry) == king or (rx + i, ry) == king:
                print("Success")
                return True  # fix #1

    for qx, qy in queens:
        for i in range(1, n):
            if (qx, qy - i) == king or (qx, qy + i) == king or (qx - i, qy) == king or (qx + i, qy) == king or (qx - i, qy - i) == king or (qx - i, qy + i) == king or (qx + i, qy - i) == king or (qx + i, qy + i) == king:
                print("Success")
                return True  # fix #1

    print("No checkmate")
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