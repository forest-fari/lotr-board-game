import numpy as np
from numpy import array as arr
from numpy import random as choose
from math import ceil as ceil
from recordclass import recordclass, RecordClass

class Cut ( RecordClass ):
    name: str
    tiles: (int, int)
    

class Player ( RecordClass ):
    name: str
    tile: int
    ring: bool
    vector: int
    good: bool
    is_chasing: str



# int -> Dict {int: List str}
def empty_board ( board_size ):

    if board_size == 1:
        return {0: []}
    else:
        board = empty_board ( board_size - 1 )
        board[board_size - 1] = []
        return board

# int, List Cut --> Dict {int: List str}
def generate_board ( board_size, all_cuts ):
    
    board =  empty_board ( board_size )

    # List Cut -> None
    def place_cuts ( cuts ):
        this_cut = cuts[0]
        one_tile, other_tile = this_cut.tiles
        board[one_tile].append ( this_cut.name )
        board[other_tile].append ( this_cut.name )
        if len ( cuts ) > 1:
            place_cuts ( cuts[1:] )

    place_cuts ( all_cuts )

    return board

# Dict, List Player -> Dict {int: List str}
def put_players_on_board ( board, all_players ):

    # List Player -> None
    def place_players ( players ):
        this_player = players[0]
        board[this_player.tile].append ( this_player.name )
        if len (players) > 1:
            place_players ( players[1:] )

    place_players ( all_players )
    
    return board

# List str, List str, List, str, int -> List Cut
def generate_cuts ( names_long, names_med, names_short, board_size ):

    # float, int, int -> List int
    def get_cut_lengths ( min_length, max_add, num ):
        cut_length_mins = [(int(min_length))] * num
        cut_length_adds = list ( map ( choose.randint , [max_add] * num ))
        return  list ( arr ( cut_length_mins ) + arr ( cut_length_adds ) )

    long_cut_lengths =  get_cut_lengths ( board_size / 3, 20, len ( names_long ) )
    med_cut_lengths =  get_cut_lengths ( board_size / 6, 10, len ( names_med ) )
    short_cut_lengths =  get_cut_lengths ( board_size / 20, 5, len ( names_short ) )
    all_cut_lengths = long_cut_lengths + med_cut_lengths + short_cut_lengths

    all_cut_names = names_long + names_med + names_short

    # str, int, List int -> Cut
    def create_one_cut ( naam, length, choices ):
        ind = choose.randint ( len (choices) )
        one_end = choices[ind]
        other_endA = one_end - length
        other_endB = one_end + length
        if other_endA in choices:
            return Cut ( name = naam, tiles = ( other_endA, one_end ) )
        elif other_endB in choices:
            return Cut ( name = naam, tiles = ( one_end, other_endB ) )
        else: 
            new_choices = np.delete ( choices, ind )
            return create_one_cut ( naam, length, new_choices )

    # Could change create_all_cuts (...) to output None and just recursively update an 
    # initially empty list of cuts like above with board but wanted to change things up. 
    # Need to look up later if there is some advantage to one method over the other

    # List Cut, List str, List int, List int -> List Cut
    def create_all_cuts ( cuts, cut_names, cut_lengths, tiles ):
        new_cut = create_one_cut ( cut_names[0], cut_lengths[0], tiles )
        loc_one = np.where ( tiles == new_cut.tiles[0] )[0]
        loc_other = np.where ( tiles == new_cut.tiles[1] )[0]
        remaining_tiles = np.delete ( tiles, [loc_one, loc_other] )
        cuts.append ( new_cut )
        if len ( cut_names ) > 1:
            create_all_cuts ( cuts, cut_names[1:], cut_lengths[1:], remaining_tiles )
        return cuts
    
    all_tiles = np.arange ( board_size )[1:-1] 
    all_cuts = create_all_cuts ( [], all_cut_names, all_cut_lengths, all_tiles )
    
    return all_cuts

# int, int -> List Player
def generate_players ( board_size, num_players ):
    num_good_players = ceil ( num_players / 2 )

    # str -> Player
    create_good_player = lambda naam: Player ( name = naam, good = True, ring = False, tile = 0, vector = 1, is_chasing = None)

    # str -> Player
    create_evil_player = lambda naam: Player ( name = naam, good = False, ring = False, tile = board_size - 1, vector = -1, is_chasing = None)

    # List Player -> List Player
    def assign_ring_holder ( players ): 
        chosen_one = choose.randint( num_good_players )
        players[chosen_one].ring = True

    # List Player
    def create_all_players ():
        possible_good_players = ['Frodo', 'Sam', 'Gandalf']
        possible_evil_players = ['Sauron', 'Witch King', 'Mordu']

        good_player_names = possible_good_players[: num_good_players ]
        evil_player_names = possible_evil_players[: ( num_players - num_good_players ) ]
        good_players = list ( map ( create_good_player, good_player_names ))
        evil_players = list ( map ( create_evil_player, evil_player_names ))
        return good_players + evil_players

    players = create_all_players ()
    assign_ring_holder ( players )
    
    return players

