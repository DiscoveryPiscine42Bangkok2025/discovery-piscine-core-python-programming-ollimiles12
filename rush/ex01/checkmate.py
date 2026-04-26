def checkmate(p):
    #split part
    rows = p.split('\n')
    grid = [list(row) for row in rows] 

    king = None
    queens = []
    bishops = []
    pawns = []
    rooks = []

    for x in range(len(grid)):        
        for y in range(len(grid[x])): 
            sector_value = grid[x][y]
            if "R" in sector_value:
                rooks.append((x,y))
            elif "P" in sector_value:
                pawns.append((x,y))
            elif "B" in sector_value:
                bishops.append((x,y))
            elif "Q"in sector_value:
                queens.append((x,y))
            elif "K" in sector_value:
                king = (x,y)

    #analyzed
    for px, py in pawns:
        if (px - 1, py - 1) == king or (px - 1, py + 1) == king:
            print("Success")
            return

    for bx, by in bishops:
        for i in range(4):
            if (bx - i, by - i) == king or (bx - i, by + i) == king or (bx + i, by - i) == king or (bx + i, by + i) == king:
                print("Success")
                return

    for rx, ry in rooks:
        for i in range(4):
            if (rx, ry - i) == king or (rx, ry + i) == king or (rx - i, ry) == king or (rx + i, ry) == king:
                print("Success")
                return
    
    for qx,qy in queens:
        for i in range(4):
            if (qx, qy - i) == king or (qx, qy + i) == king or (qx - i, qy) == king or (qx + i, qy) == king or (qx - i, qy - i) == king or (qx - i, qy + i) == king or (qx + i, qy - i) == king or (qx + i, qy + i) == king:
                print("Success")
                return
    print("No checkmate")