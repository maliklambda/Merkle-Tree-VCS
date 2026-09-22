import math
import copy

class DataNode():
    def __init__(self, start: int, block_sz: int, data: str) -> None:
        self.end = start + block_sz -1
        self.start = start
        self.hash = hash(data[self.start:self.end])
        print("DataNode hash:", self.hash)
    def __str__(self) -> str: return f"DataNode({self.start} - {self.end})"

class InternalNode():
    def __init__(self, left, right) -> None: 
        self.left = left
        self.right = right
        self.hash = hash(f"{left.hash}{right.hash}")
        print("Internal Node hash:", self.hash)
    def __str__(self) -> str: return f"InternalNode({self.hash})"


class Diff():
    def __init__(self) -> None:
        self.internal = {} # {level: (l_hash, r_hash, n)}
        self.data = {} # {(l_hash, r_hash): (l_data, r_data, n)}
        self.is_empty = True

    def append_internal(self, n: int, lvl: int, l_hash, r_hash):
        self.is_empty = False
        if not lvl in self.internal:  self.internal[lvl] = []
        self.internal[lvl].append((l_hash, r_hash, n))

    # n = index into data-array (start)
    def append_data(self, n, l_hash, r_hash, l_data, r_data):
        self.is_empty = False
        self.data[(l_hash, r_hash)] = (l_data, r_data, n)

    def __str__(self) -> str:
        return f"Diff({self.internal} - {self.data})"


class MerkleTree():
    def __init__(self, data: str, block_sz: int) -> None:
        self.root: InternalNode | None = None
        assert block_sz > 0, "Negative (or 0) block_sz"
        assert block_sz < len(data), "block_sz greater than data.len"
        assert len(data) > 0, "Empty data input"
        assert len(data) % block_sz == 0, "Invalid block_sz (modulo)"

        # TODO: Enable variable data size
        assert (len(data) / block_sz) % 2 == 0, "data.len / block_sz must be a multiple of 2"
        self.data = data
        self.block_sz = block_sz
        self.height = self._calc_height()
        self.root = self._build_tree()

    def _build_tree(self):

        # build data-nodes
        i = 0
        data_nodes = []
        while i<len(self.data):
            data_nodes.append(DataNode(i, self.block_sz, self.data))
            i += self.block_sz
        [print(d) for d in data_nodes]

        # build leaf-nodes
        num_nodes = len(data_nodes)
        i = 0
        nodes = []
        while i < num_nodes:
            nodes.append(InternalNode(data_nodes[i], data_nodes[i+1]))
            i += 2
        [print(f"DATA-NODE: {n.left} - {n.right}") for n in nodes]
        root = self._build_tree_recur(nodes)
        print("Root:", root)
        return root

    def _build_tree_recur(self, current_nodes):
        if len(current_nodes) == 1: 
            return current_nodes[0]
        i = 0
        print("Iteration:", len(current_nodes))
        new_nodes = []
        while i < len(current_nodes):
            new_nodes.append(InternalNode(current_nodes[i], current_nodes[i+1]))
            i += 2
        print(new_nodes)
        [print(f"{n.left} - {n.right}") for n in new_nodes]
        return self._build_tree_recur(new_nodes)

    # Iterate the tree from its root.
    def iter_tree_root(self) -> dict[int, InternalNode]:
        assert self.root
        return self.iter_tree_lvls(self.root)

    # nodes_lvls = {level0: [nodes], level1: [nodes]}
    def iter_tree_lvls(self, node: InternalNode) -> dict[int, InternalNode]:
        print("Starting iteration")
        nodes_lvls = {}
        self._iter_tree_recur(node, 0, nodes_lvls)
        print("Nodes:", nodes_lvls)
        return nodes_lvls

    def _iter_tree_recur(self, current_node, lvl: int, nodes_lvls: dict):
        # check if node is data or internal
        if not lvl in nodes_lvls: nodes_lvls[lvl] = []
        nodes_lvls[lvl].append(current_node)
        if type(current_node) == InternalNode: 
            print("Node:", current_node)
            self._iter_tree_recur(current_node.left, lvl+1, nodes_lvls)
            self._iter_tree_recur(current_node.right, lvl+1, nodes_lvls)
        elif type(current_node) == DataNode:
            if not lvl+1 in nodes_lvls: nodes_lvls[lvl+1] = []
            s = self.data[current_node.start:current_node.end+1]
            print("Data nodee:", s)
            nodes_lvls[lvl+1].append(s)
        else:
            print("Reached leaf")
            print(current_node)

    def _calc_height(self) -> int:
        return math.ceil(math.log2(len(self.data)/self.block_sz))

    # Apply forwards-difference to merkle-tree.
    # The difference self -> mt2 will be applied to mt2.
    # self is considered as left in Diff
    def apply_diff_forward(self, diffs: Diff):
        if diffs.is_empty: 
            print("No diff found.")
            return
        lvls = copy.deepcopy(self.iter_tree_root())
        print("BEFORE:", lvls)
        print("Diffs:", diffs)
        # update internal nodes
        for k, v in diffs.internal.items():
            for (before, after) in zip(lvls[k], v):
                print(f"lvls: {before} -> {after}")
                assert before.hash == after[0] # assert that the right tuple is chosen
                print(f"lvls[k]:", lvls[k])
                lvls[k][after[2]].hash = after[1]
        # update data nodes
        max_lvls = max(lvls.keys())
        for k, v in diffs.data.items():
            idx = v[2]
            new_val = v[1]
            lvls[max_lvls][idx] = new_val
            print(f"k: {k} - v: {v}")
            
        return lvls

    # Apply backwards-difference to merkle-tree.
    # The difference mt1 <- self will be applied to mt2.
    # self is considered as right in Diff
    def apply_diff_backward(self, diffs: Diff):
        if diffs.is_empty: 
            print("No diff found.")
            return
        lvls = copy.deepcopy(self.iter_tree_root())
        print("BEFORE:", lvls)
        print("Diffs:", diffs)
        # update internal nodes
        for k, v in diffs.internal.items():
            for (before, after) in zip(lvls[k], v):
                print(f"lvls (2): {before} -> {after}")
                # assert before.hash == after[1] # assert that the right tuple is chosen
                print(f"lvls[k]:", lvls[k])
                lvls[k][after[2]].hash = after[0]
        # update data nodes
        max_lvls = max(lvls.keys())
        for k, v in diffs.data.items():
            idx = v[2]
            new_val = v[0]
            lvls[max_lvls][idx] = new_val
            print(f"k: {k} - v: {v}")
            print(f"Res:", lvls[max_lvls][idx])

        return lvls

