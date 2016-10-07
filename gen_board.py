import random, math, sys, argparse
##### generate gang board HW2

N = 5
MODE = 'MINIMAX'
# YOUPLAY = ''
MAX_DEPTH = 5
DEPTH = 3
CELL_VALUES = []
BOARD = []

MAX_VAL = 100


######################### randomize paras #########################
MODE = random.choice(['MINIMAX', 'ALPHABETA']) # and 'COMPETITION'
YOUPLAY = random.choice(['X', 'O'])
MAX_DEPTH = int(N * N / 2)

######################### parsing #########################
DEBUG = False
FILE_NAME = ''

parser = argparse.ArgumentParser(description='Randomly generate gang board')
parser.add_argument('-n', metavar = 'N', type=int, default=random.randrange(26))
parser.add_argument('-m', metavar = 'mode', default = 'MINIMAX', 
                    choices= ['MINIMAX', 'ALPHABETA'])
parser.add_argument('-depth', metavar ='depth', type=int, 
                default=random.randrange(1, MAX_DEPTH + 1))
parser.add_argument('-f', metavar ='filename', default='input.txt')

parser.add_argument('-d', action='store_true', default=False)
args = parser.parse_args()
N = args.n
MODE = args.m
DEPTH = args.depth
FILE_NAME = args.f
DEBUG = args.d
# print (DEBUG)
# quit()

######################### initialize board info #########################
CELL_VALUES = [[random.randrange(MAX_VAL) for j in range(N)] for i in range(N)]
BOARD = [['.' for j in range(N)] for i in range(N)] 
# dont use * N to declare a 2-d array, which copy the pointer of the first row

######################### generate board utility #########################
AVAILABLES = [] # might be outdated, because only updated when 50% 25%...
NUM_AVAILABLES = 0
UPDATE_POINT = 0
OWNED_PIECES = {}

def init():
    global N, AVAILABLES, NUM_AVAILABLES, OWNED_PIECES, UPDATE_POINT
    AVAILABLES = [x for x in range(N * N)]
    NUM_AVAILABLES = N * N
    OWNED_PIECES = {'X':set(), 'O':set()}
    UPDATE_POINT = math.floor(N / 2)

def update_avails():
    global N, AVAILABLES, BOARD
    AVAILABLES = []
    for i in range(N):
        for j in range(N):
            if BOARD[i][j] == '.':
                AVAILABLES.append(i * N + j)

def decrease_availables():
    global N, AVAILABLES, NUM_AVAILABLES, UPDATE_POINT
    if NUM_AVAILABLES == 0:
        print('To decrease NUM_AVAILABLES when it has been 0')
        raise()
    
    NUM_AVAILABLES -= 1
    if NUM_AVAILABLES == UPDATE_POINT:
        update_avails()
        UPDATE_POINT /= 2 #

def get_opponent(player):
    opponent = ''
    if player == 'X':
        opponent = 'O'
    else:
        opponent = 'X'
    return opponent
    

######################### game operators #########################

# randomly stake an unoccupied cell
def random_stake(player):
    global N, BOARD, OWNED_PIECES, DEBUG
    
    while (1):
        r, c = random.randrange(N), random.randrange(N)
        # print(N, r, c)
#         print(BOARD)
        if BOARD[r][c] == '.':
            BOARD[r][c] = player
            OWNED_PIECES[player].add(r * N + c)
            decrease_availables() # not necessary in solver
            if DEBUG:
                print('staked:', r, c)
            break

# get the possible moves for raiding from cell (r, c)
def get_raid_moves(r,c):
    global BOARD, N
    
    moves = []
    if r > 0:
        if BOARD[r-1][c] == '.':
            moves.append((-1, 0))
    if r < N - 1:
        if BOARD[r+1][c] == '.':
            moves.append((1, 0))
    if c > 0:
        if BOARD[r][c-1] == '.':
            moves.append((0, -1))
    if c < N - 1:
        if BOARD[r][c+1] == '.':
            moves.append((0, 1))
    return moves

# change the ownership of cell (row, col) into player
def change_ownership(player, opponent, row, col):
    global N, BOARD, OWNED_PIECES, DEBUG
    cell = row * N + col
    BOARD[row][col] = player
    OWNED_PIECES[opponent].remove(cell)
    OWNED_PIECES[player].add(cell)
    if DEBUG:
        print('swallowed: ', row, col)

# swallow the surrounding opponent tiles
def swallow_around(player, r, c):
    global N, BOARD
    opponent = get_opponent(player)
    if r > 0:
        if BOARD[r-1][c] == opponent:
            change_ownership(player, opponent, r-1, c)
    if r < N - 1:
        if BOARD[r+1][c] == opponent:
            change_ownership(player, opponent, r+1, c)
    if c > 0:
        if BOARD[r][c-1] == opponent:
            change_ownership(player, opponent, r, c-1)
    if c < N - 1:
        if BOARD[r][c+1] == opponent:
            change_ownership(player, opponent, r, c+1)

# raid from cell (row, col) using move
def raid(player, row, col, move):
    global N, BOARD, OWNED_PIECES, DEBUG
    if (row * N + col) not in OWNED_PIECES[player]:
        print('raid from a cell not from ' + player + '\'s territory')
        raise
    r = row + move[0]
    c = col + move[1]
    BOARD[r][c] = player
    OWNED_PIECES[player].add(r * N + c)
    decrease_availables() # not necessary in solver
    if DEBUG:
        print('raided from:', row, col, 'move:', move)
    # print_board()
    # occupy touching cells owned by enemy
    swallow_around(player, r, c)    
            
# randomly raid from the piece owned by player
def random_raid(player):
    global N, OWNED_PIECES
    
    if len(OWNED_PIECES[player]) == 0:
        return False            
    # choose piece to raid from until success, at most 5 times
    for i in range(5):
        cell = random.sample(OWNED_PIECES[player], 1)[0]
        r, c = int(cell / N), cell % N
        moves = get_raid_moves(r, c)
        if len(moves):
            break
    if len(moves) == 0: # no valid move after sampling five times
        return False
        
    move = random.choice(moves) # choose a valid move    
    raid(player, r, c, move)
    return True
    
# randomly choose to stake or raid
def random_play(player):
    if random.random() < 0.5:
        if random_raid(player):
            return
    random_stake(player)

############################## other utilities ##############################
def print_board():
    global N, BOARD
    for r in range(N):
        for c in range(N):
            print(BOARD[r][c], end = '')
        print()
    print()


############################## main ##############################
init()

num_plays = random.randrange( int(N * N / 2) )
print('N: ' + str(N) + '\tnum_ply: ' + str(num_plays) + '\n')

player = 'X'
while ( num_plays ):
    if DEBUG:
        print(player + ':')
    random_play(player)
    if DEBUG:
        print(OWNED_PIECES)
        print_board()
    player = get_opponent(player)
    num_plays -= 1


with open(FILE_NAME, 'w') as f:
    f.write(str(N) + '\n')
    f.write(MODE + '\n')
    f.write(player + '\n')
    f.write(str(DEPTH) + '\n')
    
    for row in CELL_VALUES:
        for cell in row:
            print(str(cell) + ' ', end = '')
        print()
        s = ' '.join(repr(val) for val in row) + '\n'
        f.write(s)
    print()
    
    for r in range(N):
        for c in range(N):
            print(BOARD[r][c], end = '')
            f.write(str(BOARD[r][c]))
        print()
        f.write('\n')
    print()


