import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import RectangleSelector
from functools import partial
from datetime import datetime

history = []

def mandelbrot(c, max_iter):

    z=0

    for i in range(max_iter):
        if abs(z) > 2:
            return i

        z = z*z + c

    return max_iter


def mandelbrot_vectorized(xmin, xmax, ymin, ymax, width, height, max_iter):
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    C = x[np.newaxis, :] + 1j * y[:, np.newaxis]   

    Z = np.zeros_like(C)
    div_time = np.zeros(C.shape, dtype=int)
    mask = np.ones(C.shape, dtype=bool)   # if True then still iterating

    for i in range(max_iter):
        Z[mask] = Z[mask]**2 + C[mask]      #again, if corresponding mask returns True then it takes it        
        escaped = np.abs(Z) > 2      
        newly_escaped = escaped & mask      
        div_time[newly_escaped] = i      
        mask &= ~escaped      

    div_time[mask] = max_iter
    return div_time

def julia_vectorized(xmin, xmax, ymin, ymax, width, height, c, max_iter):
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)

    Z = x[np.newaxis, :] + 1j * y[:, np.newaxis]   # grid becomes the STARTING Z, not C

    div_time = np.zeros(Z.shape, dtype=int)
    mask = np.ones(Z.shape, dtype=bool)

    for i in range(max_iter):
        Z[mask] = Z[mask]**2 + c        # c is now a single fixed constant, not indexed by mask
        escaped = np.abs(Z) > 2
        newly_escaped = escaped & mask
        div_time[newly_escaped] = i
        mask &= ~escaped

    div_time[mask] = max_iter
    return div_time


def parse_complex(w):
    w = w.strip().replace(' ', '').replace('i', 'j').replace('I', 'j')
    try:
        return complex(w)
    except ValueError:
        return None

mandelbrot_bounds= [-2, 1.2, -1.5, 1.5]
julia_bounds= [-1.5, 1.5, -1.5, 1.5]
bounds = list(mandelbrot_bounds)
active_default_bounds = mandelbrot_bounds
width, height = 600, 600
max_iter = 100
target_ratio = width/height

current_c = None
fractal_name = "Mandelbrot"

render_fn = partial(mandelbrot_vectorized, width=width, height=height)

shortcuts = """
--- Fractal Explorer Shortcuts ---
Drag left-click : zoom into selected box
Spacebar        : zoom out (undo)
m               : switch to Mandelbrot
j               : switch to Julia (c = center of current Mandelbrot view)
Type in "c="    : enter a custom julia constant, press Enter
r               : reset current fractal to its default view
s               : save current view as PNG
h               : show this shortcut list again
-----------------------------------
""" 

def calc_max_iter(current_bounds):
    default_width = active_default_bounds[1] - active_default_bounds[0]
    current_width = current_bounds[1] - current_bounds[0]
    zoom_level = default_width/current_width

    if zoom_level <= 1:
        return max_iter

    computed =  int(max_iter + 50 * np.log2(zoom_level))
    return min(computed, 500)

def render(current_bounds):
    max_iter = calc_max_iter(current_bounds)
    image = render_fn(*current_bounds, max_iter=max_iter)

    return image, max_iter

def refresh_title():
    if fractal_name == 'Julia':
        ax.set_title(f"Julia | c = {current_c:.5f} | max_iter = {calc_max_iter(bounds)}")
    else:
        ax.set_title(f"Mandelbrot | max_iter = {calc_max_iter(bounds)}")


fig, ax = plt.subplots()

initial_image, initial_max_iter = render(bounds)

im = ax.imshow(initial_image, extent=[*bounds], cmap='hot', origin='lower')
im.set_clim(0, initial_max_iter)
fig.colorbar(im, ax=ax)
ax.set_xlabel("Re(z)")
ax.set_ylabel("Im(z)")
refresh_title()

print(shortcuts)



def redraw():
    new_image, max_iter = render(bounds)
    im.set_data(new_image)
    im.set_clim(0, max_iter)
    im.set_extent(bounds)
    ax.set_xlim(bounds[1], bounds[0]) if bounds[0] > bounds[1] else ax.set_xlim(bounds[0], bounds[1])
    ax.set_ylim(bounds[2], bounds[3])
    refresh_title()
    fig.canvas.draw_idle()


