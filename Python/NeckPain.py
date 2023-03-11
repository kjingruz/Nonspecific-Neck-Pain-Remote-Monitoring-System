from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.popup import Popup

import serial
import serial.tools.list_ports
import sqlite3
from plyer import notification
from datetime import datetime

Builder.load_string('''
<MyScreenManager>:
    WelcomeScreen:
    LoginScreen:
    ModeScreen:
    MainMode3Screen:

<WelcomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        Image:
            source: '/Users/kjingruz/Documents/Nonspecific-Neck-Pain-Remote-Monitoring-System/IMG/WelcomeBackground.png'
            allow_stretch: True
            keep_ratio: False
        Label:
            text: "Say GoodBye to all of your neck pain"
            size_hint: 1, 0.8
            font_size: '40sp'
        Button:
            text: 'Login'
            size_hint: 0.5, 0.2
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            on_press: root.enter()

<LoginScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: '/Users/kjingruz/Documents/Nonspecific-Neck-Pain-Remote-Monitoring-System/IMG/LoginBackground.jpeg'
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        BoxLayout:
            orientation: 'vertical'
            size_hint: 1, 0.8
            spacing: 10
            padding: 10
            Label:
                text: 'Username:'
                font_size: '20sp'
                size_hint: None, None
                size: self.texture_size
                color: (0,0,0,1)
            TextInput:
                id: username
                multiline: False
                size_hint: 0.8, None
                height: 40
                font_size: '20sp'
                background_color: (1, 1, 1, 0.7)
            Label:
                text: 'Password:'
                font_size: '20sp'
                size_hint: None, None
                size: self.texture_size
                color: (0,0,0,1)
            TextInput:
                id: password
                multiline: False
                password: True
                size_hint: 0.8, None
                height: 40
                font_size: '20sp'
                background_color: (1, 1, 1, 0.7)
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, 0.2
            spacing: 20
            padding: 10
            Button:
                text: 'Login'
                size_hint: 0.4, None
                height: 60
                pos_hint: {"center_x": 0.5}
                font_size: '20sp'
                background_color: (0.4, 0.8, 0.7, 1)
                color: (1, 1, 1, 1)
                on_press: root.login()

<ModeScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Neck Only'
            on_press: root.mode1()
            background_normal: '/Users/kjingruz/Documents/Nonspecific-Neck-Pain-Remote-Monitoring-System/IMG/neck.jpg'
        Button:
            text: 'Back Only'
            on_press: root.mode2()
            background_normal: '/Users/kjingruz/Documents/Nonspecific-Neck-Pain-Remote-Monitoring-System/IMG/back.jpeg'
        Button:
            text: 'Neck and Back'
            on_press: root.mode3()
            background_normal: '/Users/kjingruz/Documents/Nonspecific-Neck-Pain-Remote-Monitoring-System/IMG/neck_back.jpg'

<CustomSpinner>:
    text: '10'
    values: [str(i) for i in range(10, 61, 5)]

<MainMode3Screen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            id: start_btn
            text: 'Start'
            size_hint: (0.2, 0.1)
            on_press: root.start()
        Button:
            text: 'Setting'
            size_hint: (0.2, 0.1)
            on_press: root.show_settings_popup()
        ScrollView:
            Label:
                id: label
                text: 'No data received yet.'

''')


class WelcomeScreen(Screen):
    def enter(self):
        screen_manager.current = 'login'


class LoginScreen(Screen):
    def login(self):
        username = self.ids.username.text
        password = self.ids.password.text

        if password == '1':
            screen_manager.current = 'mode'
        else:
            self.add_widget(Label(text='Invalid password.'))


class ModeScreen(Screen):
    def mode1(self):
        screen_manager.current = 'main_mode1'

    def mode2(self):
        screen_manager.current = 'main_mode2'

    def mode3(self):
        screen_manager.current = 'main_mode3'


class CustomSpinner(Spinner):
    pass


