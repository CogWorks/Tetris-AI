import subprocess

command = "python cross_entropy.py -d 64 -op score -c 200 -rt linear -rtp 0 -cou 0.0 -dr 0.15 -ip 100 -e 600 -f landing_height eroded_cells row_trans col_trans pits cuml_wells deep_wells max_well cuml_cleared pit_depth pit_rows tetris -gcw -18.594110 -49.89329 -19.93395 -56.59616 -55.51307 -7.937560 -0.2377499 78.28183 -3.5911434 -5.924762 1.182153 28.57080 -gcv 17.29559 34.16077 10.54538 28.83381 32.28161 7.527053 13.9974 19.67477 20.71313 8.146976 32.3329 20.97502"

subprocess.call(command,shell=True)