def update_view(xmin, xmax, ymin, ymax):
    #function to update the bounds physically everytime the image is zoomed into
    global history, bounds, target_ratio
    history.append(bounds)

    box_height = ymax-ymin
    box_width = xmax-xmin
    box_ratio = box_width/box_height

    if box_ratio > target_ratio:
        y_center = (ymax+ymin)/2
        box_height = box_width/target_ratio
        new_ymin = y_center - box_height/2
        new_ymax = y_center + box_height/2
        new_xmin, new_xmax = xmin, xmax

    elif box_ratio < target_ratio:
        x_center = (xmax+xmin)/2
        box_width = box_height * target_ratio
        new_xmin = x_center - box_width/2
        new_xmax = x_center + box_width/2
        new_ymin, new_ymax = ymin, ymax

    else:
        new_xmin, new_xmax, new_ymin, new_ymax = xmin, xmax, ymin, ymax

    bounds = [new_xmin, new_xmax, new_ymin, new_ymax]

    redraw()

def onselect(eclick, erelease):

    x1,y1 = eclick.xdata, eclick.ydata
    x2,y2 = erelease.xdata, erelease.ydata

    if None in (x1, y1, x2, y2):
        return

    if abs(x2 - x1) < 1e-6 or abs(y2 - y1) < 1e-6:
        return

    new_xmin, new_xmax = sorted([x1,x2])
    new_ymin, new_ymax = sorted([y1,y2])

    update_view(new_xmin, new_xmax, new_ymin, new_ymax)

def zoom_out(event):
    global bounds, target_ratio, history
    if event.key == ' ':
        if not history:
            return
        bounds = history.pop()

        redraw()

def reset_view(event):
    global bounds, history
    if event.key == 'r':
        bounds = list(active_default_bounds)
        history = []
        redraw()

def save_view(event):
    if event.key == 's':
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"fractal_{fractal_name.lower()}_{timestamp}.png"
        fig.savefig(filename, dpi=200)
        print(f"Saved: {filename}")


def show_help(event):
    if event.key == 'h':
        print(shortcuts)

from matplotlib.widgets import TextBox

textbox_ax = fig.add_axes([0.15, 0.02, 0.3, 0.05]) 
c_textbox = TextBox(textbox_ax, "c = ")
textbox_ax.set_visible(False)

def on_c_submit(text):
    global render_fn, bounds, history, active_default_bounds, fractal_name, current_c
    parsed = parse_complex(text)
    if parsed is None:
        print("Couldn't parse, keeping current value...")
        return
    current_c = parsed
    render_fn = partial(julia_vectorized, width=width, height=height, c=current_c)
    bounds = list(julia_bounds)
    active_default_bounds = julia_bounds
    fractal_name = "Julia"
    history = []
    redraw()

c_textbox.on_submit(on_c_submit)

def switch_fractal(event):
    global render_fn, bounds, history, active_default_bounds, fractal_name, current_c
    if event.key == 'j':
        textbox_ax.set_visible(True)
        xmin,xmax,ymin,ymax = bounds
        c = complex((xmin+xmax)/2, (ymin+ymax)/2)
        render_fn = partial(julia_vectorized, width=width, height=height, c=c)
        bounds = list(julia_bounds)
        active_default_bounds = julia_bounds
        fractal_name = "Julia"
        current_c = c

    elif event.key == 'm':
        textbox_ax.set_visible(False)
        render_fn = partial(mandelbrot_vectorized, width=width, height=height)
        bounds = list(mandelbrot_bounds)
        active_default_bounds = mandelbrot_bounds
        fractal_name = "Mandelbrot"
        current_c = None

    else:
        return

    
    history = []
    redraw()



selector = RectangleSelector(ax, onselect, useblit=True, button= [1], interactive=False)
fig.canvas.mpl_connect('key_press_event', zoom_out)
fig.canvas.mpl_connect('key_press_event', switch_fractal)
fig.canvas.mpl_connect('key_press_event', reset_view)
fig.canvas.mpl_connect('key_press_event', save_view)
fig.canvas.mpl_connect('key_press_event', show_help)

plt.rcParams['keymap.save'] = []
plt.rcParams['keymap.home'] = []

plt.show()
