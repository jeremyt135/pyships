from PIL import Image, ImageTk
import tkinter

from . import battleship
from .battleshipconfig import *
from .errortypes import BadLocationError, PlacementError
from .gamecanvas import GameCanvas
from .targetgridcanvas import TargetGridCanvas
from .startmenucanvas import StartMenuCanvas
from .imageloader import instance as gImageLoader
from .pegsprite import PegSprite

# Canvas for setup portion of the game (placing ships). Also maintains
# visual representation of a player's own board state.
class OceanGridCanvas(GameCanvas):
    def __init__(self, parent: tkinter.Tk, player: battleship.ClassicPlayer, width: int, height: int, on_ships_are_placed: 'func'):
        super().__init__(parent, bg='blue', width=width, height=height)
        self._parent = parent
        self._width = width
        self._height = height

        self._player = player
        self._on_ships_are_placed = on_ships_are_placed

        ### load images of the board and ships ###
        ocean_grid = gImageLoader.load(OCEAN_GRID_PATH)
        self._ocean_grid_img = ocean_grid
        self._ocean_grid_photo = ImageTk.PhotoImage(self._ocean_grid_img)
        self._ocean_grid_id = None

        carrier_img = gImageLoader.load(CARRIER_PATH)
        self._carrier_img = carrier_img

        battleship_img = gImageLoader.load(BATTLESHIP_PATH)
        self._battleship_img = battleship_img

        destroyer_img = gImageLoader.load(DESTROYER_PATH)
        self._destroyer_img = destroyer_img

        patrolboat_img = gImageLoader.load(PATROLBOAT_PATH)
        self._patrolboat_img = patrolboat_img

        submarine_img = gImageLoader.load(SUBMARINE_PATH)
        self._submarine_img = submarine_img

        # Pegs to show enemy moves / hits
        self._pegs = [[PegSprite() for _ in range(battleship.COLUMNS)] for _ in range(battleship.ROWS)]

        # Images to be manipulated and turned into Photos
        self._ship_imgs = {battleship.Carrier.__name__: {0: self._carrier_img, 90: None, 180: None, 270: None, 360: None},
                           battleship.BattleShip.__name__: {0: self._battleship_img, 90: None, 180: None, 270: None, 360: None},
                           battleship.Destroyer.__name__: {0: self._destroyer_img, 90: None, 180: None, 270: None, 360: None},
                           battleship.Submarine.__name__: {0: self._submarine_img, 90: None, 180: None, 270: None, 360: None},
                           battleship.PatrolBoat.__name__: {0: self._patrolboat_img, 90: None, 180: None, 270: None, 360: None}}

        # Photos passed into create_image functions
        self._ship_photos = {battleship.Carrier.__name__: {0:ImageTk.PhotoImage(self._carrier_img),90: None, 180: None, 270: None, 360: None},
                             battleship.BattleShip.__name__: {0: ImageTk.PhotoImage(self._battleship_img), 90: None, 180: None, 270: None, 360: None},
                             battleship.Destroyer.__name__: {0: ImageTk.PhotoImage(self._destroyer_img), 90: None, 180: None, 270: None, 360: None},
                             battleship.Submarine.__name__: {0: ImageTk.PhotoImage(self._submarine_img), 90: None, 180: None, 270: None, 360: None},
                             battleship.PatrolBoat.__name__: {0:ImageTk.PhotoImage(self._patrolboat_img), 90: None, 180: None, 270: None, 360: None}}


        self._mouse_btn1_down = False
        self.bind('<Button-1>', self._on_mouse_btn1_down)
        self.bind('<ButtonRelease-1>', self._on_mouse_btn1_release)

        self._ships_are_placed = False # true if all ships placed
        self._is_placement_phase = True
        self._confirm_text_id = None
        self._confirm_text = "Press enter to confirm ship placement"
        self._confirm_x = 0
        self._confirm_y = 0
        self._confirm_width = 0
    
        self._has_ship_selected = False
        self._selected_ship = None
        self._selected_ship_type = None
        self._selected_ship_is_vertical = True
        self._selected_ship_degree = 0

    def display(self) -> None:
        print('Ocean should display')
        self._start()
        self.focus_set()
        self.pack()

    def hide(self) -> None:
        self.pack_forget()

    # sets peg colors depending on board state and redraws
    def on_hit(self) -> None:
        x_spacing = DEFAULT_PEG_AREA_WIDTH / battleship.COLUMNS
        y_spacing = DEFAULT_PEG_AREA_WIDTH / battleship.ROWS

        # set the PegSprite location, color for every peg
        for r in range(battleship.ROWS):
            for c in range(battleship.COLUMNS):
                peg = self._pegs[r][c]
                if self._player.ocean_grid.pegs[r][c] == battleship.RED:
                    peg.color = PEG_HIT
                else:
                    peg.color = PEG_MISS

                peg.x1 = c * x_spacing + DEFAULT_HEADER_WIDTH + DEFAULT_PEG_SIZE
                peg.y1 = r * y_spacing + DEFAULT_HEADER_HEIGHT + DEFAULT_PEG_SIZE
                peg.x2 = (c + 1) * x_spacing + DEFAULT_HEADER_WIDTH - DEFAULT_PEG_SIZE
                peg.y2 = (r + 1) * y_spacing + DEFAULT_HEADER_HEIGHT - DEFAULT_PEG_SIZE

                peg.id = self.create_oval((peg.x1, peg.y1), (peg.x2, peg.y2), fill=peg.color)
                self._pegs[r][c] = peg
                    
        self._redraw()

    def _start(self) -> None:
        #self.delete(self._click_text_id)
        self._redraw()
        self.bind('<Motion>', self._on_mouse_moved)
        self.bind('<Shift_L>', self._on_shift_down)
        self.bind('<Return>', self._on_return_down)

    def _on_return_down(self, event: tkinter.Event) -> None:
        if self._ships_are_placed:
            self._on_ships_are_placed()
            
            if self._confirm_text_id:
                self.delete(self._confirm_text_id)
            
            self.unbind('<Return>')
            self._is_placement_phase = False
            

    def _redraw(self) -> None:
        # Redraw ships ( and later pegs )
        if self._ocean_grid_id:
            self.delete(self._ocean_grid_id)
            
        self._ocean_grid_id = self.create_image((round(self._width/2), round(self._height/2)),
                                                image=self._ocean_grid_photo, anchor='center')

        if self._confirm_text_id:
            self.delete(self._confirm_text_id)

            if self._ships_are_placed and self._is_placement_phase:
                self._confirm_text_id = self.create_text((self._confirm_x, self._confirm_y), width=self._confirm_width,
                                                         text=self._confirm_text, fill='white', anchor='w')

        for ship in self._player.ships.values():
            if ship:
                sprite = ship.sprite
                if sprite.id:
                    self.delete(sprite.id)

                    sprite.id = self.create_image(
                        (sprite.x, sprite.y),
                        image=sprite.photo, 
                        anchor="center")

        for r in range(battleship.ROWS):
            for c in range(battleship.COLUMNS):
                if self._player.ocean_grid.pegs[r][c] != None:
                    peg = self._pegs[r][c]
                    if peg.id:
                        self.delete(peg.id)  

                    peg.id = self.create_oval((peg.x1, peg.y1), (peg.x2, peg.y2), fill=peg.color) 
    
    def _on_mouse_btn1_down(self, event: tkinter.Event) -> None:
        self._mouse_btn1_down = True

