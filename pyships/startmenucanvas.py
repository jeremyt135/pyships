import tkinter

from . import battleship
from .gamecanvas import GameCanvas
from .playersetupdialog import PlayerSetupDialog

# Clickable canvas that starts the game
class StartMenuCanvas(GameCanvas):
    def __init__(self, parent: tkinter.Tk, width: int, height: int, on_game_start):
        super().__init__(parent, bg='blue', width=width, height=height)
        self._parent = parent
        self._width = width
        self._height = height
        self._player1 = self._player2 = None
        self._on_game_start = on_game_start

        self.bind('<Button-1>', self._on_mouse_btn1_down)

    def display(self) -> None:
        click_here = 'Click here to start the game'
        font_size = int(self.winfo_width() / len(click_here))
        
        self._click_text_id = self.create_text((self._width/2, self._height/2),
                                               text=click_here, fill='white', font=('Arial', font_size))

        self.pack()
        
    def hide(self) -> None:
        self.pack_forget()

    # creates a dialog to get player names, returning true if names were entered
    def _player_setup(self) -> bool:
        names = PlayerSetupDialog(self._parent).show()
        if names:
            self._player1 = battleship.ClassicPlayer(names[0], battleship.OceanGrid(), battleship.TargetGrid(), None)
            self._player2 = battleship.ClassicPlayer(names[1], battleship.OceanGrid(), battleship.TargetGrid(), None)
            return True
        
        return False
        
    def _on_mouse_btn1_down(self, event: tkinter.Event) -> None:
        # get player names and start game if got both names
        if self._player_setup():
            self.delete(self._click_text_id)
            self._on_game_start(self._player1, self._player2)
