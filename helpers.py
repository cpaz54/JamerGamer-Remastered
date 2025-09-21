# helpers.py
from settings import *

def draw_text_wrap(surface, text, font, color, x, y, max_width):
    """
    Draws text with wrapping at max_width starting at (x, y)
    """
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    for i, line in enumerate(lines):
        text_surf = font.render(line, True, color)
        surface.blit(text_surf, (x, y + i * font.get_linesize()))

def get_last_line_position(text, font, max_width, x, y):
    """
    Returns the position (x, y) for the blinking cursor after wrapped text
    """
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    last_line = lines[-1]
    cursor_x = x + font.size(last_line)[0]
    cursor_y = y + (len(lines) - 1) * font.get_linesize()
    return cursor_x, cursor_y

# -------------------------
# Developer skip function
# -------------------------
game_flow = ["menu", "cutscene", "snake", "cutscene2", "platformer", "cutscene3", "adventure", "cutscene4", "doom", "cutscene5"]

def skip_to_next_state(current_state):
    """
    Returns the next game state in the flow.
    If at the end, returns the current state.
    """
    if current_state in game_flow:
        idx = game_flow.index(current_state)
        if idx + 1 < len(game_flow):
            return game_flow[idx + 1]
    return current_state
