Tetris-AI with Pylearn2
=======================

http://vdumoulin.github.io/articles/extending-pylearn2/

Workflow
* For each subject
** Load all episodes, split into list(list(features),list(moves))
*** where a move is a tuple(row,column,rotation)
** Train net
** stop if delta RMSE < threshold