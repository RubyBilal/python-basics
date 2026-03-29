from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import math

Window.size = (400, 700)  # Suitable for mobile
Window.clearcolor = (0.75, 0.9, 1, 1)  # Soft light blue

class Calculator(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 5
        self.rows = 10  # Increased for guide and settings
        self.spacing = 5
        self.padding = 10

        self.icon_label = Label(text='👋 Hi', font_size=24, size_hint_y=None, height=40, color=(0,0,0,1))
        self.add_widget(self.icon_label)

        self.display = TextInput(text="0", font_size=32, readonly=True, halign='right', size_hint_y=None, height=80)
        self.add_widget(self.display)

        self.history = []
        self.memory = 0.0
        self.shift = False

        buttons = [
            ["7", "8", "9", "÷", "log"],
            ["4", "5", "6", "×", "ln"],
            ["1", "2", "3", "−", "exp"],
            ["0", ".", "=", "+", "x^y"],
            ["sin", "cos", "tan", "√", "shift"],
            ["π", "e", "C", "⌫", "("],
            [")", "sinh", "cosh", "tanh", "!"],
            ["M+", "M-", "MR", "MC", "hist"],
            ["Settings", "", "", "", ""]
        ]

        for row in buttons:
            for btn in row:
                if btn:
                    button = Button(text=btn, on_press=self.on_button_press, background_color=(1, 0.9, 0.9, 1))
                    self.add_widget(button)
                else:
                    self.add_widget(Label())  # Empty cell

        self.guide = Label(text="Guide:\nShift: Inverse\nHist: History\nM+: Memory", size_hint_y=None, height=100, halign='left', valign='top')
        self.guide.bind(size=self.guide.setter('text_size'))
        self.add_widget(self.guide)

    def on_button_press(self, instance):
        btn = instance.text
        current = self.display.text
        if self.shift and btn in ["sin", "cos", "tan", "log"]:
            func = {"sin": "asin", "cos": "acos", "tan": "atan", "log": "10^"}[btn]
            self.apply_function(func)
            self.shift = False
            return
        if btn == "=":
            self.calculate()
        elif btn == "C":
            self.display.text = "0"
        elif btn == "⌫":
            self.display.text = current[:-1] or "0"
        elif btn in ["sin", "cos", "tan", "√", "log", "ln", "exp", "x^2", "1/x", "!", "sinh", "cosh", "tanh"]:
            self.apply_function(btn)
        elif btn == "π":
            if current == "0":
                self.display.text = str(math.pi)
            else:
                self.display.text = current + str(math.pi)
        elif btn == "e":
            if current == "0":
                self.display.text = str(math.e)
            else:
                self.display.text = current + str(math.e)
        elif btn == "x^y":
            self.display.text = current + "^"
        elif btn in ["(", ")"]:
            self.display.text = current + btn
        elif btn == "shift":
            self.shift = not self.shift
        elif btn == "M+":
            try:
                self.memory += float(current)
            except:
                pass
        elif btn == "M-":
            try:
                self.memory -= float(current)
            except:
                pass
        elif btn == "MR":
            self.display.text = str(self.memory)
        elif btn == "MC":
            self.memory = 0.0
        elif btn == "hist":
            self.show_history()
        elif btn == "Settings":
            self.show_settings()
        else:
            if current == "0":
                self.display.text = btn
            else:
                self.display.text = current + btn

    def calculate(self):
        try:
            expr = self.display.text
            expr = expr.replace("÷", "/").replace("×", "*").replace("−", "-").replace("^", "**")
            result = eval(expr)
            self.display.text = str(result)
            self.history.append((expr, str(result)))
            if len(self.history) > 100:
                self.history.pop(0)
        except:
            self.display.text = "Error"

    def apply_function(self, func):
        try:
            value = float(self.display.text)
            if func == "sin":
                result = math.sin(math.radians(value))
            elif func == "cos":
                result = math.cos(math.radians(value))
            elif func == "tan":
                result = math.tan(math.radians(value))
            elif func == "√":
                result = math.sqrt(value)
            elif func == "log":
                result = math.log10(value)
            elif func == "ln":
                result = math.log(value)
            elif func == "exp":
                result = math.exp(value)
            elif func == "x^2":
                result = value ** 2
            elif func == "1/x":
                result = 1 / value
            elif func == "!":
                result = math.factorial(int(value))
            elif func == "sinh":
                result = math.sinh(value)
            elif func == "cosh":
                result = math.cosh(value)
            elif func == "tanh":
                result = math.tanh(value)
            elif func == "asin":
                result = math.degrees(math.asin(value))
            elif func == "acos":
                result = math.degrees(math.acos(value))
            elif func == "atan":
                result = math.degrees(math.atan(value))
            elif func == "10^":
                result = 10 ** value
            self.display.text = str(result)
        except:
            self.display.text = "Error"

    def show_history(self):
        content = BoxLayout(orientation='vertical')
        text = Label(text='\n'.join([f"{expr} = {res}" for expr, res in reversed(self.history)]), halign='left', valign='top')
        text.bind(size=self.guide.setter('text_size'))
        content.add_widget(text)
        close_btn = Button(text='Close', size_hint_y=None, height=50)
        content.add_widget(close_btn)
        popup = Popup(title='History', content=content, size_hint=(0.8, 0.8))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_settings(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text='Choose Background Color:'))
        colors = [
            ('Pink', (1, 0.75, 0.8, 1)),
            ('Blue', (0.7, 0.9, 1, 1)),
            ('Green', (0.8, 1, 0.8, 1)),
            ('White', (1, 1, 1, 1)),
            ('Gray', (0.9, 0.9, 0.9, 1))
        ]
        for name, color in colors:
            btn = Button(text=name, size_hint_y=None, height=50)
            btn.bind(on_press=lambda instance, c=color: self.set_bg_color(c))
            content.add_widget(btn)
        close_btn = Button(text='Close', size_hint_y=None, height=50)
        content.add_widget(close_btn)
        popup = Popup(title='Settings', content=content, size_hint=(0.6, 0.6))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def set_bg_color(self, color):
        Window.clearcolor = color

class CalculatorApp(App):
    def build(self):
        return Calculator()

if __name__ == "__main__":
    CalculatorApp().run()