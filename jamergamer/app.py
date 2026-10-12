"""Window, main loop, scene switching, pause menu and global hotkeys."""
import pygame

from . import ui
from .audio import Audio
from .config import WINDOW_SIZE, FPS, STEP, TITLE, BLACK, NEON, NEON_DIM
from .save import Save


class App:
    def __init__(self, start_step=None):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.save = Save()
        self.fullscreen = False
        self.window = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        if self.save["fullscreen"]:
            self.toggle_fullscreen()
        self.clock = pygame.time.Clock()
        self.audio = Audio(self.save)
        self.canvas = None
        self.scene = None
        self.pending = None            # factory for the next scene (during fade-out)
        self.fade = 1.0                # 1 = fully black
        self.fade_dir = -1             # -1 fading in, +1 fading out
        self.fade_speed = 3.0
        self.paused = False
        self.pause_menu = None
        self.running = True
        self.t = 0.0

        from .story import Story
        self.story = Story(self)
        if start_step is not None:
            self.story.goto(start_step, fade=False)
        else:
            from .scenes.title import TitleScene
            self.set_scene(TitleScene(self))

    # --------------------------------------------------------------- scenes
    def set_scene(self, scene):
        if self.scene:
            self.scene.exit()
        self.scene = scene
        # Plain 32-bit RGB. convert() would copy the display format, which on
        # macOS has an alpha channel, and fading sprites then blit as black boxes.
        self.canvas = pygame.Surface(scene.size, 0, 32)
        self.paused = False
        self._apply_grab()
        scene.enter()

    def switch(self, factory, fade=True):
        """Fade to black, then build the next scene with factory()."""
        if not fade:
            self.set_scene(factory())
            self.fade, self.fade_dir = 1.0, -1
            return
        self.pending = factory
        self.fade_dir = 1

    # --------------------------------------------------------------- window
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        self.save["fullscreen"] = self.fullscreen

    def _apply_grab(self):
        grab = bool(self.scene and self.scene.grab_mouse and not self.paused and pygame.display.get_active())
        pygame.event.set_grab(grab)
        # pygame 2: hidden cursor + grab switches SDL into relative mouse mode
        pygame.mouse.set_visible(not grab)
        pygame.mouse.get_rel()

    def view_rect(self):
        ww, wh = self.window.get_size()
        cw, ch = self.canvas.get_size()
        scale = min(ww / cw, wh / ch)
        w, h = int(cw * scale), int(ch * scale)
        return pygame.Rect((ww - w) // 2, (wh - h) // 2, w, h)

    # --------------------------------------------------------------- pause
    def pause(self):
        if self.paused or not self.scene.pausable:
            return
        self.paused = True
        self.pause_menu = PauseMenu(self)
        self.scene.on_pause()
        if self.audio.enabled:
            pygame.mixer.music.pause()
            pygame.mixer.pause()
        self._apply_grab()

    def resume(self):
        self.paused = False
        self.scene.on_resume()
        if self.audio.enabled:
            pygame.mixer.music.unpause()
            pygame.mixer.unpause()
        self._apply_grab()

    # --------------------------------------------------------------- loop
    def run(self):
        acc = 0.0
        while self.running:
            frame = self.clock.tick(FPS) / 1000.0
            acc += min(frame, 0.1)
            self.t += frame
            self._events()
            if not self.running:
                break
            steps = 0
            while acc >= STEP and steps < 4:
                acc -= STEP
                steps += 1
                if not self.paused and self.pending is None:
                    self.scene.update(STEP)
                self._update_fade(STEP)
            self._draw()
        pygame.quit()

    def _events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == getattr(pygame, "WINDOWFOCUSLOST", -1):
                if self.scene.grab_mouse and self.pending is None:
                    self.pause()
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11 or (event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT):
                    self.toggle_fullscreen()
                    continue
                if self.pending is not None:
                    continue
                if event.key == pygame.K_ESCAPE and self.scene.pausable:
                    if self.paused:
                        self.resume()
                    else:
                        self.pause()
                    continue
                if event.unicode == "*" and not self.paused:
                    self.scene.skip()
                    continue
            if self.pending is not None:
                continue
            if self.paused:
                self.pause_menu.handle(event)
            else:
                self.scene.handle_event(event)

    def _update_fade(self, dt):
        if self.fade_dir > 0:
            self.fade = min(1.0, self.fade + dt * self.fade_speed)
            if self.fade >= 1.0 and self.pending is not None:
                factory, self.pending = self.pending, None
                self.set_scene(factory())
                self.fade_dir = -1
        elif self.fade_dir < 0:
            self.fade = max(0.0, self.fade - dt * self.fade_speed)

    def _draw(self):
        self.scene.draw(self.canvas)
        if self.paused:
            self.pause_menu.draw(self.canvas)
        if self.fade > 0:
            veil = pygame.Surface(self.canvas.get_size())
            veil.set_alpha(int(255 * self.fade))
            self.canvas.blit(veil, (0, 0))
        self.window.fill(BLACK)
        rect = self.view_rect()
        if rect.size == self.canvas.get_size():
            self.window.blit(self.canvas, rect)
        else:
            pygame.transform.scale(self.canvas, rect.size, self.window.subsurface(rect))
        pygame.display.flip()

    def quit(self):
        self.running = False


class PauseMenu:
    def __init__(self, app):
        self.app = app
        self.mode = "main"
        self.t = 0.0
        self._build()

    def _build(self):
        s = self.app.save
        if self.mode == "main":
            items = [("RESUME", "resume")]
            if getattr(self.app.story, "current", None) is not None:
                items.append(("RESTART CHAPTER", "restart"))
            items += [("SETTINGS", "settings"), ("QUIT TO TITLE", "title"), ("QUIT GAME", "quit")]
        else:
            items = [
                (lambda: f"MUSIC  < {int(round(s['music_volume'] * 10))} >", "music"),
                (lambda: f"SOUND  < {int(round(s['sfx_volume'] * 10))} >", "sfx"),
                (lambda: f"FULLSCREEN  {'ON' if self.app.fullscreen else 'OFF'}", "full"),
                ("BACK", "back"),
            ]
        self.menu = ui.Menu(items, size=14, gap=30)

    def handle(self, event):
        res = self.menu.handle(event, self.app.audio)
        if not res:
            return
        action, key = res
        s = self.app.save
        if key in ("music", "sfx") and action in ("left", "right", "select"):
            field = "music_volume" if key == "music" else "sfx_volume"
            delta = -0.1 if action == "left" else 0.1
            val = round(s[field] + delta, 2)
            if action == "select":
                val = 0.0 if s[field] >= 1.0 else val
            s[field] = max(0.0, min(1.0, val))
            self.app.audio.apply_volume()
            self.app.audio.blip("move")
            return
        if action != "select":
            return
        if key == "resume":
            self.app.resume()
        elif key == "restart":
            self.app.resume()
            self.app.story.restart()
        elif key == "settings":
            self.mode = "settings"
            self._build()
        elif key == "back":
            self.mode = "main"
            self._build()
        elif key == "full":
            self.app.toggle_fullscreen()
        elif key == "title":
            self.app.resume()
            self.app.audio.stop_music()
            self.app.story.to_title()
        elif key == "quit":
            self.app.quit()

    def draw(self, surf):
        self.t += 1 / 60
        w, h = surf.get_size()
        veil = pygame.Surface((w, h), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 170))
        surf.blit(veil, (0, 0))
        title = "PAUSED" if self.mode == "main" else "SETTINGS"
        ui.draw_text(surf, title, 28, (w // 2, h // 2 - 120), NEON, "midtop", shadow=BLACK)
        self.menu.draw(surf, w // 2, h // 2 - 50, self.t)
        hint = "ESC TO RESUME" if self.mode == "main" else "LEFT/RIGHT TO ADJUST"
        ui.draw_text(surf, hint, 8, (w // 2, h - 24), NEON_DIM, "midtop")
