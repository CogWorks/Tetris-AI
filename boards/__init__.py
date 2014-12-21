from tetris_zoid import *
from tetris_cow import *
from _helpers import print_board

try: from tetris_cpp import tetris_cow2, set_row_cache_size, get_row_cache_size, set_board_cache_size, get_board_cache_size
except ImportError as error:
  import sys
  print >> sys.stderr, 'ImportError:', str(error), '(tetris_cpp)'
