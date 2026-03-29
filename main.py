import sys

try:
    from trigoo_ui import Calculator
    GUI_AVAILABLE = True
except Exception as e:
    print('GUI is not available (Kivy missing or failed to launch):', e)
    GUI_AVAILABLE = False

from trigoo_math import evaluate_expression


def run_cli():
    angle_mode = 'deg'
    print('Fallback console calculator running.')
    print('Type expressions (or QUIT/EXIT).')
    print('Use MODE DEG or MODE RAD to switch angle mode.')
    while True:
        try:
            expr = input('calc> ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nExiting.')
            break

        if not expr:
            continue
        lower = expr.lower()
        if lower in ('quit', 'exit'):
            print('Exiting.')
            break
        if lower.startswith('mode '):
            mode = lower.split(' ', 1)[1]
            if mode in ('deg', 'rad'):
                angle_mode = mode
                print('Angle mode set to', angle_mode)
            else:
                print('Mode must be DEG or RAD')
            continue

        try:
            result = evaluate_expression(expr, angle_mode=angle_mode)
            print(result)
        except Exception as err:
            print('Error:', err)


if __name__ == '__main__':
    if GUI_AVAILABLE:
        try:
            Calculator().run()
        except Exception as e:
            print('Failed to run GUI, falling back to CLI:', e)
            run_cli()
    else:
        run_cli()
