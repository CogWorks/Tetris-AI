from simulator import TetrisSimulator
import sys
import os
import time

header = ["game_num"]
outputs = ["lines", "l1", "l2", "l3", "l4", "score", "level", "eps"]


def write_header(file_out):
    """
    Writes a header to a file.
    """
    outheader = header + outputs
    file_out.write("\t".join(outheader) + "\n")


def write_output(file_out, game_num, outs):
    """
    Writes a controller to a file
    """
    outlist = [str(game_num)]

    for o in outputs:
        if outs:
            outlist.append(str(outs[o]))
        else:
            outlist.append("")
    file_out.write("\t".join(outlist) + "\n")


def main():
    """
    Plays a given amount of games and outputs the scores and information to a given file
    usage: python playXgames.py <number of games> <output file> <starting game number (optional)>
    """
    controller = {"landing_height": -91.72377,
                  "eroded_cells": -161.2506,
                  "row_trans": -65.59098,
                  "col_trans": -206.4665,
                  "pits": -266.285,
                  "cuml_wells": -5.155716}

    outfile = open("runs/" + sys.argv[2] + ".incomplete.tsv", "w")
    write_header(outfile)

    starting_number = 0
    if len(sys.argv) == 4:
        starting_number = int(sys.argv[3])
    for g in range(starting_number, starting_number + int(sys.argv[1])):
        test_name = "G" + str(g)
        test_sim = TetrisSimulator(controller=controller,
                                   show_result=True,
                                   show_choice=False,
                                   choice_step=500,
                                   name=test_name,
                                   seed=time.time(),
                                   overhangs=True)
        test_res = test_sim.run()
        write_output(outfile, g, test_res)

    outfile.close()
    os.rename("runs/" + sys.argv[2] + ".incomplete.tsv", "runs/" + sys.argv[2] + ".tsv")


if __name__ == '__main__':
    main()
