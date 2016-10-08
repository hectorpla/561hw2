# 561 hw2: minimax game playing
import time, copy

N = 5
MODE = ''
YOUPLAY = ''
CELL_VALUES = []
DEPTH = 1

# game state
board = []
AVAILABLES = set()
OWNED_PIECES = {'X':set(), 'O':set()}

######################### parsing #########################    
def parse_values(value_lines):
    """
    :rtype: list (2-d) containg cell value
    """
    value_board = []
    for line in value_lines:
        value_board.append( list(map(int, line.split())) )
    return value_board
        
def parse_board(board_lines):
    """
    :rtype: list (2-d containing ownership), int
    """
    global AVAILABLES, OWNED_PIECES
    size = len(board_lines)
    board = []
    for r in range(size):
        board.append([])
        for c in range(size):
            board[-1].append(board_lines[r][c])
            if board_lines[r][c] is '.': AVAILABLES.add((r,c))
            if board_lines[r][c] is 'X': OWNED_PIECES['X'].add((r,c))
            if board_lines[r][c] is 'O': OWNED_PIECES['O'].add((r,c))
            
    return board

######################### utility #########################
def print_board(board, delim):
    size = len(board)
    
    for r in range(size):
        for c in range(size):
            print(str(board[r][c]) + delim, end = '')
        print()
    print()
    
def write_board(f, board):
    size = len(board)    
    for line in board:
        f.write(''.join(line) + '\n')
 
def print_paras():
    global N, MODE, YOUPLAY, DEPTH
    print('N = ' + str(N) + '\nMODE = ' + MODE + '\nYOUPLAY = ' + YOUPLAY
        + '\nDEPTH = ' + str(DEPTH) + '\n')

def get_opponent(player):
    opponent = ''
    if player == 'X': opponent = 'O'
    else: opponent = 'X'
    return opponent
    
def compute_eval(board, player):
    global N, CELL_VALUES
    
    opponent = get_opponent(player)
    res = 0
    for r in range(N):
        for c in range(N):
            if board[r][c] is player: res += CELL_VALUES[r][c]
            if board[r][c] is opponent: res -= CELL_VALUES[r][c]
    return res

######################### game operators #########################
# stake a position and return the gain
def stake(board, player, pos):
    global N, CELL_VALUES, AVAILABLES
#     print(player + ' staking ' + str(pos)) ## print
    r, c = pos[0], pos[1]
    assert board[r][c] is '.'
    board[r][c] = player
    AVAILABLES.remove(pos)
    OWNED_PIECES[player].add(pos)
    return CELL_VALUES[r][c]
    
def remove_ownership(board, player, pos):
    global N, AVAILABLES, OWNED_PIECES
#     print(player + ' revert stake/raid ' + str(pos)) ## print
    r, c = pos[0], pos[1]
    assert board[r][c] != '.'
    board[r][c] = '.'
    OWNED_PIECES[player].remove(pos)
    AVAILABLES.add(pos)

# change the ownership of pos into player, return the gain
def change_ownership(board, player, opponent, r, c):
    global OWNED_PIECES
    assert board[r][c] is opponent
    board[r][c] = player
    OWNED_PIECES[opponent].remove((r,c))
    OWNED_PIECES[player].add((r,c))
    return 2 * CELL_VALUES[r][c]


# swallow the surrounding opponent tiles, return the gain
def swallow_around(board, player, pos):
    global N, OWNED_PIECES
    opponent = get_opponent(player)
    assert pos in OWNED_PIECES[player]
    r, c = pos[0], pos[1]
    
    gain = 0
    swallowed = []
    if r > 0 and board[r-1][c] == opponent:
        gain += change_ownership(board, player, opponent, r-1, c)
        swallowed.append((r-1, c))
    if r < N - 1 and board[r+1][c] == opponent:
        gain += change_ownership(board, player, opponent, r+1, c)
        swallowed.append((r+1, c))
    if c > 0 and board[r][c-1] == opponent:
        gain += change_ownership(board, player, opponent, r, c-1)
        swallowed.append((r, c-1))
    if c < N - 1 and board[r][c+1] == opponent:
        gain += change_ownership(board, player, opponent, r, c+1)
        swallowed.append((r, c+1))
