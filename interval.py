import threading

class SetInterval:
    def __init__(self, func, sec):
        self.func = func
        self.sec = sec
        self.thread = threading.Timer(self.sec, self.handle_function)

    def handle_function(self):
        self.func()
        self.thread = threading.Timer(self.sec, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

