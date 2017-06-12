import subprocess

command = "python cross_entropy.py -op score -c 200 -rt step -rtp 0 -dr 0.2 -ip 3 -e 500 -f landing_height eroded_cells row_trans col_trans pits cuml_wells mean_ht max_ht min_ht all_ht max_ht_diff min_ht_diff cleared deep_wells max_well cuml_cleared cuml_eroded pit_depth pit_rows column_9 tetris"

subprocess.call(command,shell=True)
