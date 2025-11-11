# GUI 窗口管理器，不再导入 popup 模块
class WindowManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.active_windows = []

    def register_window(self, window):
        self.active_windows.append(window)

    def close_all(self):
        for win in self.active_windows:
            try:
                win.destroy()
            except:
                pass
        self.active_windows.clear()

