# Interactive Fractal Explorer

A Python-based interactive explorer for the Mandelbrot and Julia sets, built with NumPy and Matplotlib. Supports real-time zoom via click-and-drag, zoom history (undo), live switching between fractals, and a mathematically meaningful link between the two: switching to Julia renders the set corresponding to wherever you're currently zoomed into on the Mandelbrot set.

<img width="2940" height="1773" alt="fractal_julia_20260914_003733" src="https://github.com/user-attachments/assets/f06aaf42-acb8-4398-94d6-1b66a020bc9b" />

<img width="1280" height="960" alt="fractal_mandelbrot_20260913_191542" src="https://github.com/user-attachments/assets/b6f37e8b-9c96-464a-bfad-8de200f33800" />

<img width="1280" height="960" alt="fractal_julia_20260913_190041" src="https://github.com/user-attachments/assets/e46e5b66-a4df-4b3a-aaf8-5a5eafd1c7f8" />



## Features

- **Vectorized rendering** of both the Mandelbrot and Julia sets using NumPy's boolean masking — no per-pixel Python loops
- **Interactive zoom**: click and drag to select a region; automatically corrects for aspect ratio so the image never looks stretched
- **Zoom-out history**: press Spacebar to step back through previous views
- **Fractal switching**: press `m` for Mandelbrot, `j` for Julia (using the center of your current Mandelbrot view as the Julia constant `c`)
- **Custom Julia constants**: type directly into the on-screen text box to explore any `c` value
- **Dynamic iteration scaling**: `max_iter` increases automatically as you zoom deeper, to preserve boundary detail (capped for performance — see Limitations)
- **Save current view**: press `s` to export the current view as a timestamped PNG
- **In-app shortcut reference**: press `h` at any time to reprint the controls

## Controls

| Key / Action     | Effect                                                       |
|-------------------|---------------------------------------------------------------|
| Click + drag       | Zoom into the selected region                                 |
| Spacebar           | Zoom out (undo last zoom)                                    |
| `m`                | Switch to the Mandelbrot set                                  |
| `j`                | Switch to the Julia set for the current Mandelbrot view's center |
| Type in `c =` box  | Set a custom Julia constant (e.g. `-0.7+0.27j`), press Enter  |
| `r`                | Reset the current fractal to its default view                |
| `s`                | Save the current view as a PNG                                |
| `h`                | Reprint the shortcut list to the console                      |

## Getting Started

### Requirements
- Python 3.9+
- NumPy
- Matplotlib


## How It Works

### The escape-time algorithm

Both fractals are generated using the same underlying idea: for each point on a grid, repeatedly apply `z = z² + c` and check whether the sequence stays bounded or escapes to infinity. The number of iterations before escape determines the pixel's color.

- **Mandelbrot set**: `z` starts at `0` for every pixel; `c` varies per pixel (it *is* the pixel's coordinate on the complex plane).
- **Julia set**: `c` is a single fixed constant for the whole image; `z` starts at the pixel's coordinate instead.

This shared structure is why the two fractals can be rendered through nearly identical code, and why any point on the Mandelbrot set can be used as the `c` for a corresponding Julia set — the two are deeply mathematically linked, not just visually similar.

> The file also includes `mandelbrot()`, a naive, non-vectorized, single-point version of the algorithm using a plain Python loop. It isn't used by the interactive app — it's kept as a reference/baseline, since it was the first working version of the algorithm before vectorization, and is a useful point of comparison for the performance discussion below.

### Vectorization

Rather than looping over pixels in Python (as `mandelbrot()` does, one point at a time), the entire grid is processed as NumPy arrays. A boolean mask tracks which pixels are still actively iterating; once a pixel's value exceeds the escape threshold, it's excluded from further updates via masked assignment (`Z[mask] = ...`), which both avoids wasted computation and prevents numerical overflow from repeatedly squaring an already-diverged value. This is the difference between computing a 600×600 image pixel-by-pixel in Python versus operating on the whole grid at once via NumPy's compiled array operations — the latter is dramatically faster and is what makes real-time interactive zoom feasible at all.

### Fractal-switching architecture

Both fractal functions are unified behind a single `render_fn`, built using `functools.partial` to pre-bind the arguments that don't change per-frame (grid dimensions, and `c` for Julia). This means the zoom, pan, and redraw logic never needs to know which fractal is currently active — switching fractals is just a matter of reassigning what `render_fn` points to.

## Limitations / Known Trade-offs

- **Performance vs. detail**: `max_iter` is dynamically scaled up with zoom depth to preserve boundary detail, but capped at 500 iterations, and render resolution is set to 600×600 rather than higher, to keep interactive zoom responsive. Very deep zooms may show slightly softer detail than an uncapped, higher-resolution render would produce.
- **Manual `c` input** is handled via a Matplotlib `TextBox` widget rather than a full GUI form — functional, but minimal.
- **No real-time animation**: zoom transitions are instantaneous re-renders rather than animated/smoothed transitions.

## Future Work

Given time constraints, this prototype prioritized correctly implementing and understanding the core vectorized escape-time algorithm — applied to both Mandelbrot and Julia sets, with full interactive zoom — over building out additional rendering infrastructure. Natural next steps:

- **Smooth/continuous coloring** using a continuous escape-time formula, to eliminate banding entirely
- **Burning Ship fractal** and other escape-time variants (the `render_fn` abstraction should make this a relatively small addition)
- **Performance optimization via Numba** (`@njit`) to allow higher resolution and uncapped iteration counts without sacrificing responsiveness
- **Animated zoom sequences** exported as GIF/video
- **Real-time interactive rendering** via a dedicated loop-based library (e.g. Pygame), for smoother continuous zoom rather than discrete click-to-zoom

