#!/usr/bin/env bash

per_cell=1
count=$(echo {1..25})
times=250
methods='deep cow deep2 cow2'
# per_cell=1
# times=1

echo "method,per_cell,rep,times,num_calls,call_time,time_per_call,cum_time,cum_per_call,call"

for p in $per_cell; do

  for t in $count; do

    echo $methods | tr ' ' $'\n' | sort -R | while read method; do
      "$(dirname "$0")/profile_boards.py" "$method" "$p" "$times" | egrep 'SET|GET|run_test_' | \
      while read ncalls tottime percall cumtime percall2 call; do
        call="$(echo "$call" | sed -r 's/.*\((.+)\)/\1/')"
        echo "$method,$p,$t,$times,$ncalls,$tottime,$percall,$cumtime,$percall2,$call"
      done
    done

  done

done