#     print(player + ' swallowed: ' + str(swallowed))
    return gain, swallowed

# return all the possible raid moves from pos
def get_raid_moves(board, pos):
    """
    : rtype: lists of two tuple (row_move, col_move)
    """
    global N
    moves = []
    r, c = pos[0], pos[1]
    if r > 0 and board[r-1][c] == '.':
        moves.append((-1, 0))
    if r < N - 1 and board[r+1][c] == '.':
            moves.append((1, 0))
    if c > 0 and board[r][c-1] == '.':
            moves.append((0, -1))
    if c < N - 1 and board[r][c+1] == '.':
            moves.append((0, 1))
    return moves

# raid from pos using move, return the gain
def raid(board, player, pos, move):
    global N, CELL_VALUES
#     print(player + ' raiding from:' + str(pos) + ' move: ' + str(move)) ## print
    assert pos in OWNED_PIECES[player]
    r, c = pos[0] + move[0], pos[1] + move[1]
    assert board[r][c] is '.'
    board[r][c] = player
    AVAILABLES.remove((r,c))
    OWNED_PIECES[player].add((r,c))
    raid_gain = CELL_VALUES[r][c]
    # occupy touching cells owned by enemy
    swallow_gain, swallowed = swallow_around(board, player, (r,c))
    return raid_gain + swallow_gain, swallowed

# revert a swallow
def revert_swallow(board, swallowed, player, opponent):
    global OWNED_PIECES
    for s in swallowed:
        r, c = s[0], s[1]
        assert board[r][c] is player
        board[r][c] = opponent
        OWNED_PIECES[player].remove(s)
        OWNED_PIECES[opponent].add(s)
#     print(player + ' revert swallow: ' + str(swallowed)) ## print
    

######################## algos #########################
def MiniMax(board, player, depth, eval, abp):
    """
    : return the minimax decision
    """
    global CELL_VALUES, DEPTH, AVAILABLES, OWNED_PIECES
    move_type = 'Stake'
    move_target = (0, 0)
    print('MINIMAX, pruned: ' + str(abp))
    
    alpha, beta = float('-inf'), float('inf')
    max_val = float('-inf')
    opponent = get_opponent(player)  
    
    print(AVAILABLES)
    avails = copy.copy(AVAILABLES)
    own_pieces = OWNED_PIECES[player]
    # stake
    for tile in avails:
        change_eval = stake(board, player, tile)
        new_eval = eval + change_eval
#         print(player + " new eval: " + str(new_eval)) ## print        
        temp = Min_Value(board, opponent, depth + 1, new_eval, abp, alpha, beta) # compute 
        if temp > max_val:
            max_val = temp
            move_target = tile
        print(player + " stake " + str(tile) + " min value: " + str(temp)) ## print
        # restore the original state
        remove_ownership(board, player, tile)
#         print()
    # raid
    for tile in own_pieces:
        moves = get_raid_moves(board, tile)
        for move in moves:            
            change_eval, swallowed = raid(board, player, tile, move)
            new_eval = eval + change_eval
            raided = (tile[0] + move[0], tile[1] + move[1])
            temp = Min_Value(board, opponent, depth + 1, new_eval, abp, alpha, beta) # compute
            if temp > max_val:
                max_val = temp
                move_type = 'Raid'
                move_target = (tile, move)
            print(player + " raid  " + str(raided) + " min value: " + str(temp)) ## print
            # restore the original state
            revert_swallow(board, swallowed, player, opponent)
            remove_ownership(board, player, raided)
        
    return move_target, move_type
       
