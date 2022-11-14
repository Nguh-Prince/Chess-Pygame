class Node:
    def __init__(self, data, children: list=None, parent=None):
        self.data = data

        if children is None:
            self.children = []
        else:
            self.children = children

        self.parent = parent

    def add_child(self, node):
        self.children.append(node)
        node.parent = self

    def remove_child(self, index=-1):
        node = self.children.pop(index)
        node.parent = None

        return node

    def replace_child(self, index, node):
        self.children[index] = node

    def is_leaf_node(self) -> bool:
        return len(self.children) == 0

    def compare_data(self, data_1, data_2) -> int:
        """
        This method exists because data can be anything from default data types 
        to other objects and we want the node to be as flexible as possible.

        Returns 0 if the data are equal, 1 if data_1 > data_2 and -1 if data_1 < data_2
        """
        if data_1 == data_2:
            return 0
        if data_1 < data_2:
            return -1
        if data_1 > data_2:
            return 1

    def __lt__(self, other):
        return self.compare(other) == -1

    def __gt__(self, other):
        return self.compare(other) == -1

    def __gte__(self, other):
        return self.compare(other) >= 0

    def __lte__(self, other):
        return self.compare(other) <= 0

    def compare(self, other):
        return self.compare_data(self.data, other.data)

    def __eq__(self, other) -> bool:
        return self.compare_data(self.data, other.data) == 0

    def __str__(self) -> str:
        return f"{self.data}"

class Tree:
    def __init__(self, root_node: Node=None) -> None:
        self.root_node = root_node
        self.height = 0

    def get_height(self, node=None) -> int:
        modify_height = False

        if node is None:
            node = self.root_node
            modify_height = True

        if not node:
            return 0

        if not node.children:
            return 1

        child_heights = [ self.get_height(child) for child in node.children ]

        height = max( child_heights ) + 1

        if modify_height:
            self.height = height

        return height

    def add_node(self, parent_node: Node, new_node: Node):
        parent_node.add_child(new_node)

        self.height += self.get_height(new_node) - 1

    def dfs(self, visited=None, node=None):
        """
        Depth First Search on the tree
        """
        if visited is None:
            visited = []
        if node is None:
            node = self.root_node

        if node not in visited:
            visited.append(node)
            print(f"Node {node.__str__()} has been visited")
            print(f"The visited nodes are: {[ n.__str__() for n in visited ]}")

        for child in node.children[::-1]:
            self.dfs(visited, child)

        return visited

    def find_smallest_and_largest_node(self, visited=None, node=None, minimum_node=None, maximum_node=None, search_depth=None) -> tuple:
        """
        finds the node with the smallest data value
        """
        if visited is None:
            visited = set()

        if node is None:
            node = self.root_node
            minimum_node = self.root_node
            maximum_node = self.root_node

        if node not in visited:
            visited.append(node)
            
            if node.compare(minimum_node) == -1:
                minimum_node = node
            elif node.compare(maximum_node) == 1:
                maximum_node = node
            else:
                maximum_node = node
            
        for child in node.children[::-1]:
            self.find_smallest_and_largest_node(visited, child, minimum_node, maximum_node)

        return ( minimum_node, maximum_node, visited )

    def get_leaf_nodes(self, root_node: Node=None):
        leaf_nodes = []

        if root_node is None:
            root_node = self.root_node

        if not root_node:
            return None
        
        if not root_node.children:
            return root_node
        
        for child in root_node.children:
            leaf_nodes.append( [node for node in self.get_leaf_nodes(child)] )

        return leaf_nodes

    def get_leaf_nodes(self, visited=None, node=None, leaf_nodes=None):
        if visited is None:
            visited = []
        if leaf_nodes is None:
            leaf_nodes = []

        if node is None:
            node = self.root_node

        if node not in visited:
            visited.append(node)

            if not node.children:
                leaf_nodes.append(node)

        for child in node.children:
            self.get_leaf_nodes(visited, child, leaf_nodes)
        
        return leaf_nodes
