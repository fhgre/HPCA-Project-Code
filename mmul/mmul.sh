#!/bin/bash

for row in 256 512 1024; do

	for column in 256 512 1024; do

                for TEST in 1 2 3 4; do

                	for NODES in 1 2 4 8; do

                                                mpiexec -n $NODES python -m matrixmul_rect.py $row $column $column $row >> mat_mul.$row.$column.$test.txt

			done
		done
	done
done
