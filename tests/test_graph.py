import mintf


def test():
    
    o2p = mintf.Frame([1, 0, 0])
    p2a = mintf.Frame([0, 1, 1])
    p2b = mintf.Frame([0, -1, 1])
    g = mintf.Graph(
        ("o", "p", o2p),
        ("p", "a", p2a),
        ("p", "b", p2b),
    )

    assert g("o", "p")() == [ 1, 0, 0]
    assert g("p", "o")() == [-1, 0, 0]
    
    assert g("o", "a")() == [ 1, 1, 1]
    assert g("o", "b")() == [ 1,-1, 1]
    assert g("a", "o")() == [-1,-1,-1]
    assert g("b", "o")() == [-1, 1,-1]

    assert g("a", "b")() == [ 0,-2, 0]
    assert g("b", "a")() == [ 0, 2, 0]
