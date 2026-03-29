# Calculator App (Python + Kivy/CLI)

This project is a modular calculator with GUI and CLI modes.

## Run Modes

- `python calculator_launcher.py` : tries GUI first, falls back to CLI if Kivy isn't available.
- `python calculator_launcher.py --cli` : force console mode.
- `python calculator_launcher.py --gui` : force Kivy UI mode.

## Dependencies

- Python 3.9+ (tested up to 3.14 in CLI).
- Optional Kivy for GUI.

### Install Kivy (recommended dev env)

```bash
pip install kivy[base] kivy_deps.sdl2 kivy_deps.glew
```

For Python 3.14, use Python 3.12 if you hit package compatibility issues.

## Files

- `calculator_math.py` : expression evaluation, math/parsing features.
- `calculator_ui.py` : Kivy GUI implementation.
- `calculator_launcher.py` : entry point and mode selection.
- `calc_buttons.json` : GUI button layout config.

## Quick start

1. Open terminal in project folder.
2. `python calculator_launcher.py --cli`
3. Enter expressions, commands are printed.

## Notes

- Persistent mode info can be added via `calc_config.json` (future enhancement).
- Handles `DERIV`, `INT`, `EQN`, `PS`, and trig functions.