class MainMode3Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.internal_timer = None
        self.stagnation_time = 10
        self.start_time = 0
        self.serial_port = None
        self.scroll_view = None
        self.datalabel = None

        # create label to display stagnation time
        self.stagnation_time_label = Label(text="Stagnation Time: seconds", size_hint=(1, 0.1))
        self.add_widget(self.stagnation_time_label)

        # create database connection and cursor
        self.conn = sqlite3.connect('mydatabase.db')
        self.cursor = self.conn.cursor()

        # create table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings
                                      (id INTEGER PRIMARY KEY, stagnation_time INTEGER)''')

        # create table to store stagnation times and dates
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS stagnation_times
                                  (id INTEGER PRIMARY KEY, stagnation_time INTEGER, date_time TEXT)''')

        # get the last selected stagnation time from the database
        self.cursor.execute('SELECT stagnation_time FROM settings ORDER BY id DESC LIMIT 1')
        row = self.cursor.fetchone()
        if row:
            self.stagnation_time = row[0]
            self.stagnation_time_label.text = f"Stagnation Time: {self.stagnation_time} seconds"

        layout = BoxLayout(orientation='vertical')

        # Add a ScrollView to the layout
        self.scroll_view = ScrollView()
        layout.add_widget(self.scroll_view)

        # Create a Label to display the serial data
        self.datalabel = Label(text="No data received yet.", font_size=20)

        # Add the Label to the ScrollView
        self.scroll_view.add_widget(self.datalabel)


    def update_option(self, spinner, option, value):
        spinner.text = option.text
        spinner.dismiss_dropdown()

    def show_settings_popup(self):
        content = BoxLayout(orientation='vertical')

        stagnation_time_dropdown = CustomSpinner(size_hint=(1, 0.2))
        stagnation_time_dropdown.values = ['5', '10', '15', '20', '25']

        confirm_button = Button(text='Confirm', size_hint=(1, 0.2))

        close_button = Button(text='Close', size_hint=(1, 0.2))

        content.add_widget(Label(text='Stagnation Time (seconds):'))
        content.add_widget(stagnation_time_dropdown)
        content.add_widget(confirm_button)
        content.add_widget(close_button)

        popup = Popup(title='Settings', content=content, size_hint=(0.8, 0.6), auto_dismiss=False)

        confirm_button.bind(on_press=lambda x: self.confirm_settings(popup, stagnation_time_dropdown))
        close_button.bind(on_press=popup.dismiss)

        popup.open()

    def confirm_settings(self, popup, stagnation_time_dropdown):
        selected_stagnation_time = stagnation_time_dropdown.text
        self.stagnation_time = int(selected_stagnation_time)

        # update label with selected stagnation time
        self.stagnation_time_label.text = f"Stagnation Time: {self.stagnation_time} seconds"

        # store the selected stagnation time in the database
        self.cursor.execute('INSERT INTO settings (stagnation_time) VALUES (?)', (self.stagnation_time,))
        self.conn.commit()

        popup.dismiss()

    def stop(self):
        # close database connection when the screen is destroyed
        self.conn.close()

    def start_timer(self):
        self.start_time = Clock.get_time()
        self.internal_timer = Clock.schedule_interval(self.check_time, 1)

    def check_time(self, dt):
        elapsed_time = int(Clock.get_time() - self.start_time)
        if elapsed_time >= self.stagnation_time * 60:
            # store the date and time when the stagnation time meets the selected_stagnation_time
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('INSERT INTO stagnation_times (stagnation_time, date_time) VALUES (?, ?)',
                                (self.stagnation_time, now))
            self.conn.commit()

            self.internal_timer.cancel()
            notification.notify(title='Stagnation Time Reached',
                                message='You have been in the same posture for {} seconds.'.format(self.stagnation_time),
                                app_name=App.get_running_app().title)

    def stop_timer(self):
        if self.internal_timer is not None:
            self.internal_timer.cancel()

    def start(self):
        try:
            # Open the serial port
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if 'Arduino' in port.description:
                    self.arduino_port = port.device
                    break
            # Establish serial communication
            self.serial_port = serial.Serial(self.arduino_port, 115200, timeout=1)

            # Schedule the receive_data method to be called every 0.1 seconds
            Clock.schedule_interval(self.receive_data, .1)

        except serial.serialutil.SerialException:
            error_message = "Could not connect \nto the serial port."
            error_popup = Popup(title="Error",
                                content=GridLayout(cols=1,
                                                   rows=2,
                                                   size_hint=(None, None),
                                                   size=(400, 400),
                                                   padding=50,
                                                   spacing=20,
                                                   ),
                                size_hint=(None, None),
                                size=(400, 400))

            # Create the Label and add it to the GridLayout
            error_label = Label(text=error_message, halign='center', valign='middle')
            error_popup.content.add_widget(error_label)

            # Create the button and add it to the GridLayout
            okay_button = Button(text='Okay', size_hint=(None, None), size=(100, 50))
            okay_button.bind(on_release=error_popup.dismiss)
            error_popup.content.add_widget(okay_button)

            error_popup.open()

        return self.scroll_view

    def on_stop(self):
        if self.serial_port:
            self.serial_port.close()

    def receive_data(self, dt):
        # Connect to SQLite database
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()

        # Create table
        cursor.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                        (back_shift REAL, back_lean REAL, head_lean REAL, head_shift REAL, timestamp TEXT)''')
        conn.commit()
        time.sleep(2)
        if self.serial_port and self.serial_port.in_waiting > 0:
            rolling_back_shift = []
            rolling_back_lean = []
            rolling_head_lean = []
            rolling_head_shift = []

            # Start reading and storing data from Arduino
            start_time = time.time()
            while True:
                try:
                    # Read data from serial port
                    data = ser.readline().decode().strip().split(',')
                    if len(data) == 4:
                        # Store data in variables
                        back_shift = float(data[0])
                        back_lean = float(data[1])
                        head_lean = float(data[2])
                        head_shift = float(data[3])
                        # Add data to rolling average
                        rolling_back_shift.append(back_shift)
                        rolling_back_lean.append(back_lean)
                        rolling_head_lean.append(head_lean)
                        rolling_head_shift.append(head_shift)
                        # Remove oldest data if rolling average exceeds 10 seconds
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 10:
                            rolling_back_shift.pop(0)
                            rolling_back_lean.pop(0)
                            rolling_head_lean.pop(0)
                            rolling_head_shift.pop(0)
                            start_time = time.time()
                        # Calculate rolling average
                        avg_back_shift = sum(rolling_back_shift) / len(rolling_back_shift)
                        avg_back_lean = sum(rolling_back_lean) / len(rolling_back_lean)
                        avg_head_lean = sum(rolling_head_lean) / len(rolling_head_lean)
                        avg_head_shift = sum(rolling_head_shift) / len(rolling_head_shift)
                        # Insert data into SQLite database
                        cursor.execute(
                            "INSERT INTO sensor_data (back_shift, back_lean, head_lean, head_shift, timestamp) VALUES (?, ?, ?, ?, ?)",
                            (avg_back_shift, avg_back_lean, avg_head_lean, avg_head_shift, time.time()))
                        conn.commit()
                        # Print data for testing purposes
                        print(
                            f"Back Shift: {avg_back_shift}, Back Lean: {avg_back_lean}, Head Lean: {avg_head_lean}, Head Shift: {avg_head_shift}")
                except:
                    print("Failed to read data from Arduino")
                    break

                self.serial_port.close()
                cursor.close()
                conn.close()

                # Scroll to the bottom of the ScrollView
                self.scroll_view.scroll_y = 0


class MainMode1Screen(BoxLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Hello World"))

class MainMode2Screen(BoxLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Hello World"))


class MyScreenManager(ScreenManager):
    pass

screen_manager = MyScreenManager()

screen_manager.add_widget(WelcomeScreen(name='welcome'))
screen_manager.add_widget(LoginScreen(name='login'))
screen_manager.add_widget(ModeScreen(name='mode'))
screen_manager.add_widget(MainMode1Screen(name='main_mode1'))
screen_manager.add_widget(MainMode2Screen(name='main_mode2'))
screen_manager.add_widget(MainMode3Screen(name='main_mode3'))

class NeckPainApp(App):
    def build(self):
        return screen_manager

if __name__ == '__main__':
    NeckPainApp().run()

