# encoding = utf-8
from ideas1_utilities import ideas1_multiple_processing

if __name__=="__main__":
    input_comd_list = ['python add_two_nums.py 1 2','python add_two_nums.py 3 4','python add_two_nums.py 5 6','python add_two_nums.py 7 8',
                       'python add_two_nums.py 1 2','python add_two_nums.py 3 4','python add_two_nums.py 5 6','python add_two_nums.py 7 8']
    run = ideas1_multiple_processing(5,input_comd_list)
    run.run_all_for_executable(timeout=100)