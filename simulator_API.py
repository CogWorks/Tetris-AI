import sys, platform
if platform.system() == 'Linux':
    sys.path.insert(1,"lib/lib.linux-x86_64-2.7")
elif platform.system() == 'Darwin':
    sys.path.insert(1,"lib/lib.macosx-10.10-x86_64-2.7")
from tetris_cpp import *
from boards import all_zoids
from simulator import TetrisSimulator


## UNTESTED - Predict function - given a board and a zoid and a controller, returns best placement as determined by the controller

# def predict(space, zoid, controller):
#         sim = TetrisSimulator(controller = controller)
#         sim.space = sim.convert_space(space)
#         sim.curr_z = zoid
#
#         sim.get_options()
#         return sim.control()



def get_features(board, zoid, controller):
    sim = TetrisSimulator(controller=controller)
    sim.space = tetris_cow2.convert_old_board(board)
    sim.curr_z = zoid

    all_options_and_features = []
    for orient, pos in sim.get_options():
        option = {}
        zoid = sim.curr_z.get_copy()
        option['zoid'] = zoid
        option['row'] = pos[0]
        option['col'] = pos[1]
        option['orient'] = orient
        board = sim.space.get_cow()
        board.imprint_zoid(zoid, orient=orient, pos=pos, value=2)
        option['board'] = sim.space
        option['features'] = sim.get_features(board, sim.space)
        all_options_and_features.append(option)
    return all_options_and_features

def pretty_print_features(board, zoid, controller):
    feats = get_features(board, zoid, controller)
    for f in feats:
        print "Current Zoid:", f['zoid']
        print "Row:", f['row']
        print "Col:", f['col']
        print "Orientation:", f['orient']
        print "Board:", f['board']
        print "Features:"
        for lf in f['features']:
            print "  ", lf, ":", f['features'][lf]
        print

board = [[0]*10 for i in range(20)]
test_zoid = all_zoids['L']
controller1 = {"landing_height": -1,
               "eroded_cells": 1,
               "row_trans": -1,
               "col_trans": -1,
               "pits": -4,
               "cuml_wells": -1}
pretty_print_features(board, test_zoid, controller1)
