from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import serial


class LoginScreen(BoxLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # username_label = Label(text='Username:', size_hint=(0.3, 1))
        # password_label = Label(text='Password:', size_hint=(0.3, 1))
        self.username_input = TextInput(multiline=False)
        self.password_input = TextInput(multiline=False, password=True)
        self.add_widget(Label(text='Username:'))
        self.add_widget(self.username_input)
        self.add_widget(Label(text='Password:'))
        self.add_widget(self.password_input)
        self.add_widget(Button(text='Login', on_press=self.login))

    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if password == 'password':
            screen_manager.current = 'main'
        else:
            self.add_widget(Label(text='Invalid password.'))


class MainScreen(BoxLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serial_data = ""
        self.startButton = Button(text='Start', on_press=self.build)
        self.add_widget(self.startButton)

    def build(self, instance):
        print("serial communication begins")

        self.scroll_view = ScrollView()
        instance.opacity = 0

        # Create a Label to display the serial data
        self.label = Label(text="No data received yet.", font_size=20)

        # Add the Label to the ScrollView
        self.scroll_view.add_widget(self.label)

        # Open the serial port
        self.serial_port = serial.Serial("/dev/cu.usbserial-1120", 115200)

        # Schedule the receive_data method to be called every 0.1 seconds
        Clock.schedule_interval(self.receive_data, 1)

        return self.scroll_view

    def receive_data(self, dt):
        # Check if there is data available on the serial port
        if self.serial_port.in_waiting > 0:
            # Read the data from the serial port
            print("1")
            data = self.serial_port.readline().decode()
            print("2")

            # Add the new data to the existing data
            self.serial_data += "\n" + data

            # Update the Label with the new data
            self.label.text = self.serial_data

            # Scroll to the bottom of the ScrollView
            self.scroll_view.scroll_y = 0


class MyScreenManager(ScreenManager):
    pass


class MyApp(App):
    def build(self):
        global screen_manager
        screen_manager = MyScreenManager()
        screen_manager.add_widget(LoginScreen(name='login'))
        screen_manager.add_widget(MainScreen(name='main'))
        return screen_manager


if __name__ == '__main__':
    MyApp().run()
