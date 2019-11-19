import tkinter

# Setup dialog for setting player names
class PlayerSetupDialog(tkinter.Toplevel):
    def __init__(self, parent: tkinter.Tk):
        super().__init__(parent)
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()

        # display slightly offset from parent topleft corner
        offset = 20
        self.geometry('+{}+{}'.format(parent_x+offset, parent_y+offset))
        self.transient(parent)
        self.title('Player Names')
        
    def show(self) -> [str]:
        self._p1_name = self._p2_name = ''

        # display and try to grab input focus
        self._make_body()
        self.wait_visibility()
        self.focus_set()
        self.grab_set()
        self.wait_window()

        if self._p1_name and self._p2_name:
            return [self._p1_name, self._p2_name]
        else:
            return []
    
    def _make_body(self) -> None:
        # label and entry for player 1 name
        self._p1_frame = tkinter.Frame(self)
        self._p1_label = tkinter.Label(self._p1_frame, text='Player 1 name:')
        self._p1_field = tkinter.Entry(self._p1_frame)      
        
        # label and entry for player 2 name
        self._p2_frame = tkinter.Frame(self)
        self._p2_label = tkinter.Label(self._p2_frame, text='Player 2 name:')
        self._p2_field = tkinter.Entry(self._p2_frame)

        # create start/cancel buttons
        self._btn_frame = tkinter.Frame(self)
        self._play_btn = tkinter.Button(self._btn_frame, text='START', command=self._on_press_play)
        self._cancel_btn = tkinter.Button(self._btn_frame, text='CANCEL', command=self._on_press_cancel)

        # position elements in a standard dialog flow
        self._p1_frame.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self._p1_label.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self._p1_field.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)

        self._p2_frame.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self._p2_label.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self._p2_field.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)

        self._play_btn.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self._cancel_btn.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        
        self._p1_frame.pack(side=tkinter.TOP, expand=True, fill=tkinter.BOTH)
        self._p2_frame.pack(side=tkinter.TOP, expand=True, fill=tkinter.BOTH)
        self._btn_frame.pack(side=tkinter.TOP, expand=True, fill=tkinter.BOTH)

    def _on_press_play(self) -> None:
        self._p1_name = self._p1_field.get()
        self._p2_name = self._p2_field.get()

        # only allow play button to close with nonempty names
        if self._p1_name.strip() != '' and self._p2_name.strip() != '':
            self.destroy()

    def _on_press_cancel(self) -> None:
        self.destroy()