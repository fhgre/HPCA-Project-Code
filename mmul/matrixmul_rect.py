""" execute with anaconda prompt from the directory of matrixmul.py
    
    mpi4py and Microsoft MPI must be installed:
        https://www.microsoft.com/en-us/download/details.aspx?id=57467

    with the code:    mpiexec -n [NUMBER OF NODES] python -m matrixmul_rect.py 
    [NUMBER OF ROWS A] [NUMBER OF COLUMNS A] [NUMBER OF ROWS B] 
    [NUMBER OF COLUMNS B]
    
	All the code must be in the same line and whithout "[]"
	
"""
from mpi4py import MPI
import numpy as np
import math
from sys import argv
#########################################################################
#							Function Definition							#
#########################################################################

def matrixmul(A, B, Partial, Rank, Tile_width, last_tile , num_nodes, Row_dim_B, Col_dim_B):
    offset= Tile_width*(Rank)
    if Rank == num_nodes -1:
		for i in range(last_tile):
			for j in range(Col_dim_B):
			    for k in range(Row_dim_B):
				Partial[i+ offset][j] += A[i+ offset][k] * B[k][j]
    else:
		
		for i in range(Tile_width):
		    for j in range(Col_dim_B):
		        for k in range(Row_dim_B):
		            Partial[i+offset][j] += A[i+offset][k] * B[k][j]
		
#########################################################################
#				   		   Get Matrices' Dimensions						#
#########################################################################

Row_dim_A = int(argv[1]) if len(argv) > 1 else 128
Col_dim_A = int(argv[2]) if len(argv) > 1 else 128

Row_dim_B = int(argv[3]) if len(argv) > 1 else 128
Col_dim_B = int(argv[4]) if len(argv) > 1 else 128

#########################################################################
#						    Checking Dimensions							#
#########################################################################

if Col_dim_A != Row_dim_B:
    
    print('Wrong matrices dimensions, quitting.')

#########################################################################
#								   Main									#
#########################################################################

else:
        
    comm = MPI.COMM_WORLD
    # Get the number of nodes on comm channel
    num_nodes = comm.Get_size()
    # Get their rank
    Rank = comm.Get_rank()
    # Compute tile_width
    Tile_width = np.round(Row_dim_A / num_nodes).astype(int)
    last_tile = Row_dim_A - Tile_width*(num_nodes - 1)
    Partial=np.zeros((Row_dim_A,Col_dim_B))   #partial matrix initialization
    Result=np.zeros((Row_dim_A,Col_dim_B))  #final matrix initialization
    
    if(Rank==0):   
        A=np.zeros((Row_dim_A,Col_dim_A))   #first matrix initialization
        B=np.zeros((Row_dim_B,Col_dim_B))   #second matrix initialization    
        C=np.zeros((Row_dim_A,Col_dim_B))   #check matrix initialization
        P=np.zeros((Row_dim_A,Col_dim_B))   #check matrix initialization 2
        #Generating matrix 1
        for i in range(Row_dim_A):
            for j in range(Col_dim_A):
                A[i][j]=np.random.rand()
        #Generating matrix 2
        for i in range(Row_dim_B):
            for j in range(Col_dim_B):
                B[i][j]=np.random.rand()
        
        #Sending the generated matrices to the other nodes
        for i in range(1,num_nodes):
            comm.send(A,dest=i, tag=11)
            comm.send(B,dest=i, tag=12)
    else:
        #Receiving matrices from node 0
        A=comm.recv(source=0, tag=11)
        B=comm.recv(source=0, tag=12)
    
    comm.Barrier() #Waiting for all the processes to have the same data
    start = MPI.Wtime()
    #Execute matrix multiplication
    matrixmul(A,B,Partial,Rank, Tile_width, last_tile, num_nodes, Row_dim_B, Col_dim_B)
    comm.Barrier()
    #Merge the blocks of matrix from the processes into a single matrix
    comm.Reduce([Partial, MPI.DOUBLE],[Result, MPI.DOUBLE],op=MPI.SUM,root=0)
    #Record the time when the function is done
    finish = MPI.Wtime()
    #Check the result and/or print time elapsed

#########################################################################
#					     Checksum and time print							#
#########################################################################
	
    if (Rank==0):
	#Generating serial product matrix
	print('Generating serial product matrix')
        for i in range(Row_dim_A):
            for j in range(Col_dim_B):
                for k in range(Row_dim_B):
                    C[i][j]+= A[i][k] * B[k][j] 

	#print('Dimensioni matrice A', A.shape)
	#print('Dimensioni matrice B', B.shape)
	#print('Dimensioni matrice risultato Seriale', C.shape)
	#print('Dimensioni matrice risultato MPI', Result.shape)
    #Comparing Result matrix (parallel exexution) with C matrix (serial)
        for i in range(Row_dim_A):
            for j in range(Col_dim_B):
                    P[i][j]= C[i][j]-Result[i][j]
		    #if P[i][j] != 0:
			#print('Not zero in position ({},{}), P value {}, C value {},'.format(i,j, P[i][j], C[i][j]))
			#print('Result Value', Result[i][j])
		
        if(np.sum(P) != 0):
            print("""Something wrong happened! Serial and parallel executions 
                  provide different results""")
        else:
            #print("\nResult:\n\n",Result)
            print("\nMPI part time elapsed:\n\n",finish - start,"s")
        
