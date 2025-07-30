class Node:
    def __init__(self, value: int):
        self.value = value
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self, node=None):
        self.node = node
    
    def insert(self, num):
        if self.node is None:
            self.node = Node(num)
        else:
            self._insert(self.node, num)
    
    def _insert(self, node, num):
        if num > node.value:
            if node.right is None:
                node.right = Node(num)
            self._insert(node.right, num)
        elif num < node.value:
            if node.left is None:
                node.left = Node(num)
            self._insert(node.left, num)
    
    def read(self) -> list[int]:
        if self.node is None:
            return []
        else:
            return self._read(self.node)

    def _read(self, node):
        nums=[]
        if not node.right is None:
            nums.extend(self._read(node.right))
        nums.append(node.value)
        if not node.left is None:
            nums.extend(self._read(node.left))
        return nums

    def exist(self, num) -> bool:
        if self.node is None:
            return False
        else: 
            return self._exist(self.node, num)
    
    def _exist(self, node, num):
        if node.value == num:
            return True

        if num > node.value:
            if node.right is None:
                return False
            else:
                return self._exist(node.right, num)
        elif num < node.value:
            if node.left is None:
                return False
            else:
                return self._exist(node.left, num)

obj = BinaryTree()

obj.insert(13)
obj.insert(10)
obj.insert(3)
obj.insert(7)
obj.insert(19)
obj.insert(1000)

print(obj.read())
print(obj.read())
print(obj.read())
print(obj.exist(18))

class ReadTree:
    def a(self, root):
        root = root.node
        ans = []
        def read(root): 
            if root:
                ans.append(root.value)
                read(root.right)
                read(root.left)
        read(root)
        return ans

obj2 = ReadTree()
print(obj2.a(obj))

