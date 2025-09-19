import os
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIWindow, UIButton, UIDropDownMenu, UIHorizontalSlider, UILabel


class OptionsWindow:
    def __init__(self, manager, window_size, initial_speed=50):
        self.manager = manager
        self.window_size = window_size
        self.is_open = False
        self.window = None
        self.speed_slider = None
        self.speed_label = None
        self.speed_value_label = None
        self.graph_dropdown = None
        self.graph_label = None
        self.close_button = None
        self.speed_value = initial_speed

    def open_window(self):
        if self.is_open:
            return

        self.is_open = True
        window_rect = pygame.Rect(
            (self.window_size[0] - 400) // 2,
            (self.window_size[1] - 300) // 2,
            400, 300
        )

        self.window = UIWindow(
            rect=window_rect,
            manager=self.manager,
            window_display_title='Options',
            object_id = ObjectID(class_id='window', object_id='window'),
        )

        # Speed controls
        self.speed_label = UILabel(
            relative_rect=pygame.Rect(20, 20, 80, 30),
            text='Speed:',
            manager=self.manager,
            container=self.window,
            object_id = ObjectID(class_id='options_label', object_id='options_label')
        )

        self.speed_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(110, 20, 200, 30),
            start_value=self.speed_value,
            value_range=(1, 100),
            manager=self.manager,
            container=self.window,
            object_id = ObjectID(class_id='horizontal_slider', object_id='horizontal_slider'),
        )

        self.speed_value_label = UILabel(
            relative_rect=pygame.Rect(320, 20, 50, 30),
            text=str(self.speed_value),
            manager=self.manager,
            container=self.window,
            object_id = ObjectID(class_id='options_label', object_id='options_label')
        )

        # Graph file dropdown
        graph_files = self._get_graph_files()
        self.graph_label = UILabel(
            relative_rect=pygame.Rect(20, 70, 80, 30),
            text='Graph:',
            manager=self.manager,
            container=self.window,
            object_id=ObjectID(class_id='options_label', object_id='options_label')
        )

        self.graph_dropdown = UIDropDownMenu(
            options_list=graph_files,
            starting_option=graph_files[0] if graph_files else "No graphs found",
            relative_rect=pygame.Rect(110, 70, 200, 30),
            manager=self.manager,
            container=self.window
        )

        # Close button
        self.close_button = UIButton(
            relative_rect=pygame.Rect(300, 220, 80, 30),
            text='Close',
            manager=self.manager,
            container=self.window,
            object_id = ObjectID(class_id=None, object_id='#button-label'),
        )

    def _get_graph_files(self):
        graph_dir = "./graphs"
        if not os.path.exists(graph_dir):
            return ["No graphs found"]

        files = []
        for file in os.listdir(graph_dir):
            if file.endswith(('.json', '.txt', '.graph')):
                files.append(file)

        return files if files else ["No graphs found"]

    def close_window(self):
        if not self.is_open:
            return

        self.is_open = False
        if self.window:
            self.window.hide()
            self.window = None
            self.speed_slider = None
            self.speed_label = None
            self.graph_dropdown = None
            self.close_button = None

    def handle_event(self, event):
        if not self.is_open:
            return None

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_WINDOW_CLOSE:
                self.close_window()
                return None

            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.close_button:
                    self.close_window()
                    return None

            elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.speed_slider:
                    self.speed_value = int(self.speed_slider.get_current_value())
                    self.speed_value_label.set_text(str(self.speed_value))
                    return {'type': 'speed_changed', 'value': self.speed_value}

            elif event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.graph_dropdown:
                    selected_graph = self.graph_dropdown.selected_option
                    return {'type': 'graph_changed', 'value': selected_graph}
        return None
