This is a Python extension for a 20x10 tetris board written in C++. The C++ code
contains a class that can be sized to whatever board dimensions you want;
however, fixing the board dimensions allows for faster code. It would be fairly
easy to add Python bindings for that class; I'm just too lazy at the moment.

To install on Linux (etc.) or OS X, 'cd' to this directory and do the following:

> python setup.py build
> python setup.py install --user

This will install the module 'tetris_cpp' in your home directory. To use it,

from tetris_cpp import *

This should give you a class 'tetris_cow2', which is pretty much the same as
'boards.tetris_cow', except you can't specify the size when you create it. Also,
if you 'import boards', that will automatically pull in 'tetris_cow2' if it's
available.

'tetris_cow2' has the same copy-on-write behavior as 'tetris_cow', with the
following exceptions:

- 'tetris_cow2' has better copy-on-write because changing the original board
  won't affect temporary copies you made of it (unlike 'tetris_cow').

- 'tetris_cow2' uses an object pool to reuse rows that have been discarded. This
  substantially reduces the time spent allocating/deallocating rows; however,
  the savings are only about 25%, given the overhead that Python adds.

Kevin P. Barry, 20141218
