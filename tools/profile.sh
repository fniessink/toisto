#/bin/bash

python -m cProfile -o build/profile.out venv/bin/toisto
gprof2dot -f pstats build/profile.out > build/profile.dot
dot -Tpng build/profile.dot > build/profile.png
open build/profile.png
