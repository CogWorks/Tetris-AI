#!/usr/bin/env python
import sys, random, time
from boards import *


class board_manager_cow(object):
    '''a class to manage board creation and temporary boards using
    copy-on-write and partial boards'''
    @staticmethod
    def new_board():
        '''create a new board'''
        if 'tetris_cow2' in globals():
            return tetris_cow2()
        else:
            return tetris_cow(max_rows2=20,cols=10)

    @staticmethod
    def copy_board_zoid(board,*args,**kwds):
        """create a copy of the board with a zoid"""
        zoid_board = board.get_cow()
        #'check': check for cell collisions
        zoid_board.imprint_zoid(*args,check=True,**kwds)
        return zoid_board

    @staticmethod
    def copy_board_hide(board):
        """create a copy of the board with rows hidden"""
        cleared_board = board.get_cow()
        cleared_board.check_full(True)
        return cleared_board

    @staticmethod
    def score_board(board,board2=None):
        """score the board (pile height only)"""
        if board2:
            return -board2.pile_height() - random.random()
        else:
            return -board.pile_height() - random.random()


#select the board manager
board_manager = board_manager_cow


if __name__ == '__main__':
    cleared_lines = 0

    # new 20x10 board (zero rows by default; use 'rows=n' to start with n writable rows)
    main_board = board_manager.new_board()

    # (print all of the zoids, just to make sure orientation works properly)
    for zoid_name,zoid in all_zoids.items():
        for orient in xrange(4):
            print >> sys.stderr, 'zoid "%s/%i":'%(zoid_name,orient)
            zoid = zoid.get_copy()
            zoid.set_orient(orient)
            print_board(zoid)

    #simulate a random game
    for _ in xrange(100):
        # get the profile of the top of the board
        # i.e, open cells below the top of the pile, per col
        board_profile = main_board.get_top_profile()


        # choose a random zoid
        zoid_name,zoid = random.choice(all_zoids.items())
        # copy it so its orientation can be changed (this is a shallow copy and
        # the zoid cells and profiles cached with 'get_bottom_profile' will be
        # shared among all copies)
        zoid = zoid.get_copy()

        print >> sys.stderr, 'you must now deal with "%s"!'%zoid_name

        # some hasty scoring nonsense...
        scores = []

        # check all of the orientations
        for orient in xrange(4):

            # set the zoid orientation for future steps
            zoid.set_orient(orient)

            # get the profile of the bottom of the zoid (# open cells above
            # the bottom of the zoid, per col)
            # note that this is cached in the original zoid for each orientation;
            # therefore, it's only computed once ever per zoid per orientation
            zoid_profile = zoid.get_bottom_profile()

            for c in main_board.cols():
                # don't check positions past the end of the board
                if c+zoid.col_count() > main_board.col_count():
                    break

                # determine how low the zoid rests relative to the top of
                # the pile
                heights = tuple(board_profile[c+cc]+zoid_profile[cc]
                        for cc in xrange(len(zoid_profile)))
                r = main_board.pile_height()-min(heights)

                # skip it if it will be too high up
                if r+zoid.row_count() > main_board.row_count():
                    continue

                # copy the board and imprint the zoid
                # 'pos' and 'value' are properties of the zoid that are
                # overridden when imprinting it
                # 'pos': position of the bottom left of the zoid's bounding box
                # 'value': value to multiply the cells by
                zoid_board = board_manager.copy_board_zoid(
                        main_board,zoid,pos=(r,c),value=2)

                # copy the imprinted board and remove full rows
                cleared_board = board_manager.copy_board_hide(zoid_board)

                # score the board
                score = board_manager.score_board(zoid_board,cleared_board)

                # record the score
                scores.append((score,orient,(r,c)))

        if not scores:
            raise RuntimeError('OMG you lost with %i lines'%cleared_lines)

        # determine the best move
        scores.sort(key=lambda x: x[0],reverse=True)
        best_move = scores[0]

        # imprint the zoid and clear rows if necessary
        main_board.imprint_zoid(zoid,orient=best_move[1],pos=best_move[2],
                check=True)
        # ('False' means full rows aren't cleared here; just counted)
        full_rows = main_board.check_full(False)
        cleared_lines += full_rows

        print >> sys.stderr, 'you placed "%s" at %s, clearing %i line(s)'%(zoid_name,best_move[2],full_rows)

        # print the board for fun
        print_board(main_board,entire=True,show_full=True)
        raw_input(main_board.get_top_profile())
        #time.sleep(0.1)

        # slow it down so it looks like a game
        # ('True' means full rows are cleared here)
        main_board.check_full(True)
        print_board(main_board,entire=True)
        time.sleep(0.1)
