from PIL import Image, ImageTk
import tkinter

from . import battleship
from .battleshipconfig import *
from .errortypes import (
    GameError, 
    BadLocationError,
    HitError, 
    TargetError
    )
from .oceangridcanvas import OceanGridCanvas
from .startmenucanvas import StartMenuCanvas
from .targetgridcanvas import TargetGridCanvas

class BattleshipGame(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self._game_in_progress = False

        self._width = DEFAULT_WIDTH
        self._height = DEFAULT_HEIGHT

        self._player1 = self._player2 = None
        self._player_placing = None
        self._next_player_placing = None
        self._placement_phase = True
        self._game = None

        self._ocean_canvases = dict()
        self._target_canvases = dict()
        self._gamecanvas_is_ocean = False
        self._gamecanvas = None

        self._INFO_LABEL_HEIGHT = 100
        self._FONT = 'Arial'
        self._FONTSIZE = int(self._INFO_LABEL_HEIGHT / 3)

        self._TURN_TEXT = "{}'s turn to shoot"
        self._HIT_TEXT = "{} hit a ship at {}-{}"
        self._MISS_TEXT = "{}'s shot didn't hit anything" 
        self._PLACEMENT_TEXT = "{}'s placement phase"
        self._WINNER_TEXT = "{} won the game! Showing opponent's ships."
        self._info_text = ''

        self._info_label = tkinter.Label(self, width=self._width, height=self._INFO_LABEL_HEIGHT)
        self._gamecanvas_frame = tkinter.Frame(self, width=self._width, height=self._height)
        
        self._menucanvas = StartMenuCanvas(self, self._width, self._height, self._on_game_start)
        self._menucanvas.display()    
        

    def _on_game_start(self, player1: battleship.ClassicPlayer, player2: battleship.ClassicPlayer) -> None:
        self._player1 = player1
        self._player2 = player2
        if self._player1 and self._player2:
            
            self._game = battleship.ClassicGame(self._player1, self._player2)
            self._ocean_canvases[self._player1] = OceanGridCanvas(self._gamecanvas_frame, self._player1, self._width, self._height, self._on_ships_are_placed)
            self._target_canvases[self._player1] = TargetGridCanvas(self._gamecanvas_frame, self._player1, self._width, self._height, self._on_shot_attempt)

            self._ocean_canvases[self._player2] = OceanGridCanvas(self._gamecanvas_frame, self._player2, self._width, self._height, self._on_ships_are_placed)
            self._target_canvases[self._player2] = TargetGridCanvas(self._gamecanvas_frame, self._player2, self._width, self._height, self._on_shot_attempt)

            self._menucanvas.hide()
            self._player_placing = self._player1
            self._next_player_placing = self._player2
            
            self._gamecanvas = self._ocean_canvases[self._player_placing]

            self._info_text = self._PLACEMENT_TEXT.format(self._player_placing.name)
            self._set_info_label_text(self._info_text)

            self._gamecanvas_frame.pack(side=tkinter.TOP)
            self._info_label.pack(side=tkinter.TOP)
            self.geometry('{}x{}'.format(DEFAULT_WIDTH, DEFAULT_HEIGHT + self._INFO_LABEL_HEIGHT))
            self.pack_propagate(False)
            
            self._gamecanvas.display()

            self._gamecanvas_is_ocean = True
            self.bind('<Control_L>', lambda e: self._on_control_down())

    def _set_info_label_text(self, text: str) -> None:
        self._info_label.config(text=text, font=(self._FONT, self._FONTSIZE))

    def _swap_canvas(self) -> None:
        # swap to current player's target canvas and back
        self._gamecanvas.hide()
        if self._gamecanvas_is_ocean:
            self._gamecanvas_is_ocean = False
            self._gamecanvas = self._target_canvases[self._game.current_player]
        else:
            self._gamecanvas_is_ocean = True
            self._gamecanvas = self._ocean_canvases[self._game.current_player]
        self._gamecanvas.display()
        
    def _on_control_down(self) -> None:
        if not self._placement_phase:
            self._swap_canvas()

    def _on_shot_attempt(self, row: str, col: int) -> str:
        # Player attempts to shoot using their target grid
        color = None
        attacker = self._game.current_player
        if not self._game.is_over:
            hit_ship = None
            try:
                # The shot is taken by the 'current player' which, if the turn is valid,
                # causes the 'current player' to be the next player...
                hit_ship = self._game.take_shot((row, col))
            except (GameError, BadLocationError,
                    HitError, TargetError) as e:
                print(e)
            else:
                if hit_ship:
                    self._set_info_label_text(self._HIT_TEXT.format(self._game.current_player.name, row, col+1))
                    color = PEG_HIT
                    if hit_ship.is_destroyed:
                        print('Destroyed: {}'.format(type(hit_ship).__name__))
                        # ship_owner_canvas = self._ocean_canvases[self._game.current_player]
                        self._target_canvases[attacker].on_sunk_ship(hit_ship)
                else:
                    self._set_info_label_text(self._MISS_TEXT.format(self._game.current_player.name))
                    color = PEG_MISS

                #now we want to do the on_hit of the 'current player' which will no longer
                #be the same player that fired the shot.
                self._ocean_canvases[self._game.current_player].on_hit()

                if not self._game.is_over:
                    self._on_player_turn()
                else:
                    self._on_game_over()

        return color
        
            
            
    def _on_ships_are_placed(self) -> None:
        self._gamecanvas.hide()
        if self._next_player_placing:
            self._player_placing = self._next_player_placing
            self._next_player_placing = None # Only handles 2 players so no next placing player
            
            self._info_text = self._PLACEMENT_TEXT.format(self._player_placing.name)
            self._set_info_label_text(self._info_text)
            
            self._gamecanvas = self._ocean_canvases[self._player_placing]
            
            self._gamecanvas.display()
            
        if self._player1.ships_are_placed() and self._player2.ships_are_placed():
            self._placement_phase = False

            self._info_text = self._TURN_TEXT.format(self._game.current_player.name)
            self._set_info_label_text(self._info_text)
            
            self._gamecanvas = self._target_canvases[self._game.current_player]
            self._gamecanvas_is_ocean = False
            self._gamecanvas.display()

    def _on_game_over(self) -> None:
        winner = self._game.winner
        self._info_text = self._WINNER_TEXT.format(winner.name)
        self._FONTSIZE = int(self._width / len(self._info_text))
        self._set_info_label_text(self._info_text)
        self._gamecanvas.hide()
        if winner == self._player1:
            self._gamecanvas = self._ocean_canvases[self._player2]
        else:
            self._gamecanvas = self._ocean_canvases[self._player1]
        self._gamecanvas.display()
        
    def _on_player_turn(self) -> None:
        self._gamecanvas.hide()
        self._info_text = self._TURN_TEXT.format(self._game.current_player.name)
        self._set_info_label_text(self._info_text)
        self._gamecanvas = self._target_canvases[self._game.current_player]
        self._gamecanvas.display()
        
    def run(self) -> None:
        self.mainloop()

