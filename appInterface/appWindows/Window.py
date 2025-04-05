import tkinter as tk


class Window:
    def __init__(self, root: tk.Toplevel,  *, title='title', placer: tk.Toplevel = None):
        window = tk.Toplevel()
        window.title(title)
        self._window = window
        self._root = root
        self.isShown = True
        if placer == None:
            self._placer = root
        else:
            self._placer = placer
        self._on_window_resize = lambda e: print(
            f"Window resized to {e[0]}x{e[1]}")
        self._on_window_resize_handler_id = None
        self._window_size = (window.winfo_width(), window.winfo_height())

        self.showButton = tk.Button(self._placer, text=(
            'показать ' + title), state=tk.NORMAL, command=self.show)
        window.protocol("WM_DELETE_WINDOW", self.hide)

    def init_resize(self, time=2000):
        self._window.after_idle(lambda: self._window.after(
            time, lambda: self._window.bind("<Configure>", self._on_configure)))
        return self

    def _get_resize_handler_id(self):
        return self._on_window_resize_handler_id

    def _set_resize_handler_id(self, id):
        self._on_window_resize_handler_id = id


    def set_on_resize(self, callback):
        self._on_window_resize = callback
        return self

    def _on_configure(self, event):
        if (self._window_size[0] < 200) | (self._window_size[1] < 200):
            self._window_size = (event.width, event.height)
            return

        id = self._get_resize_handler_id()
        if id != None:
            return
        if (id == None):
            if ((event.width == self._window_size[0]) & (event.height == self._window_size[1])):
                return
            self._set_resize_handler_id(self._window.after(
                1000, self._on_window_resize_handler, event))

    def _on_window_resize_handler(self, event):
        self._window_size = (self._window.winfo_width(),
                             self._window.winfo_height())
        self._on_window_resize(self._window_size)
        self._set_resize_handler_id(None)

    def destroy(self):
        if not (self._get_resize_handler_id() == None):
            self._window.after_cancel(self._get_resize_handler_id())
        self._window.destroy()

    def hide(self, event=None):
        self.isShown = False
        self._window.withdraw()
        self.showButton.config(state=tk.NORMAL)

    def show(self, event=None):
        self.isShown = True
        self._window.deiconify()
        self.showButton.config(state=tk.DISABLED)
