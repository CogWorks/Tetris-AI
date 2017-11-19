import sys, platform
if platform.system() == 'Linux':
    sys.path.insert(1,"lib/lib.linux-x86_64-2.7")
elif platform.system() == 'Darwin':
    sys.path.insert(1,"lib/lib.macosx-10.10-x86_64-2.7")
from tetris_cpp import *
from boards import all_zoids
from simulator import TetrisSimulator


def get_features(board, zoid_str, controller, dictionaries=True):
    """ Given a board (with list of list representation), future zoid,
    and controller, this function returns the set of all possible options
    and their feature values.

    Params:
    board - [[int]] - list of list representation of board
    zoid_str - string - string value for a zoid (e.g. "T")
    controller - {string: int} - dictionary controller for a simulator

    If dictionaries=True then it will return it as a series of nested
    dictionaries organized as:
        return_val[orientation][row][col] = {zoid: '', board: [[]], features: {}}
    If dictionaries=False then it will return it as a list of dictionaries,
    with one dictionary for each option/feature set:
        return_val = [{'zoid': zoid, 'orient': orientation, 'row': row,
                        'col': col, 'board': [[]], 'features': {}}]
    """

    sim = TetrisSimulator(controller=controller)
    sim.space = tetris_cow2.convert_old_board(board)
    sim.curr_z = all_zoids[zoid_str]

    if dictionaries == True:
        # Return all features as an organized dictionary structure
        all_feats = {}
        for orient, pos in sim.get_options():
            if orient not in all_feats.keys():
                all_feats[orient] = {}
            if pos[0] not in all_feats[orient].keys():
                all_feats[orient][pos[0]] = {}
            zoid = sim.curr_z.get_copy()
            board = sim.space.get_cow()
            # Not really sure what the value=2 does, but was used in simulator.py
            board.imprint_zoid(zoid, orient=orient, pos=pos, value=2)
            board_and_feats = {'zoid': zoid_str, 'board': board.row_space(), 'features': sim.get_features(board, sim.space)}
            all_feats[orient][pos[0]][pos[1]] = board_and_feats
        return all_feats
    else:
        all_feats = []
        for orient, pos in sim.get_options():
            option = {}
            zoid = sim.curr_z.get_copy()
            option['zoid'] = zoid_str
            option['row'] = pos[0]
            option['col'] = pos[1]
            option['orient'] = orient
            board = sim.space.get_cow()
            board.imprint_zoid(zoid, orient=orient, pos=pos, value=2)
            option['board'] = board.row_space()
            option['features'] = sim.get_features(board, sim.space)
            all_feats.append(option)
        return all_feats

def pretty_print_features(board, zoid, controller):
    feats = get_features(board, zoid, controller, dictionaries=False)
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

# board = [[0]*10 for i in range(20)]
# controller1 = {"landing_height": -1,
#                "eroded_cells": 1,
#                "row_trans": -1,
#                "col_trans": -1,
#                "pits": -4,
#                "cuml_wells": -1}
# a = get_features(board, 'L', controller1)
