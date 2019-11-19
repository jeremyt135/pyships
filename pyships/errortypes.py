class HitError(Exception):
    def __init__(self, message: str = 'Part has already been hit'):
        super().__init__(message)


# Error when placing ship on board
class PlacementError(Exception):
    def __init__(self, message: str = ''):
        super().__init__(message)

class ShipInWayError(PlacementError):
    def __init__(self, message: str = 'Ship in the way of placement'):
        super().__init__(message)

class OffBoardError(PlacementError):
    def __init__(self, message: str = 'Ship would be placed off ocean grid'):
        super().__init__(message)

class LengthError(PlacementError):
    def __init__(self, message: str = 'Placement would be different than ship length'):
        super().__init__(message)

class BadLocationError(Exception):
    def __init__(self, message: str = 'Location is not a location on ocean grid'):
        super().__init__(message)

class BadShotLocationError(BadLocationError):
    def __init__(self, message: str = 'Shot location is not a location on ocean grid'):
        super().__init__(message)

                    
class GameError(Exception):
    def __init__(self, message: str = ''):
        super().__init__(message)

class GameOverError(GameError):
    def __init__(self, message: str = 'Game is already over. Move cannot be taken.'):
        super().__init__(message)


# Error when placing peg on target grid
class TargetError(Exception):
    def __init__(self, message: str = ''):
        super().__init__(message)

class HasPegError(TargetError):
    def __init__(self, message: str = 'Peg location already has a peg on target grid'):
        super().__init__(message)

class BadPegLocationError(BadLocationError):
    def __init__(self, message: str = 'Peg location is not a location on target grid'):
        super().__init__(message)

