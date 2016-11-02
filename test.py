from simulator import TetrisSimulator
from boards import all_zoids

if __name__ == "__main__":
    simulator = TetrisSimulator(show_episodes = True,show_options = True,show_choice = True,option_step = 1)
    simulator.run(max_eps=10,printstep=1)
    ##print(simulator.space)
      #  print(simulator.space[1,1])