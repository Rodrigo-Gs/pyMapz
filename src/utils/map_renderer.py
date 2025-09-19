import geopandas as gpd
import numpy as np
import pygame
from src.utils.colors import Color


class MapRenderer:
    """
    Object-oriented renderer for mapping and drawing graphs over geographic districts.
    """

    def __init__(self, shapefile_path="./utils/maps/PRT_ADM1.shp", window_size=(960, 740), margin=150, manager=None):
        """
        Load the shapefile, compute centroids and polygon shapes, and prepare scaling.
        Args:
            shapefile_path (str): Path to the GPKG/SHAPEFILE with district geometries.
            window_size (tuple): (width, height) of the rendering surface.
            margin (int): margin in pixels around the map.
        """
        self.window_width, self.window_height = window_size
        self.margin = margin
        self.manager = manager
        self.visited_nodes, self.path_nodes = set(), set()
        self._font_cache = pygame.font.SysFont('Tahoma', 12)
        self._background_surface = None
        self._edge_data = {}
        self._weight_surfaces = {}

        # Load geodata and drop metadata rows
        gdf = gpd.read_file(shapefile_path, encoding='utf-8')
        gdf = gdf.iloc[2:].reset_index(drop=True)

        # Compute centroids and raw bounds
        self._centroids = {}
        xs, ys = [], []
        for _, row in gdf.iterrows():
            name = str(row.get("NAME") or row.get("Name") or row.get("NAME_1") or '')
            geom = row.geometry
            if geom is None:
                continue
            cx, cy = geom.centroid.x, geom.centroid.y
            self._centroids[name] = (cx, cy)
            xs.append(cx)
            ys.append(cy)
        if not xs:
            raise ValueError("No centroids found in shapefile.")

        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)
        geo_w = self.max_x - self.min_x
        geo_h = self.max_y - self.min_y

        # Compute scale factoring margin
        avail_w = self.window_width - 2 * self.margin
        avail_h = self.window_height - 2 * self.margin
        self.scale = min(avail_w / geo_w, avail_h / geo_h)

        # Compute offsets to center map within margin
        raw_w, raw_h = geo_w * self.scale, geo_h * self.scale
        self.off_x = self.margin + (avail_w - raw_w) / 2
        self.off_y = self.margin + (avail_h - raw_h) / 2

        # Helper to transform geographic to screen coords
        def tf(x, y):
            sx = self.off_x + (x - self.min_x) * self.scale
            sy = self.off_y + (self.max_y - y) * self.scale
            return int(sx), int(sy)

        # Precompute shapes
        self.shapes = []
        for geom in gdf.geometry:
            if geom.geom_type == 'Polygon':
                self.shapes.append([tf(x, y) for x, y in geom.exterior.coords])
                for hole in geom.interiors:
                    self.shapes.append([tf(x, y) for x, y in hole.coords])
            elif geom.geom_type == 'MultiPolygon':
                for poly in geom.geoms:
                    self.shapes.append([tf(x, y) for x, y in poly.exterior.coords])
                    for hole in poly.interiors:
                        self.shapes.append([tf(x, y) for x, y in hole.coords])

    def map_positions(self, graph):
        pos = {}
        for node in graph.nodes():
            centroid = self._centroids.get(str(node))
            if centroid:
                x, y = centroid
                sx = self.off_x + (x - self.min_x) * self.scale
                sy = self.off_y + (self.max_y - y) * self.scale
                pos[node] = (int(sx), int(sy))
            else:
                default = (self.window_width // 2, self.window_height // 2)
                pos[node] = default
        print(f"[GUI] Mapped {len(pos)} nodes to screen positions.")
        return pos

    def draw(self, screen, graph, nodes, visualizer, found_path, animation_done, radius=20):
        """
        Draw the map polygons, graph edges, weights, and nodes onto the screen.
        Args:
            screen: pygame Surface to draw on.
            graph: graph object with .nx_graph.edges and .start_node/.end_node.
            nodes: dict of node_label -> Node instance with .pos and draw()
            visualizer: SearchVisualizer with visited_nodes list.
            found_path: list of node labels representing the final path.
            animation_done (bool): whether the search animation completed.
            radius (int): node circle radius.
        """
        # Draw map shapes
        if self._background_surface is None:
            self._background_surface = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
            for poly in self.shapes:
                pygame.draw.polygon(self._background_surface, Color.WHITE.value, poly)
                pygame.draw.polygon(self._background_surface, Color.BLACK.value, poly, 2)

        # Fill the background
        screen.blit(self._background_surface, (0, 0))

        # Get visited and path nodes
        self.visited_nodes = set(visualizer.visited_nodes)
        self.path_nodes = set(found_path) if animation_done else set()

        # Draw edges
        edge_labels = []
        for u, v in graph.nx_graph.edges:
            # Calculate edge key
            edge_key = (u, v)
            if edge_key not in self._edge_data:
                p1 = np.array(nodes[u].pos, float)
                p2 = np.array(nodes[v].pos, float)
                d = p2 - p1
                dist = np.linalg.norm(d)
                if dist == 0:
                    continue

                direction = d / dist
                perp = np.array([-direction[1], direction[0]])
                tip = p2 - radius * direction
                offset = 15 * direction * 0.5
                left = tip - offset - 15 * perp * 0.7
                right = tip - offset + 15 * perp * 0.7

                self._edge_data[edge_key] = {
                    'p1': tuple(p1),
                    'tip': tuple(tip),
                    'left': tuple(left),
                    'right': tuple(right),
                    'mid': tuple((p1 + p2) / 2)
                }

            data = self._edge_data[edge_key]

            # Draw edge line
            pygame.draw.line(screen, Color.BLACK.value, data['p1'], data['tip'], 1)
            pygame.draw.line(screen, Color.BLACK.value, data['tip'], data['left'], 1)
            pygame.draw.line(screen, Color.BLACK.value, data['tip'], data['right'], 1)

            # Draw edge weight
            weight = graph.nx_graph[u][v].get('weight', '')
            if weight:
                weight_str = str(weight)
                if weight_str not in self._weight_surfaces:
                    txt = self._font_cache.render(weight_str, True, Color.BLACK.value, Color.WHITE.value)
                    tw, th = txt.get_size()
                    surf = pygame.Surface((tw + 3, th + 3))
                    surf.fill(Color.WHITE.value)
                    surf.blit(txt, (3, 3))
                    self._weight_surfaces[weight_str] = surf
                edge_labels.append((self._weight_surfaces[weight_str], data['mid']))

        # Draw nodes
        for name, node in nodes.items():
            if name == graph.start_node:
                color = Color.BLACK.value
            elif name == graph.end_node:
                color = Color.RED.value
            elif name in self.path_nodes:
                color = Color.YELLOW.value
            elif name in self.visited_nodes:
                color = Color.GREEN.value
            else:
                color = Color.BLUE.value
            node.set_color(color)
            node.draw(screen)

        # At last, draw edge labels
        for surf, mid_pos in edge_labels:
            rect = surf.get_rect(center=mid_pos)
            screen.blit(surf, rect.topleft)

    def reset_animation(self):
        self.visited_nodes.clear()
        self.path_nodes.clear()
