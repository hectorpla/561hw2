import os

for f in range(10):
    os.system('cp inputs/intput{0}.txt  input.txt'.format(f))
    os.system('python3 homework3.py')
    input("PRESS ENTER TO CONTINUE.")