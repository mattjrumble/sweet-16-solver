# Sweet 16 Solver

Finds a solution to a puzzle like the following:

   Find values for A, B, ..., O, P, (let's call them stones), where each stone has a unique integer value between 1 and 16 inclusive.
   We are given that A+B=C, E+F=G, J+K=L, M+N=O, E+I=M, B*F=J, C-G=K, H-L=P (using the letters interchangeably to mean either the stone or the
   value of the stone, depending on the context).

In general, finds a solution to the following puzzle:

   Find values for stones A_1, A_2, ..., A_N, where each stone has a unique integer value between 1 and N inclusive.
   We are given a set of constraints of the form f(A_x, A_y)=A_z, where A_x, A_y, A_z are different stones, and f is some function between integers.