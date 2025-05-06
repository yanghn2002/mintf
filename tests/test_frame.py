import mintf
import numpy as np
from scipy.spatial.transform import Rotation as R


rand_frame = mintf.Frame(np.random.rand(3), R.from_euler('xyz', np.random.random(3)*np.pi).as_quat())


def test_init():

    f = rand_frame()

    rot = f.get_rot()
    trs = f.get_trs()

    assert np.allclose(f.trs, trs)
    assert np.allclose(f.rot, rot)

    assert mintf.Frame(f).addr == f.addr
    assert mintf.Frame(f.mat).addr != f.addr

    check = True
    try:
        mintf.Frame([1, 2, 3], [1, 2, 3])
        check = False
    except: pass
    if not check: assert False


def test_eq():

    assert mintf.Frame() == np.eye(4)
    assert mintf.Frame() == np.eye(4).tolist()
    assert mintf.Frame([1, 2, 3]) == [1, 2, 3]
    assert mintf.Frame([1, 2, 3], [np.sqrt(2)/2, np.sqrt(2)/2, 0, 0]) != [1, 2, 3]
    assert not mintf.Frame() == np.array([])
    assert not mintf.Frame() == None


def test_hash():

    f1, f2, f3 = mintf.Frame(), mintf.Frame(), mintf.Frame()
    f2.tx(1).ty(2).tz(3)
    frame_dict = {
        f1: 1,
        f2: 2,
        mintf.Frame(f3): 3,
    }
    assert frame_dict[f1] == 1
    assert frame_dict[f2] == 2
    assert frame_dict[f3] == 3


def test_call():

    t0 = [1, 2, 3]
    t1 = [4, 6, 9]

    r0 = R.from_euler('xyz', [30, 60, 90], degrees=True).as_matrix()
    r1 = R.from_euler('xyz', [35, 25, 15], degrees=True).as_matrix()

    m0, m1 = np.eye(4), np.eye(4)
    m0[:3, :3] = r0
    m1[:3, :3] = r1
    m0[:3, 3] = t0
    m1[:3, 3] = t1
    
    assert mintf.Frame(r0, t0)(r1, t1) == m0 @ m1


def test_repr():

    f = rand_frame()

    assert eval(repr(f)) == f


def test_inv():

    f = rand_frame()

    f.get().inv() == np.linalg.inv(f.mat)


def test_mean():

    f_1 = mintf.Frame([1, -2, 3]).rx(np.deg2rad(30))
    f_2 = mintf.Frame([2, -4, 6]).rx(np.deg2rad(15))
    f_mean = mintf.Frame.mean((mintf.Frame([3, -6, 9]), f_1, f_2), [1/4, 1/4, 1/2])
    assert f_mean == mintf.Frame([2, -4, 6]).rx(np.deg2rad(15))
