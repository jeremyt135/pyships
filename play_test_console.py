from pyships.battleship import *

def play() -> None:
    player1 = ClassicPlayer(name='Player1')
    player2 = ClassicPlayer(name='Player2')
    players = [player1, player2]

    for p in range(2):
        print('Player {} setup:'.format(p+1))
        _place_ships(players[p])

    game = ClassicGame(player1, player2)

    while not game.is_over:
        while True:
            print('YOUR OCEAN, PLAYER {}'.format(game.current_player.name))
            print(game.current_player.ocean_grid, end = '\n\n')
            print('YOUR TARGETS, PLAYER {}'.format(game.current_player.name))
            print(game.current_player.target_grid, end = '\n\n')
            loc = input('Player {}\'s move: '.format(game.current_player.name)).split('-')
            row, col = loc[0], (int(loc[1]) - 1)
            hit_ship = False
            try:
                hit_ship = game.take_shot((row, col))
            except Exception as e:
                print(e)
            else:
                if hit_ship:
                    print('HIT!')
                else:
                    print('MISS!')
                break

    print('Winner is {}'.format(game.winner.name))
    
def _parse_loc(msg: str) -> (str, int):
    loc = input(msg).split('-')
    return (loc[0], int(loc[1]) - 1)

def _place_ships(player) -> None:
    print(player.ocean_grid)
    player.ocean_grid.place(_parse_loc('Enter start for your Carrier (Letter-Number): '),
                     _parse_loc('Enter end for your Carrier: '),
                     Carrier())
    print(player.ocean_grid)
    player.ocean_grid.place(_parse_loc('Enter start for your BattleShip (Letter-Number): '),
                     _parse_loc('Enter end for your BattleShip: '),
                     BattleShip())
    print(player.ocean_grid)
    player.ocean_grid.place(_parse_loc('Enter start for your Destroyer (Letter-Number): '),
                     _parse_loc('Enter end for your Destroyer: '),
                     Destroyer())
    print(player.ocean_grid)
    player.ocean_grid.place(_parse_loc('Enter start for your Submarine (Letter-Number): '),
                     _parse_loc('Enter end for your Submarine: '),
                     Submarine())
    print(player.ocean_grid)
    player.ocean_grid.place(_parse_loc('Enter start for your Patrol Boat (Letter-Number): '),
                     _parse_loc('Enter end for your Patrol Boat: '),
                     PatrolBoat())
    print(player.ocean_grid)

if __name__=='__main__':
    play()
    

