from typing import Protocol

from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeShape
from OCP.TopoDS import TopoDS_Shape


class EvolutionTrackingHandler(Protocol):
    def __call__(
        self, input_shapes: set[TopoDS_Shape], operation: BRepBuilderAPI_MakeShape
    ) -> None: ...


_hooks: list[EvolutionTrackingHandler] = []


def register_hook(hook: EvolutionTrackingHandler) -> None:
    """Register a hook to be called when a BRepBuilderAPI_MakeShape operation is performed."""
    _hooks.append(hook)


def unregister_hook(hook: EvolutionTrackingHandler) -> None:
    """Unregister a hook"""
    _hooks.remove(hook)


def track(
    input_shapes: set[TopoDS_Shape],
    operation: BRepBuilderAPI_MakeShape,
) -> None:
    """
    Call all registered hooks with the input shapes and operation.
    This allow the user to track the evolution of the underlying TopoDS_Shapes.
    """
    if not _hooks:
        return
        
    for hook in _hooks:
        hook(input_shapes, operation)
