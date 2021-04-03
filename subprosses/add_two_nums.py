# encoding = utf-8
import sys

def add_two_nums(a1,a2):
    print("a1 + a2 = ",a1+a2)
    
if __name__=='__main__':
    add_two_nums(int(sys.argv[1]),int(sys.argv[2]))