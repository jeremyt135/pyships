import tkinter

# Interface for canvases that are part of the game
class GameCanvas(tkinter.Canvas):
    def __init__(self, parent: tkinter.Tk, cnf={}, **kw):
        super().__init__(parent, cnf=cnf, **kw)

    # what to do when canvas should display
    def display(self) -> None:
        pass

    # what to do when canvas should hide
    def hide(self) -> None:
        pass
