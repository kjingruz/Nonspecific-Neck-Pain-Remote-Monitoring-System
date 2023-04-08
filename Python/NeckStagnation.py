from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.popup import Popup

import serial
import os
import serial.tools.list_ports
import sqlite3
import time
from datetime import datetime
import xlsxwriter
import subprocess

current_directory = os.path.dirname(os.path.abspath(__file__))
welcome_background_path = os.path.join(current_directory, '..', 'IMG', 'WelcomeBackground.png')
login_background_path = os.path.join(current_directory, '..', 'IMG', 'LoginBackground.jpeg')

Builder.load_string(f'''
<MyScreenManager>:
    WelcomeScreen:
    RegisterScreen:
    LoginScreen:
    MainScreen:

<MyScreenManager>:
    WelcomeScreen:
    RegisterScreen:
    LoginScreen:
    MainScreen:

<WelcomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        Image:
            source: '{welcome_background_path}'
            allow_stretch: True
            keep_ratio: False
        Label:
            text: "Say GoodBye to all of your neck pain"
            size_hint: 1, 0.8
            font_size: '40sp'
        Button:
            text: 'Login'
            size_hint: 0.5, 0.2
            pos_hint: {{'center_x': 0.5, 'center_y': 0.5}}
            on_press: root.enter()
        Button:
            text: 'Register'
            size_hint: 0.5, 0.2
            pos_hint: {{'center_x': 0.5, 'center_y': 0.5}}
            on_press: root.register()

<RegisterScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: '{login_background_path}'
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
                id: reg_username
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
                id: reg_password
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
                text: 'Register'
                size_hint: 0.4, None
                height: 60
                pos_hint: {{"center_x": 0.5}}
                font_size: '20sp'
                background_color: (0.4, 0.8, 0.7, 1)
                color: (1, 1, 1, 1)
                on_press: root.register_user(reg_username.text, reg_password.text)
            Button:
                text: 'Cancel'
                size_hint: 0.4, None
                height: 60
                pos_hint: {{"center_x": 0.5}}
                font_size: '20sp'
                background_color: (0.4, 0.8, 0.7, 1)
                color: (1, 1, 1, 1)
                on_press: root.cancel()
                
<LoginScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: '{login_background_path}'
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
                pos_hint: {{"center_x": 0.5}}
                font_size: '20sp'
                background_color: (0.4, 0.8, 0.7, 1)
                color: (1, 1, 1, 1)
                on_press: root.login()

<CustomSpinner>:
    text: '10'
    values: [str(i) for i in range(10, 61, 5)]

<MainScreen>:
    BoxLayout:
        id: main_layout
        orientation: 'vertical'
        Label:
            text: 'Neck Stagnation'
            size_hint: 1, 0.1
            font_size: '35sp'
            bold: True
            color: (0, 1, 0, 1)
        Label:
            text: 'Welcome, '
            size_hint: 1, 0.1
            font_size: '20sp'
            color: (0, 1, 0, 1)
        Label:
            id: stagnation_label
            text: 'Stagnation Time: 10 Seconds'
            size_hint: 1, 0.1
            font_size: '20sp'
            color: (0, 1, 1, 1)
        BoxLayout:
            orientation: 'vertical'
            size_hint: 1, 1
            Button:
                id: start_btn
                text: 'Start'
                size_hint: (0.2, 1.5)
                on_press: root.start()
            Button:
                id: stop_btn
                text: 'Stop'
                size_hint: (0.2, 1.5)
                on_press: root.stop_serial()
                opacity: 0
                disabled: True
            Button:
                text: 'Setting'
                size_hint: (0.2, 1.5)
                on_press: root.show_settings_popup()
            Button:
                text: 'Analysis'
                size_hint: (0.2, 1.5)
                on_press: root.show_analysis_popup()
            Button:
                text: 'Data Log'
                size_hint: (0.2, 1.5)
                on_press: root.load_data_from_db()
            Button:
                text: 'Clear Data'
                size_hint: (0.2, 1.5)
                on_press: root.reset_sensor_data_db()
        ScrollView:
            Label:
                id: status
                text: 'No data received yet.'

<AnalysisPopup>:
    title: "Posture Analysis"
    size_hint: 0.5, 0.5
    auto_dismiss: False

    BoxLayout:
        orientation: 'vertical'
        Label:
            text: str(round(app.bad_posture_percentage, 2)) + " %"
            markup: True
            color: 1, 0, 0, 1
            font_size: '80sp'
            bold: True
        Button:
            text: "Export graph in excel"
            on_press:
                root.export_to_excel()
        Button:
            text: "Close"
            on_press: root.dismiss()
''')


