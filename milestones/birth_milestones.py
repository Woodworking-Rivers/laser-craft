"""Create a file """
import itertools

import FreeCAD as App
import Draft
import importSVG

from python.runfiles import Runfiles

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


# Epilog Legend 36EXT bed size: 36" x 24" (914mm x 610mm) according to:
# https://www.epiloglaser.com/laser-machines/legacy-systems/legend-36ext/#tech-specs
EPILOG_LEGENT_36EXT = inch(36), inch(24)
# Epilog Mini 24 bed size: 24″ x 12″ (610mm x 305 mm) according to:
# https://www.epiloglaser.com/laser-machines/legacy-systems/mini-18-24-helix-24/#tech-specs
EPILOG_MINI_24 = inch(24), inch(12)

# Set the bed size
bed_size_x, bed_size_y = EPILOG_LEGENT_36EXT


r = Runfiles.Create()

FUNNEL_FONT_FILE = r.Rlocation("+http_file+funnel_font/file/FunnelSans-Regular.ttf")
TANGERINE_FONT_FILE = r.Rlocation("+http_file+tangerine_font/file/Tangerine-Regular.ttf")

FONT_SIZE = 4.0
FIRST_NAME = '<Name>'
MIDDLE_NAME = '<Middle>'

def place_text(text: str, center_position: App.Vector,
               font_file=FUNNEL_FONT_FILE, font_size=FONT_SIZE) -> list[Draft.DraftObject]:
    """Place the given letter at the given position"""
    (x, y, _) = center_position
    shape_string = Draft.makeShapeString(String=text, FontFile=font_file, Size=font_size)
    x_length = shape_string.Shape.BoundBox.XLength
    y_length = shape_string.Shape.BoundBox.YLength
    shape_string.Placement.Base.x = x - x_length / 2
    shape_string.Placement.Base.y = y - y_length / 2
    return shape_string

def place_marker(doc, radius: float, center_position: App.Vector, age:str) -> list[Draft.DraftObject]:
    """
    Places a milestone marker with the giver radius at the given position.
    """
    def offset(x_percent: float, y_percent: float)-> App.Vector:
        return center_position.add(App.Vector(radius * x_percent, radius * y_percent, 0))

    (x, y, _) = center_position
    marker = Draft.make_circle(radius)
    marker.Placement.Base.x = x
    marker.Placement.Base.y = y
    circle_group = doc.addObject('App::DocumentObjectGroup', f'circle_group_{age}')
    circle_group.Group = [marker]
    
    age_group = doc.addObject('App::DocumentObjectGroup', f'age_group_{age}')
    age_group.Group = [
        place_text('Hello', offset(0.00, 0.75)),
        place_text('My name is', offset(0.00, 0.60)),
        place_text(FIRST_NAME, offset(-0.30, 0.40), font_file=TANGERINE_FONT_FILE, font_size=16),
        place_text(MIDDLE_NAME, offset(0.30, 0.00), font_file=TANGERINE_FONT_FILE, font_size=16),
        place_text(f'{age}', offset(0, -0.65), font_size=6),
    ]

    return [
        circle_group,
        age_group,
    ]

def place_birthday_marker(doc, radius: float, center_position: App.Vector, age:str) -> list[Draft.DraftObject]:
    """
    Places the birthday marker with the giver radius at the given position.
    """
    def offset(x_percent: float, y_percent: float)-> App.Vector:
        return center_position.add(App.Vector(radius * x_percent, radius * y_percent, 0))

    (x, y, _) = center_position
    marker = Draft.make_circle(radius)
    marker.Placement.Base.x = x
    marker.Placement.Base.y = y
    circle_group = doc.addObject('App::DocumentObjectGroup', f'main_circle_group_{age}')
    circle_group.Group = [marker]
    
    age_group = doc.addObject('App::DocumentObjectGroup', f'main_age_group_{age}')
    age_group.Group = [
        place_text('Hello! My name is', offset(0.00, 0.75)),
        # place_text('My name is', offset(0.00, 0.60)),
        place_text(FIRST_NAME, offset(-0.30, 0.45), font_file=TANGERINE_FONT_FILE, font_size=18),
        place_text(MIDDLE_NAME, offset(0.30, 0.10), font_file=TANGERINE_FONT_FILE, font_size=18),
        place_text('Date:', offset(-0.29, -0.25), font_size=5),
        place_text(' ______________', offset(0.25, -0.27), font_size=5),
        place_text('Time:', offset(-0.30, -0.40), font_size=5),
        place_text(' ______________', offset(0.25, -0.42), font_size=5),
        place_text('Weight:', offset(-0.35, -0.55), font_size=5),
        place_text(' ______________', offset(0.25, -0.58), font_size=5),
        place_text('Length:', offset(-0.35, -0.70), font_size=5),
        place_text(' ______________', offset(0.25, -0.73), font_size=5),
    ] 
    return [
        circle_group,
        age_group,
    ]


def main():
    """
    The entry point to the program.
    """
    ages = [
        '1 Day',
        '1 Week',
        '2 Weeks',
        '3 Weeks',
        '1 Month',
        '2 Months',
        '3 Months',
        '4 Months',
        '5 Months',
        '6 Months',
        '7 Months',
        '8 Months',
        '9 Months',
        '10 Months',
        '11 Months',
        '12 Months', 
    ]
    rows = 4
    columns = 4
    tabulated_ages = [(i % rows, rows - i // rows , age)
           for (i, age) in enumerate(ages, columns)]
    document_name = 'birthday_milestones'
    doc = App.newDocument(document_name)
    App.setActiveDocument(document_name)
    bounding_box = Draft.make_rectangle(bed_size_x, bed_size_y, face=True)

    main_group = doc.addObject('App::DocumentObjectGroup', 'Borders')
    emblem = place_text('🌱', center_position=App.Vector(cm(0.5), cm(.5), 0))
    main_group.Group = [bounding_box, emblem]

    marker_radius = cm(5)
    marker_gap_fraction = 0.05
    x_offset = cm(0)
    y_offset = cm(19)

    birthday_marker_radius = cm(7)

    def marker_center_position(radius: float, row: int, column: int) -> App.Vector:
        x = x_offset + radius * (1+ marker_gap_fraction) + radius * (2 + marker_gap_fraction) * row
        y = y_offset + radius * (1+ marker_gap_fraction) + radius * (2 + marker_gap_fraction) * column
        return App.Vector(x, y, 0)

    milestones = [
        place_marker(doc, marker_radius, marker_center_position(marker_radius, row=r, column=c), age=age)
            for r, c, age in tabulated_ages]
    birthday_milestore = \
        place_birthday_marker(doc,
                     birthday_marker_radius,
                     App.Vector(500, 520, 0), age='new born')
    objects = [
        main_group,
        *itertools.chain(*milestones),
        *birthday_milestore,
        emblem,
    ]
    doc.recompute()
    importSVG.export(objects, 'birth-milestones.svg')


main()
