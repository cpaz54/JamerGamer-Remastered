"""Base class for every screen in the game."""


class Scene:
    #: logical resolution this scene renders at (scaled to the window by App)
    size = (960, 540)
    #: capture the mouse (relative mode) while this scene is active and unpaused
    grab_mouse = False
    #: whether ESC opens the pause menu (title screen handles ESC itself)
    pausable = True
    #: name shown in the pause menu
    title = ""

    def __init__(self, app):
        self.app = app
        self.t = 0.0

    @property
    def audio(self):
        return self.app.audio

    def enter(self):
        pass

    def exit(self):
        pass

    def on_pause(self):
        pass

    def on_resume(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        pass

    def skip(self):
        """Developer skip (*): by default just completes the scene."""
        self.app.story.complete()
