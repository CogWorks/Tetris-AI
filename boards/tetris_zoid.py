import copy

import _helpers


class tetris_zoid(object):
    """Tetris zoid object, for use with 'tetris_cow'."""
    def __init__(self,values,dims,pos=(0,0),value=1,orient=0):
        """Initialize zoid: pass 2d array of values, dims of array, and orientation."""

        #shared among copies
        self._values = [tuple(values[len(values)-r-1] for r in range(len(values)))]+[None]*3
        self._dims = dims
        self._profiles = [None]*4

        #stored per copy
        self._value = value
        self._pos = pos
        self._orient = orient


    #ZOID MANIPULATION >>>>>

    def set_value(self,value):
        """Value: constant multiple for zoid cells when using []."""
        self._value = value

    def get_value(self):
        """Value: constant multiple for zoid cells when using []."""
        return self._value

    def set_pos(self,pos):
        """Position: board position of bottom left cell of the zoid."""
        self._pos = pos

    def get_pos(self):
        """Position: board position of bottom left cell of the zoid."""
        return self._pos

    def set_orient(self,orient):
        """Orientation: 90deg clockwise per increment."""
        self._orient = orient

    def get_orient(self):
        """Orientation: 90deg clockwise per increment."""
        return self._orient

    #<<<<< ZOID MANIPULATION


    #ELEMENT ACCESS >>>>>

    def __getitem__(self,(row,col)):
        """Get a cell value (row first), e.g., 'myzoid[0,0]'."""

        if not self._values[self._orient]: self._generate_orientation()

        row -= self._pos[0]
        col -= self._pos[1]

        if not (0 <= row < self.row_count()): return 0
        if not (0 <= col < self.col_count()): return 0

        return self._value*self._values[self._orient][row][col]

    def get_dims(self,orient=None):
        """Get zoid dimensions for current orientation. Optional: provide orientation."""
        return (self.row_count(),self.col_count())

    def row_count(self):
        """Get the number of rows in the zoid."""
        return self._dims[1] if self._orient%2 else self._dims[0]

    def col_count(self):
        """Get the number of columns in the zoid."""
        return self._dims[0] if self._orient%2 else self._dims[1]

    def rows(self,reverse=False,absolute=True):
        """Get a generator for the rows of the zoid in its current position and orientation. Optional: reverse order for printing."""
        offset = self._pos[0] if absolute else 0
        return xrange(self.row_count()+offset-1,-1,-1) if reverse else xrange(self.row_count()+offset)

    def cols(self,absolute=True):
        """Get a generator for the cols of the zoid in its current position and orientation."""
        return xrange(self.col_count()+(self._pos[1] if absolute else 0))

    def row_iter(self,row,*args,**kwds):
        """Iterate a particular row of cells. (Generates cell indices.)"""
        for col in self.cols(*args,**kwds): yield self[row,col]

    def col_iter(self,col,*args,**kwds):
        """Iterate a particular col of cells. (Generates cell indices.)"""
        for row in self.rows(*args,**kwds): yield self[row,col]

    def max_row(self):
        """Get the row number of the top of the zoid in its current position and orientation."""
        return self._pos[0]+self.row_count()-1

    def get_bottom_profile(self):
        """Get the profile of the bottom of the zoid."""
        if not self._profiles[self._orient]: self._generate_profile()
        return self._profiles[self._orient]

    #<<<<< ELEMENT ACCESS


    #COPYING >>>>>

    def get_copy(self):
        """Get a shallow copy of the zoid."""
        return copy.copy(self)

    #<<<<< COPYING


    #HELPERS >>>>>

    def _generate_profile(self):
        self._profiles[self._orient] = tuple(_helpers._find_outline(self,False))

    def _generate_orientation(self):
        if not self._values[0]: raise AttributeError('original zoid orientation not defined')

        cells = [[0]*self.col_count() for _ in xrange(self.row_count())]

        for r in self.rows():
            for c in self.cols():
                row,col = r,c

                if self._orient == 0: pass
                elif self._orient == 1: #90deg clockwise
                    row,col = col,self._dims[1]-row-1
                elif self._orient == 2: #180deg
                    row,col = self._dims[0]-row-1,self._dims[1]-col-1
                elif self._orient == 3: #270deg clockwise
                    row,col = self._dims[0]-col-1,row
                else: raise IndexError

                cells[r][c] = self._values[0][row][col]

        self._values[self._orient] = tuple(tuple(x) for x in cells)


    #<<<<< HELPERS


all_zoids = {
    'I': tetris_zoid(((1,1,1,1),),(1,4)),

    'T': tetris_zoid(((1,1,1),
                      (0,1,0)),(2,3)),

    'L': tetris_zoid(((1,1,1),
                      (1,0,0)),(2,3)),

    'J': tetris_zoid(((1,1,1),
                      (0,0,1)),(2,3)),

    'O': tetris_zoid(((1,1),
                      (1,1)),(2,2)),

    'Z': tetris_zoid(((1,1,0),
                      (0,1,1)),(2,3)),

    'S': tetris_zoid(((0,1,1),
                      (1,1,0)),(2,3)) }
