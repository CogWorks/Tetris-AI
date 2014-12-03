#!/usr/bin/env python

import sys, random

from boards import *


#put board creation in one place so it can be globally changed
def new_board(*args,**kwds): return tetris_cow(*args,**kwds)

#pretend to score the board
def score_board(board,board2=None):
    return -(board2.pile_height() if board2 else board.pile_height())


if __name__ == '__main__':
    cleared_lines = 0

    #new 20x10 board (zero rows by default; use 'rows=n' to start with n writable rows)
    main_board = new_board(max_rows=20,cols=10)

    #simulate a random game
    for _ in xrange(100):
        #get the profile of the top of the board (# open cells below the top of the pile, per col)
        board_profile = main_board.get_top_profile()

        #choose a random zoid
        #copy it so its orientation can be changed (this is a shallow copy and
        #the zoid cells and profiles cached with 'get_bottom_profile' will be
        #shared among all copies)
        zoid_name,zoid = random.choice(all_zoids.items())
        zoid = zoid.get_copy()

        print >> sys.stderr, 'you must now deal with "%s"!'%zoid_name

        #some hasty scoring nonsense...
        scores = {}

        #check all of the orientations
        for orient in xrange(4):

            #set the zoid orientation for future steps
            zoid.set_orient(orient)

            #get the profile of the bottom of the zoid (# open cells above the bottom of the zoid, per col)
            #note that this is cached in the original zoid for each orientation;
            #therefore, it's only computed once ever per zoid per orientation
            zoid_profile = zoid.get_bottom_profile()

            for c in main_board.cols():
                #don't check positions past the end of the board
                if c+zoid.get_dims()[1] > main_board.get_dims()[1]: break

                #determine how low the zoid rests relative to the top of the pile
                heights = tuple(board_profile[cc+c]+zoid_profile[cc] for cc in zoid.cols())
                r = main_board.pile_height()-min(heights)

                #skip it if it will be too high up
                if r+zoid.get_dims()[0] > main_board.get_dims(max=True)[0]: continue

                #copy the board and imprint the zoid
                #'pos' and 'value' are properties of the zoid that are overridden when imprinting it
                #'pos': position of the bottom left of the zoid's bounding box
                #'value': value to multiply the cells by
                #'check': make sure the zoid doesn't overlap with the pile
                zoid_board = main_board.get_cow()
                zoid_board.imprint_zoid(zoid,pos=(r,c),value=2,check=True)

                #copy the imprinted board and remove full rows
                cleared_board = zoid_board.get_cow()
                cleared_board.del_rows(cleared_board.check_rows(full=True))

                #pretend to score the board
                score = score_board(zoid_board,cleared_board)

                #record the score
                scores[orient,(r,c)] = score

        if not scores: raise RuntimeError('OMG you lost with %i lines'%cleared_lines)

        #determine the best move
        scores = sorted(scores.items(),key=lambda x: x[1],reverse=True)
        best_move = scores[0]

        #imprint the zoid and clear rows if necessary
        main_board.imprint_zoid(zoid,pos=best_move[0][1],orient=best_move[0][0],check=True)
        full_rows = main_board.check_rows(full=True)
        cleared_lines += len(full_rows)
        main_board.del_rows(full_rows)

        print >> sys.stderr, 'you placed "%s" at %s, clearing %i line(s)'%(zoid_name,best_move[0][1],len(full_rows))

        #print the board for fun
        print_board(main_board,all=True)
