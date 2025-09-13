import pygame

def draw_text_wrap(surface, text, font, color, x, y, max_width, line_spacing=5):
    """
    Draw multi-line wrapped text onto a surface.
    """
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    lines.append(current_line)

    for i, line in enumerate(lines):
        line_surf = font.render(line, True, color)
        surface.blit(line_surf, (x, y + i * (font.get_height() + line_spacing)))

def get_last_line_position(displayed_text, font, max_width, x_start, y_start, line_spacing=5):
    """
    Calculate the x, y position for the blinking cursor at the end of the last line.
    """
    words = displayed_text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    lines.append(current_line)
    cursor_x = x_start + font.size(lines[-1])[0]
    cursor_y = y_start + (len(lines) - 1) * (font.get_height() + line_spacing)
    return cursor_x, cursor_y
