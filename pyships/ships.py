from PIL import ImageTk

from .errortypes import HitError, LengthError

class ShipSprite:
    # Use in place wherever an ID is needed
    def __init__(self):
        self.id = None
        self.image = None
        self.photo = None
        self.degree = 0
        self.x = self.y = 0

    def copy(self) -> 'ShipSprite':
        # Return copy but without the same ID
        new_sprite = ShipSprite()
        new_sprite.x = self.x
        new_sprite.y = self.y
        new_sprite.degree = self.degree
        new_sprite.is_placed = self.is_placed
        new_sprite.image = self.image
        new_sprite.photo = ImageTk.PhotoImage(self.image)
        return new_sprite

class Ship:
    def __init__(self, length: int):
        self._length = length
        self._parts = [ShipPart(self) for p in range(length)]
        self._is_destroyed = False
        self._is_placed = False
        self._sprite = ShipSprite()

    @property
    def is_placed(self) -> bool:
        return self._is_placed

    @property
    def sprite(self) -> ShipSprite:
        return self._sprite

    @property
    def length(self) -> int:
        return self._length
    
    def start(self) -> (str, int):
        return self._parts[0].location

    def end(self) -> (str, int):
        return self._parts[-1].location

    def place(self, locations: [(str, int)]) -> None:
        if len(locations) != self._length:
            raise LengthError()

        for i in range(self._length):
            self._parts[i].place(locations[i])
            
        self._is_placed = True

    def unplace(self) -> None:
        for part in self._parts:
            part.unplace()

        self._is_placed = False
        
    def on_hit(self) -> None:
        if self._is_destroyed:
            raise HitError('Ship is already destroyed')
        hits = [part for part in self._parts if part.is_hit]
        if len(hits) == len(self._parts):
            self._is_destroyed = True

    @property
    def parts(self) -> '[ShipPart]':
        return self._parts

    @property     
    def is_destroyed(self) -> bool:
        return self._is_destroyed

class ShipPart:
    def __init__(self, owner: Ship):
        self._owner = owner
        self._is_hit = False
        self._location = None
        
    def on_hit(self) -> None:
        if self._is_hit:
            raise HitError()
        self._is_hit = True
        self._owner.on_hit()

    def place(self, location: (str, int)) -> None:
        self._location = location

    def unplace(self) -> None:
        self._location = None

    @property
    def location(self) -> (str, int):
        return self._location

    @property
    def is_hit(self) -> bool:
        return self._is_hit
    
    @property
    def owner(self) -> Ship:
        return self._owner

    def __str__(self):
        if self._is_hit:
            return 'H'
        else:
            return 'S'

        
class Carrier(Ship):
    def __init__(self):
        super().__init__(5)

class BattleShip(Ship):
    def __init__(self):
        super().__init__(4)

class Destroyer(Ship):
    def __init__(self):
        super().__init__(3)

class Submarine(Ship):
    def __init__(self):
        super().__init__(3)

class PatrolBoat(Ship):
    def __init__(self):
        super().__init__(2)
