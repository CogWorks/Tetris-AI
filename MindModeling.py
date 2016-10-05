### MindModeling.py
# Contains functions that allow MindModeling system to run Tetris games

from simulator import TetrisSimulator

### CUT OUT OF SIMULATOR.PY - may be alterate dependencies that need to work - check before using again

def mm_test(landing_height, eroded_cells, row_trans, col_trans, pits, cuml_wells, pit_depth, pit_rows):

    controller = {
        "landing_height": landing_height,
        "eroded_cells": eroded_cells,
        "row_trans": row_trans,
        "col_trans": col_trans,
        "pits": pits,
        "cuml_wells":cuml_wells,
        "pit_depth": pit_depth,
        "pit_rows": pit_rows
    }

    osim = TetrisSimulator(
        controller=controller,
            board=tetris_cow2(),
            curr=all_zoids["L"],
            next=all_zoids["S"],
            show_choice=False,
            show_scores=False,
            show_options=False,
            show_result=False,
            seed=1
    )

    return osim.run()


if __name__ == "__main__":
    print mm_test(1,1,1,1,1,1,1,1)

def mm_test2(landing_height, eroded_cells, row_trans, col_trans, pits, cuml_wells, pit_depth, pit_rows, max_eps):

    controller = {
        "landing_height": landing_height,
        "eroded_cells": eroded_cells,
        "row_trans": row_trans,
        "col_trans": col_trans,
        "pits": pits,
        "cuml_wells":cuml_wells,
        "pit_depth": pit_depth,
        "pit_rows": pit_rows
    }

    osim = TetrisSimulator(
        controller=controller,
            board=tetris_cow2(),
            curr=all_zoids["L"],
            next=all_zoids["S"],
            show_choice=False,
            show_scores=False,
            show_options=False,
            show_result=False,
            seed=1
    )

    return osim.run(max_eps = max_eps)
    
if __name__ == "__main__":
    print mm_test2(1,1,1,1,1,1,1,1)