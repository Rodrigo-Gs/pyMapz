class Algorithms:
    def __init__(self, graph):
        self.found_path = []
        self.visit_order = []
        self.graph = graph
        self.designations = ['Profundidade Primeiro', 'Largura Primeiro', 'Greedy BFS', 'A*', 'Dijkstra']

    def dfs(self, start_node, end_node):
        self.found_path.append(start_node)

        if start_node == end_node: return self.found_path.copy(), start_node
        if start_node in self.visit_order:
            self.found_path.pop()
            return False

        self.visit_order.append(start_node)

        for node in self.get_neighbors(start_node):
            result = self.dfs(node, end_node)
            if result: return result

        self.found_path.pop()
        return False

    def bfs(self, start_node, end_node):
        visited = set()
        self.visit_order = [start_node]

        while self.visit_order:
            node, path = self.visit_order.pop(0)
            if node == end_node: return node
            if node in visited: continue
            visited.add(node)
            self.visit_order += self.get_neighbors(node)

        return

    def greedy_bfs(self, start_node, end_node):
        return [], []

    def a_star(self, start_node, end_node):
        return [], []

    def dijkstra(self, start_node, end_node):
        return [], []

    def perform_search(self, search_type, start_node, end_node):
        match search_type:
            case "Profundidade Primeiro":
                self.visit_order, self.found_path = self.dfs(start_node, end_node)
                return self.visit_order, self.found_path
            case "Largura Primeiro":
                self.visit_order, self.found_path = self.bfs(start_node, end_node)
                return self.visit_order, self.found_path
            case "Greedy BFS":
                self.visit_order, self.found_path = self.greedy_bfs(start_node, end_node)
                return self.visit_order, self.found_path
            case "A*":
                self.visit_order, self.found_path = self.a_star(start_node, end_node)
                return self.visit_order, self.found_path
            case "Dijkstra":
                self.visit_order, self.found_path = self.dijkstra(start_node, end_node)
                return self.visit_order, self.found_path