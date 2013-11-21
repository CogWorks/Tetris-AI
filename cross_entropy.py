from simulator import TetrisSimulator

#staring from Dellacherie model
start_controller = [["landing_height",-1],
                ["eroded_cells",1],
                ["row_trans",-1],
                ["col_trans",-1],
                ["pits",-4],
                ["cuml_wells",-1]]
				
sim_test = TetrisSimulator(controller = controller)
sim_test.run()