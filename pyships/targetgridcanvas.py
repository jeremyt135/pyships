import tkinter
from PIL import Image, ImageTk

from . import battleship
from .battleshipconfig import (
    DEFAULT_PEG_AREA_WIDTH,
    DEFAULT_PEG_SIZE, 
    DEFAULT_HEADER_HEIGHT, 
    DEFAULT_HEADER_WIDTH,
    TARGET_GRID_PATH,
    DEFAULT_SHIPBAY_X1,
    DEFAULT_WIDTH
    )
from .gamecanvas import GameCanvas
from .imageloader import instance as gImageLoader
from .pegsprite import PegSprite

# Canvas for the core gameplay (clicking grids to find opponent ships). Maintains
# the visual representation of the opponent's grid from discovered information.
class TargetGridCanvas(GameCanvas):
    def __init__(self, parent: tkinter.Tk, player: battleship.ClassicPlayer, width: int, height: int, on_shot_attempt: 'str (*)(str, int)'):
        super().__init__(parent, bg='blue', width=width, height=height)
        self._parent = parent
        self._width = width
        self._height = height

        self._player = player
        self._on_shot_attempt = on_shot_attempt # callback to determine if a grid location contains an enemy ship

        # Create background image of game board (2D matrix of pegs)
        target_grid = gImageLoader.load(TARGET_GRID_PATH)
        self._target_grid_img = target_grid
        self._target_grid_photo = ImageTk.PhotoImage(self._target_grid_img)
        self._target_grid_id = None

        # Initialize peg locations
        self._pegs = [[PegSprite() for _ in range(battleship.COLUMNS)] for _ in range(battleship.ROWS)]
        
        # Enemy ships placed onto canvas
        self._sunk_ships = []

        # Has the player clicked
        self._has_clicked = False
        
        # Click position
        self._shot_row = None
        self._shot_col = None

        # Attempted shots are shown as green pegs
        self._ATTEMPTED_SHOT_COLOR = 'green'
        self._shot_attempt_peg = None

        # Confirmation text for taking a shot
        self._confirm_text_id = None
        self._confirm_text = "Press enter to confirm shot at {}-{}"
        self._confirm_x = 0
        self._confirm_y = 0
        self._confirm_width = 0

    def display(self) -> None:
        print('Target should display')
        self._start()
        self.focus_set()
        self.pack()

    def hide(self) -> None:
        self.pack_forget()

    def on_sunk_ship(self, ship: battleship.Ship) -> None:
        # add sunken ship to the player's game board (drawn ship is opponent's)
        self._sunk_ships.append(ship)
        self._redraw()
        
    # redraws the entire play area
    def _redraw(self) -> None:
        if self._target_grid_id:
            self.delete(self._target_grid_id)
            
        # redraw grid
        self._target_grid_id = self.create_image((round(self._width/2), round(self._height/2)),
                                                image=self._target_grid_photo, anchor='center')

        # redraw confirmation text
        if self._confirm_text_id:
            self.delete(self._confirm_text_id)

        if self._has_clicked:
            self._confirm_text_id = self.create_text((self._confirm_x, self._confirm_y), width=self._confirm_width,
                                                 fill='white',
                                                 text=self._confirm_text.format(battleship.ROW_LETTERS[self._shot_row], self._shot_col + 1),
                                                 anchor='w')

        # redraw the green attempted shot peg
        if self._has_clicked and self._shot_attempt_peg:
            if self._shot_attempt_peg.id:
                self.delete(self._shot_attempt_peg.id)

            self._shot_attempt_peg.id = self.create_oval((self._shot_attempt_peg.x1, self._shot_attempt_peg.y1),
                             (self._shot_attempt_peg.x2, self._shot_attempt_peg.y2),
                             fill=self._shot_attempt_peg.color)
        
        # redraw all pegs
        for r in range(battleship.ROWS):
            for c in range(battleship.COLUMNS):
                peg = self._pegs[r][c]
                if peg.id:
                    self.delete(peg.id)

                peg.id = self.create_oval((peg.x1, peg.y1), (peg.x2, peg.y2), fill=peg.color)

        # draw opponent's sunken ships
        for ship in self._sunk_ships:
            sprite = ship.sprite
            if sprite.id:
                self.delete(sprite.id)

            sprite.id = self.create_image(
                    (sprite.x, sprite.y),
                    image=sprite.photo, 
                    anchor="center")

            

    def _on_mousebtn1_down(self, event: tkinter.Event) -> None:
        x_spacing = DEFAULT_PEG_AREA_WIDTH / battleship.COLUMNS
        y_spacing = DEFAULT_PEG_AREA_WIDTH / battleship.ROWS

        # get the row and column (grid on the board) of the click
        click_col = int(event.x/x_spacing)
        col = click_col - 1

        click_row = int(event.y/y_spacing)
        row = click_row - 1

        row_str = None
        
        # determine if the click is a valid spot on the grid of pegs
        try:
            row_str = battleship.ROW_LETTERS[row]
            if col >= battleship.COLUMNS:
                raise ValueError()
        except (KeyError, ValueError) as err:
            print('Bad Target click location: {}-{}'.format(row, col+1))
        else:
            self._has_clicked = True
            self._shot_row = row
            self._shot_col = col
            self._draw_attempted_shot() 
            self._draw_confirm_text()
            
    # draws a green peg at the player's last click location
    def _draw_attempted_shot(self) -> None:
        if self._shot_attempt_peg:
            if self._shot_attempt_peg.id:
                self.delete(self._shot_attempt_peg.id)

        if self._confirm_text_id:
            self.delete(self._confirm_text_id)
        
        x_spacing = DEFAULT_PEG_AREA_WIDTH / battleship.COLUMNS
        y_spacing = DEFAULT_PEG_AREA_WIDTH / battleship.ROWS
        
        peg = PegSprite()
        peg.color = self._ATTEMPTED_SHOT_COLOR
        peg.x1 = self._shot_col * x_spacing + DEFAULT_HEADER_WIDTH + DEFAULT_PEG_SIZE
        peg.y1 = self._shot_row * y_spacing + DEFAULT_HEADER_HEIGHT + DEFAULT_PEG_SIZE
        peg.x2 = (self._shot_col + 1) * x_spacing + DEFAULT_HEADER_WIDTH - DEFAULT_PEG_SIZE
        peg.y2 = (self._shot_row + 1) * y_spacing + DEFAULT_HEADER_HEIGHT - DEFAULT_PEG_SIZE
        # peg.id = peg.id = self.create_oval((peg.x1, peg.y1), (peg.x2, peg.y2), fill=peg.color)
        peg.id = self.create_oval((peg.x1, peg.y1), (peg.x2, peg.y2), fill=peg.color)
        self._shot_attempt_peg = peg

    # draws a message displaying the row-column location the player clicked
    def _draw_confirm_text(self) -> None:
        self._confirm_x = DEFAULT_SHIPBAY_X1
        self._confirm_y = DEFAULT_HEADER_HEIGHT
        self._confirm_width = DEFAULT_WIDTH - self._confirm_x
        
        self._confirm_text_id = self.create_text((self._confirm_x, self._confirm_y), width=self._confirm_width,
                                                 fill='white',
                                                 text=self._confirm_text.format(battleship.ROW_LETTERS[self._shot_row], self._shot_col + 1),
                                                 anchor='w')

    # attempt to send a shot at the other player
    def _on_return_down(self, event: tkinter.Event) -> None:
        if self._has_clicked:
            # determine if the shot hit a ship on the other board
            color = self._on_shot_attempt(battleship.ROW_LETTERS[self._shot_row], self._shot_col)

            if color: # only get a color back if click was good, but may not be a hit
                x_spacing = DEFAULT_PEG_AREA_WIDTH / battleship.COLUMNS
                y_spacing = DEFAULT_PEG_AREA_WIDTH / battleship.ROWS

                # draw a peg representing the hit or miss
                peg = PegSprite()
                peg.color = color
                peg.x1 = self._shot_col * x_spacing + DEFAULT_HEADER_WIDTH + DEFAULT_PEG_SIZE
                peg.y1 = self._shot_row * y_spacing + DEFAULT_HEADER_HEIGHT + DEFAULT_PEG_SIZE
                peg.x2 = (self._shot_col + 1) * x_spacing + DEFAULT_HEADER_WIDTH - DEFAULT_PEG_SIZE
                peg.y2 = (self._shot_row + 1) * y_spacing + DEFAULT_HEADER_HEIGHT - DEFAULT_PEG_SIZE
                peg.id = self.create_oval((peg.x1, peg.y1), (peg.x2, peg.y2), fill=peg.color)
                self._pegs[self._shot_row][self._shot_col] = peg

                self._has_clicked = False
                self._attempted_shot = None

                if self._confirm_text_id:
                    self.delete(self._confirm_text_id)
            
    def _start(self) -> None:
       self._redraw()
       self.bind('<Button-1>', self._on_mousebtn1_down)
       self.bind('<Return>', self._on_return_down)