##        if not self._ships_are_placed:
        x_ratio = event.x / self.winfo_width() # ratio of click in relation to entire window
        bay_x_ratio = DEFAULT_SHIPBAY_X1 / DEFAULT_WIDTH

        print(event.x, event.y)
        print(x_ratio, bay_x_ratio)

        if self._is_placement_phase:
            if x_ratio <=1 and x_ratio >= bay_x_ratio:
                self._select_ship_from_bay(event.y)
                if self._selected_ship_type:
                    existing_ship = self._player.ships[self._selected_ship_type]
                    if existing_ship:
                        if existing_ship.is_placed:
                            self._deselect_ship(False)
                            return
                        print(self._selected_ship_type, existing_ship.is_placed)
                    
                    ROTATION_DEGREE = 0

                    selected_sprite = self._selected_ship.sprite
                    selected_sprite.x = event.x
                    selected_sprite.y = event.y
                    selected_sprite.degree = self._selected_ship_degree
                    selected_sprite.image = self._ship_imgs[self._selected_ship_type][ROTATION_DEGREE]
                    selected_sprite.photo = self._ship_photos[self._selected_ship_type][ROTATION_DEGREE]
                    selected_sprite.id = self.create_image(
                        (selected_sprite.x, selected_sprite.y),
                        image=selected_sprite.photo,
                        anchor="center") 

                    print(selected_sprite.id)

            else:
                x_ratio = DEFAULT_PEG_AREA_WIDTH / battleship.COLUMNS
                y_ratio = DEFAULT_PEG_AREA_WIDTH / battleship.ROWS

                click_col = int(event.x/x_ratio)
                col = click_col - 1
                
                click_row = int(event.y/y_ratio)
                row = click_row - 1

                row_str = None
                try:
                    row_str = battleship.ROW_LETTERS[row]
                except KeyError as e:
                    print(e)
                else:
                    try:
                        ship_at_click = self._player.ocean_grid.at((row_str, col))
                    except BadLocationError as e:
                        print(e)
                    else:
                        if ship_at_click:
                            self._select_ship(ship_at_click)
                            self._player.ocean_grid.unplace(ship_at_click)
                    
                

                
                      
    def _on_mouse_btn1_release(self, event: tkinter.Event) -> None:
        self._mouse_btn1_down = False
        if self._has_ship_selected:
            col_width = DEFAULT_PEG_AREA_WIDTH / battleship.COLUMNS
            row_height = DEFAULT_PEG_AREA_WIDTH / battleship.ROWS

            print(int(event.y/row_height))
            click_col = int(event.x/col_width)
            col = click_col - 1
            
            click_row = int(event.y/row_height)
            row = click_row - 1
            start_row = end_row = start_col = end_col = None

            if self._selected_ship_is_vertical:
                print('Vertical placement')
                if self._selected_ship.length > 2:
                    if self._selected_ship.length % 2 != 0:
                        start_row = row - int(self._selected_ship.length/2)
                        end_row = row + int(self._selected_ship.length/2)
                    else:
                        start_row = row - self._selected_ship.length % 3
                        end_row = row + int(self._selected_ship.length/2)
                else:
                    start_row = row
                    end_row = row + 1

                start_col = end_col = col
            else:
                print('Horizontal placement')
                if self._selected_ship.length > 2:
                    if self._selected_ship.length % 2 != 0:
                        start_col = col - int(self._selected_ship.length/2)
                        end_col = col + int(self._selected_ship.length/2)
                        print('col: {}, click_col: {}, start_col: {}, end_col: {}'.format(col, click_col, start_col, end_col))
                    else:
                        start_col = col - self._selected_ship.length % 3
                        end_col = col + int(self._selected_ship.length/2)
                else:
                    start_col = col
                    end_col = col + 1

                start_row = end_row = row

            try:
                start_row_str = battleship.ROW_LETTERS[start_row]
                end_row_str = battleship.ROW_LETTERS[end_row]
                print('Attempting place. Degree: {}'.format(self._selected_ship_degree))
                self._player.ocean_grid.place((start_row_str, start_col), (end_row_str, end_col), self._selected_ship)
            except PlacementError as place_error:
                print(place_error)
                print('Failed place, x: {} y: {}, row1: {} col1: {}, row2: {} col2: {}'.format(
                    event.x, event.y, start_row_str, start_col+1, end_row_str, end_col+1))
                self._deselect_ship(True)
            except KeyError as key_error:
                print('Failed place. Numeric key is out of expected range (ship will be placed out of board).')
                print('start_row: {}, end_row: {}'.format(start_row, end_row))
                print('start_col: {}, end_col: {}'.format(start_col, end_col))
                self._deselect_ship(True)
            else:
                # Player's ship should now be placed
                print(self._selected_ship.is_placed)
                selected_sprite = self._selected_ship.sprite
                if selected_sprite.id:
                    self.delete(selected_sprite.id)

                x = y = 0

                if self._selected_ship_is_vertical: 
                    if self._selected_ship.length % 2 != 0:
                        x = (click_col * DEFAULT_COL_WIDTH) + (DEFAULT_COL_WIDTH/3)
                        y = (click_row * DEFAULT_ROW_HEIGHT) + (DEFAULT_ROW_HEIGHT/3)
                    else:
                        x = (click_col * DEFAULT_COL_WIDTH) + (DEFAULT_COL_WIDTH/3)
                        y = (click_row * DEFAULT_ROW_HEIGHT) + (DEFAULT_ROW_HEIGHT * 5/6)
                else:
                    if self._selected_ship.length % 2 != 0:
                        x = (click_col * DEFAULT_COL_WIDTH) + (DEFAULT_COL_WIDTH /3)
                        y = (click_row * DEFAULT_ROW_HEIGHT) + (DEFAULT_ROW_HEIGHT/3)
                    else:
                        x = (click_col * DEFAULT_COL_WIDTH) + (DEFAULT_COL_WIDTH * 5/6)
                        y = (click_row * DEFAULT_ROW_HEIGHT) + (DEFAULT_ROW_HEIGHT/3)
                    
                print('Click: {}, {}. Placed at: {},{}'.format(event.x, event.y, x, y))
                print('row1: {} col1: {}, row2: {} col2: {}'.format(start_row_str, start_col+1, end_row_str, end_col+1))
                print('Degrees: {}'.format(self._selected_ship_degree))

                selected_sprite.x = x
                selected_sprite.y = y
                selected_sprite.degree = self._selected_ship_degree
                selected_sprite.image = self._ship_imgs[self._selected_ship_type][self._selected_ship_degree]
                selected_sprite.photo = self._ship_photos[self._selected_ship_type][self._selected_ship_degree]
                selected_sprite.id = self.create_image(
                    (selected_sprite.x, selected_sprite.y),
                    image=selected_sprite.photo,
                    anchor="center")

                self._player.ships[self._selected_ship_type] = self._selected_ship
                print(self._player.ships)
                
                self._deselect_ship(False)

                print('Checking if all placed')
                self._ships_are_placed = self._player.ships_are_placed()
                if self._ships_are_placed:
                    print('all placed: {}'.format(self._ships_are_placed))
                    print('All ships placed')
