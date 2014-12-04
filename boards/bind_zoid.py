import copy


class bind_zoid(object):
    """Bind a Tetris zoid to a Tetris board, without modifying the board."""
    def __init__(self,board,zoid,pos=None,value=None,orient=None,hide=False):
        self._board = board
        self._zoid = copy.copy(zoid)
        if pos is not None: self._zoid.set_pos(pos)
        if value is not None: self._zoid.set_value(value)
        if orient is not None: self._zoid.set_orient(orient)
        self._hide = hide
        self._rows = None
        self._hide_rows()


    #ELEMENT ACCESS >>>>>

    def get_dims(self,max=False,*args,**kwds):
        """Get board dimensions (use 'max=True' for max size)."""
        r,c = self._board.get_dims(max=max,*args,**kwds)
        return (r,c) if max or not self._hide else (sum(r >= 0 for r in self._rows),c)

    def rows(self,all=False,*args,**kwds):
        """Get a generator for the rows of the zoid in its current position and orientation. Optional: reverse order for printing."""
        return (r for r in self._board.rows(all=all,*args,**kwds) if (all or not self._hide) or self._rows[r] >= 0)

    def cols(self,*args,**kwds):
        """Get a generator for the cols of the zoid in its current position and orientation."""
        return self._board.cols(*args,**kwds)

    def pile_height(self):
        """Get the height of the pile, in terms of the top row of the board."""
        return self.get_dims()[0]

    def __getitem__(self,(row,col)):
        """Get a cell value (row first), e.g., 'myboard[0,0]'."""
        if self._hide:
            row = self._rows[row]
            if not (0 <= col < self.get_dims()[1]): raise IndexError('index out of range')
            if row < 0: return 0
        return self._actual_item(row,col)

    def __setitem__(self,(row,col),value):
        """Set a cell value (row first), e.g., 'myboard[0,0] = 1'."""
        if self._hide: raise AttributeError('cannot write with hidden rows')
        self._board[row,col] = value
        return value

    #<<<<< ELEMENT ACCESS


    #ZOID MANIPULATION >>>>>

    def set_value(self,value):
        """Set zoid value."""
        self._zoid.set_value(value)
        self._hide_rows()

    def get_value(self):
        """get zoid value."""
        return self._zoid.get_value()

    def set_pos(self,pos):
        """Set zoid position."""
        self._zoid.set_pos(pos)
        self._hide_rows()

    def get_pos(self):
        """Get zoid position."""
        return self._zoid.get_pos()

    def set_orient(self,orient):
        """Set zoid orientation."""
        self._zoid.set_orient(orient)

    def get_orient(self):
        """Get zoid orientation."""
        return self._zoid.get_orient()

    def imprint_zoid(self,pos=None,value=None,orient=None):
        """Imprint the zoid onto the underlying board."""
        if self._hide: raise AttributeError('cannot imprint with hidden rows')
        if pos is not None: self._zoid.set_pos(pos)
        if value is not None: self._zoid.set_value(value)
        if orient is not None: self._zoid.set_orient(orient)
        self._board.imprint_zoid(self._zoid)

    #<<<<< ZOID MANIPULATION


    #ROW HIDING >>>>>

    def set_hide(self,hide):
        """Set hiding state of full rows. Board cannot be modified while rows are hidden!"""
        self._hide = hide
        self._hide_rows()

    def get_hide(self):
        """Get hiding state of full rows. Board cannot be modified while rows are hidden!"""
        return self._hide

    def get_shown_rows(self):
        """Get a tuple of rows row numbers that are not hidden."""
        return tuple(r for r in self._rows if r >= 0) if self._hide else range(self.get_dims()[0])

    def get_hidden_rows(self):
        """Get a tuple of rows row numbers that are hidden."""
        return tuple(sorted(set(range(self.get_dims()[0]))-set(self.get_shown_rows())))

    #<<<<< ROW HIDING


    #HELPERS >>>>>

    def _actual_item(self,row,col):
        """Get the cell value from the board without accounting for hidden rows."""
        return max(self._board[row,col],self._zoid[row,col])

    def _hide_rows(self):
        """Mark rows as hidden if they are full."""
        self._rows = []
        count = 0
        for r in xrange(self._board.get_dims()[0]):
            if not all(self._actual_item(r,c) for c in xrange(self._board.get_dims()[1])): self._rows.append(r)
        self._rows = tuple(self._rows+[-1]*(self._board.get_dims(max=True)[0]-len(self._rows)))

    #<<<<< HELPERS
