import os

list = [i for i in range(20)] + [i for i in range(30, 40)]

for f in list:
    os.system('cp inputs/intput{0}.txt  input.txt'.format(f))
    os.system('python3 homework3.py')
    os.system('cp output.txt  outputs/output{0}.txt'.format(f))
#     input("PRESS ENTER TO CONTINUE.")