# int, int -> List Player, Dict
def initialize_board ( board_size ):

    ### CUTS
    cuts = generate_cuts ( ['L1', 'L2', 'L3'], ['M1', 'M2', 'M3', 'M4', 'M5'], ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'], board_size )

    ### BOARD
    board =  generate_board ( board_size, cuts )
    
    return cuts, board

def initialize_players ( board_size, num_players):

    ### PLAYERS
    players = generate_players ( board_size, num_players )

    return players






class GameState ( RecordClass ):
    finished: bool
    winner: bool # True if GOOD, False if EVIL
    num_turns: int
    players: list
    whose_turn: int

class GameStatistics ( RecordClass ):
    num_games: int
    num_finished: int
    num_good_won: int
    winners: list
    turns: list



# List Cut -> List Int
def collapse_cuts ( all_cuts ):

    collapsed = []

    def collapse ( list_of_cuts ):
        cut = list_of_cuts[0] 
        collapsed.append ( cut.tiles[0] )
        collapsed.append ( cut.tiles[1] )
        if len ( list_of_cuts ) > 1:
            collapse ( list_of_cuts[1:] )

    collapse ( all_cuts )
    return np.array ( collapsed )

# int, List Cut -> int
def get_other_cut_end ( ends, this_end ):
    ind = np.where ( ends == this_end )[0]
    if ind % 2 == 1:
        return ends [ind - 1][0]
    else:
        return ends [ind + 1][0]


# available variables: board, cuts, players, cut_ends

# Player -> int
get_player_loc = lambda player: player.tile
get_player_name = lambda player: player.name
get_player_goodness = lambda player: player.good
player_has_ring = lambda player: player.ring

# int -> GameState
def play_game ( moves_left, init_players, cut_ends, die_faces ):

    num_players = len (init_players)
    num_good_players = ceil ( num_players / 2 )
    max_tile = init_players[-1].tile 

    # None -> int
    def roll_dice ():
        return choose.randint ( die_faces )

    # GameState -> GameState
    def play_turn ( state ):
        
        all_players = state.players
        all_player_locs = np.array ( list ( map ( get_player_loc, all_players ) ) )
        
        this_turn = ( state.whose_turn + 1 ) % (num_players)
        this_player = all_players[this_turn]
        this_loc = this_player.tile

        
        '''
        if there's only one good player and they've crossed you, obviously start chasing them

        if you've been crossed by all good players, you should start chasing one of them

        if you've been crossed by a subset of good players, 
        you will chase one of them with probability num_crossers / num_good_players
        '''
        # None -> None (updates this player's chasing state and vector)
        def maybe_chase ( ):

            # Player -> List Player
            def good_crossers ( player ):
                
                good_players = all_players[:num_good_players]
                good_locs = np.array ( list ( map ( get_player_loc, good_players ) ) )
                crosser_inds = np.where ( good_locs > this_player.tile )[0]
                
                return [good_players[ind] for ind in crosser_inds]

            crossers = good_crossers ( this_player )
            num_good_crossers = len ( crossers )
            
            if num_good_crossers > 0: 
                
                pick = choose.randint ( num_good_players )
                
                if pick < num_good_crossers:
                    this_player.is_chasing = crossers[pick].name
                    this_player.vector = 1


        '''
        if a bad player is not chasing anyone currently, they have the option to chase a good player who's passed them earlier
        '''
        if not this_player.good and this_player.is_chasing == None:
            maybe_chase ()


        '''
        don't fall off the board!
        '''
        # int -> int (don't fall off the board!)
        def stay_on_board ( tile ):
            if tile > max_tile:
                return max_tile
            elif tile < 0:
                return 0
            else:
                return tile

        '''
        roll a dice, move forward, take a cut if you land on a cut end
        '''
        # None -> None
        def update_location ():
            
            steps = roll_dice ()
            maybe_new_loc = stay_on_board ( this_loc + this_player.vector * steps )
    
            if maybe_new_loc in cut_ends:
                take_cut = choose.randint ( 2 )
                if take_cut:
                    new_loc = get_other_cut_end ( cut_ends, maybe_new_loc )
                else:
                    new_loc = maybe_new_loc
            else:
                new_loc = maybe_new_loc
            
            this_player.tile = new_loc

            
        update_location ()

        
        '''
        query properties of other players on the tile this player just landed on
        '''
        cohab_inds = np.where ( all_player_locs == this_player.tile )[0]
        num_cohabitors = len ( cohab_inds )
        if num_cohabitors > 1:
            
            cohabitors = [all_players[ind] for ind in cohab_inds] # drasted for loops here, list.map is leading to dumb errors and I'm tired
            cohabitor_names = list ( map ( get_player_name, cohabitors ) )
            
            cohabitor_goods = list ( map ( get_player_goodness, cohabitors ) )
            all_cohabitors_good = all ( cohabitor_goods )
            
            is_ring_here = np.array ( list ( map ( player_has_ring, cohabitors ) ) )
            ring_location = np.where ( is_ring_here )[0]
            ring_bearer_here = len ( ring_location )
            
            if ring_bearer_here > 0:
                ring_bearer = all_players[ring_location[0]]
            
        else:
            ring_bearer_here = 0


        
        # None -> None (change direction to shire, stop chasing)
        def to_shire_and_stop_chasing ():
            this_player.vector = -1
            this_player.is_chasing = None


        '''
        ring bearer maybe swaps the ring with one of those other good players, unbeknownst to bad players
        50% chance of swap, other 50% equally divided amongst potential swapees
        '''
        def maybe_give_away_ring ():
            cohab_inds_except_this_one = np.delete ( cohab_inds, np.where ( cohab_inds == this_turn ) )
            num_others = len ( cohab_inds_except_this_one )
            maybe_swap = choose.randint ( 2 * num_others )
            
            if maybe_swap < num_others:
                ring_swapee_ind = cohab_inds_except_this_one[maybe_swap]
                ring_swapee = all_players[ring_swapee_ind]
                this_player.ring = False
                ring_swapee.ring = True

        '''
        good non-ring bearer maybe takes the ring, unbeknownst to bad players
        50% chance of take
        '''
        def maybe_take_ring ():
            take = choose.randint ( 2 )
            if take:
                ring_bearer.ring = False
                this_player.ring = True
            
        '''
        if the ring bearer reaches Mt. Doom
        '''
        
        if this_player.ring and this_player.tile == max_tile:
            who_won = True
            gameover = True
            
        elif this_player.ring and num_cohabitors > 1:
            
            if not all_cohabitors_good:
                '''
                if the ring bearer stumbles upon a bad player
                '''
                who_won = False
                gameover = True
                
            else:
                '''
                if the ring bearer stumbles upon other good players
                '''
                who_won = None
                gameover = False
                maybe_give_away_ring ()

        
        elif this_player.good and ring_bearer_here > 0:
            '''
            if this good player stumbles upon the ring bearer
            '''
            who_won = None
            gameover = False
            maybe_take_ring ()
        
        
        elif not this_player.good and ( ( this_player.tile == max_tile ) or ( num_cohabitors > 1 and ring_bearer_here == 0 and this_player.is_chasing in cohabitor_names ) ): 
            '''
            if this bad player is on the last tile
            or happened to have landed on the tile of who they were chasing but found out they didn't have the ring after all,
            then they stop chasing that player and turn towards shire
            -- note that this can get reversed immediately if on their next turn they chase another good crosser
            -- not also that they don't pick a new good player to chase until the next round
            '''
            who_won = None
            gameover = False
            to_shire_and_stop_chasing ()

        elif not this_player.good and ring_bearer_here > 0:
            '''
            if this bad player caught or stumbled upon the ring bearer
            '''
            who_won = False
            gameover = True

        else:
            '''
            if none of those critical situations happen, just proceed
            '''
            who_won = None
            gameover = False

        new_state = GameState (whose_turn = this_turn, num_turns = state.num_turns + 1, players = all_players, winner = who_won, finished = gameover)
        return new_state

    if moves_left == 0:
        
        initial_state  = GameState (finished = False, winner = None, num_turns = 0, players = init_players, whose_turn = -1)
        return initial_state

    else:
        
        last_state = play_game ( moves_left - 1, init_players, cut_ends, die_faces )

        if not last_state.finished:
            return play_turn ( last_state )
        else:
            return last_state



# GameStatistics, GameState -> GameStatistics
def update_stats ( current_stats, new_result ):
    
    current_stats.num_games += 1
    current_stats.turns.append ( new_result.num_turns )
    
    if new_result.finished:
        current_stats.num_finished += 1

    if new_result.winner:
        current_stats.num_good_won += 1
        current_stats.winners.append ( True )

    else:
        current_stats.winners.append ( False )
            


# Ugh wanted to use this recursive function but frikkin' python exceeds max recursion depth if my num_games > 1000
# I suppose python is rightfully afraid of stack overflow
# So I guess I'll do a damn for loop, in the function after this...

# int -> GameStatistics
def play_many_games_recursively ( num_games, max_moves ):

    game_stats = GameStatistics ( num_games = 0, num_finished = 0, num_good_won = 0, turns = [], winners = [] )

    size = 70
    numplay = 6

    cuts, board = initialize_board ( size )
    print ( board )
    print ()
    cut_ends = collapse_cuts ( cuts )

    # int -> None
    def play ( games_left ):

        init_players = initialize_players ( size, numplay )
        result = play_game ( max_moves, init_players )
        update_stats ( game_stats, result )
        
        if games_left > 1:
            play ( games_left - 1 )

    play ( num_games )
    
    return game_stats



# int -> GameStatistics
def play_many_games ( cuts, num_games, *params ):

    moves_per_player, size, die_faces, numplay = params
    max_moves = moves_per_player * numplay

    game_stats = GameStatistics ( num_games = 0, num_finished = 0, num_good_won = 0, turns = [], winners = [] )

    cut_ends = collapse_cuts ( cuts )

    # int -> None
    def play ():

        init_players = initialize_players ( size, numplay )
        result = play_game ( max_moves, init_players, cut_ends, die_faces )
        update_stats ( game_stats, result )

    for i in range ( num_games ):
        play ()
    
    return game_stats


from itertools import product
from tqdm import tqdm

get_good_win_fraction = lambda stats: stats.num_good_won / stats.num_finished
get_finish_fraction = lambda stats: stats.num_finished / stats.num_games

num_boardsizes = 5
num_diefaces = 1
num_numplayers = 2
boardsizes_to_test = np.linspace ( 66, 70, num_boardsizes )
die_faces_to_test = np.linspace ( 4, 4, num_diefaces )
numplayers_to_test = np.linspace ( 4, 6, num_numplayers )
numboards_to_test = 50 

total_num_games = num_boardsizes * num_diefaces * num_numplayers * numboards_to_test

cutoff_turns_per_player = 30
min_frac_won = 0.45
max_frac_won = 0.55
desired_frac_finished_in_reasonable_time = 0.55

games_per_board = 2000


all_games = []
preferred_games_and_player_numbers = []
preferred_games = []
i = 1

pbar = tqdm ( total = total_num_games )

for boardsize, diefaces in product(boardsizes_to_test, die_faces_to_test):

    for b in range ( numboards_to_test ):

        these_cuts, this_board = initialize_board ( boardsize )
        good_for_all_player_numbers = True
    
        for numplayers in numplayers_to_test:
    
            these_params = [cutoff_turns_per_player, int(boardsize), int(diefaces), int(numplayers)]
            these_game_stats = play_many_games (these_cuts, games_per_board, *these_params)
            all_games.append ( (numplayers, diefaces, this_board, these_game_stats) )
            
            good_win_fraction = get_good_win_fraction ( these_game_stats )
            finish_fraction = get_finish_fraction ( these_game_stats )
    
            pbar.update ( 1 )
            
            if good_win_fraction < min_frac_won or good_win_fraction > max_frac_won or finish_fraction < desired_frac_finished_in_reasonable_time:
                good_for_all_player_numbers = False
            else:
                preferred_games_and_player_numbers.append ( (numplayers, diefaces, this_board, these_game_stats) )
    
        if good_for_all_player_numbers:
            for game in preferred_games_and_player_numbers[-1 * num_numplayers:]:
                preferred_games.append ( game )

pbar.close ()



i = 0
num_pref = len ( preferred_games )
for game in preferred_games:
    print( 'PREFERRED GAME NUMBER ' + str ( i + 1 ) + ' OUT OF ' + str ( num_pref ) )
    numplayers, diefaces, this_board, these_game_stats = game
    
    print ('num players', numplayers)
    print()

    print ('die faces', diefaces)
    print()

    print ('board', this_board)
    print()

    print ('good win fraction', get_good_win_fraction ( these_game_stats ) )
    print()

    print ('finish fraction', get_finish_fraction ( these_game_stats ) )
    print()
    print()
    print()

    i += 1

# save these to a .txt file
