import os
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton, UIDropDownMenu, UILabel

from gui.config_legend import ConfigLegend
from gui.options_window import OptionsWindow
from src.algorithms import Algorithms
from src.gui.color_legend import ColorLegend
from src.gui.heuristics_table import HeuristicsTable
from src.node import Node
from src.search_visualizer import SearchVisualizer
from src.utils.colors import Color
from src.utils.map_renderer import MapRenderer
from src.graph import Graph


class GUIManager:
    def __init__(self, graph):
        self.found_path = None
        self.visit_order = None
        self.graph = graph
        self.animation_completed = False
        self._cached_font = pygame.font.SysFont("Tahoma", 16)

        # Ajustar se necessario
        self.window_size = (800, 800)
        self.top = pygame.Rect(0, 0, self.window_size[0], 50)  # Top bar
        self.down = pygame.Rect(0, self.window_size[1] - 40, self.window_size[1], 40)
        self.DARKBLUE = (52, 73, 94)
        self.graph_margin = 100
        self.animation_speed = 50
        self.animation_timer = 0
        self.legend_margin_left = 200
        self.heuristics_margin_left = 10
        self.heuristics_margin_top = 75
        self.config_legend_margin_right = 10
        self.config_legend_margin_top = 75
        self.node_radius = 20
        self.background_color = Color.WHITE.value
        self.node_color = Color.BLUE.value

        # Configurations
        self.current_configs = {
            "Animation Speed": self.animation_speed,
            "Graph": self.graph.get_graph_name()
        }

        # Initialize pygame components
        self.screen = pygame.display.set_mode(self.window_size)
        self.manager = pygame_gui.UIManager(self.window_size, './gui/theme.json')

        # Inicializar motor
        self.algorithms = Algorithms(self.graph)
        self.visualizer = SearchVisualizer(self.graph)
        self.heuristics_table = HeuristicsTable((self.heuristics_margin_left, self.heuristics_margin_top), graph)
        self.color_legend = ColorLegend(self.legend_margin_left, self.window_size[1] - 40, self.down)

        self.config_legend = ConfigLegend((self.window_size[0] - self.config_legend_margin_right - 150, self.config_legend_margin_top), graph, self.current_configs)
        self.options_window = OptionsWindow(self.manager, self.window_size, self.animation_speed)

        # Initialize map renderer and nodes
        self.map_renderer = MapRenderer(shapefile_path="./utils/maps/PRT_ADM1.shp", window_size=self.window_size, margin=self.graph_margin, manager=self.manager)
        self.positions = self.map_renderer.map_positions(self.graph.nx_graph)
        self.nodes = {name: Node(name, pos, self._cached_font) for name, pos in self.positions.items()}

        # UI elements configs
        space_between_elements = 10
        center_group_width = 60 + space_between_elements + 200 + space_between_elements + 50
        right_group_width = 100 + space_between_elements + 100
        left_start_x = space_between_elements
        center_start_x = (self.window_size[0] - center_group_width) // 2
        right_start_x = self.window_size[0] - right_group_width - space_between_elements

        # Options button
        self.options_button = UIButton(
            relative_rect=pygame.Rect((left_start_x, 10), (100, 40)),
            text='Options',
            manager=self.manager,
            object_id=ObjectID(class_id=None, object_id='#button-label'),
        )
        left_start_x += 100 + space_between_elements
        self.options_button.rect.centery = self.top.centery

        # Dropdown menu for algorithm choice
        self.algorithm_dropdown = UIDropDownMenu(
            options_list=self.algorithms.designations,
            starting_option=self.algorithms.designations[0],
            relative_rect=pygame.Rect((left_start_x, 5), (200, 40)),
            manager=self.manager,
            object_id=ObjectID(class_id=None, object_id='drop_down_menu'),
        )
        self.algorithm_dropdown.rect.centery = self.top.centery
        center_start_x += 150 + space_between_elements

        # Begin button
        self.begin_button = UIButton(
            relative_rect=pygame.Rect((center_start_x, 10), (100, 40)),
            text='Begin',
            manager=self.manager,
            object_id=ObjectID(class_id=None, object_id='#button-begin'),
        )
        self.begin_button.rect.centery = self.top.centery

        # Reset button
        self.reset_button = UIButton(
            relative_rect=pygame.Rect((right_start_x, 10), (100, 40)),
            text='Reset',
            manager=self.manager,
            object_id=ObjectID(class_id=None, object_id='#button-label'),
        )
        right_start_x += 100 + space_between_elements
        self.reset_button.rect.centery = self.top.centery

        # Exit button
        self.exit_button = UIButton(
            relative_rect=pygame.Rect((right_start_x, 10), (100, 40)),
            text='Exit',
            manager=self.manager,
            object_id=ObjectID(class_id=None, object_id='#button-label'),
        )
        self.exit_button.rect.centery = self.top.centery

        # Info toggle heuristics table
        self.heuristics_table_info_label = UILabel(
            relative_rect=pygame.Rect((10, 50), (210, 30)),
            text="Click 'H' key to toggle heuristics table",
            manager=self.manager,
            object_id=ObjectID(class_id=None, object_id='#normal-label')
        )

        # Config legend label
        self.config_legend_label = UILabel(
            relative_rect=pygame.Rect((self.window_size[0] - self.config_legend_margin_right - 160, self.config_legend_margin_top - 30), (150, 50)),
            text="Current Configurations:",
            manager=self.manager,
            object_id=ObjectID(class_id=None, object_id='#normal-label')
        )

    def process_events(self, event):
        # Handle options window events first
        options_result = self.options_window.handle_event(event)
        if options_result:
            if options_result['type'] == 'speed_changed':
                self.animation_speed = options_result['value']
                self.update_config_legend('Animation Speed', options_result['value'])
            elif options_result['type'] == 'graph_changed':
                self.load_graph(options_result['value'][0])
                self.update_config_legend('Graph', options_result['value'][0])

        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.begin_button:
                self.reset()  # Reset the visualizer and algorithms before starting a new search
                selected_algorithm = self.algorithm_dropdown.selected_option[0]
                print("[ALGO] Begin search for search algorithm:", selected_algorithm)
                self.visit_order, self.found_path = self.algorithms.perform_search(selected_algorithm, self.graph.start_node, self.graph.end_node)

            elif event.ui_element == self.options_button:
                self.options_window.open_window()

            elif event.ui_element == self.reset_button:
                print("[ALGO] Graph search reset!")
                self.reset()

            elif event.ui_element == self.exit_button:
                pygame.quit()
                print("[ROOT] pyMapz exited.")
                exit()

        # For the heuristics table
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:  # Press 'h' to toggle heuristics table
                self.heuristics_table.show = not self.heuristics_table.show

        self.manager.process_events(event)

    def update(self, time_delta):
        self.manager.update(time_delta)

        # Process animation updates, if visit_order is set
        if hasattr(self, 'visit_order') and self.visit_order:
            self.animation_timer += time_delta * 1000  # Convert to milliseconds
            animation_interval = max(50, 1000 - (self.animation_speed * 10))  # Adjust interval based on speed

            if self.animation_timer >= animation_interval:
                self.animation_timer = 0  # Reset timer

                # Process the next node in visit_order
                if self.visit_order:
                    next_node_name = self.visit_order.pop(0)
                    self.visualizer.add_visited_node(next_node_name)
                    self.nodes[next_node_name].set_order(len(self.visualizer.visited_nodes))

                # Check if the animation is completed
                self.animation_completed = not self.visit_order

    def draw(self):
        # Clear or fill the screen
        self.screen.fill(self.background_color)
        pygame.draw.rect(self.screen, self.DARKBLUE, self.top)  # Draw TOP BAR
        pygame.draw.rect(self.screen, self.DARKBLUE, self.down)  # Draw DOWN BAR
        # Draw map + edges + nodes in one shot
        self.map_renderer.draw(
            screen=self.screen,
            graph=self.graph,
            nodes=self.nodes,
            visualizer=self.visualizer,
            found_path=self.found_path or [],
            animation_done=self.animation_completed,
            radius=self.node_radius
        )

        # Then draw your GUI overlays (buttons, legends, tables)
        self.manager.draw_ui(self.screen)
        self.color_legend.draw(self.screen)
        self.config_legend.draw(self.screen)
        self.heuristics_table.draw(self.screen) if hasattr(self.heuristics_table, 'show') and self.heuristics_table.show else None

    def update_config_legend(self, key, value):
        """Updates the configuration legend when a configuration changes."""
        self.current_configs[key] = value
        self.config_legend.update_configs(self.current_configs)

    def load_graph(self, graph_file):
        """Loads a graph from a file and updates the visualizer and algorithms."""
        try:
            # Build the full path to the graph file
            graph_path = os.path.join('./graphs', graph_file)

            # Check if the graph file exists
            if not os.path.exists(graph_path):
                print(f"[ERRO] Arquivo de grafo não encontrado: {graph_path}")
                return False

            # Load the graph from the specified file
            self.graph = Graph(graph_path)

            # Update the visualizer and algorithms with the new graph
            self.visualizer.set_graph(self.graph)
            self.algorithms = Algorithms(self.graph)
            self.heuristics_table = HeuristicsTable((self.heuristics_margin_left, self.heuristics_margin_top), self.graph)

            # Update map nodes and positions
            self.positions = self.map_renderer.map_positions(self.graph.nx_graph)
            self.nodes = {name: Node(name, pos, self._cached_font) for name, pos in self.positions.items()}

            # Reset the visualizer and algorithms
            self.reset()

            print(f"[GRAPH] Graph '{graph_file}' loaded successfully!")
            return True

        except Exception as e:
            print(f"[ERRO] Failed to load graph '{graph_file}': {e}")
            return False

    def reset(self):
        self.visualizer.clear_visited_nodes()  # Clear visited nodes
        self.visit_order = []  # Reset visit_order
        self.found_path = []  # Reset found path
        self.algorithms.found_path = []  # Reset found path in algorithms
        self.algorithms.visit_order = []  # Reset visit order in algorithms
        self.map_renderer.reset_animation()
        for node in self.nodes.values():
            node.reset_surf_order()
        self.animation_completed = False  # Reset animation completed flag
