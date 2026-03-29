from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from trigoo_math import evaluate_expression, apply_math_function
import math


Window.size = (400, 760)
Window.clearcolor = (0.75, 0.9, 1, 1)  # Soft light blue background


class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0.93, 0.96, 1, 1)
        self.color = (0.1, 0.1, 0.2, 1)
        self.font_size = 18
        self.size_hint = (None, None)
        self.height = 60
        self.width = 70
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(radius=[20], pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Calculator(App):
    def load_button_config(self):
        import json, os
        path = os.path.join(os.path.dirname(__file__), 'calc_buttons.json')
        try:
            with open(path, 'r') as f:
                self.button_config = json.load(f)
        except Exception:
            self.button_config = {
                'normal': [
                    '7', '8', '9', '/', 'C',
                    '4', '5', '6', '*', 'DEL',
                    '1', '2', '3', '-', 'M+',
                    '0', '.', '=', '+', 'M-',
                    '(', ')', 'x', 'MR', 'MC',
                    'Help', 'Settings', '__MODE__', '', ''
                ],
                'scientific': [
                    '7', '8', '9', '/', 'log',
                    '4', '5', '6', '*', 'ln',
                    '1', '2', '3', '-', 'exp',
                    '0', '.', '=', '+', 'power',
                    'sin', 'cos', 'tan', 'sqrt', 'shift',
                    'DEG', 'PI', 'e', 'C', 'DEL',
                    'SUM', 'AVG', 'MIN', 'MAX', 'ABS',
                    'ROUND', 'MOD', 'DERIV', 'INT', 'EQN', 'PS', 'x',
                    '(', ')', 'fact',
                    'M+', 'M-', 'MR', 'MC', 'hist',
                    'Help', 'Settings', '__MODE__', '', ''
                ]
            }

    def get_buttons(self):
        if not hasattr(self, 'button_config'):
            self.load_button_config()
        mode_list = self.button_config['scientific' if self.scientific else 'normal']
        mode_label = 'Norm' if self.scientific else 'Sci'
        return [mode_label if b == '__MODE__' else b for b in mode_list]

    def update_buttons(self):
        self.grid.clear_widgets()
        for btn in self.get_buttons():
            if not btn:
                self.grid.add_widget(Label())
                continue
            b = RoundedButton(text=btn)
            b.bind(on_press=self.on_press)
            self.grid.add_widget(b)

    def load_mode(self):
        try:
            with open('calc_mode.cfg', 'r') as f:
                mode = f.read().strip().lower()
                self.scientific = (mode == 'scientific')
        except FileNotFoundError:
            self.scientific = False

    def save_mode(self):
        with open('calc_mode.cfg', 'w') as f:
            f.write('scientific' if self.scientific else 'normal')

    def update_mode_title(self):
        mode_name = 'Scientific' if self.scientific else 'Normal'
        self.title.text = f'Calculator - {mode_name}'

    def build(self):
        self.load_mode()
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        top = BoxLayout(orientation='horizontal', size_hint_y=None, height=70, spacing=10)
        icon = Label(text='Hi', font_size=28, size_hint=(None, 1), width=50)
        self.title = Label(text='Calculator', font_size=20, size_hint=(1, 1), halign='left', valign='middle')
        self.title.bind(size=lambda *args: self.title.setter('text_size')(self.title, self.title.size))
        top.add_widget(icon)
        top.add_widget(self.title)
        root.add_widget(top)
        self.update_mode_title()

        self.display = TextInput(text='0', readonly=True, halign='right', font_size=30,
                                 size_hint_y=None, height=70, background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1), cursor_color=(0,0,0,1))
        root.add_widget(self.display)

        self.history = []
        self.memory = 0.0
        self.shift = False
        self.angle_mode = 'deg'

        self.grid = GridLayout(cols=5, spacing=8, size_hint_y=None, height=580)
        self.update_buttons()
        root.add_widget(self.grid)

        self.guide = Label(text='Guide: shift=inv; DEG toggles RAD; hist=history; M+/M-/MR/MC=memory; DEL=backspace; functions sin(),cos(),tan(),sqrt(),log(),ln(),exp(); SUM/AVG/MIN/MAX/MOD/ROUND/ABS are Excel-style; DERIV(expr, x), INT(expr, a, b), EQN(x1,y1,x2,y2), PS(x1,y1,m)',
                            size_hint_y=None, height=40, font_size=12, color=(0.1,0.1,0.4,1))
        root.add_widget(self.guide)

        return root

    def apply_unary_insert(self, btn, current):
        text = f'{btn}()'
        if current == '0':
            self.display.text = text
        else:
            self.display.text = current + text
        self.display.cursor = (len(self.display.text) - 1, 0)

    def append_or_replace(self, current, text):
        self.display.text = text if current == '0' else current + text

    def on_press(self, instance):
        btn = instance.text
        current = self.display.text

        if self.shift and btn in ['sin', 'cos', 'tan', 'log']:
            func = {'sin': 'asin', 'cos': 'acos', 'tan': 'atan', 'log': '10^'}[btn]
            self.apply_function(func)
            self.shift = False
            return

        simple_actions = {
            '=': lambda: self.calculate(),
            'C': lambda: setattr(self.display, 'text', '0'),
            'DEL': lambda: setattr(self.display, 'text', current[:-1] or '0'),
            '1/x': lambda: self.apply_function('1/x'),
            'fact': lambda: self.apply_function('fact'),
            'sinh': lambda: self.apply_function('sinh'),
            'cosh': lambda: self.apply_function('cosh'),
            'tanh': lambda: self.apply_function('tanh'),
            'shift': lambda: setattr(self, 'shift', not self.shift),
            'PI': lambda: setattr(self.display, 'text', str(math.pi) if current == '0' else current + str(math.pi)),
            'e': lambda: setattr(self.display, 'text', str(math.e) if current == '0' else current + str(math.e)),
            'hist': lambda: self.show_history(),
            'Settings': lambda: self.show_settings(),
        }

        if btn in simple_actions:
            simple_actions[btn]()
            return

        if btn == ')':
            if current != '0' and current.count('(') > current.count(')'):
                self.append_or_replace(current, ')') if current == '0' else setattr(self.display, 'text', current + ')')
            return

        if btn in ['sin', 'cos', 'tan', 'sqrt', 'log', 'ln', 'exp']:
            self.apply_unary_insert(btn, current)
            return

        if btn == 'power':
            self.append_or_replace(current, '**')
            return

        if btn == 'DEG':
            self.angle_mode = 'rad' if self.angle_mode == 'deg' else 'deg'
            instance.text = 'RAD' if self.angle_mode == 'rad' else 'DEG'
            return

        if btn in ['SUM', 'AVG', 'MIN', 'MAX', 'ABS', 'ROUND', 'MOD', 'DERIV', 'INT', 'EQN', 'PS']:
            self.append_or_replace(current, f'{btn}(')
            return

        if btn == 'Help':
            self.guide.text = ('Commands:\n'
                               ' - sin(x), cos(x), tan(x), sqrt(x), log(x), ln(x), exp(x)\n'
                               ' - auto pair parentheses and close with )\n'
                               ' - EQN(x1,y1,x2,y2), PS(x1,y1,m) for line equations\n'
                               ' - DERIV(expr, x), INT(expr, a, b)\n'
                               ' - Use DEL for backspace, C to clear')
            return

        if btn == 'M+':
            try:
                self.memory += float(current)
            except Exception:
                pass
            return

        if btn == 'M-':
            try:
                self.memory -= float(current)
            except Exception:
                pass
            return

        if btn == 'MR':
            self.display.text = str(self.memory)
            return

        if btn == 'MC':
            self.memory = 0.0
            return

        if btn == 'Reload':
            self.load_button_config()
            self.update_buttons()
            self.guide.text = 'Layouts reloaded from calc_buttons.json'
            return

        if btn in ['Norm', 'Sci']:
            self.scientific = not self.scientific
            self.save_mode()
            self.update_mode_title()
            self.update_buttons()
            self.guide.text = 'Mode switched to ' + ('scientific' if self.scientific else 'normal')
            return

        self.append_or_replace(current, btn)

    def calculate(self):
        try:
            expr = self.display.text
            res = evaluate_expression(expr, angle_mode=self.angle_mode)
            self.display.text = str(res)
            self.history.append((expr, str(res)))
            if len(self.history) > 100:
                self.history.pop(0)
        except Exception:
            self.display.text = 'Error'

    def apply_function(self, func):
        try:
            val = float(self.display.text)
            result = apply_math_function(func, val, angle_mode=self.angle_mode)
            self.display.text = str(result)
        except Exception:
            self.display.text = 'Error'

    def show_history(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        if not self.history:
            content.add_widget(Label(text='No history yet', halign='left', valign='top'))
        else:
            content.add_widget(Label(text='\n'.join(f'{e} = {r}' for e, r in reversed(self.history)), halign='left', valign='top'))
        close = Button(text='Close', size_hint_y=None, height=50)
        content.add_widget(close)
        popup = Popup(title='History', content=content, size_hint=(0.8, 0.8))
        close.bind(on_press=popup.dismiss)
        popup.open()

    def show_settings(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text='Choose background color:'))
        colors = [
            ('Pink', (1, 0.75, 0.8, 1)),
            ('Blue', (0.75, 0.9, 1, 1)),
            ('Green', (0.8, 1, 0.8, 1)),
            ('White', (1, 1, 1, 1)),
            ('Gray', (0.9, 0.9, 0.9, 1)),
        ]
        for name, col in colors:
            btn = Button(text=name, size_hint_y=None, height=40)
            btn.bind(on_press=lambda instance, c=col: self.set_bg_color(c))
            content.add_widget(btn)
        close = Button(text='Close', size_hint_y=None, height=40)
        content.add_widget(close)
        popup = Popup(title='Settings', content=content, size_hint=(0.6, 0.6))
        close.bind(on_press=popup.dismiss)
        popup.open()

    def set_bg_color(self, color):
        Window.clearcolor = color
