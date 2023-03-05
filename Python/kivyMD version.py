from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import MDLabel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import MDTextField
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDIcon
from kivymd.uix.list import OneLineListItem, ThreeLineAvatarListItem
from kivymd.uix.list import MDList

import serial
from kivy.clock import Clock
from plyer import notification

Builder.load_string('''
<MyScreenManager>:
    WelcomeScreen:
    LoginScreen:
    ModeScreen:
    Mode3Screen:

<WelcomeScreen>:
    orientation: 'vertical'
    spacing: '20dp'
    padding: '50dp'

    MDLabel:
        text: "Say Bye to all of your neck pain"
        halign: 'center'
        font_style: 'H5'

    MDFlatButton:
        text: "Login"
        font_size: '20sp'
        on_press: root.enter()

<LoginScreen>:
    orientation: 'vertical'
    spacing: '20dp'
    padding: '50dp'

    MDLabel:
        text: "Login"
        halign: 'center'
        font_style: 'H5'

    MDTextField:
        id: username
        hint_text: "Username"
        mode: "rectangle"

    MDTextField:
        id: password
        hint_text: "Password"
        mode: "rectangle"
        password: True

    MDFlatButton:
        text: "Login"
        font_size: '20sp'
        on_press: root.login()

<ModeScreen>:
    orientation: 'vertical'
    spacing: '20dp'
    padding: '50dp'

    MDCard:
        orientation: "vertical"
        size_hint: None, None
        size: "350dp", "350dp"
        radius: '10dp'

        ThreeLineAvatarListItem:
            text: "Neck Only"
            secondary_text: "Select to choose mode 1"
            tertiary_text: " "
            on_release: root.mode1()
            IconLeftWidget:
                icon: "human-greeting"

        ThreeLineAvatarListItem:
            text: "Back Only"
            secondary_text: "Select to choose mode 2"
            tertiary_text: " "
            on_release: root.mode2()
            IconLeftWidget:
                icon: "human-greeting"

        ThreeLineAvatarListItem:
            text: "Neck and Back"
            secondary_text: "Select to choose mode 3"
            tertiary_text: " "
            on_release: root.mode3()
            IconLeftWidget:
                icon: "human-greeting"

<Mode3Screen>:
    orientation: 'vertical'
    spacing: '20dp'
    padding: '50dp'

    MDLabel:
        text: "Mode 3"
        halign: 'center'
        font_style: 'H5'

    MDFlatButton:
        text: "Start"
        font_size: '20sp'
        on_press: root.build()

    ScrollView:
        do_scroll_x: False
        MDList:
            id: serial_data

''')


class WelcomeScreen(Screen):
    def enter(self):
        self.manager.current = 'login'
