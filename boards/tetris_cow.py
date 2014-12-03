import sys, math, copy

import _helpers


class tetris_cow(object):
    """Copy-on-write Tetris board."""
    def __init__(self,max_rows=20,cols=10,rows=0):
        """Initialize board: number of cols, max number of rows, initial number of rows."""
        self._cols = cols
        self._max_rows = max_rows
        self._board = [self._default_row() for _ in range(rows)]
        self._cow_list = [False]*len(self._board)
        self._profile = None


    #ELEMENT ACCESS >>>>>

    def __getitem__(self,(r,c)):
        """Get a cell value (row first), e.g., 'myboard[0,0]'."""
        if self._max_rows > r >= len(self._board) and 0 <= c < self._cols: return 0
        else: return self._board[r][c]

    def __setitem__(self,(r,c),val):
        """Set a cell value (row first), e.g., 'myboard[0,0] = 1'."""
        if self._cow_list[r]:
            self._board[r] = list(self._board[r])
            self._cow_list[r] = False
        self._board[r][c] = val
        self._profile = None
        return val

    def get_dims(self,max=False):
        """Get board dimensions (use 'max=True' for max size)."""
        return (self._max_rows if max else len(self._board),self._cols)

    def rows(self,reverse=False,all=False):
        """Get a generator for the rows of the zoid in its current position and orientation. Optional: reverse order."""
        return xrange(self.get_dims(max=all)[0]-1,-1,-1) if reverse else xrange(self.get_dims(max=all)[0])

    def cols(self):
        """Get a generator for the cols of the zoid in its current position and orientation."""
        return xrange(self.get_dims()[1])

    def get_top_profile(self):
        """Get the profile of the top of the board."""
        if not self._profile: self._generate_profile()
        return self._profile

    #<<<<< ELEMENT ACCESS


    #ROW MANIPULATION >>>>>

    def del_row(self,r):
        """Delete a single row from the board"""
        if not (0 <= r < self._max_rows): raise IndexError('index out of range')
        if r >= len(self._board): return
        self._board.pop(r)
        self._cow_list.pop(r)
        self._profile = None

    def del_rows(self,rows):
        """Delete multiple rows from the board."""
        rows = sorted(list(frozenset(rows)),reverse=True)
        for r in rows: self.del_row(r)

    def new_rows(self,rows=1):
        """Add blank rows to the top of the board."""
        if rows <= 0: return
        if len(self._board)+rows > self._max_rows: raise IndexError('row limit exceeded')
        self._board += [self._default_row() for _ in range(rows)]
        self._cow_list += [False]*rows
        self._profile = None

    def fill_max(self):
        """Add rows until the board is at its maximum size."""
        self.new_rows(self._max_rows-len(self._board))

    def check_rows(self,rows=None,full=None):
        """Check for full or empty rows. ('full' is None: empty/full (default), True: full, False: empty.)"""
        if rows is None: rows = range(len(self._board))
        if full is None: return tuple(r for r in rows if all(self._board[r]) or not any(self._board[r]))
        if full: return tuple(r for r in rows if all(self._board[r]))
        else: return tuple(r for r in rows if not any(self._board[r]))

    def pile_height(self):
        """Get the height of the pile, in terms of the top row of the board."""
        return self.get_dims()[0]

    #<<<<< ROW MANIPULATION


    #COPY-ON-WRITE >>>>>

    def get_cow(self):
        """Get a copy-on-write copy of the board."""
        new = copy.copy(self)
        new._board = list(self._board)
        new._cow_list = [True]*len(self._board)
        return new

    def get_clone(self):
        """Get a full (deep) copy of the board."""
        return copy.deepcopy(self)

    def uncow_rows(self,rows=None):
        """Replace copy-on-write rows with new rows."""
        if rows is None: rows = range(len(self._board))
        for r in rows:
            if self._cow_list[r]:
                self._board[r] = list(self._board[r])
                self._cow_list[r] = False

    def imprint_zoid(self,zoid,pos=None,value=None,orient=None,check=False):
        """Imprint a zoid on the board. Position specifies bottom left of zoid."""
        if not all((pos is None,value is None,orient is None)):
            zoid = zoid.get_copy()
            if pos is not None: zoid.set_pos(pos)
            if value is not None: zoid.set_value(value)
            if orient is not None: zoid.set_orient(orient)
        self.new_rows(rows=zoid.max_row()-len(self._board)+1)
        for r in zoid.rows():
            for c in zoid.cols():
                if zoid[r,c]:
                    if check and self[r,c]: raise ValueError('board cell not empty')
                    self[r,c] = zoid[r,c]

    def get_cow_mask(self):
        """Get copy-on-write mask of board rows."""
        return list(self._cow_list)

    #<<<<< COPY-ON-WRITE


    #HELPERS >>>>>

    def _default_row(self):
        return [0]*self._cols

    def _generate_profile(self):
        self._profile = tuple(_helpers._find_outline(self,True))

    #<<<<< HELPERS
