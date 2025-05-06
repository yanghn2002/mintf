from typing import Any, Tuple
from mpl_toolkits.mplot3d.axes3d import Axes3D
from .frame import Frame



def draw_frame(axes:Axes3D, frame:Frame, size:float, alpha:float=1.0, text:str='', **kwargs) -> Tuple[Any]:

    assert isinstance(axes, Axes3D), "Invaild axes"

    kwargs = { 'alpha': alpha, 'arrow_length_ratio': 0.25, **kwargs }

    return(
        axes.quiver(*frame.trs, *frame.rot@[size, 0, 0], color='r', **kwargs),
        axes.quiver(*frame.trs, *frame.rot@[0, size, 0], color='g', **kwargs),
        axes.quiver(*frame.trs, *frame.rot@[0, 0, size], color='b', **kwargs),
        axes.text(*frame.trs, text),
    )