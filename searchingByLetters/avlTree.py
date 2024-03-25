class Node:
  def __init__(self, value):
    self.value = value
    self.left_child = None
    self.right_child = None

class AvlNode(Node):
  def __init__(self, value):
      super().__init__(value)
      self.height = 1
      self.imbalance = 0


  def calculate_height_and_imbalance(self):
      left_height = 0
      if self.left_child is not None:
          left_height = self.left_child.height

      right_height = 0
      if self.right_child is not None:
          right_height = self.right_child.height

      self.height = 1 + max(left_height, right_height)

      self.imbalance = left_height - right_height

class BinaryTree:
  def __init__(self):
    self.root = None


  def add(self, value):
    if self.root is None:
      self.root = Node(value)
    else:
      self._add_recursive(self.root, value)


  def _add_recursive(self, current_node, value):
    if value <= current_node.value:
      if current_node.left_child is None:
        current_node.left_child = Node(value)
      else:
        self._add_recursive(current_node.left_child, value)
    else:
      if current_node.right_child is None:
        current_node.right_child = Node(value)
      else:
        self._add_recursive(current_node.right_child, value)


  def _contains(self, current_node, value):
    if current_node is None:
      return False
    if current_node.value == value:
      return True
    if value < current_node.value:
      return self._contains(current_node.left_child, value)
    return self._contains(current_node.right_child, value)


  def contains(self, value):
    return self._contains(self.root, value)
  
  

class AvlTree(BinaryTree):
  def __init__(self):
    super().__init__()

  def add(self, value):
    self.root = self._add_recursive(self.root, value)

  def _add_recursive(self, current_node, value):
    if current_node is None:
        return AvlNode(value)
    if isinstance(current_node, Node) and not isinstance(current_node, AvlNode):
        current_node = AvlNode(current_node.value)
        current_node.left_child = self.root.left_child
        current_node.right_child = self.root.right_child
        self.root = current_node

    if value <= current_node.value:
        current_node.left_child = self._add_recursive(current_node.left_child, value)
    else:
        current_node.right_child = self._add_recursive(current_node.right_child, value)

    current_node.calculate_height_and_imbalance()

    if abs(current_node.imbalance) == 2:
       return self._balance(current_node)

    return current_node

  def get_height(self):
    if self.root is None:
        return 0
    return self.root.height


  def _rotate_left(self, node):
    pivot = node.right_child

    node.right_child = pivot.left_child

    pivot.left_child = node

    node.calculate_height_and_imbalance()

    pivot.calculate_height_and_imbalance()

    return pivot


  def _rotate_right(self, node):
    pivot = node.left_child

    node.left_child = pivot.right_child

    pivot.right_child = node

    node.calculate_height_and_imbalance()

    pivot.calculate_height_and_imbalance()

    return pivot


  def _balance(self, node):
    if node.imbalance == 2:
      pivot = node.left_child

      if pivot.imbalance == 1:
        return self._rotate_right(node)
      else:
        node.left_child = self._rotate_left(pivot)
        return self._rotate_right(node)
    else:
      pivot = node.right_child
      if pivot.imbalance == -1:
        return self._rotate_left(node)
      else:
        node.right_child = self._rotate_right(pivot)
        return self._rotate_left(node)