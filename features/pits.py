
import sys
sys.path.append("..")
from boards import *


def get_all_pits(board):
        #return values
        col_pits = []
        pit_rows = [] 
        lumped_pits = 0
        
        #for each column in the board
        for c in board._cols:
            pits, lumped = get_pits(c)
            lumped_pits += lumped
            col_pits.append(len(pits))
            for j in pits:
                if j not in pit_rows:
                    pit_rows.append(j)
        return(col_pits, pit_rows, lumped_pits)
    ###

def get_pits(col):
        
        state = v[0]
        pits = 0
        lumped_pits = 0
        curr_pit = 0
        rows = []
        row = 18
        for i in v[1:]:
            if i != 0:
                state = 1
                curr_pit = 0 #lumped pit ends.
            if i == 0 and state == 1:   #top detected and found a pit
                if curr_pit == 0:    #we hadn't seen a pit yet
                    lumped_pits += 1    #so this is a new lumped pit
                curr_pit = 1
                pits += 1
                rows.append(row)
            row -= 1
        return rows, lumped_pits
    ###



if __name__ == '__main__':
    #board = tetris_cow()
    
    boardrows = [
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,1,0,0,0,0,0,0,0,0],
                    [0,1,0,0,0,1,0,0,0,0],
                    [0,1,1,1,0,1,0,0,0,0],
                    [1,1,1,0,1,1,1,1,0,0]
                ]
    
    board = tetris_cow.convert_old_board(boardrows)
    print_board(board, all=True)
    
    
    for cell in board.col_iter(0): print cell, #iterate cells in column 0 of the board
    for cell in board.col_iter(0,reverse=True): print cell, #...from top to bottom
    
    
    #print get_all_pits(board)
    
    
    