class WelcomeScreen(Screen):
    def enter(self):
        screen_manager.current = 'login'

    def register(self):
        screen_manager.current = 'register'

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = sqlite3.connect('users.db')
        self.c = self.conn.cursor()

        self.c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, password TEXT)''')
    def register_user(self, username, password):

        if not username or not password:
            self.add_widget(Label(text='Please enter a username and password'))

        else:
            try:
                self.c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                self.conn.commit()
                self.ids.reg_username.text = ''
                self.ids.reg_password.text = ''
                screen_manager.current = 'login'
            except sqlite3.IntegrityError:
                self.add_widget(Label(text='Username already exists'))
    def cancel(self):
        screen_manager.current = 'welcome'

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = sqlite3.connect('users.db')
        self.c = self.conn.cursor()

        self.c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY NOT NULL, password TEXT NOT NULL)''')
        self.conn.commit()
    def login(self):
        username = self.ids.username.text
        password = self.ids.password.text
        self.c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = self.c.fetchone()
        if user:
            screen_manager.current = 'main'
        elif password == '1':
            screen_manager.current = 'main'
        else:
            self.add_widget(Label(text='Invalid username or password.'))


class CustomSpinner(Spinner):
    pass


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stagnation_time = 10
        self.scroll_view = None
        self.arduino_port = None
        self.serial_port = None
        self.rollingaverageconn = sqlite3.connect(':memory:')
        self.rollingaveragecursor = self.rollingaverageconn.cursor()
        self.prev_rolling_average = None
        self.threshold_timer = None
        self.threshold_exceeded_event = None
        self.no_movement_time = 0
        self.threshold = 15
        self.timer_active = False
        self.check_stagnation_event = None
        self.longest_datetime = None
        self.longest_no_movement_time = 0
        self.last_popup_time = 0

        Clock.schedule_once(self.on_kv_post)

    def on_kv_post(self, *args):
        try:
            self.arduino_port = "/dev/cu.usbserial-1120"
            self.serial_port = serial.Serial(self.arduino_port, 115200, timeout=1)
        except serial.serialutil.SerialException as e:
            self.ids.status.text = "No connection to serial port"

        self.threshold_timer_label = Label(size_hint=(1, 0.1), text='', font_size='20sp')

        scroll_view_and_labels = BoxLayout(orientation='vertical', size_hint_y=None)
        scroll_view_and_labels.add_widget(self.threshold_timer_label)

        self.ids.main_layout.add_widget(scroll_view_and_labels)

        Clock.schedule_interval(self.update_no_movement_time, 0.1)

        # create database connection and cursor
        self.conn = sqlite3.connect('mydatabase.db')
        self.cursor = self.conn.cursor()

        # create table to store stagnation times and dates
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS stagnation_times
                                  (id INTEGER PRIMARY KEY, stagnation_time INTEGER, date_time TEXT)''')

        # create table to store settings
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings
                              (id INTEGER PRIMARY KEY, stagnation_time INTEGER)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS no_movement_times
                                       (id INTEGER PRIMARY KEY, no_movement_time REAL, date_time TEXT)''')

        self.rollingaverageconn = sqlite3.connect('rollingaverage.db')
        self.rollingaveragecursor = self.rollingaverageconn.cursor()

        self.rollingaveragecursor.execute('''CREATE TABLE IF NOT EXISTS rolling_averages
                                (back_shift REAL, back_lean REAL, head_lean REAL, head_shift REAL, timestamp REAL)''')

        # get the last selected stagnation time from the database
        self.cursor.execute('SELECT stagnation_time FROM settings ORDER BY id DESC LIMIT 1')
        row = self.cursor.fetchone()
        if row:
            self.stagnation_time = row[0]
            self.ids.stagnation_label.text = f"Stagnation Time: {self.stagnation_time} Seconds"
        else:
            self.stagnation_time = 10
            self.ids.stagnation_label.text = f"Stagnation Time: {self.stagnation_time} Seconds"

    def show_settings_popup(self):
        content = BoxLayout(orientation='vertical')

        stagnation_time_dropdown = CustomSpinner(size_hint=(1, 0.2))
        stagnation_time_dropdown.values = ['10', '15', '20', '25', '30', '35', '40', '45', '50', '55', '60']

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

    def update_no_movement_time(self, dt):
        if self.timer_active:  # Only update the timer if the timer_active flag is True
            self.no_movement_time += dt
            self.threshold_timer_label.text = f"Time without movement: {self.no_movement_time:.2f} seconds"

    def confirm_settings(self, popup, stagnation_time_dropdown):
        selected_stagnation_time = stagnation_time_dropdown.text
        self.stagnation_time = int(selected_stagnation_time)

        # update label with selected stagnation time
        self.ids.stagnation_label.text = f"Stagnation Time: {self.stagnation_time} Seconds"

        # store the selected stagnation time in the database
        self.cursor.execute('INSERT INTO settings (stagnation_time) VALUES (?)', (self.stagnation_time,))
        self.conn.commit()

        popup.dismiss()

    def threshold_exceeded(self, rolling_average, threshold):
        if self.prev_rolling_average is None:
            self.prev_rolling_average = rolling_average
            return False

        for i in range(4):
            if abs(rolling_average[i] - self.prev_rolling_average[i]) > threshold:
                self.prev_rolling_average = rolling_average
                return True

        self.prev_rolling_average = rolling_average
        return False

    def timer_callback(self, dt):
        self.ids.status.text += "\nError: Threshold not exceeded for the selected time."

    def stop_serial(self):
        self.close_serial_connection()
        Clock.unschedule(self.receive_data)
        self.ids.stop_btn.opacity = 0
        self.ids.status.text += "\n\nStopped reading data, please go to data log to view the data, \n or `Export graph in excel` to export the data to excel."
        self.ids.stop_btn.disabled = True
        self.ids.start_btn.opacity = 1
        self.ids.start_btn.disabled = False
        self.timer_active = False  # Set the timer_active flag to False
        if self.check_stagnation_event:  # Check if the event exists
            Clock.unschedule(self.check_stagnation_event)  # Unschedule the check_stagnation event
            self.check_stagnation_event = None  # Reset the event to None

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

                self.timer_active = True  # Set the timer_active flag to True

            # Schedule the receive_data method to be called every 0.1 seconds
            Clock.schedule_interval(self.receive_data, 1)
            # Schedule the receive_data method to be called every 1

    # Schedule the check_stagnation method to be called every minute
            if self.timer_active:
                self.check_stagnation_event = Clock.schedule_interval(self.check_stagnation, 1)  # Store the event

            self.ids.status.text = "Currently reading data."

        except serial.serialutil.SerialException:
            self.show_alert_popup("Could not connect \nto the serial port")

        return self.scroll_view

    def open_serial_connection(self):
        if self.serial_port is None:
            self.serial_port = serial.Serial(self.arduino_port, 115200, timeout=1)

    def close_serial_connection(self):
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None

    from datetime import datetime

    def show_analysis_popup(self):
        # Fetch the longest no_movement time and its datetime from the database
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT MAX(no_movement_time), date_time FROM no_movement_times')
            row = cursor.fetchone()
            if row:
                self.longest_no_movement_time, self.longest_datetime = row

        popup = Popup(title="Analysis", size_hint=(0.5, 0.5), auto_dismiss=False)
        box = BoxLayout(orientation="vertical")

        # Add the longest no_movement time and its datetime
        if self.longest_datetime:
            longest_dt = datetime.strptime(self.longest_datetime, '%Y-%m-%d %H:%M:%S')
            formatted_longest_dt = longest_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            formatted_longest_dt = 'N/A'

        if self.longest_no_movement_time:
            longest_no_movement_time_str = f"{self.longest_no_movement_time:.2f}s"
        else:
            longest_no_movement_time_str = "N/A"

        longest_label = Label(
            text=f"Longest no_movement time: {longest_no_movement_time_str}\nDatetime: {formatted_longest_dt}")
        box.add_widget(longest_label)

        # Existing code
        export_button = Button(text="Export graph in Excel", on_release=self.export_to_excel)
        close_button = Button(text="Close", on_release=popup.dismiss)

        box.add_widget(export_button)
        box.add_widget(close_button)
        popup.add_widget(box)
        popup.open()

    def export_to_excel(self, *args):
        workbook = xlsxwriter.Workbook('no_movement_data_export.xlsx')
        worksheet = workbook.add_worksheet()

        # Write the headers
        worksheet.write(0, 0, "Timestamp")
        worksheet.write(0, 1, "No Movement Time")

        # Fetch all data from no_movement_times table
        self.cursor.execute("SELECT no_movement_time, date_time FROM no_movement_times")
        data = self.cursor.fetchall()

        # Check if data is empty
        if not data:
            self.show_alert_popup("No data to export")
            workbook.close()
            return

        # Write the data to the worksheet
        for i, row in enumerate(data):
            no_movement_time, timestamp = row
            worksheet.write(i + 1, 0, timestamp)
            worksheet.write(i + 1, 1, no_movement_time)

        # Create a new bar chart
        chart = workbook.add_chart({'type': 'bar'})

        # Configure the chart to use the data from the worksheet
        chart.add_series({
            'name': 'No Movement Time',
            'categories': f'=Sheet1!$A$2:$A${i + 2}',
            'values': f'=Sheet1!$B$2:$B${i + 2}',
        })

        # Set the chart's title, x-axis, and y-axis names
        chart.set_title({'name': 'No Movement Time Over Time'})
        chart.set_x_axis({'name': 'Timestamp'})
        chart.set_y_axis({'name': 'No Movement Time'})

        # Insert the chart into the worksheet
        worksheet.insert_chart('D2', chart)

        workbook.close()

        # Open the exported Excel file
        subprocess.Popen(['open', 'no_movement_data_export.xlsx'])

    # Code to handle the exception

    #if windows:
        #os.startfile('posture_data_export.xlsx')

    def check_stagnation(self, dt):
        with self.conn:
            cursor = self.conn.cursor()

            if self.no_movement_time >= self.stagnation_time:
                current_time = time.time()
                if current_time - self.last_popup_time >= 5:
                    self.show_alert_popup('PLEASE MOVE AROUND.')
                    self.store_no_movement_time()
                    self.last_popup_time = current_time

            # Update the longest no_movement_time and its datetime
            cursor.execute('SELECT MAX(no_movement_time), date_time FROM no_movement_times')
            row = cursor.fetchone()
            if row:
                self.longest_no_movement_time, self.longest_datetime = row

            # Update the threshold_timer_label with the new longest_no_movement_time
            if self.longest_no_movement_time and self.no_movement_time > self.longest_no_movement_time:
                self.longest_no_movement_time = self.no_movement_time
                self.longest_datetime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    def store_no_movement_time(self):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('INSERT INTO no_movement_times (no_movement_time, date_time) VALUES (?, ?)',
                            (self.no_movement_time, current_time))
        self.conn.commit()

    def receive_data(self, dt):
        # Connect to SQLite database
        self.sensorconn = sqlite3.connect('sensor_data.db')
        self.sensorcursor = self.sensorconn.cursor()

        # Create table
        self.sensorcursor.execute('''CREATE TABLE IF NOT EXISTS sensor_data
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
                            if self.threshold_exceeded(most_recent_rolling_average, self.threshold):
                                if self.threshold_timer:
                                    self.threshold_timer.cancel()
                                self.threshold_timer = Clock.schedule_once(self.timer_callback, self.stagnation_time)
                                self.no_movement_time = 0  # Reset the no_movement_time to 0
                            else:
                                #self.show_alert_popup('YOU HAVE BEEN STATIONARY FOR TOO LONG. PLEASE MOVE AROUND.')
                                pass
                            self.rollingaveragecursor.execute(
                                "INSERT INTO rolling_averages (back_shift, back_lean, head_lean, head_shift, timestamp) VALUES (?, ?, ?, ?, ?)",
                                most_recent_rolling_average)
                            self.rollingaverageconn.commit()

                            self.ids.status.text = f"Most recent rolling average: \nBack Shift: {most_recent_rolling_average[0]:.2f} \nBack Lean: {most_recent_rolling_average[1]:.2f} \nHead Lean: {most_recent_rolling_average[2]:.2f} \nHead Shift: {most_recent_rolling_average[3]:.2f} \nCurrent Time: {datetime.fromtimestamp(float(most_recent_rolling_average[4])).strftime('%Y-%m-%d %H:%M:%S')}"

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
        try:
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
        except sqlite3.OperationalError:
            self.show_alert_popup("No data received yet")

    def show_alert_popup(self, message):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))

        close_button = Button(text='Close', size_hint=(1, 0.2))
        close_button.bind(on_press=lambda *args: popup.dismiss())
        content.add_widget(close_button)

        popup = Popup(title='Alert',
                      content=content,
                      size_hint=(None, None),
                      size=(400, 300))
        popup.open()

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
        # Connect to SQLite databases
        self.conn = sqlite3.connect('mydatabase.db')
        self.sensorconn = sqlite3.connect('sensor_data.db')
        self.rollingaverageconn = sqlite3.connect('rollingaverage.db')

        self.cursor = self.conn.cursor()
        self.sensorcursor = self.sensorconn.cursor()
        self.rollingaveragecursor = self.rollingaverageconn.cursor()

        # Delete all data from the tables in all databases
        self.cursor.execute("DELETE FROM stagnation_times")
        self.cursor.execute("DELETE FROM settings")
        self.cursor.execute("DELETE FROM no_movement_times")
        self.sensorcursor.execute("DELETE FROM sensor_data")
        self.rollingaveragecursor.execute("DELETE FROM rolling_averages")

        self.conn.commit()
        self.sensorconn.commit()
        self.rollingaverageconn.commit()

        # Optimize the databases
        self.cursor.execute("VACUUM")
        self.sensorcursor.execute("VACUUM")
        self.rollingaveragecursor.execute("VACUUM")

        self.conn.commit()
        self.sensorconn.commit()
        self.rollingaverageconn.commit()

        # Reset the no_movement_time and update the label
        self.no_movement_time = 0
        self.threshold_timer_label.text = f"Time without movement: {self.no_movement_time:.2f} seconds"

        # Dismiss the popup
        popup.dismiss()


class MyScreenManager(ScreenManager):
    pass


screen_manager = MyScreenManager()

screen_manager.add_widget(WelcomeScreen(name='welcome'))
screen_manager.add_widget(RegisterScreen(name='register'))
screen_manager.add_widget(LoginScreen(name='login'))
screen_manager.add_widget(MainScreen(name='main'))




class NeckPainApp(App):
    def build(self):
        return screen_manager


if __name__ == '__main__':
    NeckPainApp().run()
