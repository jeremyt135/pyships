from PIL import Image, ImageTk

from .errortypes import (
    OffBoardError, 
    LengthError, 
    ShipInWayError, 
    BadShotLocationError,
    BadLocationError,
    GameError,
    GameOverError,
    TargetError,
    BadPegLocationError,
    HasPegError
    )

from .ships import (
    Ship,
    ShipPart,
    BattleShip,
    Carrier,
    Destroyer,
    Submarine,
    PatrolBoat
)

ROWS = 10
COLUMNS = 10
ROW_NUMBERS = {'A':0, 'B': 1, 'C': 2, 'D': 3, 'E':4,
                'F':5, 'G': 6, 'H': 7, 'I': 8, 'J': 9}
ROW_LETTERS = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E',
                5:'F', 6:'G', 7:'H', 8:'I', 9:'J'}

def _location_is_valid(location: (str, int)) -> bool:
    if location[0] in ROW_NUMBERS:
        row = ROW_NUMBERS[location[0]]
        col = location[1]

        return not (row < 0 or row >= ROWS
                    or col < 0 or col >= COLUMNS)


    return False
        
RED = _HIT = 1
WHITE = _MISS = 0

def _place_ship_parts(start: (str, int), end: (str, int), holes: [[ShipPart]], ship: Ship) -> None:
    if not _location_is_valid(start) or not _location_is_valid(end):
        raise OffBoardError()
    
    start_row, start_col = ROW_NUMBERS[start[0]], start[1]
    end_row, end_col = ROW_NUMBERS[end[0]], end[1]

    if (start_row != end_row) and (start_col != end_col):
        raise OffBoardError()

    assumed_length = 0
    if start_row == end_row:
        assumed_length = abs(end_col - start_col) + 1
    else:
        assumed_length = abs(end_row - start_row) + 1
        
    actual_length = ship.length

    if assumed_length != actual_length:
        raise LengthError()
    
    is_vertical = start_row != end_row

    locations = []
    if is_vertical:
        row = 0
        col = start_col
        if start_row < end_row:
            row = start_row
        else:
            row = end_row
        for i in range(ship.length):
            if not holes[row + i][col]:
                locations.append((ROW_LETTERS[row + i], col))
                holes[row + i][col] = ship.parts[i]
            else:
                raise ShipInWayError()
    else:
        col = 0
        row = start_row
        if start_col < end_col:
            col = start_col
        else:
            col = end_col
            
        for i in range(ship.length):
            if not holes[row][col + i]:
                locations.append((ROW_LETTERS[row], col + i))
                holes[row][col + i] = ship.parts[i]
            else:
                raise ShipInWayError()

    ship.place(locations)

class OceanGrid:
    def __init__(self):
        # Cells to place ships on 
        self._holes = [[None for c in range(COLUMNS)] for r in range(ROWS)]
        # Cells for pegs
        self._pegs = [[None for c in range(COLUMNS)] for r in range(ROWS)]

    def place(self, start: (str, int), end: (str, int), ship: Ship) -> None:
        _place_ship_parts(start, end, self._holes, ship)

    def unplace(self, ship: Ship) -> None:
        part_locations = [part.location for part in ship.parts]

        for loc in part_locations:
            row = ROW_NUMBERS[loc[0]]
            col = loc[1]
            # TODO: Raise UnplaceError if part has been shot
            self._holes[row][col] = None
            
        ship.unplace()

    def shoot(self, location: (str, int)) -> bool:
        if not _location_is_valid(location):
            raise BadShotLocationError()
        
        shot_row, shot_col = ROW_NUMBERS[location[0]], location[1]
        ship_part = self._holes[shot_row][shot_col]

        if ship_part:
            ship_part.on_hit()
            self._place_peg(location, _HIT)
            return True
        else:
            self._place_peg(location, _MISS)
            return False

        
        return False

    def at(self, location: (str, int)) -> Ship:
        # Return the ship at location
        if not _location_is_valid(location):
            raise BadLocationError()

        row, col = ROW_NUMBERS[location[0]], location[1]
        part = self._holes[row][col]
        part_owner = None
        if part:
            part_owner = part.owner

        return part_owner

    @property
    def pegs(self) -> [[int]]:
        return self._pegs

    def _place_peg(self, location: (str, int), peg: int) -> None:
        shot_row, shot_col = ROW_NUMBERS[location[0]], location[1]
        if not self._pegs[shot_row][shot_col]:
            self._pegs[shot_row][shot_col] = peg

        
    def __str__(self):
        string = '  '
        part_str = '{:<2}'
        for c in range(COLUMNS):
            string += '{:<2}'.format(c+1)
        string += '\n'
        for r in range(ROWS):
            string += '{} '.format(ROW_LETTERS[r])
            for c in range(COLUMNS):
                if self._holes[r][c]:
                    string += part_str.format(str(self._holes[r][c]))
                else:
                    if self._pegs[r][c] != None:
                        string += part_str.format(self._pegs[r][c])
                    else:
                        string += part_str.format('..')
            string += '\n'

        return string.rstrip()

