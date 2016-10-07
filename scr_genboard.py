# generate gang board examples
import os

for f in range(5):
    os.system('python3 gen_board.py -n 3 -depth 3 -m MINIMAX -f inputs/intput{0}.txt'.format(f))

for f in range(5, 10):
    os.system('python3 gen_board.py -n 5 -depth 3 -m MINIMAX -f inputs/intput{0}.txt'.format(f))

for f in range(10, 20):
    os.system('python3 gen_board.py -n 10 -depth 3 -m MINIMAX -f inputs/intput{0}.txt'.format(f))

for f in range(20, 30):
    os.system('python3 gen_board.py -n 26 -depth 3 -m MINIMAX -f inputs/intput{0}.txt'.format(f))

for f in range(30, 40):
    os.system('python3 gen_board.py -n 5 -depth 4 -m MINIMAX -f inputs/intput{0}.txt'.format(f))

for f in range(40, 50):
    os.system('python3 gen_board.py -n 10 -depth 4 -m MINIMAX -f inputs/intput{0}.txt'.format(f))
