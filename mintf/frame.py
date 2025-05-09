from typing import *
import numpy as np
from quaternion import \
    from_float_array as quat_from_array,\
    from_rotation_matrix as quat_from_rot,\
    as_rotation_matrix as quat2mat,\
    as_float_array as quat_to_array


DTYPE = np.dtype(float)

ZERO_MAT = np.eye(4, dtype=DTYPE)

ARR_T = np.ndarray|tuple|list
def is_array(array): return type(array) in (np.ndarray, tuple, list)
def np_array(array:ARR_T):
    return array if type(array) == np.ndarray else np.array(array, dtype=DTYPE)


class Frame:

    @property
    def addr(self) -> int: return self.__mat.__array_interface__['data'][0]

    @property
    def mat(self) -> np.ndarray: return self.__mat[...]
    @mat.setter
    def mat(self, mat:ARR_T) -> None:
        mat = np_array(mat)
        assert mat.shape == (4, 4)
        self.__mat[...] = mat

    @property
    def trs(self) -> np.ndarray: return self.__mat[:3, 3]
    @trs.setter
    def trs(self, trs:ARR_T) -> None:
        trs = np_array(trs)
        assert trs.shape == (3, )
        self.__mat[:3, 3] = trs

    @property
    def rot(self) -> np.ndarray: return self.__mat[:3, :3]
    @rot.setter
    def rot(self, rot:ARR_T) -> None:
        rot = np_array(rot)
        assert rot.shape == (3, 3)
        self.__mat[:3, :3] = rot
    
    def __no_mat(self): return np.allclose(self.mat, ZERO_MAT)
    def __no_trs(self): return np.allclose(self.trs, ZERO_MAT[:3, 3])
    def __no_rot(self): return np.allclose(self.rot, ZERO_MAT[:3, :3])

    def __init__(self, *args) -> None:

        self.__mat = np.eye(4)
        for arg in args:
            if type(arg) == type(self):
                self.__mat = arg.mat
            elif is_array(arg):
                array = np_array(arg)
                match array.shape:
                    case (4, 4):
                        assert self.__no_mat()
                        self.mat = array
                    case (3,  ):
                        assert self.__no_trs()
                        self.trs = array
                    case (3, 3):
                        assert self.__no_rot()
                        self.rot = array
                    case (4,  ):
                        assert self.__no_rot()
                        self.rot = quat2mat(quat_from_array(array))
                    case _: raise ValueError(f"Invaild frame shape {array.shape}")
            else: raise ValueError(f"Invaild frame type {type(arg).__name__}")
    
    def __eq__(self, other) -> bool:
        
        if type(other) == type(self):
            if self.addr == other.addr: return True
            else: return np.allclose(self.mat, other.mat)
        elif is_array(other):
            array = np_array(other)
            match array.shape:
                case (4, 4): return np.allclose(self.mat, array)
                case (3,  ): return self.__no_rot() and\
                             np.allclose(self.trs, array)
                case (3, 3): return self.__no_trs() and\
                             np.allclose(self.rot, array)
                case (4,  ): return self.__no_trs() and\
                             np.allclose(self.rot, quat2mat(quat_from_array(array)))
                case _: return False
        else: return False
    
    def __hash__(self): return hash(self.addr)
    
    def __call__(self, *other, inv:bool=False):

        other = Frame(*other).mat
        self.mat @= np.linalg.inv(other) if inv else other
        return self

    def __str__(self) -> str:

        mat = self.mat
        trs = self.trs
        quat = self.get_quat()
        return f"""Frame: {self.addr}
xyz:  {trs[0]}, {trs[1]}, {trs[2]}
wxyz: {quat[0]}, {quat[1]}, {quat[2]}, {quat[3]}
matrix:
\t{mat[0][0]}\t{mat[0][1]}\t{mat[0][2]}\t{mat[0][3]}
\t{mat[1][0]}\t{mat[1][1]}\t{mat[1][2]}\t{mat[1][3]}
\t{mat[2][0]}\t{mat[2][1]}\t{mat[2][2]}\t{mat[2][3]}
\t{mat[3][0]}\t{mat[3][1]}\t{mat[3][2]}\t{mat[3][3]}\
"""
    
    def __repr__(self) -> str:

        return f"mintf.Frame({self.get_trs().tolist()}, {self.get_quat().tolist()})"

    def inv(self, *other):

        self.mat = np.linalg.inv(self.mat)
        return self(*other)
    
    def set_to(self, *other):

        self.mat = Frame(*other).mat

        return self

    def get(self, *other, inv=False): return Frame(self.mat).inv(*other) if inv else Frame(self.mat)(*other)
    def get_mat(self, inv=False) -> np.ndarray: return np.linalg.inv(self.mat) if inv else self.mat.copy()
    def get_trs(self, inv=False) -> np.ndarray: return np.linalg.inv(self.mat) if inv else self.trs.copy()
    def get_rot(self, inv=False) -> np.ndarray: return np.linalg.inv(self.mat) if inv else self.rot.copy()
    def get_quat(self, inv=False) -> np.ndarray: return quat_to_array(quat_from_rot(np.linalg.inv(self.rot) if inv else self.rot))
    
    def tx(self, tx:float): return self([tx, 0, 0])
    def ty(self, ty:float): return self([0, ty, 0])
    def tz(self, tz:float): return self([0, 0, tz])
    def rx(self, rx:float): return self([[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]])
    def ry(self, ry:float): return self([[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]])
    def rz(self, rz:float): return self([[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]])
    
    @staticmethod
    def mean(frames:tuple|list, weights:ARR_T|None=None):

        if not weights: weights = np.full(len(frames), 1/len(frames))

        mat = np.zeros((4, 4))
        trs = np.zeros(3)
        sum = np.sum(weights)
        for f, w in iter(zip(frames, weights)):
            q = f.get_quat().reshape(4, 1)
            mat += w * (q @ q.T)
            trs += w * f.trs
        eigvals, eigvecs = np.linalg.eig(mat/sum)
        return Frame(trs/sum, eigvecs[:, np.argmax(eigvals)])