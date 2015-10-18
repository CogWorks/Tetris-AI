from _tetris_cpp import *


class tetris_cow2(tetris_20_10):
    """Copy-on-write Tetris board."""
    def __init__(self,max_rows=20,cols=10,rows=0):
        """Initialize board: number of cols, max number of rows, initial
        number of rows."""
        if max_rows != 20 or cols != 10:
            raise ValueError('this class can only be used with 20x10 boards')
        tetris_20_10.__init__(self,rows)
        self._profile = None

    def __len__(self):
        try:
            return self.row_count()
        except:
            raise Exception("tetris_cow2.__len__(self) is broken")

    def __iter__(self):
        for i in xrange(self.row_count()):
            yield (c for c in self.row_iter(i))

    '''
    def __getitem__(self, i, j=None):
        if j == None:
            return [x for x in self.row_iter(i)]
        else:
            return self[i,j]
    '''

    @staticmethod
    def convert_old_board(board,clear=True):
        """Create a new board from a "list-of-rows" board."""
        all_cols = tuple(len(row) for row in board)
        if len(all_cols) == 20:
            if max(all_cols) != min(all_cols):
                raise ValueError('rows are not all the same length')
            if max(all_cols) != 10:
                raise ValueError('rows must all be of length 10')
            cols = all_cols[0]
        else:
            raise ValueError('board must contain 20 rows')
        new_board = tetris_cow2(rows=20)
        for r in new_board.rows():
            for c in new_board.cols():
                new_board[r,c] = board[len(board)-r-1][c]
        if clear: new_board.check_empty(True)
        return new_board

    #ELEMENT ACCESS >>>>>

    def rows(self,reverse=False,all=False):
        """Get a generator for the rows of the zoid in its current position
        and orientation. Optional: reverse order."""
        count = self.row_count() if all else self.pile_height()
        return xrange(count-1,-1,-1) if reverse else xrange(count)

    def cols(self):
        """Get a generator for the cols of the zoid in its current position
        and orientation."""
        return xrange(self.col_count())

    def row_iter(self,row,*args,**kwds):
        """Iterate a particular row of cells. (Generates cell values.)"""
        for col in self.cols(*args,**kwds):
            yield self[row,col]

    def col_iter(self,col,*args,**kwds):
        """Iterate a particular col of cells. (Generates cell values.)"""
        for row in self.rows(*args,**kwds):
            yield self[row,col]

    def get_top_profile(self):
        """Get the profile of the top of the board."""
        # NOTE: 'get_tamper_seal' is managed by 'tetris_20_10'; when the board
        # is modified, it unsets the seal
        if not self.get_tamper_seal():
            self._generate_profile()
            self.set_tamper_seal()
        return self._profile

    #<<<<< ELEMENT ACCESS


    # ROW MANIPULATION >>>>>

    def fill_max(self):
        """Add rows until the board is at its maximum size."""
        self.add_rows(self.row_count()-self.pile_height())

    #<<<<< ROW MANIPULATION


    # COPY-ON-WRITE >>>>>

    def get_cow(self):
        """Get a copy-on-write copy of the board."""
        new = type(self)()
        new.mirror(self)
        return new

    def get_clone(self):
        """Get a deep copy of the board."""
        new = self.get_cow()
        new.uncow_all()
        return new

    def imprint_zoid(self,zoid,pos=None,value=None,orient=None,check=False):
        """Imprint a zoid on the board. Position specifies bottom left of zoid.
        pos=(i,j)"""
        if not all((pos is None,value is None,orient is None)):
            zoid = zoid.get_copy()
            if pos is not None:
                zoid.set_pos(pos)
            if value is not None:
                zoid.set_value(value)
            if orient is not None:
                zoid.set_orient(orient)
        self.add_rows(zoid.max_row()-self.pile_height()+1)
        for r in zoid.rows():
            for c in zoid.cols():
                if zoid[r,c]:
                    if check and self[r,c]:
                        raise ValueError('board cell not empty')
                    self[r,c] = zoid[r,c]

    #<<<<< COPY-ON-WRITE


    #HELPERS >>>>>

    def _generate_profile(self):
        counts = [0]*self.col_count()
        for c in self.cols():
            for cell in self.col_iter(c,reverse=True):
                if not cell:
                    counts[c] = 1
                else:
                    break
        self._profile = tuple(counts)

    #<<<<< HELPERS