def Max_Value(board, player, depth, last_eval, abp, alpha, beta):
    global CELL_VALUES, DEPTH, AVAILABLES, OWNED_PIECES
    
    if len(AVAILABLES) == 0 or depth == DEPTH: 
        return last_eval # should simply call compute function?
    
    max_val = float('-inf')
    opponent = get_opponent(player)
    
    avails = copy.copy(AVAILABLES)
    own_pieces = OWNED_PIECES[player]
    # stake
    for tile in avails:
        change_eval = stake(board, player, tile)
        new_eval = last_eval + change_eval
        max_val = max(max_val, Min_Value(board, opponent, depth + 1, new_eval, abp, alpha, beta)) #
        remove_ownership(board, player, tile)
        # pruning
        if abp and max_val >= beta: return max_val
        alpha = max(alpha, max_val)
    # raid
    for tile in own_pieces:
        moves = get_raid_moves(board, tile)
        for move in moves:            
            change_eval, swallowed = raid(board, player, tile, move)
            new_eval = last_eval + change_eval
            max_val = max(max_val, Min_Value(board, opponent, depth + 1, new_eval, abp, alpha, beta))
            revert_swallow(board, swallowed, player, opponent)
            raided = (tile[0] + move[0], tile[1] + move[1])
            remove_ownership(board, player, raided)
            # pruning
            if abp and max_val >= beta: return max_val
            alpha = max(alpha, max_val)
        
    return max_val
    
def Min_Value(board, player, depth, last_eval, abp, alpha, beta):
    global CELL_VALUES, DEPTH, AVAILABLES, OWNED_PIECES
    
    if len(AVAILABLES) == 0 or depth == DEPTH: 
        return last_eval # should simply call compute function?
    
    min_val = float('inf')
    opponent = get_opponent(player)
    
    avails = copy.copy(AVAILABLES)
    own_pieces = OWNED_PIECES[player]
    # stake
    for tile in avails:
        change_eval = stake(board, player, tile)
        new_eval = last_eval - change_eval
        min_val = min(min_val, Max_Value(board, opponent, depth + 1, new_eval, abp, alpha, beta)) #
        remove_ownership(board, player, tile)
        # pruning
        if abp and min_val <= alpha: return min_val
        beta = min(beta, min_val)
    # raid
    for tile in own_pieces:
        moves = get_raid_moves(board, tile)
        for move in moves:            
            change_eval, swallowed = raid(board, player, tile, move)
            new_eval = last_eval - change_eval
            min_val = min(min_val, Max_Value(board, opponent, depth + 1, new_eval, abp, alpha, beta))
            revert_swallow(board, swallowed, player, opponent)
            raided = (tile[0] + move[0], tile[1] + move[1])
            remove_ownership(board, player, raided)
            # pruning
            if abp and min_val <= alpha: return min_val
            beta = min(beta, min_val)
        
    return min_val
    
######################### main #########################
with open('input.txt', 'r') as f:
    lines = f.read().splitlines()
    # print(mylist)

N = int(lines[0])
MODE = lines[1]
YOUPLAY = lines[2]
DEPTH = int(lines[3])
CELL_VALUES = parse_values(lines[4:4+N])
board = parse_board(lines[4+N:4+2*N])

print_paras()
# print_board(CELL_VALUES, ' ')
print_board(board, '') 
# print(AVAILABLES) 
# print(OWNED_PIECES)

eval = compute_eval(board, YOUPLAY)
# print('initial eval: ' + str(eval))
ABP = False
if MODE == 'ALPHABETA': ABP = True
# print('MODE: ' + MODE + ', ' + 'MODE: ' + str(MODE == 'ALPHABETA'))
# print('ABP ' + str(ABP))
    
start_time = time.time()
target, type = MiniMax(board, YOUPLAY, 0, eval, ABP)
print("Runing time: {0}ms".format(int((time.time() - start_time) * 1000)))
print(type, target)


with open('output.txt', 'w') as f:
    cell = 0
    if type is 'Stake': 
        stake(board, YOUPLAY, target)
        cell = target        
    else:
        cell, move = target[0], target[1]
        raid(board, YOUPLAY, cell, move)
        cell = (cell[0] + move[0], cell[1] + move[1])
    move = '%c%d %s\n' % (cell[1] + 65, cell[0] + 1, type)
    f.write(move)    
    write_board(f, board)
    

