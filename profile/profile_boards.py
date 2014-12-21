#!/usr/bin/env python

import sys, time, random, cProfile, pstats

sys.path.append('..')
import boards

board_type = boards.tetris_cow


class access_test(object):
    def __init__(self,method=None,per_cell=None,times=None,full=None):
        self._method = method if method is not None else 'deep'
        self._per_cell = per_cell if per_cell is not None else 1
        self._times = times if times is not None else 1
        self._full = full if full is not None else False

    def GET_CELL(self,board,r,c):
        return board[r,c]

    def SET_ZOID(self,func,*args,**kwds):
        return func(*args,**kwds)

    def run_test_access(self,board):
        for _ in xrange(self._per_cell):
            total = 0
            for r in board.rows():
                for c in board.cols():
                    total += self.GET_CELL(board,r,c)

    def run_test_zoid(self,board,zoid):
        new_board = None
        place_function = getattr(self,self._method)
        for orient in range(4):
            zoid.set_orient(orient) #(only necessary for 'pos' below)
            for c in board.cols():
                pos = (c,0 if self._full else board.pile_height())
                try: new_board = self.SET_ZOID(place_function,board,zoid=zoid,pos=pos,orient=orient)
                except IndexError: break
                self.run_test_access(new_board)

    def run_test_board(self,board):
        for name,zoid in boards.all_zoids.items():
            self.run_test_zoid(board,zoid)

    def run_test_all(self,max_rows,cols,rows=None):
        if rows is None: rows = max_rows
        for _ in xrange(self._times):
            board = board_type(max_rows=max_rows,cols=cols,rows=max_rows if self._full else 0)
            for _ in xrange(rows):
                if not self._full: board.add_rows(1)
                self.run_test_board(board)

    def deep(self,board,*args,**kwds):
        board = board.get_clone()
        board.imprint_zoid(*args,**kwds)
        return board

    def cow(self,board,*args,**kwds):
        board = board.get_cow()
        board.imprint_zoid(*args,**kwds)
        return board


if __name__ == '__main__':
    method=sys.argv[1] if len(sys.argv) > 1 else None
    per_cell=int(sys.argv[2]) if len(sys.argv) > 2 else None
    times=int(sys.argv[3]) if len(sys.argv) > 3 else None

    if method[-1] == '2':
        board_type = boards.tetris_cow2
        method = method[:-1]

    #if uppercase is passed for 'method', use full boards
    if method is not None:
        full = method.lower() != method
        method = method.lower()
    else: full = None

    test = access_test(method=method,per_cell=per_cell,times=times,full=full)
    cProfile.run('test.run_test_all(20,10)')