##                    self._on_ships_are_placed()
                    self._draw_confirm_text()

            if self._is_placement_phase and not self._ships_are_placed and self._confirm_text_id:
                self.delete(self._confirm_text_id)

                    

    def _draw_confirm_text(self) -> None:
        self._confirm_x = DEFAULT_SHIPBAY_X1
        self._confirm_y = DEFAULT_SHIPBAY_Y2 + DEFAULT_ROW_HEIGHT
        self._confirm_width = DEFAULT_WIDTH - self._confirm_x

        if self._confirm_text_id:
            self.delete(self._confirm_text_id)
        self._confirm_text_id = self.create_text((self._confirm_x, self._confirm_y), width=self._confirm_width,
                                                 fill='white', text=self._confirm_text, anchor='w')

    def _select_ship(self, ship: battleship.Ship) -> None:
        self._has_ship_selected = True
        self._selected_ship = ship
        self._selected_ship_type = type(ship).__name__
        print(self._selected_ship_type)
        self._selected_ship_degree = ship.sprite.degree
        self._selected_ship_is_vertical = (self._selected_ship_degree == 0
                                               or self._selected_ship_degree == 180
                                               or self._selected_ship_degree == 360)
        self._ships_are_placed = False
        
    def _select_ship_from_bay(self, y: int) -> None:
        ship = self._get_bay_ship_type(y)
        if ship:
            self._has_ship_selected = True
            self._selected_ship = ship()
            self._selected_ship_type = ship.__name__
            print(self._selected_ship_type)
            self._selected_ship_degree = 0
            self._selected_ship_is_vertical = True

    def _deselect_ship(self, should_delete: bool) -> None:
        # Deselect currently selected ship
        selected_sprite = self._selected_ship.sprite
        if selected_sprite.id:
            if should_delete:
                self.delete(selected_sprite.id)

                self._player.ships[self._selected_ship_type] = None
                
        self._has_ship_selected = False
        self._selected_ship = None
        self._selected_ship_type = None
        self._selected_ship_degree = 0
        self._selected_ship_is_vertical = True
        
    def _on_mouse_moved(self, event: tkinter.Event) -> None:
        if self._mouse_btn1_down:
            if self._has_ship_selected and self._is_placement_phase:
                if self._is_placement_phase and not self._ships_are_placed and self._confirm_text_id:
                    self.delete(self._confirm_text_id)
                    
                selected_sprite = self._selected_ship.sprite
                if selected_sprite.id:
                    self.delete(selected_sprite.id)
                    selected_sprite.x = 0
                    selected_sprite.y = 0
                    selected_sprite.degree = 0
                    selected_sprite.photo = None
                    selected_sprite.image = None


                selected_sprite.x = event.x
                selected_sprite.y = event.y
                selected_sprite.degree = self._selected_ship_degree
                selected_sprite.image = self._ship_imgs[self._selected_ship_type][self._selected_ship_degree]
                selected_sprite.photo = self._ship_photos[self._selected_ship_type][self._selected_ship_degree]
                selected_sprite.id = self.create_image(
                    (event.x, event.y),
                    image=selected_sprite.photo,
                    anchor="center")
            
    def _on_shift_down(self, event: tkinter.Event) -> None:
        if self._mouse_btn1_down and self._has_ship_selected:
            ROTATION_DEGREE = 90
            
            if self._selected_ship_degree >= 360:
                self._selected_ship_degree = 0
            self._selected_ship_degree += ROTATION_DEGREE
            
            

            print('[SHIFT] Degree: {}'.format(self._selected_ship_degree))

            self._selected_ship_is_vertical = (self._selected_ship_degree == 0
                                               or self._selected_ship_degree == 180
                                               or self._selected_ship_degree == 360)


            
            
            if not self._ship_photos[self._selected_ship_type][self._selected_ship_degree]:
                BASE_DEGREE = 0
                self._ship_imgs[self._selected_ship_type][self._selected_ship_degree] = (
                    self._ship_imgs[self._selected_ship_type][BASE_DEGREE].rotate(self._selected_ship_degree, expand=True))
                
                self._ship_photos[self._selected_ship_type][self._selected_ship_degree] = (
                    ImageTk.PhotoImage(self._ship_imgs[self._selected_ship_type][self._selected_ship_degree]))


            selected_sprite = self._selected_ship.sprite
            if selected_sprite.id:
                    self.delete(selected_sprite.id)
                    selected_sprite.x = 0
                    selected_sprite.y = 0
                    selected_sprite.degree = 0
                    selected_sprite.photo = None
                    selected_sprite.image = None


            selected_sprite.x = event.x
            selected_sprite.y = event.y
            selected_sprite.degree = self._selected_ship_degree
            selected_sprite.image = self._ship_imgs[self._selected_ship_type][self._selected_ship_degree]
            selected_sprite.photo = self._ship_photos[self._selected_ship_type][self._selected_ship_degree]
            selected_sprite.id = self.create_image(
                (selected_sprite.x, selected_sprite.y),
                image=selected_sprite.photo,
                anchor="center")   

    def _get_bay_ship_type(self, y: int) -> battleship.Ship:
        y_ratio = y / self.winfo_height()
        height = DEFAULT_HEIGHT
        
        patrolboat_y1_ratio = 0
        patrolboat_y2_ratio = DEFAULT_PATROLBOAT_Y2 / height
        battleship_y1_ratio = DEFAULT_BATTLESHIP_Y1 / height
        battleship_y2_ratio = DEFAULT_BATTLESHIP_Y2 / height
        submarine_y1_ratio = DEFAULT_SUBMARINE_Y1 / height
        submarine_y2_ratio = DEFAULT_SUBMARINE_Y2 / height
        carrier_y1_ratio = DEFAULT_CARRIER_Y1 / height
        carrier_y2_ratio = DEFAULT_CARRIER_Y2 / height
        destroyer_y1_ratio = DEFAULT_DESTROYER_Y1 / height
        destroyer_y2_ratio = DEFAULT_DESTROYER_Y2 / height

        if y_ratio >= patrolboat_y1_ratio and y_ratio <= patrolboat_y2_ratio:
            return battleship.PatrolBoat
        if y_ratio >= battleship_y1_ratio and y_ratio <= battleship_y2_ratio:
            return battleship.BattleShip
        if y_ratio >= submarine_y1_ratio and y_ratio <= submarine_y2_ratio:
            return battleship.Submarine
        if y_ratio >= carrier_y1_ratio and y_ratio <= carrier_y2_ratio:
            return battleship.Carrier
        if y_ratio >= destroyer_y1_ratio and y_ratio <= destroyer_y2_ratio:
            return battleship.Destroyer

        return None
        