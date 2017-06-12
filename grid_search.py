#a program to expedite the process of trying different annealing schemes and parameter values
import numpy as np
import argparse
import subprocess
from cross_entropy import *

if __name__ == "__main__":

	parser = argparse.ArgumentParser( formatter_class = argparse.ArgumentDefaultsHelpFormatter )
	#The user will indicate the type of regularization they want to perform, as well as the upper and lower limits of the two parameters, update_value and initial_penalty. The user also indicates
	#how finely they wish to divide the interval given
	#May try to improve short form of command line flags
	
	parser.add_argument( '-mip', '--max_initial_penalty',
                        action = "store", dest = "max_initial_penalty",
                        type = float, default = 0,
                        help = "Upper limit of initial penalty.")
	parser.add_argument( '-nip', '--min_initial_penalty',
                        action = "store", dest = "min_initial_penalty",
                        type = float, default = 0,
                        help = "Lower limit of initial penalty.")
	parser.add_argument( '-muv', '--max_update_value',
                        action = "store", dest = "max_update_value",
                        type = float, default = 0,
                        help = "Upper limit of update value.")
	parser.add_argument( '-nuv', '--min_update_value',
                        action = "store", dest = "min_update_value",
                        type = float, default = 0,
                        help = "Lower limit of update value.")
	parser.add_argument( '-rt', '--regularization_type',
                        action = "store", dest = "regularization_type",
                        type = str, default = 'none',
                        help = "Type of regularization.")
	parser.add_argument( '-gr', '--granularity',
                        action = "store", dest = "granularity",
                        type = int, default = 3,
                        help = "How many samples the user wishes to divide the constructed intervals into.")		
	parser.add_argument('-no','--norm',action = "store", dest = "norm_type", type = int, default = 0,
		 help = "The type of penalty norm to use. Choices are 0, length of feature list, 1 absolute value of features, 2 sum 			 of squared features.")				
	
	#harvest the collected arguments
	
	args = parser.parse_args()
	
	max_initial_penalty = args.max_initial_penalty
	min_initial_penalty = args.min_initial_penalty
	max_update_value = args.max_update_value
	min_update_value = args.min_update_value
	regularization_type = args.regularization_type
	granularity = args.granularity
	norm_type = args.norm_type
	
	#creates the potential values the grid search will visit. Experiments or runs consist of running cross_entropy using 1 value from each of the following arrays.
	initial_penalty_samples = np.linspace(min_initial_penalty,max_initial_penalty,num=granularity)
	update_value_samples = np.linspace(min_update_value,max_initial_penalty,num=granularity)
	
	#loops over all possible combinations of the parameter values given in initial_penalty_samples and update_value_samples and runs cross_entropy using them to determine penalties.
	#NOTE: this procedure is costly, each loop calls cross_entropy. As such, it is recommended that granularity be kept rather low, not exceeding nine at the very most.
	#Point of improvement: could multithreading be used here? Something to look into.
	
	for pen in initial_penalty_samples: 
		for upd in update_value_samples:
			#puts a string on the command line to call cross_entropy.py, passing as arguments the regularization type, 				pen, and upd. Other parameters are hard-coded below
			command = "python cross_entropy.py -ip " + str(pen) + " -rtp " + str(upd) + " -rt " + regularization_type 	+ " -no " + str(norm_type) + " -d " + str(30) + " -dr 0.1" + " -e " + str(500) + " -f " + "landing_height eroded_cells row_trans col_trans pits cuml_wells mean_ht max_ht min_ht all_ht max_ht_diff min_ht_diff cleared deep_wells max_well cuml_cleared cuml_eroded pit_depth pit_rows column_9 tetris" + " -op score"
			subprocess.call(command,shell=True)
	print 'The run has been completed. Output files should be stored in the runs directory.'
			
