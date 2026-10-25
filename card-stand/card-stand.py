"""
Creates the buleprint for laser cutting a card Stand.
A stand is a rectangle with a solt cut in the top part to hold the card.

```
┌──────┐┌──────┐
│      └┘      │
│              │
│              │
│              │
│              │
└──────────────┘

```

"""
import FreeCAD as App
import Part
import Draft

import importSVG

import os
import sys

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
bed_size_x, bed_size_y = cm(25.5), cm(25.5)

def stand(doc, width: float, height: float, cutout_width: float, cutout_height:float, center_position: App.Vector) ->  list[Draft.DraftObject]:
    """
    Returns a stad in form of an array of paths
    """
    (cx, cy, _) = center_position
    plate_placement = App.Placement(App.Vector(cx - width / 2, cy - height / 2, 0), App.Rotation())
    cutout_placement = App.Placement(App.Vector(cx - cutout_width / 2, cy + height / 2 -cutout_height, 0), App.Rotation())
    plate_outline = Draft.make_rectangle(width, height, placement=plate_placement, face=True)
    cutout_outline = Draft.make_rectangle(cutout_width, cutout_height, placement=cutout_placement, face=True)
    # card_stand = doc.addObject("App::DocumentObjectGroup", "card_stand")
    # card_stand.Group = [
    #     plate_outline,
    #     cutout_outline,
    # ]

    # Create the boolean cut
    stand_cut = doc.addObject("Part::Cut", "card_stand")
    stand_cut.Base = plate_outline
    stand_cut.Tool = cutout_outline
    return stand_cut


def main():
    """
    The entry point to the program.
    """
    document_name = 'Card Stand'
    doc = App.newDocument(document_name)
    bounding_box = Draft.make_rectangle(bed_size_x, bed_size_y, face=True)
    main_group = doc.addObject('App::DocumentObjectGroup', 'Borders')
    main_group.Group = [
        bounding_box,
    ]
    stands = [
      stand(
        doc,
        width=mm(20),
        height=mm(20),
        cutout_width=mm(2),
        cutout_height=mm(5),
        center_position=App.Vector(mm(-10) + i * 22, mm(-10) + j * 22),
    )
    for i in range (1, 12)
    for j in range (1, 12)
    ]

    doc.recompute()
    
    # Export both the bounding box and the owl curve
    # Order matters for SVG layering (first is bottom)
    objects_to_export = [
        main_group,
    ] + stands
    importSVG.export(objects_to_export, 'card_stand.svg')

main()
