from merkle import MerkleTree, cmp_mt_dicts, diff

mt1 = MerkleTree("Hello"*8, 5)
mt1.iter_tree_root()

mt2 = MerkleTree("Mello"+ "Hello"*6 +"Yello", 5)
d = diff(mt1, mt2)

mt1_plus_diff = mt1.apply_diff_forward(d)
assert mt1_plus_diff
assert cmp_mt_dicts(mt2.iter_tree_root(), mt1_plus_diff), "Applying forward-diff(mt1 -> mt2) to mt1 should result in mt2"

mt2_minus_diff = mt2.apply_diff_backward(d)
assert mt2_minus_diff
assert cmp_mt_dicts(mt1.iter_tree_root(), mt2_minus_diff), "Applying backward-diff(mt1 -> mt2) to mt2 should result in mt1"
