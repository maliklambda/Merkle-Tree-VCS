# Merkle-Tree-VCS
A POC for a version-control-system based on a merkle tree.

## Example

    # Build two Merkle Trees each with a different data-array.
    mt1 = MerkleTree("Hello"*8, 5)
    mt2 = MerkleTree("Mello"+ "Hello"*6 +"Yello", 5)

    # Calculate difference between the Merkle Trees.
    d = diff(mt1, mt2)

    # Assert that the forward-difference applied to the first Merkle Tree results in the second.
    mt1_plus_diff = mt1.apply_diff_forward(d)
    assert mt1_plus_diff
    assert cmp_mt_dicts(mt2.iter_tree_root(), mt1_plus_diff)

    # Assert that the backward-difference applied to the second Merkle Tree results in the first.
    mt2_minus_diff = mt2.apply_diff_backward(d)
    assert mt2_minus_diff
    assert cmp_mt_dicts(mt1.iter_tree_root(), mt2_minus_diff)



## Merkle Trees
A very cool data structure that consists of three layers, 1) the data-array, 2) DataNodes and 3) TreeNodes.
Essentially, a Merkle Tree splits an array of bytes (in this example, Python's str type is used, but any byte-array works) into chunks.
Each chunk is referenced by a DataNode. And that's basically all that a DataNode does, reference a chunk in the data-array.
Above the layer of the DataNodes, TreeNodes build the heart of the Merkle Tree.
Every DataNode is referenced by a TreeNode. 
That means that ```len(data_array)/chunk_size``` is equal to the number of TreeNodes in the lowest layer (so the TreeNode's leaf nodes, if you will).
Every two TreeNodes are referenced from above by another TreeNode, cutting the number of TreeNodes per layer in half as you move up the tree.
This goes on, until there are only two TreeNodes left, which are referenced by the Merkle Tree's root node. 
Because the number of TreeNodes halves per layer, the height of the tree can be calculated as follows ```height = log2(len(data_array)/chunk_size)```.

### Hashes in Merkle Trees
The whole point of the Merkle Tree is to track changes in the data-array as efficient as possible. 
Every TreeNode keeps track of the hash of its children. 
This allows for very efficient comparison of two Merkle Trees because only those subtrees with differing hashes.
When encountering two TreeNodes with the same hash, the entire subtree below this node may be skipped. 
(If the roots' hashes match, there is no difference between the two Merkle Trees.)
A change in a single block of the data-array will only effect a single subtree, resulting in a single logarithmic traversal to find all changes between two states.

## VCS with Merkle Trees
Essentially, all that VCS is doing, is tracking the state of a file-system, with the ability to revert to previous states.
A file-system can easily be represented as a stream of bytes, as can a single file. 
So that means, that both a single file and a file-system can be represented as a Merkle Tree's data-array.
Each commit will then build a new Merkle Tree from the difference between the state before and after the commit.
The comparison of the two resulting trees is then very performant due to the nature of Merkle Tree comparisons.

### About this POC
In this POC, the state of a data-array is tracked using a Merkle Tree.
Changes in the state are represented by Diffs between Merkle Trees.
Diffs can be applied to a Merkle Tree, both forward and backward.
This allows for, not only tracking changes, but reverting them also.
the most basic functionalities of a VCS are therefore implemented.
