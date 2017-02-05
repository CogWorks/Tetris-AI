import platform, sys
if platform.system() == 'Linux':
    sys.path.insert(1,"lib/lib.linux-x86_64-2.7")
elif platform.system() == 'Darwin':
    sys.path.insert(1,"lib/lib.macosx-10.10-x86_64-2.7")
from tetris_cpp import *
from boards import print_board, all_zoids
import time, random
from simulator import TetrisSimulator

# class testSim(object):
#     def __init__(self, board):
#         ''' board = tetris_cow2
#         '''
#         self.space = board
#
#     def get_overhangs(self):
#         overhangs = {}
#         for c, c_val in enumerate(self.space.col_space()):
#             top = False
#             for r, r_val in enumerate(c_val):
#                 if (not top) and r_val != 0:
#                     top = True
#                 if top and r_val == 0:
#                     if c in overhangs:
#                         # iterating from top down, so reverse r with 19-r
#                         overhangs[c].append(len(c_val)-1-r)
#                     else:
#                         overhangs[c] = [len(c_val)-1-r]
#         return overhangs



boardRaw = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
[1, 1, 0, 0, 0, 0, 0, 1, 0, 0],
[1, 0, 0, 0, 0, 0, 0, 1, 0, 0]]

board = tetris_cow2.convert_old_board(boardRaw)
for row in board.row_space():
    print row
# test = TetrisSimulator(board)
# print "\n\n", test.get_overhangs()

controller = {"landing_height": -1,
               "eroded_cells": 1,
               "row_trans": -1,
               "col_trans": -1,
               "pits": -4,
               "cuml_wells": -1}

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

print
heights = tuple(osim.get_height(col) for col in
                osim.space.col_space())
osim.curr_z.set_orient(1)
print heights
print
print heights[1:1+osim.curr_z.col_count()]

print osim.get_options()
osim.space.imprint_zoid(osim.curr_z, orient=1, pos=(0,2))
print
for row in osim.space.row_space():
    print row
# scores = {x: self.control(*x) for x in self.options}
# best_moves = tuple(k for k, v in scores.items()
#                    if v == max(scores.values()))
# print
# print osim.sequence
