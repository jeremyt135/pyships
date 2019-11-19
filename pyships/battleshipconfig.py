### Hard coded config values, these are required to make the game work correctly ###

# Sprite filepaths
OCEAN_GRID_PATH = 'res/battleship_ocean.gif'
TARGET_GRID_PATH = 'res/battleship_target.gif'
CARRIER_PATH = 'res/carrier.gif'
BATTLESHIP_PATH = 'res/battleship.gif'
PATROLBOAT_PATH = 'res/patrolboat.gif'
SUBMARINE_PATH = 'res/submarine.gif'
DESTROYER_PATH = 'res/destroyer.gif'

# Canvas dimensions
DEFAULT_WIDTH = 765
DEFAULT_HEIGHT = 650

# Location of ship bay (ship placement sprites)
DEFAULT_SHIPBAY_X1 = 665
DEFAULT_SHIPBAY_Y2 = 500

# Y positions of ship sprites in ship bay
DEFAULT_PATROLBOAT_Y1 = 0
DEFAULT_PATROLBOAT_Y2 = 49
DEFAULT_BATTLESHIP_Y1 = 50
DEFAULT_BATTLESHIP_Y2 = 109
DEFAULT_SUBMARINE_Y1 = 110
DEFAULT_SUBMARINE_Y2 = 169
DEFAULT_CARRIER_Y1 = 170
DEFAULT_CARRIER_Y2 = 229
DEFAULT_DESTROYER_Y1 = 230
DEFAULT_DESTROYER_Y2 = 289

# Ocean (play area) dimensions
DEFAULT_OCEANGRID_WIDTH = 650
DEFAULT_PEG_AREA_WIDTH = 600
DEFAULT_COL_WIDTH = 60
DEFAULT_ROW_HEIGHT = 60
# Row and column label grid dimensions
DEFAULT_HEADER_HEIGHT = DEFAULT_HEADER_WIDTH = 50


# pixel offset and diameter of the peg circle from the edge of its containing cell
DEFAULT_PEG_SIZE = 20 

# peg colors
PEG_HIT = 'red'
PEG_MISS = '#B4D1F0'