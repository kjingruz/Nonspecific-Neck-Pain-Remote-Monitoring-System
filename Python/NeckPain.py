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
import time
from datetime import datetime
from plyer import notification

Builder.load_string('''
<MyScreenManager>:
    WelcomeScreen:
    LoginScreen:
    MainScreen:

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

<CustomSpinner>:
    text: '10'
    values: [str(i) for i in range(10, 61, 5)]

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            id: start_btn
            text: 'Start'
            size_hint: (0.2, 0.1)
            on_press: root.start()
        Button:
            id: stop_btn
            text: 'Stop'
            size_hint: (0.2, 0.1)
            on_press: root.stop_serial()
            opacity: 0
            disabled: True
        Button:
            text: 'Setting'
            size_hint: (0.2, 0.1)
            on_press: root.show_settings_popup()
        Button:
            text: 'Analysis'
            size_hint: (0.2, 0.1)
        Button:
            text: 'Data Log'
            size_hint: (0.2, 0.1)
            on_press: root.load_data_from_db()
        Button:
            text: 'Clear Data'
            size_hint: (0.2, 0.1)
            on_press: root.reset_sensor_data_db()
        ScrollView:
            Label:
                id: status
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
            screen_manager.current = 'main'
        else:
            self.add_widget(Label(text='Invalid password.'))


class CustomSpinner(Spinner):
    pass


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.internal_timer = None
        self.stagnation_time = 10
        self.start_time = 0
        self.scroll_view = None
        self.arduino_port = None
        self.serial_port = None

        Clock.schedule_once(self.on_kv_post)

    def on_kv_post(self, *args):
        try:
            # Open the serial port
            self.arduino_port = "/dev/cu.usbserial-120"
            self.serial_port = serial.Serial(self.arduino_port, 115200, timeout=1)
        except serial.serialutil.SerialException as e:
            self.ids.status.text = "No connection to serial port"

        # create label to display stagnation time
        self.stagnation_time_label = Label(text="Stagnation Time: seconds", size_hint=(1, 0.1))
        self.add_widget(self.stagnation_time_label)

        # create database connection and cursor
        self.conn = sqlite3.connect('mydatabase.db')
        self.cursor = self.conn.cursor()

        # create table to store stagnation times and dates
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS stagnation_times
                                  (id INTEGER PRIMARY KEY, stagnation_time INTEGER, date_time TEXT)''')

        # get the last selected stagnation time from the database
        self.cursor.execute('SELECT stagnation_time FROM settings ORDER BY id DESC LIMIT 1')
        row = self.cursor.fetchone()
        if row:
            self.stagnation_time = row[0]
            self.stagnation_time_label.text = f"Stagnation Time: {self.stagnation_time} seconds"

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
                                message='You have been in the same posture for {} seconds.'.format(
                                    self.stagnation_time),
                                app_name=App.get_running_app().title)

    def stop_serial(self):
        self.close_serial_connection()
        Clock.unschedule(self.receive_data)
        self.ids.stop_btn.opacity = 0
        self.ids.status.text += "\n\nStopped reading data, please view data log to view the data"
        self.ids.stop_btn.disabled = True
        self.ids.start_btn.opacity = 1
        self.ids.start_btn.disabled = False

    def calculate_rolling_average(self, data, rolling_interval):
        rolling_data = []
        rolling_averages = []

        for current_data in data:
            rolling_data.append(current_data)

            while rolling_data and float(rolling_data[-1][4]) - float(rolling_data[0][4]) > rolling_interval:
                rolling_data.pop(0)

            avg_back_shift = sum([x[0] for x in rolling_data]) / len(rolling_data)
            avg_back_lean = sum([x[1] for x in rolling_data]) / len(rolling_data)
            avg_head_lean = sum([x[2] for x in rolling_data]) / len(rolling_data)
            avg_head_shift = sum([x[3] for x in rolling_data]) / len(rolling_data)

            rolling_averages.append((avg_back_shift, avg_back_lean, avg_head_lean, avg_head_shift, current_data[4]))

        return rolling_averages

    def start(self):
        try:
            # Open the serial port
            self.open_serial_connection()

            if self.serial_port:
                self.ids.stop_btn.opacity = 1
                self.ids.stop_btn.disabled = False
                self.ids.start_btn.opacity = 0
                self.ids.start_btn.disabled = True

            # Schedule the receive_data method to be called every 0.1 seconds
            Clock.schedule_interval(self.receive_data, 1)
            self.ids.status.text = "Currently reading data."

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

    def open_serial_connection(self):
        if self.serial_port is None:
            self.serial_port = serial.Serial(self.arduino_port, 115200, timeout=1)

    def close_serial_connection(self):
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None

    def is_bad_posture(self, avg_back_shift, avg_back_lean, avg_head_lean, avg_head_shift, threshold=30):
        return (
                abs(avg_back_shift) > threshold
                or abs(avg_back_lean) > threshold
                or abs(avg_head_lean) > threshold
                or abs(avg_head_shift) > threshold
        )
    def check_stagnation(self, dt):
    # Calculate the time range to check for stagnation
        start_time = time.time() - self.stagnation_time * 60

    # Fetch rolling averages within the specified time range
        self.sensorcursor.execute(
            "SELECT * FROM rolling_averages WHERE timestamp >= ?",
            (start_time,))
        recent_rolling_averages = self.sensorcursor.fetchall()

    # Count the bad postures
        bad_postures = 0
        for ra in recent_rolling_averages:
            if self.is_bad_posture(ra[0], ra[1], ra[2], ra[3]):
                bad_postures += 1

    # Calculate the percentage of bad postures
        bad_posture_percentage = (bad_postures / len(recent_rolling_averages)) * 100

    # Check for stagnation and send a notification if necessary
        if bad_posture_percentage > 50:
            self.ids.status.color = (1, 0, 0, 1)  # Red color
            self.ids.status.text += "\nWarning: Stagnation detected!"
            notification.notify(
                title='Stagnation Warning',
                message='More than 50% bad postures detected in the last {} minutes.'.format(self.stagnation_time),
                app_name=App.get_running_app().title)
        else:
            self.ids.status.color = (1, 1, 1, 1)  # White color

    def receive_data(self, dt):
        # Connect to SQLite database
        self.sensorconn = sqlite3.connect('sensor_data.db')
        self.sensorcursor = self.sensorconn.cursor()

        # Create table
        self.sensorcursor.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                            (back_shift REAL, back_lean REAL, head_lean REAL, head_shift REAL, timestamp REAL)''')
        self.sensorconn.commit()

        # Create rolling_averages table
        self.sensorcursor.execute('''CREATE TABLE IF NOT EXISTS rolling_averages
                            (back_shift REAL, back_lean REAL, head_lean REAL, head_shift REAL, timestamp REAL)''')
        self.sensorconn.commit()

        try:
            # Start reading and storing data from Arduino
            if self.serial_port and self.serial_port.in_waiting > 0:
                # Read data from serial port
                data = self.serial_port.readline().decode().strip().split(',')
                if len(data) == 4:
                    try:
                        # Store data in variables and append timestamp
                        current_data = [float(data[0]), float(data[1]), float(data[2]), float(data[3]), time.time()]

                        # Insert data into SQLite database
                        self.sensorcursor.execute(
                            "INSERT INTO sensor_data (back_shift, back_lean, head_lean, head_shift, timestamp) VALUES (?, ?, ?, ?, ?)",
                            (current_data[0], current_data[1], current_data[2], current_data[3], current_data[4]))
                        self.sensorconn.commit()

                        # Fetch data from the last 10 seconds
                        self.sensorcursor.execute(
                            "SELECT * FROM sensor_data WHERE timestamp >= ?",
                            (time.time() - 10,))
                        recent_data = self.sensorcursor.fetchall()

                        # Calculate the rolling average for the last 10 seconds
                        rolling_averages = self.calculate_rolling_average(recent_data, 10)

                        # Store the most recent rolling average in the database
                        if rolling_averages:
                            most_recent_rolling_average = rolling_averages[-1]
                            self.sensorcursor.execute(
                                "INSERT INTO rolling_averages (back_shift, back_lean, head_lean, head_shift, timestamp) VALUES (?, ?, ?, ?, ?)",
                                most_recent_rolling_average)
                            self.sensorconn.commit()
                            bad_posture = self.is_bad_posture(most_recent_rolling_average[0], most_recent_rolling_average[1], most_recent_rolling_average[2], most_recent_rolling_average[3])

        # Update the ScrollView label with the most recent rolling average and posture status
                            self.ids.status.text = f"Most recent rolling average: \nBack Shift: {most_recent_rolling_average[0]:.2f} \nBack Lean: {most_recent_rolling_average[1]:.2f} \nHead Lean: {most_recent_rolling_average[2]:.2f} \nHead Shift: {most_recent_rolling_average[3]:.2f}\nPosture status: {'Bad' if bad_posture else 'Good'}"

                    except ValueError:
                        self.ids.status.text = "Failed reading data, please check the data format."
                    except Exception as e:
                        self.ids.status.text = f"Unexpected error: {e}"
        except Exception as e:
            self.ids.status.text = f"Error: {e}"

    def create_data_popup(self, data):
        layout = BoxLayout(orientation='vertical')
        close_button = Button(text='Close', size_hint=(1, 0.2))
        layout.add_widget(Label(text='Data Log:'))

        # Format the header and data rows
        header = "{:<15} {:<15} {:<15} {:<15} {:<20}".format("Back Shift", "Back Lean", "Head Lean", "Head Shift",
                                                             "Timestamp")
        data_log_text = "\n".join([
                                      f"{row[0]:<15.2f} {row[1]:<15.2f} {row[2]:<15.2f} {row[3]:<15.2f} {datetime.fromtimestamp(float(row[4])).strftime('%Y-%m-%d %H:%M:%S')}"
                                      for row in data])

        # Create a scroll view and a box layout for the data log
        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=True, size_hint=(1, 0.6), bar_width=10)
        data_log_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        data_log_layout.bind(minimum_height=data_log_layout.setter('height'))

        # Add a label for the header and each data row
        data_log_layout.add_widget(Label(text=header, size_hint_y=None, height=30))
        for row in data_log_text.split("\n"):
            data_log_layout.add_widget(Label(text=row, size_hint_y=None, height=30))

        scroll_view.add_widget(data_log_layout)
        layout.add_widget(scroll_view)
        layout.add_widget(close_button)

        popup = Popup(title='Data Log', content=layout, size_hint=(0.8, 0.8), auto_dismiss=False)
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def load_data_from_db(self):
        # Connect to SQLite database
        self.sensorconn = sqlite3.connect('sensor_data.db')
        self.sensorcursor = self.sensorconn.cursor()

        # Fetch all data from sensor_data table
        self.sensorcursor.execute("SELECT * FROM sensor_data")
        data = self.sensorcursor.fetchall()

        # Create and show the data log popup
        self.create_data_popup(data)

        # Close the cursor and the connection
        self.sensorcursor.close()
        self.sensorconn.close()

    def reset_sensor_data_db(self):
        content = BoxLayout(orientation='vertical')

        message = Label(text="Are you sure you want to reset the data?")
        content.add_widget(message)

        buttons_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        yes_button = Button(text='Yes')
        no_button = Button(text='No')

        buttons_layout.add_widget(yes_button)
        buttons_layout.add_widget(no_button)
        content.add_widget(buttons_layout)

        confirm_reset_popup = Popup(title='Confirm Reset', content=content, size_hint=(0.4, 0.3), auto_dismiss=False)

        yes_button.bind(on_press=lambda x: self.perform_reset(confirm_reset_popup))
        no_button.bind(on_press=confirm_reset_popup.dismiss)

        confirm_reset_popup.open()

    def perform_reset(self, popup):
        # Connect to SQLite database
        self.sensorconn = sqlite3.connect('sensor_data.db')
        self.sensorcursor = self.sensorconn.cursor()

        # Delete all data from sensor_data table
        self.sensorcursor.execute("DELETE FROM sensor_data")
        self.sensorconn.commit()

        # Optimize the database
        self.sensorcursor.execute("VACUUM")
        self.sensorconn.commit()

        # Close the cursor and the connection
        self.sensorcursor.close()
        self.sensorconn.close()

        # Dismiss the popup
        popup.dismiss()


class MyScreenManager(ScreenManager):
    pass


screen_manager = MyScreenManager()

screen_manager.add_widget(WelcomeScreen(name='welcome'))
screen_manager.add_widget(LoginScreen(name='login'))
screen_manager.add_widget(MainScreen(name='main'))


class NeckPainApp(App):
    def build(self):
        return screen_manager


if __name__ == '__main__':
    NeckPainApp().run()
