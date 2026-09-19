import FreeCAD as App
import Draft
import importSVG

origin = App.Vector(0, 0, 0)
xaxis = App.Vector(1, 0, 0)
yaxis = App.Vector(0, 1, 0)
zaxis = App.Vector(0, 0, 1)


def inch(measurement: float) -> float:
    return measurement * 25.4

def debug(msg: str, v) -> None:
    print(f"XXX: {msg} object {v}: type={type(v)}, value={v}")
    for d in dir(v):
        print(f'XXX:     dir: {d}')

# Epilog Legend 36EXT bed size: 36" x 24" (914mm x 610mm) according to:
# https://www.epiloglaser.com/laser-machines/legacy-systems/legend-36ext/#tech-specs
EPILOG_LEGENT_36EXT = inch(36), inch(24)
# Epilog Mini 24 bed size: 24″ x 12″ (610mm x 305 mm) according to:
# https://www.epiloglaser.com/laser-machines/legacy-systems/mini-18-24-helix-24/#tech-specs
EPILOG_MINI_24 = inch(24), inch(12)

# Set the bed size
bed_size_x, bed_size_y = EPILOG_LEGENT_36EXT


text_content = "Hello FreeCAD"
font_file = "/usr/share/fonts/truetype/open-sans/OpenSans-Semibold.ttf"  # Replace with the actual path to your font
font_file = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Installed by default
font_size = 28.0
text_object = Draft.makeShapeString(String=text_content, FontFile=font_file, Size=font_size)


def place_letter(letter: chr, possition: App.Vector, scale: float) -> list[Draft.DraftObject]:
    """Place the given letter at the given possition"""
    (x, y, _) = possition

    shape_string = Draft.makeShapeString(String=letter, FontFile=font_file, Size=font_size)
    return [shape_string]


def main():
    base_length = 800
    base_width = 600
    thickness = 15
    document_name = "abcpzl"
    doc = App.newDocument(document_name)
    debug("App", App)
    App.setActiveDocument(document_name)
    App.ActiveDocument.addObject("Part::Box","Test_Box")
    App.ActiveDocument.Test_Box.Length=base_length
    App.ActiveDocument.Test_Box.Width=base_width
    App.ActiveDocument.Test_Box.Height=thickness
    App.ActiveDocument.Test_Box.Placement=App.Base.Placement(origin,App.Base.Rotation(0.000,0.000,0.000,1.000))
    App.ActiveDocument.Test_Box.Label='Python Generated BOX'

    bounding_box = Draft.make_rectangle(bed_size_x, bed_size_y, face=True)

    doc.recompute()
    objects = [
        bounding_box,
        *place_letter('Baby Rivers', possition=App.Vector(inch(18), inch(12), 0), scale=1)
    ]
    importSVG.export(objects, "abcpzl.svg")


main()