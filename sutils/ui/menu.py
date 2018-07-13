def draw_menu(window, items, callbacks):
    offsety = 0
    offsetx = 0
    for il,it in enumerate(items):
        window.addstr(il + offsety, 0+offsetx, it)

