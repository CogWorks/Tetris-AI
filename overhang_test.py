import logging
import platform
import sys
import unittest
if platform.system() == 'Linux':
    sys.path.insert(1, "lib/lib.linux-x86_64-2.7")
elif platform.system() == 'Darwin':
    sys.path.insert(1, "lib/lib.macosx-10.10-x86_64-2.7")
from tetris_cpp import *
from boards import print_board, all_zoids
from boards._helpers import fill_board_with_zeros
from simulator import TetrisSimulator


class OverhangTest(unittest.TestCase):
    """
    Contains a suite of tests to test the simulator overhang functionality
    """

    def test_perfect_fit(self):
        """
        Tests if a single overhang move option is correctly identified
        :return: None
        """
        raw_board = [[1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
                     [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
                     [1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
                     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
        board = tetris_cow2.convert_old_board(fill_board_with_zeros(raw_board))
        sim = TetrisSimulator(curr=all_zoids["T"], board=board, overhangs=True)

        # ensure simulator correctly identifies overhang spaces
        self.assertDictEqual({3: [2], 6: [2]}, sim.get_overhangs())

        # ensure additional overhang moves are present
        sim_overhangs = set(sim.possible_moves_overhangs()) - set(sim.possible_moves())
        self.assertSetEqual({(1, (1, 3)), (3, (1, 5))}, sim_overhangs)

    def test_edges(self):
        """
        Tests when an overhang is next to an edge of the board
        :return: None
        """
        raw_board = [[1, 1, 1]]




def display_board(board_to_print):
    board2 = map((lambda a: map((lambda b: ' ' if b == 0 else str(b)), a)), board_to_print)
    print '_'*12
    for i in board2:
        print '|' + ''.join(i) + '|'
    print '+'*12


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(OverhangTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
    # test = OverhangTest()
    # test.test_perfect_fit()

#
# print "Overhangs:", osim.overhangs
# print "pre space"
# display_board(osim.space.row_space())
# print
#
# print "poss_moves"
# test_moves = [(o, (r, c)) for (o, (r, c)) in osim.possible_moves()]
# print test_moves
# print
#
# print "overhangs"
# print osim.get_overhangs()
# print
#
# print "overhang moves"
# print [(o, (r, c)) for (o, (r, c)) in (set(osim.possible_moves_overhangs()) - set(osim.possible_moves()))]
# print
#
# for move in [m for m in osim.possible_moves_overhangs() if m not in osim.possible_moves()]:
#     print "testing", move
#     osim.space.imprint_zoid(osim.curr_z, orient=move[0], pos=move[1], value=2)
#     display_board(osim.space.row_space())
#     print
#     osim.space = tetris_cow2.convert_old_board(boardRaw)  # revert to original board
