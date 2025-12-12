"""
build123d OCCT Builder Wrappers

name: builders.py
by:   build123d contributors
date: December 2024

desc:
    This module provides wrapper functions for OCCT BRepBuilderAPI_MakeShape and its
    subclasses. Each wrapper automatically calls the tracking hooks, enabling external
    systems to track shape evolution (Generated, Modified, Deleted).

    These are low-level wrappers that accept the same inputs as the underlying OCCT
    builders and return only the resulting TopoDS_Shape.

license:
    Copyright 2024 build123d contributors

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from __future__ import annotations

from typing import Iterable, Sequence

from OCP.BRepAlgoAPI import (
    BRepAlgoAPI_Common,
    BRepAlgoAPI_Cut,
    BRepAlgoAPI_Fuse,
    BRepAlgoAPI_Section,
    BRepAlgoAPI_Splitter,
)
from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_Copy,
    BRepBuilderAPI_GTransform,
    BRepBuilderAPI_Sewing,
    BRepBuilderAPI_Transform,
)
from OCP.BRepFeat import BRepFeat_MakeDPrism, BRepFeat_SplitShape
from OCP.BRepFilletAPI import (
    BRepFilletAPI_MakeChamfer,
    BRepFilletAPI_MakeFillet,
    BRepFilletAPI_MakeFillet2d,
)
from OCP.BRepOffsetAPI import (
    BRepOffsetAPI_DraftAngle,
    BRepOffsetAPI_MakeFilling,
    BRepOffsetAPI_MakeOffset,
    BRepOffsetAPI_MakePipeShell,
    BRepOffsetAPI_MakeThickSolid,
    BRepOffsetAPI_ThruSections,
)
from OCP.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeCone,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeHalfSpace,
    BRepPrimAPI_MakePrism,
    BRepPrimAPI_MakeRevol,
    BRepPrimAPI_MakeSphere,
    BRepPrimAPI_MakeTorus,
    BRepPrimAPI_MakeWedge,
)
from OCP.GeomAbs import GeomAbs_JoinType
from OCP.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_GTrsf, gp_Pln, gp_Pnt, gp_Trsf, gp_Vec
from OCP.TopoDS import (
    TopoDS_Edge,
    TopoDS_Face,
    TopoDS_Shape,
    TopoDS_Shell,
    TopoDS_Vertex,
    TopoDS_Wire,
)
from OCP.TopTools import TopTools_ListOfShape

from build123d.tracking_hooks import track


# =============================================================================
# Transform Operations
# =============================================================================


def ocp_transform(
    shape: TopoDS_Shape,
    trsf: gp_Trsf,
    copy: bool = True,
    copy_geom: bool = False,
) -> TopoDS_Shape:
    """Apply a transformation to a shape with tracking.

    Wraps BRepBuilderAPI_Transform.

    Args:
        shape: The TopoDS_Shape to transform
        trsf: The gp_Trsf transformation to apply
        copy: If True, copy the shape (default True)
        copy_geom: If True, also copy underlying geometry (default False)

    Returns:
        Transformed TopoDS_Shape
    """
    builder = BRepBuilderAPI_Transform(shape, trsf, copy, copy_geom)
    result = builder.Shape()
    track({shape}, builder)
    return result


def ocp_gtransform(
    shape: TopoDS_Shape,
    gtrsf: gp_GTrsf,
    copy: bool = True,
) -> TopoDS_Shape:
    """Apply a general transformation to a shape with tracking.

    Wraps BRepBuilderAPI_GTransform.

    Args:
        shape: The TopoDS_Shape to transform
        gtrsf: The gp_GTrsf general transformation to apply
        copy: If True, copy the shape (default True)

    Returns:
        Transformed TopoDS_Shape
    """
    builder = BRepBuilderAPI_GTransform(shape, gtrsf, copy)
    result = builder.Shape()
    track({shape}, builder)
    return result


def ocp_copy(
    shape: TopoDS_Shape,
    copy_geom: bool = True,
) -> TopoDS_Shape:
    """Copy a shape with tracking.

    Wraps BRepBuilderAPI_Copy.

    Args:
        shape: The TopoDS_Shape to copy
        copy_geom: If True, also copy underlying geometry (default True)

    Returns:
        Copied TopoDS_Shape
    """
    builder = BRepBuilderAPI_Copy(shape, copy_geom)
    result = builder.Shape()
    track({shape}, builder)
    return result


# =============================================================================
# Boolean Operations
# =============================================================================


def ocp_cut(
    shape: TopoDS_Shape,
    tool: TopoDS_Shape,
) -> TopoDS_Shape:
    """Boolean cut operation with tracking.

    Wraps BRepAlgoAPI_Cut (simple two-shape version).

    Args:
        shape: The shape to cut from
        tool: The shape to cut with

    Returns:
        Result TopoDS_Shape
    """
    builder = BRepAlgoAPI_Cut(shape, tool)
    builder.Build()
    result = builder.Shape()
    track({shape, tool}, builder)
    return result


def ocp_fuse(
    shape1: TopoDS_Shape,
    shape2: TopoDS_Shape,
) -> TopoDS_Shape:
    """Boolean fuse operation with tracking.

    Wraps BRepAlgoAPI_Fuse (simple two-shape version).

    Args:
        shape1: First shape to fuse
        shape2: Second shape to fuse

    Returns:
        Result TopoDS_Shape
    """
    builder = BRepAlgoAPI_Fuse(shape1, shape2)
    builder.Build()
    result = builder.Shape()
    track({shape1, shape2}, builder)
    return result


def ocp_common(
    shape1: TopoDS_Shape,
    shape2: TopoDS_Shape,
) -> TopoDS_Shape:
    """Boolean common (intersect) operation with tracking.

    Wraps BRepAlgoAPI_Common (simple two-shape version).

    Args:
        shape1: First shape
        shape2: Second shape

    Returns:
        Result TopoDS_Shape (intersection)
    """
    builder = BRepAlgoAPI_Common(shape1, shape2)
    builder.Build()
    result = builder.Shape()
    track({shape1, shape2}, builder)
    return result


def ocp_section(
    shape1: TopoDS_Shape,
    shape2: TopoDS_Shape,
    perform_now: bool = True,
) -> TopoDS_Shape:
    """Boolean section operation with tracking.

    Wraps BRepAlgoAPI_Section.

    Args:
        shape1: First shape
        shape2: Second shape
        perform_now: If True, perform immediately (default True)

    Returns:
        Result TopoDS_Shape (section curves/points)
    """
    builder = BRepAlgoAPI_Section(shape1, shape2, perform_now)
    if not perform_now:
        builder.Build()
    result = builder.Shape()
    track({shape1, shape2}, builder)
    return result


def ocp_splitter(
    arguments: Iterable[TopoDS_Shape],
    tools: Iterable[TopoDS_Shape],
) -> TopoDS_Shape:
    """Split shapes by tools with tracking.

    Wraps BRepAlgoAPI_Splitter.

    Args:
        arguments: The shapes to split
        tools: The shapes to split with

    Returns:
        Result TopoDS_Shape
    """
    args_list = list(arguments)
    tools_list = list(tools)

    builder = BRepAlgoAPI_Splitter()
    arg_los = TopTools_ListOfShape()
    for s in args_list:
        arg_los.Append(s)
    tool_los = TopTools_ListOfShape()
    for s in tools_list:
        tool_los.Append(s)

    builder.SetArguments(arg_los)
    builder.SetTools(tool_los)
    builder.Build()
    result = builder.Shape()
    track({*args_list, *tools_list}, builder)
    return result


# =============================================================================
# Fillet and Chamfer Operations
# =============================================================================


def ocp_fillet(
    shape: TopoDS_Shape,
    edge_radius_pairs: Sequence[tuple[TopoDS_Edge, float]],
) -> TopoDS_Shape:
    """Fillet edges on a shape with tracking.

    Wraps BRepFilletAPI_MakeFillet.

    Args:
        shape: The shape to fillet
        edge_radius_pairs: Sequence of (edge, radius) tuples

    Returns:
        Filleted TopoDS_Shape
    """
    builder = BRepFilletAPI_MakeFillet(shape)
    for edge, radius in edge_radius_pairs:
        builder.Add(radius, edge)
    builder.Build()
    result = builder.Shape()
    track({shape}, builder)
    return result


def ocp_chamfer(
    shape: TopoDS_Shape,
    edge_face_distance_tuples: Sequence[tuple[TopoDS_Edge, TopoDS_Face, float, float]],
) -> TopoDS_Shape:
    """Chamfer edges on a shape with tracking.

    Wraps BRepFilletAPI_MakeChamfer.

    Args:
        shape: The shape to chamfer
        edge_face_distance_tuples: Sequence of (edge, face, distance1, distance2) tuples

    Returns:
        Chamfered TopoDS_Shape
    """
    builder = BRepFilletAPI_MakeChamfer(shape)
    for edge, face, d1, d2 in edge_face_distance_tuples:
        builder.Add(d1, d2, edge, face)
    builder.Build()
    result = builder.Shape()
    track({shape}, builder)
    return result


def ocp_fillet_2d(
    face: TopoDS_Face,
    vertex_radius_pairs: Sequence[tuple[TopoDS_Vertex, float]],
) -> TopoDS_Shape:
    """Fillet vertices on a face with tracking.

    Wraps BRepFilletAPI_MakeFillet2d with AddFillet.

    Args:
        face: The face to fillet
        vertex_radius_pairs: Sequence of (vertex, radius) tuples

    Returns:
        Filleted TopoDS_Shape
    """
    builder = BRepFilletAPI_MakeFillet2d(face)
    for vertex, radius in vertex_radius_pairs:
        builder.AddFillet(vertex, radius)
    builder.Build()
    result = builder.Shape()
    track({face}, builder)
    return result


def ocp_chamfer_2d(
    face: TopoDS_Face,
    vertex_edge_distance_tuples: Sequence[
        tuple[TopoDS_Vertex, TopoDS_Edge, TopoDS_Edge, float]
    ],
) -> TopoDS_Shape:
    """Chamfer vertices on a face with tracking.

    Wraps BRepFilletAPI_MakeFillet2d with AddChamfer.

    Args:
        face: The face to chamfer
        vertex_edge_distance_tuples: Sequence of (vertex, edge1, edge2, distance) tuples

    Returns:
        Chamfered TopoDS_Shape
    """
    builder = BRepFilletAPI_MakeFillet2d(face)
    for vertex, edge1, edge2, distance in vertex_edge_distance_tuples:
        builder.AddChamfer(edge1, edge2, distance, distance)
    builder.Build()
    result = builder.Shape()
    track({face}, builder)
    return result


# =============================================================================
# Offset Operations
# =============================================================================


def ocp_thick_solid(
    shape: TopoDS_Shape,
    closing_faces: TopTools_ListOfShape,
    offset: float,
    tolerance: float,
    intersection: bool = True,
    join: GeomAbs_JoinType = GeomAbs_JoinType.GeomAbs_Arc,
    remove_internal_edges: bool = False,
) -> TopoDS_Shape:
    """Create a thick solid (hollow) with tracking.

    Wraps BRepOffsetAPI_MakeThickSolid.

    Args:
        shape: The solid to hollow
        closing_faces: Faces to remove (openings)
        offset: Thickness (positive = outward, negative = inward)
        tolerance: Tolerance for the operation
        intersection: Whether to enable intersection (default True)
        join: Join type (default Arc)
        remove_internal_edges: Whether to remove internal edges (default False)

    Returns:
        Hollowed TopoDS_Shape
    """
    builder = BRepOffsetAPI_MakeThickSolid()
    builder.MakeThickSolidByJoin(
        shape,
        closing_faces,
        offset,
        tolerance,
        Intersection=intersection,
        Join=join,
        RemoveIntEdges=remove_internal_edges,
    )
    builder.Build()
    result = builder.Shape()
    track({shape}, builder)
    return result


def ocp_draft_angle(
    shape: TopoDS_Shape,
    face_angle_tuples: Sequence[tuple[TopoDS_Face, gp_Dir, float, gp_Pln]],
) -> TopoDS_Shape:
    """Add draft angles to faces with tracking.

    Wraps BRepOffsetAPI_DraftAngle.

    Args:
        shape: The shape to add draft to
        face_angle_tuples: Sequence of (face, direction, angle_radians, neutral_plane) tuples

    Returns:
        Drafted TopoDS_Shape
    """
    builder = BRepOffsetAPI_DraftAngle(shape)
    for face, direction, angle, plane in face_angle_tuples:
        builder.Add(face, direction, angle, plane, Flag=True)
    builder.Build()
    result = builder.Shape()
    track({shape}, builder)
    return result


def ocp_offset_wire(
    wire: TopoDS_Wire,
    distance: float,
    join: GeomAbs_JoinType = GeomAbs_JoinType.GeomAbs_Arc,
) -> TopoDS_Shape:
    """Offset a wire with tracking.

    Wraps BRepOffsetAPI_MakeOffset.

    Args:
        wire: The wire to offset
        distance: Offset distance (positive = outward)
        join: Join type (default Arc)

    Returns:
        Offset TopoDS_Shape
    """
    builder = BRepOffsetAPI_MakeOffset()
    builder.Init(join)
    builder.AddWire(wire)
    builder.Perform(distance)
    result = builder.Shape()
    track({wire}, builder)
    return result


def ocp_pipe_shell(
    spine: TopoDS_Wire,
    profiles: Sequence[TopoDS_Shape],
    is_frenet: bool = False,
    auxiliary_spine: TopoDS_Wire | None = None,
    make_solid: bool = False,
) -> TopoDS_Shape:
    """Sweep profiles along a spine with tracking.

    Wraps BRepOffsetAPI_MakePipeShell.

    Args:
        spine: The path wire
        profiles: The profile shapes to sweep
        is_frenet: Use Frenet frame (default False)
        auxiliary_spine: Optional auxiliary spine for mode control
        make_solid: If True, make the result solid (default False)

    Returns:
        Swept TopoDS_Shape
    """
    builder = BRepOffsetAPI_MakePipeShell(spine)

    if auxiliary_spine is not None:
        builder.SetMode(auxiliary_spine, False)
    else:
        builder.SetMode(is_frenet)

    for profile in profiles:
        builder.Add(profile)

    builder.Build()
    if make_solid:
        builder.MakeSolid()
    result = builder.Shape()
    track({spine, *profiles}, builder)
    return result


def ocp_thru_sections(
    profiles: Sequence[TopoDS_Shape],
    is_solid: bool = True,
    ruled: bool = False,
) -> TopoDS_Shape:
    """Loft through sections with tracking.

    Wraps BRepOffsetAPI_ThruSections.

    Args:
        profiles: The profile shapes (wires or vertices)
        is_solid: If True, create a solid (default True)
        ruled: If True, create ruled surfaces (default False)

    Returns:
        Lofted TopoDS_Shape
    """
    builder = BRepOffsetAPI_ThruSections(is_solid, ruled)

    for profile in profiles:
        if isinstance(profile, TopoDS_Vertex):
            builder.AddVertex(profile)
        elif isinstance(profile, TopoDS_Wire):
            builder.AddWire(profile)

    builder.Build()
    result = builder.Shape()
    track(set(profiles), builder)
    return result


def ocp_filling(
    edges: Sequence[TopoDS_Edge],
    degree: int = 3,
    nb_pts_on_cur: int = 15,
    nb_iter: int = 2,
    anisotropie: bool = False,
    tol_2d: float = 0.00001,
    tol_3d: float = 0.0001,
    tol_ang: float = 0.01,
    tol_curv: float = 0.1,
    max_deg: int = 8,
    max_segments: int = 9,
) -> TopoDS_Shape:
    """Create a filling surface with tracking.

    Wraps BRepOffsetAPI_MakeFilling.

    Args:
        edges: Boundary edges
        degree: Degree of the surface (default 3)
        nb_pts_on_cur: Number of points on curves (default 15)
        nb_iter: Number of iterations (default 2)
        anisotropie: Anisotropic behavior (default False)
        tol_2d: 2D tolerance (default 0.00001)
        tol_3d: 3D tolerance (default 0.0001)
        tol_ang: Angular tolerance (default 0.01)
        tol_curv: Curvature tolerance (default 0.1)
        max_deg: Maximum degree (default 8)
        max_segments: Maximum segments (default 9)

    Returns:
        Filled surface TopoDS_Shape
    """
    builder = BRepOffsetAPI_MakeFilling(
        degree,
        nb_pts_on_cur,
        nb_iter,
        anisotropie,
        tol_2d,
        tol_3d,
        tol_ang,
        tol_curv,
        max_deg,
        max_segments,
    )
    for edge in edges:
        builder.Add(edge, GeomAbs_JoinType.GeomAbs_C0)
    builder.Build()
    result = builder.Shape()
    track(set(edges), builder)
    return result


# =============================================================================
# Primitive Operations
# =============================================================================


def ocp_box(
    ax2: gp_Ax2,
    dx: float,
    dy: float,
    dz: float,
) -> TopoDS_Shape:
    """Create a box primitive with tracking.

    Wraps BRepPrimAPI_MakeBox.

    Args:
        ax2: The coordinate system for the box
        dx: Length in X direction
        dy: Length in Y direction
        dz: Length in Z direction

    Returns:
        Box TopoDS_Shape
    """
    builder = BRepPrimAPI_MakeBox(ax2, dx, dy, dz)
    result = builder.Shape()
    track(set(), builder)
    return result


def ocp_cone(
    ax2: gp_Ax2,
    r1: float,
    r2: float,
    h: float,
    angle: float = 6.283185307179586,  # 2*pi
) -> TopoDS_Shape:
    """Create a cone primitive with tracking.

    Wraps BRepPrimAPI_MakeCone.

    Args:
        ax2: The coordinate system for the cone
        r1: Base radius
        r2: Top radius
        h: Height
        angle: Angular extent in radians (default 2*pi)

    Returns:
        Cone TopoDS_Shape
    """
    builder = BRepPrimAPI_MakeCone(ax2, r1, r2, h, angle)
    result = builder.Shape()
    track(set(), builder)
    return result


def ocp_cylinder(
    ax2: gp_Ax2,
    r: float,
    h: float,
    angle: float = 6.283185307179586,  # 2*pi
) -> TopoDS_Shape:
    """Create a cylinder primitive with tracking.

    Wraps BRepPrimAPI_MakeCylinder.

    Args:
        ax2: The coordinate system for the cylinder
        r: Radius
        h: Height
        angle: Angular extent in radians (default 2*pi)

    Returns:
        Cylinder TopoDS_Shape
    """
    builder = BRepPrimAPI_MakeCylinder(ax2, r, h, angle)
    result = builder.Shape()
    track(set(), builder)
    return result


def ocp_sphere(
    ax2: gp_Ax2,
    r: float,
    angle1: float = -1.5707963267948966,  # -pi/2
    angle2: float = 1.5707963267948966,  # pi/2
    angle3: float = 6.283185307179586,  # 2*pi
) -> TopoDS_Shape:
    """Create a sphere primitive with tracking.

    Wraps BRepPrimAPI_MakeSphere.

    Args:
        ax2: The coordinate system for the sphere
        r: Radius
        angle1: Start latitude angle in radians (default -pi/2)
        angle2: End latitude angle in radians (default pi/2)
        angle3: Longitude angle in radians (default 2*pi)

    Returns:
        Sphere TopoDS_Shape
    """
    builder = BRepPrimAPI_MakeSphere(ax2, r, angle1, angle2, angle3)
    result = builder.Shape()
    track(set(), builder)
    return result


def ocp_torus(
    ax2: gp_Ax2,
    r1: float,
    r2: float,
    angle1: float = 0.0,
    angle2: float = 6.283185307179586,  # 2*pi
    angle3: float = 6.283185307179586,  # 2*pi
) -> TopoDS_Shape:
    """Create a torus primitive with tracking.

    Wraps BRepPrimAPI_MakeTorus.

    Args:
        ax2: The coordinate system for the torus
        r1: Major radius
        r2: Minor radius
        angle1: Start angle around minor axis in radians (default 0)
        angle2: End angle around minor axis in radians (default 2*pi)
        angle3: Angle around major axis in radians (default 2*pi)

    Returns:
        Torus TopoDS_Shape
    """
    builder = BRepPrimAPI_MakeTorus(ax2, r1, r2, angle1, angle2, angle3)
    result = builder.Shape()
    track(set(), builder)
    return result


def ocp_wedge(
    ax2: gp_Ax2,
    dx: float,
    dy: float,
    dz: float,
    xmin: float,
    zmin: float,
    xmax: float,
    zmax: float,
) -> TopoDS_Shape:
    """Create a wedge primitive with tracking.

    Wraps BRepPrimAPI_MakeWedge.

    Args:
        ax2: The coordinate system for the wedge
        dx: Total length in X
        dy: Total length in Y
        dz: Total length in Z
        xmin: Minimum X for top face
        zmin: Minimum Z for top face
        xmax: Maximum X for top face
        zmax: Maximum Z for top face

    Returns:
        Wedge TopoDS_Shape
    """
    builder = BRepPrimAPI_MakeWedge(ax2, dx, dy, dz, xmin, zmin, xmax, zmax)
    result = builder.Shape()
    track(set(), builder)
    return result


def ocp_revol(
    shape: TopoDS_Shape,
    axis: gp_Ax1,
    angle: float = 6.283185307179586,  # 2*pi
    copy: bool = True,
) -> TopoDS_Shape:
    """Create a revolution with tracking.

    Wraps BRepPrimAPI_MakeRevol.

    Args:
        shape: The shape to revolve
        axis: The axis of revolution
        angle: The angle to revolve in radians (default 2*pi)
        copy: Whether to copy the shape (default True)

    Returns:
        Revolved TopoDS_Shape
    """
    builder = BRepPrimAPI_MakeRevol(shape, axis, angle, copy)
    result = builder.Shape()
    track({shape}, builder)
    return result


def ocp_prism(
    shape: TopoDS_Shape,
    vec: gp_Vec,
) -> TopoDS_Shape:
    """Create a prism (extrusion) with tracking.

    Wraps BRepPrimAPI_MakePrism.

    Args:
        shape: The shape to extrude
        vec: The direction and distance vector

    Returns:
        Extruded TopoDS_Shape
    """
    builder = BRepPrimAPI_MakePrism(shape, vec)
    result = builder.Shape()
    track({shape}, builder)
    return result


def ocp_half_space(
    surface: TopoDS_Face | TopoDS_Shell,
    ref_point: gp_Pnt,
) -> TopoDS_Shape:
    """Create a half space with tracking.

    Wraps BRepPrimAPI_MakeHalfSpace.

    Args:
        surface: A face or shell defining the boundary
        ref_point: A point on the solid side of the half space

    Returns:
        Half space TopoDS_Shape (infinite solid)
    """
    builder = BRepPrimAPI_MakeHalfSpace(surface, ref_point)
    result = builder.Solid()
    track({surface}, builder)
    return result


# =============================================================================
# Feature Operations
# =============================================================================


def ocp_dprism(
    solid: TopoDS_Shape,
    face: TopoDS_Face,
    sketch_face: TopoDS_Face,
    angle: float,
    fuse: int,
    modify: bool,
    height: float | None = None,
    until_face: TopoDS_Face | None = None,
    thru_all: bool = False,
) -> TopoDS_Shape:
    """Create a draft prism feature with tracking.

    Wraps BRepFeat_MakeDPrism.

    Args:
        solid: The base solid
        face: The profile face
        sketch_face: The sketch face (or empty face)
        angle: Draft angle in radians
        fuse: 0 for cut, 1 for fuse
        modify: Whether to modify the base solid
        height: Depth of the prism (if specified)
        until_face: Face to extrude until (if specified)
        thru_all: If True, extrude through all (default False)

    Returns:
        Result TopoDS_Shape
    """
    builder = BRepFeat_MakeDPrism(solid, face, sketch_face, angle, fuse, modify)

    if until_face is not None:
        builder.Perform(until_face)
    elif thru_all or height is None:
        builder.PerformThruAll()
    else:
        builder.Perform(height)

    result = builder.Shape()
    track({solid}, builder)
    return result


def ocp_split_shape(
    shape: TopoDS_Shape,
    edges: TopTools_ListOfShape,
) -> TopoDS_Shape:
    """Split a shape by edges with tracking.

    Wraps BRepFeat_SplitShape.

    Args:
        shape: The shape to split
        edges: The edges to split with

    Returns:
        Split TopoDS_Shape
    """
    builder = BRepFeat_SplitShape(shape)
    builder.Add(edges)
    builder.Build()
    result = builder.Shape()
    track({shape}, builder)
    return result


# =============================================================================
# Sewing
# =============================================================================


def ocp_sewing(
    faces: Iterable[TopoDS_Face],
    tolerance: float = 1e-6,
) -> TopoDS_Shape:
    """Sew faces into a shell with tracking.

    Wraps BRepBuilderAPI_Sewing.

    Args:
        faces: The faces to sew
        tolerance: Sewing tolerance (default 1e-6)

    Returns:
        Sewn TopoDS_Shape
    """
    faces_list = list(faces)
    builder = BRepBuilderAPI_Sewing(tolerance)
    for face in faces_list:
        builder.Add(face)
    builder.Perform()
    result = builder.SewedShape()
    track(set(faces_list), builder)
    return result


# =============================================================================
# Backwards compatibility alias
# =============================================================================

# Alias for existing code that imports `transform`
transform = ocp_transform
