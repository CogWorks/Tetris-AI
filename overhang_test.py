import platform
import sys
if platform.system() == 'Linux':
    sys.path.insert(1, "lib/lib.linux-x86_64-2.7")
elif platform.system() == 'Darwin':
    sys.path.insert(1, "lib/lib.macosx-10.10-x86_64-2.7")
from tetris_cpp import *
from boards import print_board, all_zoids
from simulator import TetrisSimulator


def display_board(board_to_print):
    board2 = map((lambda a: map((lambda b: ' ' if b == 0 else str(b)), a)), board_to_print)
    print '_'*12
    for i in board2:
        print '|' + ''.join(i) + '|'
    print '+'*12


raw_input("Press Enter to Continue (attach debugger here if desired):")

boardRaw = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 0, 0, 1, 1, 1],
            [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
            [1, 1, 1, 1, 0, 0, 0, 1, 1, 1]]

controller = {"landing_height": -12.63,
              "eroded_cells": 6.60,
              "row_trans": -9.22,
              "col_trans": -19.77,
              "pits": -13.08,
              "cuml_wells": -10.49,
              "pit_depth": -1.61,
              "pit_rows": -24.04}

board = tetris_cow2.convert_old_board(boardRaw)

osim = TetrisSimulator(
    controller=controller,
    board=board,
    curr=all_zoids["T"],
    next=all_zoids["S"],
    show_choice=True,
    show_scores=True,
    show_options=True,
    overhangs=True,
    option_step=.3,
    choice_step=1,
    seed=1
)

print "Overhangs:", osim.overhangs
print "pre space"
display_board(osim.space.row_space())
print

print "poss_moves"
test_moves = [(o, (r, c)) for (o, (r, c)) in osim.possible_moves()]
print test_moves
print

print "overhangs"
print osim.get_overhangs()
print

print "overhang moves"
print [(o, (r, c)) for (o, (r, c)) in (set(osim.possible_moves_overhangs()) - set(osim.possible_moves()))]
print

for move in [m for m in osim.possible_moves_overhangs() if m not in osim.possible_moves()]:
    print "testing", move
    osim.space.imprint_zoid(osim.curr_z, orient=move[0], pos=move[1], value=2)
    display_board(osim.space.row_space())
    print
    osim.space = tetris_cow2.convert_old_board(boardRaw)  # revert to original board
