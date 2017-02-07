import platform, sys
if platform.system() == 'Linux':
    sys.path.insert(1,"lib/lib.linux-x86_64-2.7")
elif platform.system() == 'Darwin':
    sys.path.insert(1,"lib/lib.macosx-10.10-x86_64-2.7")
from tetris_cpp import *
from boards import print_board, all_zoids
import time, random
from simulator import TetrisSimulator

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
[0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]

controller = {"landing_height": -1,
               "eroded_cells": 1,
               "row_trans": -1,
               "col_trans": -1,
               "pits": -4,
               "cuml_wells": -1}

board = tetris_cow2.convert_old_board(boardRaw)

osim = TetrisSimulator(
    controller=controller,
    board=board,
    curr=all_zoids["J"],
    next=all_zoids["S"],
    show_choice=True,
    show_scores=True,
    show_options=True,
    option_step=.3,
    choice_step=1,
    seed=1
)

print "pre space"
for row in osim.space.row_space():
    print row
print

print "poss_moves"
print [(o, (r, c)) for (o, (r, c)) in osim.possible_moves() if c > 5]
print

print "overhangs"
print osim.get_overhangs()
print

print "overhang moves"
print [(o, (r, c)) for (o, (r,c)) in osim.possible_moves_overhangs() if c > 5]
print

for move in [m for m in osim.possible_moves_overhangs() if m not in osim.possible_moves()]:
    print "testing", move
    osim.space.imprint_zoid(osim.curr_z, orient=move[0], pos=move[1], value=2)
    for row in osim.space.row_space():
        print row
    print
    osim.space = tetris_cow2.convert_old_board(boardRaw)