def compare_trees(left: MerkleTree, right: MerkleTree) -> bool:
    assert left.root and right.root
    return left.root.hash == right.root.hash


# Get difference of two MerkleTrees
def diff(left: MerkleTree, right: MerkleTree) -> Diff:
    assert left.root and right.root
    if left.root.hash == right.root.hash and left.height == right.height:
        print("Trees are equal!")
        return Diff()

    diffs = Diff()

    left_lvls = left.iter_tree_root()
    right_lvls = right.iter_tree_root()

    l_max_lvls = max(left_lvls.keys())
    r_max_lvls = max(right_lvls.keys())
    assert l_max_lvls == r_max_lvls, f"Cannot compare trees of different heights (l: {l_max_lvls}, r: {r_max_lvls})"
    print("Max lvl:", l_max_lvls)
    for lvl in range(l_max_lvls):
        for n, (l, r) in enumerate(zip(left_lvls[lvl], right_lvls[lvl])):
            print(f"Comparing level {lvl}: l = {l}; r = {r}")
            if l.hash == r.hash: print("Same hash")
            else: 
                print(f"lvl: {lvl}, l:{l}, r:{r}")
                diffs.append_internal(n, lvl, l.hash, r.hash)
                if lvl == l_max_lvls-1:
                    diffs.append_data(
                        n,
                        l.hash, 
                        r.hash, 
                        left.data[l.start:l.end+1],
                        right.data[r.start:r.end+1],
                    )
                    print("Leaf node: ", type(l))
                print("LVL:", lvl)
                print("Different hash")
                l_subtree = left.iter_tree_lvls(l)
                print("Subtree left:", l_subtree)
                r_subtree = right.iter_tree_lvls(r)
                print("Subtree right:", r_subtree)

    return diffs


def cmp_mt_dicts(l: dict, r: dict) -> bool:
    sl = str([[str(inner) for inner in i] for i in l.values()])
    sr = str([[str(inner) for inner in i] for i in r.values()])
    print(f"sl: {type(sl)} - {sl}")
    print(f"sr: {type(sr)} - {sr}")
    print("Eq:", sl == sr)
    return sl == sr
