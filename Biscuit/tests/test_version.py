from Biscuit.utils.version import Version


def test_version():
    v1 = Version(0, 1, 2, 0)
    v2 = Version(1, 2, 1, 1)
    v3 = Version(1, 11, 2, 3)
    v4 = Version.from_repr('1.3')
    v5 = Version.from_repr('v2.9.31')
    v6 = Version.from_repr('1.11.2-b3')

    assert str(v1) == '0.1.2'
    assert str(v2) == '1.2.1-b1'
    assert v2 > v1
    assert v3 >= v1
    assert v4 < v5
    assert v6 <= v3
    assert v3 == v6
