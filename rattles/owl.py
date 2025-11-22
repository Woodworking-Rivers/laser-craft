"""
On owl shaped rattle inspired by https://tinyurl.com/owl-rattle
"""
import FreeCAD as App
import Part
import Draft

import importSVG

import os
import sys

# TODO: Workaround for FreeCAD's Python path issue.
# The workaround allows a py_binary to have dependencies a py_library.
sys.path.append(os.getcwd())
from geometry import bezier

def inch(measurement: float) -> float:
    """Converts a measurement from inches to mm"""
    return measurement * 25.4

def mm(measurement: float) -> float:
    """Converts a measurment from mm to mm
    Effectively, it is a NOP.
    """
    return measurement

def cm(measuremet: float) -> float:
    """Converts a measurement from cm to mm"""
    return measuremet * 10

X_AXIS = App.Vector(1, 0, 0)
Y_AXIS = App.Vector(0, 1, 0)
Z_AXIS = App.Vector(0, 0, 1)
# Epilog Legend 36EXT bed size: 36" x 24" (914mm x 610mm) according to:
# https://www.epiloglaser.com/laser-machines/legacy-systems/legend-36ext/#tech-specs
EPILOG_LEGENT_36EXT = inch(36), inch(24)
# Epilog Mini 24 bed size: 24″ x 12″ (610mm x 305 mm) according to:
# https://www.epiloglaser.com/laser-machines/legacy-systems/mini-18-24-helix-24/#tech-specs
EPILOG_MINI_24 = inch(24), inch(12)

# Set the bed size
bed_size_x, bed_size_y = EPILOG_LEGENT_36EXT

def owl(doc, width: float, height: float, center_position: App.Vector) ->  list[Draft.DraftObject]:
    """
    Returns owl in form of an array of paths.

    Inspired by https://freesvg.org/originuum-desenho-coruja-1-0-0 (License: Public Domain)
    """
    (cx, cy, _) = center_position
    points_to_interpolate = [
        # Points in clockwise order, starting from top
        App.Vector(cx, cy + height / 2, 0),  # Top
        App.Vector(cx + width / 2, cy + height / 4, 0),  # Top Right
        App.Vector(cx + 3 * width / 8, cy - height / 4, 0),  # Bottom Right
        App.Vector(cx, cy - height / 2, 0),  # Bottom
        App.Vector(cx - 3 * width / 8, cy - height / 4, 0),  # Bottom Left
        App.Vector(cx - width / 2, cy + height / 4, 0),  # Top Left
    ]

    # Makes the curve smooter and more symetrical by creating a B-spline through the Bezier control points.
    bez_control_points = bezier.control_points(points_to_interpolate, closed=True)
    torso_outline = Draft.make_bspline(
        [point
            for tuple_poits in bez_control_points
             for point in tuple_poits],
        closed=True, face=False)

    torso = doc.addObject("App::DocumentObjectGroup", "body_group")
    torso.Group = [
        torso_outline,
    ]

    head_placement = App.Placement(App.Vector(cx, cy + height / 2, 0), App.Rotation())
    head_outline = Draft.make_circle(radius=mm(width / 2), placement=head_placement, face=True)
    head = doc.addObject("App::DocumentObjectGroup", "head_group")
    head.Group = [
        head_outline,
    ]
    def leg(x_pos: float, group_name: str):
        placement = App.Placement(App.Vector(x_pos, cy - height / 2, 0), App.Rotation(Z_AXIS, 90))
        toe_offset = mm(width / 20)  # Offset for toes
        toes = []
        toes = [
            Draft.make_ellipse(
                majradius=mm(width / 10),
                minradius=mm(width / 20),
                placement=App.Placement(App.Vector(x_pos + i * toe_offset, cy - height / 2, 0), App.Rotation(Z_AXIS, 90)),
                face=True
            )
            for i in [-1, 0, 1]
        ]

        group = doc.addObject("App::DocumentObjectGroup", group_name)
        group.Group = toes
        return group

    left_leg = leg(cx - width / 6, "left_leg_group")
    right_leg = leg(cx + width / 6, "right_leg_group")

    def eye(x_pos: float, group_name: str):
        eye_y_pos = cy + height / 2 + mm(width / 8)
        eye_radius = mm(width / 4)
        iris_radius = mm(width / 6)

        eye_placement = App.Placement(App.Vector(x_pos, eye_y_pos, 0), App.Rotation())
        eye_outline = Draft.make_circle(radius=eye_radius, placement=eye_placement, face=True)

        iris_placement = App.Placement(App.Vector(x_pos, eye_y_pos, 0), App.Rotation())
        iris_outline = Draft.make_circle(radius=iris_radius, placement=iris_placement, face=True)

        group = doc.addObject("App::DocumentObjectGroup", group_name)
        group.Group = [eye_outline, iris_outline]
        return group

    left_eye = eye(cx - mm(width / 4), "left_eye_group")
    right_eye = eye(cx + mm(width / 4), "right_eye_group")

    return [
        torso,
        head,
        left_leg,
        right_leg,
        left_eye,
        right_eye,
    ]

def main():
    """
    The entry point to the program.
    """
    document_name = 'owl_rattle'
    doc = App.newDocument(document_name)
    bounding_box = Draft.make_rectangle(bed_size_x, bed_size_y, face=True)
    main_group = doc.addObject('App::DocumentObjectGroup', 'Borders')
    main_group.Group = [
        bounding_box,
    ]

    # Create owl curve
    owl_birthday_milestore = owl(
        doc,
        width=mm(150),
        height=mm(200),
        center_position=App.Vector(mm(100), mm(150)),
    )

    doc.recompute() 
    
    # Export both the bounding box and the owl curve
    # Order matters for SVG layering (first is bottom)
    objects_to_export = [
        main_group,
        *owl_birthday_milestore,
    ]
    importSVG.export(objects_to_export, 'owl_rattle.svg')

main()