class TargetGrid:
    def __init__(self):
        # Pegs to place hit/miss markers on
        self._pegs = [[None for c in range(COLUMNS)] for r in range(ROWS)]

        # Enemy destroyed ship parts
        self._enemy_ships = [[None for c in range(COLUMNS)] for r in range(ROWS)]

    def hit(self, location: (str, int)) -> None:
        self._place_peg(location, _HIT)

    def miss(self, location: (str, int)) -> None:
        self._place_peg(location, _MISS)

    def place_enemy(self, start: (str, int), end: (str, int), ship: Ship) -> None:
        # Place enemy ship parts
        _place_ship_parts(start, end, self._enemy_ships, ship)
        
        
    def _place_peg(self, location: (str, int), peg: int) -> None:
        if not _location_is_valid(location):
            raise BadPegLocationError()
        peg_row, peg_col = ROW_NUMBERS[location[0]], location[1]
        
        if self._pegs[peg_row][peg_col] != None:
            raise HasPegError()

        self._pegs[peg_row][peg_col] = peg

    def __str__(self):
        string = '  '
        part_str = '{:<2}'
        for c in range(COLUMNS):
            string += '{:<2}'.format(c+1)
        string += '\n'
        for r in range(ROWS):
            string += '{} '.format(ROW_LETTERS[r])
            for c in range(COLUMNS):
                if self._enemy_ships[r][c]:
                    string += part_str.format(str(self._enemy_ships[r][c]))
                else:
                    if self._pegs[r][c] != None:
                        string += part_str.format(self._pegs[r][c])
                    else:
                        string += part_str.format('..')
            string += '\n'

        return string.rstrip()

class ClassicPlayer:
    def __init__(self, name: str = 'Player',
                 ocean_grid: OceanGrid = None, target_grid: TargetGrid = None, ships: 'dict[str:Ship]' = None):
        self.name = name
        self.ocean_grid = ocean_grid if ocean_grid is not None else OceanGrid()
        self.target_grid = target_grid if target_grid is not None else TargetGrid()
        DEFAULT_SHIPS = {Carrier.__name__: None, BattleShip.__name__: None, Destroyer.__name__: None,
                         Submarine.__name__: None, PatrolBoat.__name__: None}
        self.ships = ships if ships is not None else DEFAULT_SHIPS

    def ships_are_placed(self) -> bool:
        # determine if all the player's ships are placed
        all_placed = True
        if self.ships:
            all_placed = all(list(self.ships.values()))
            
##            for ship_type, ship in self.ships.items():
##                if not ship:
##                    all_placed = False
##                    break
        return all_placed

    def ships_are_destroyed(self) -> bool:
        destroyed_ships = list(filter(lambda ship: ship.is_destroyed, self.ships.values()))
        return len(destroyed_ships) == len(self.ships)
        

class ClassicGame:
    def __init__(self, player1: ClassicPlayer, player2: ClassicPlayer):
        # TODO: validate that both player's grids are valid (5 ships, empty target)
        self._player1 = player1
        self._player2 = player2
        self._current_player = player1
        self._is_over = False
        self._winner = None

    def take_shot(self, location: (str, int)) -> Ship:
        # Return the ship that was hit
        opponent = None
        player = None
        if self._current_player == self._player1:
            opponent = self._player2
            player = self._player1
        else:
            opponent = self._player1
            player = self._player2
            
        opponent_ocean_grid = opponent.ocean_grid
        current_target_grid = player.target_grid

        is_hit = False
        
        if not self._is_over:
            is_hit = opponent_ocean_grid.shoot(location)
        else:
            raise GameOverError()

        hit_ship = None
        if is_hit:
            hit_ship = opponent_ocean_grid.at(location)
            if hit_ship.is_destroyed:
                current_target_grid.place_enemy(hit_ship.start(), hit_ship.end(), hit_ship)

            # Mark spot with peg
            current_target_grid.hit(location)
            #opponent_destroyed_ships = [ship for ship in opponent.ships if ship.is_destroyed]
##            opponent_destroyed_ships = list(filter(lambda ship: ship.is_destroyed, opponent.ships.values()))
            opponent_ships_are_destroyed = opponent.ships_are_destroyed()
##            opponent_destroyed_ships = [opponent.ships[name] for name in opponent.ships if opponent.ships[name].is_destroyed]
##            if len(opponent_destroyed_ships) == len(opponent.ships):
            if opponent_ships_are_destroyed:
                self._is_over = True
                self._winner = player
        else:
            current_target_grid.miss(location)       

        if self._current_player == self._player1:
            self._current_player = self._player2
        else:
            self._current_player = self._player1
            
        return hit_ship

    @property
    def winner(self) -> ClassicPlayer:
        return self._winner
    
    @property
    def current_player(self) -> int:
        return self._current_player

    @property
    def is_over(self) -> bool:
        return self._is_over
