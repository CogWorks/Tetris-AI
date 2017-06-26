import subprocess

command = "python cross_entropy.py -d 120 -op score -c 100 -rt linear -rtp 0 -dr 0 -ip 0 -e 600 -f landing_height eroded_cells row_trans col_trans pits cuml_wells deep_wells max_well cuml_cleared pit_depth pit_rows tetris"

subprocess.call(command,shell=True)
