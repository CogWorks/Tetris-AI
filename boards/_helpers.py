import sys, math


def _find_outline(board,down=False):
    """Find the outline of the top or bottom of the board."""
    counts = [0]*board.get_dims()[1]
    for c in board.cols():
        for r in board.rows(reverse=down):
            if not board[r,c]: counts[c] += 1
            else: break
    return counts


def print_board(board,output=sys.stderr,all=False):
    """Print a Tetris board."""
    cow_mask = board.get_cow_mask() if hasattr(board,'get_cow_mask') and callable(board.get_cow_mask) else None

    try: rows = [r for r in board.rows(reverse=True,all=all)]
    except TypeError: rows = [r for r in board.rows(reverse=True)]

    if rows and rows[0] > 1: row_format = '[%%s%%.%ud] '%int(math.ceil(math.log(rows[0],10)))
    else: row_format = '[%s%.1d] '

    for r in rows:
        if r >= board.row_count(): modifier = '@'
        elif cow_mask and r < len(cow_mask) and cow_mask[r]: modifier = '*'
        else: modifier = ' '

        print >> output, row_format%(modifier,r), '|',
        for c in board.cols(): print >> output, board[r,c] if board[r,c] else ' ',
        print >> output, '|'

    #(a bit of a hack, for spacing)
    print >> output, '-'*len(row_format%(0,0)), '[',
    for c in board.cols(): print >> output, c%10,
    print >> output, ']'
