import FreeCAD as App
import PartDesign
import Sketcher
import Mesh
import Part
import FreeCAD
from FreeCAD import Vector, Rotation, Placement
from .macro import *

class PartCreator:
    def __init__(self):
        App.newDocument("Unnamed")
        self.doc = App.ActiveDocument
        self.body = self.doc.addObject('PartDesign::Body', 'Body')
        self.doc.recompute()

    def create_raw_stock(self, length, width, height):
        self.length = length
        self.width = width
        self.height = height

        # Ensure 'Body' is selected
        if not self.body:
            raise ValueError("Body object not found in the document.")

        # Create a new Sketch
        sketch = self.body.newObject('Sketcher::SketchObject', 'Sketch')
        sketch.Support = (self.doc.getObject('XY_Plane'), [''])
        sketch.MapMode = 'FlatFace'
        self.doc.recompute()

        # Define geometry for the sketch
        geoList = [
            Part.LineSegment(Vector(-length/2, -width/2, 0), Vector(-length/2, width/2, 0)),
            Part.LineSegment(Vector(-length/2, width/2, 0), Vector(length/2, width/2, 0)),
            Part.LineSegment(Vector(length/2, width/2, 0), Vector(length/2, -width/2, 0)),
            Part.LineSegment(Vector(length/2, -width/2, 0), Vector(-length/2, -width/2, 0)),
            Part.Point(Vector(0.000000, 0.000000, 0))
        ]
        sketch.addGeometry(geoList, False)

        # Define constraints for the sketch
        conList = [
            Sketcher.Constraint('Coincident', 0, 2, 1, 1),
            Sketcher.Constraint('Coincident', 1, 2, 2, 1),
            Sketcher.Constraint('Coincident', 2, 2, 3, 1),
            Sketcher.Constraint('Coincident', 3, 2, 0, 1),
            Sketcher.Constraint('Horizontal', 1),
            Sketcher.Constraint('Horizontal', 3),
            Sketcher.Constraint('Vertical', 0),
            Sketcher.Constraint('Vertical', 2),
            Sketcher.Constraint('Symmetric', 1, 2, 0, 1, 4, 1)
        ]
        sketch.addConstraint(conList)
        del geoList, conList
        sketch.addConstraint(Sketcher.Constraint('Coincident', 4, 1, -1, 1))
        self.doc.recompute()

        # Create a Pad from the Sketch
        pad = self.body.newObject('PartDesign::Pad', 'Pad')
        pad.Profile = sketch
        pad.Length = int(height)
        self.doc.recompute()

        # Configure the Pad
        pad.Length = int(height)
        pad.TaperAngle = 0.000000
        pad.UseCustomVector = 0
        pad.Direction = (0, 0, 1)
        pad.ReferenceAxis = (sketch, ['N_Axis'])
        pad.AlongSketchNormal = 1
        pad.Type = 0
        pad.UpToFace = None
        pad.Reversed = 0
        pad.Midplane = 1
        pad.Offset = 0
        self.doc.recompute()

        # Hide the Sketch
        sketch.Visibility = False
        
        # Create Datum Planes
        datum_plane_top = self.body.newObject('PartDesign::Plane', 'DatumPlaneTop')
        datum_plane_top.Support = [(self.body.getObject('Pad'), 'Face6')]
        datum_plane_top.MapMode = 'FlatFace'
        datum_plane_top.AttachmentOffset = Placement(Vector(0.0, 0.0, 0.0), Rotation(0.0, 0.0, 0.0))
        datum_plane_top.MapReversed = False
        datum_plane_top.MapPathParameter = 0.0
        self.doc.recompute()

        datum_plane_front = self.body.newObject('PartDesign::Plane', 'DatumPlaneFront')
        datum_plane_front.Support = [(self.body.getObject('Pad'), 'Face4')]
        datum_plane_front.MapMode = 'FlatFace'
        datum_plane_front.AttachmentOffset = Placement(Vector(0.0, 0.0, 0.0), Rotation(0.0, 0.0, 0.0))
        datum_plane_front.MapReversed = False
        datum_plane_front.MapPathParameter = 0.0
        self.doc.recompute()

        datum_plane_left = self.body.newObject('PartDesign::Plane', 'DatumPlaneLeft')
        datum_plane_left.Support = [(self.body.getObject('Pad'), 'Face1')]
        datum_plane_left.MapMode = 'FlatFace'
        datum_plane_left.AttachmentOffset = Placement(Vector(0.0, 0.0, 0.0), Rotation(0.0, 0.0, 0.0))
        datum_plane_left.MapReversed = False
        datum_plane_left.MapPathParameter = 0.0
        self.doc.recompute()

        # Store the Datum Planes as attributes
        self.datum_plane_top = datum_plane_top
        self.datum_plane_front = datum_plane_front
        self.datum_plane_left = datum_plane_left

    def create_feature(self, feature_type, *args):
        # Generate the feature based on the feature type
        if feature_type == MILL_IDX:
            self.create_mill_feature(*args)
        elif feature_type == DRILL_IDX:
            self.create_drill_feature(*args)
        elif feature_type == SLANT_IDX:
            self.create_slant_feature(*args)
        else:
            raise ValueError("Invalid feature type")

    def create_mill_feature(self, length, width, depth, x, y):
        # Ensure 'Body' is selected and 'Datum Plane' is defined
        if not self.body:
            raise ValueError("Body object not found in the document.")
        if not hasattr(self, 'datum_plane_top'):
            raise ValueError("Datum Plane object not found in the document.")
        
        # Create New Sketch on Datum Plane
        sketch = self.body.newObject('Sketcher::SketchObject', 'Sketch')
        sketch.Support = (self.datum_plane_top, '')
        sketch.MapMode = 'FlatFace'
        self.doc.recompute()
        
        # Define Geometry for the Sketch
        geoList = [
            Part.LineSegment(Vector(x - length/2, y - width/2, 0), Vector(x - length/2, y + width/2, 0)),
            Part.LineSegment(Vector(x - length/2, y + width/2, 0), Vector(x + length/2, y + width/2, 0)),
            Part.LineSegment(Vector(x + length/2, y + width/2, 0), Vector(x + length/2, y - width/2, 0)),
            Part.LineSegment(Vector(x + length/2, y - width/2, 0), Vector(x - length/2, y - width/2, 0)),
            Part.Point(Vector(x, y, 0.0))
        ]
        sketch.addGeometry(geoList, False)
        
        # Define Constraints for the Sketch
        conList = [
            Sketcher.Constraint('Coincident', 0, 2, 1, 1),
            Sketcher.Constraint('Coincident', 1, 2, 2, 1),
            Sketcher.Constraint('Coincident', 2, 2, 3, 1),
            Sketcher.Constraint('Coincident', 3, 2, 0, 1),
            Sketcher.Constraint('Horizontal', 1),
            Sketcher.Constraint('Horizontal', 3),
            Sketcher.Constraint('Vertical', 0),
            Sketcher.Constraint('Vertical', 2),
            Sketcher.Constraint('Symmetric', 1, 2, 0, 1, 4, 1)
        ]
        sketch.addConstraint(conList)
        del geoList, conList
        self.doc.recompute()
        
        # Create Pocket from the Sketch
        pocket = self.body.newObject('PartDesign::Pocket', 'Pocket')
        pocket.Profile = sketch
        pocket.Length = int(depth)
        pocket.TaperAngle = 0.0
        pocket.UseCustomVector = 0
        pocket.Direction = (0, 0, -1)
        pocket.ReferenceAxis = (sketch, ['N_Axis'])
        pocket.AlongSketchNormal = 1
        pocket.Type = 0
        pocket.UpToFace = None
        pocket.Reversed = 0
        pocket.Midplane = 0
        pocket.Offset = 0
        self.doc.recompute()
        
        # Hide Sketch
        sketch.Visibility = False
        self.doc.recompute()

    def create_drill_feature(self, diameter, depth, x, y):
        # Ensure 'Body' is selected and 'Datum Plane' is defined
        if not self.body:
            raise ValueError("Body object not found in the document.")
        if not hasattr(self, 'datum_plane_top'):
            raise ValueError("Datum Plane object not found in the document.")
        
        # Create New Sketch on Datum Plane
        sketch = self.body.newObject('Sketcher::SketchObject', 'Sketch')
        sketch.Support = (self.datum_plane_top, '')
        sketch.MapMode = 'FlatFace'
        self.doc.recompute()
        
        # Define Geometry for the Sketch (a circle for the hole)
        circle = Part.Circle(App.Vector(x, y, 0), App.Vector(0, 0, 1), diameter / 2)
        sketch.addGeometry(circle, False)
        
        # Define Constraints for the Sketch
        sketch.addConstraint(Sketcher.Constraint('Radius', 0, diameter / 2))
        self.doc.recompute()
        
        # Create Hole from the Sketch
        hole = self.body.newObject('PartDesign::Pocket', 'Hole')
        hole.Profile = sketch
        hole.Length = int(depth)
        hole.TaperAngle = 0.0
        hole.UseCustomVector = 0
        hole.Direction = (0, 0, -1)
        hole.ReferenceAxis = (sketch, ['N_Axis'])
        hole.AlongSketchNormal = 1
        hole.Type = 0
        hole.UpToFace = None
        hole.Reversed = 0
        hole.Midplane = 0
        hole.Offset = 0
        self.doc.recompute()
        
        # Hide the Sketch
        sketch.Visibility = False
        self.doc.recompute()

    def create_slant_feature(self, direction, size_slant, height_slant):
        # Create New Sketch on Datum Plane
        sketch = self.body.newObject('Sketcher::SketchObject', 'Sketch')
        if direction == 'left' or direction == 'right':
            sketch.Support = (self.datum_plane_front, '')
        elif direction == 'top' or direction == 'bottom':
            sketch.Support = (self.datum_plane_left, '')
        sketch.MapMode = 'FlatFace'
        self.doc.recompute()

        # Define Geometry for the Sketch
        if direction == 'left':
            geoList = [
                Part.LineSegment(Vector(-self.length/2, self.height/2, 0), Vector(-self.length/2, self.height/2 - height_slant, 0)),
                Part.LineSegment(Vector(-self.length/2, self.height/2 - height_slant, 0), Vector(-self.length/2 + height_slant, self.height/2, 0)),
                Part.LineSegment(Vector(-self.length/2 + size_slant, self.height/2, 0), Vector(-self.length/2, self.height/2, 0))
            ]
        elif direction == 'right':
            geoList = [
                Part.LineSegment(Vector(self.length/2, self.height/2, 0), Vector(self.length/2, self.height/2 - height_slant, 0)),
                Part.LineSegment(Vector(self.length/2, self.height/2 - height_slant, 0), Vector(self.length/2 - size_slant, self.height/2, 0)),  
                Part.LineSegment(Vector(self.length/2 - size_slant, self.height/2, 0), Vector(self.length/2, self.height/2, 0))
            ]
        elif direction == 'top':
            geoList = [
                Part.LineSegment(Vector(-self.width/2, self.height/2, 0), Vector(-self.width/2, self.height/2 - height_slant, 0)),
                Part.LineSegment(Vector(-self.width/2, self.height/2 - height_slant, 0), Vector(-self.width/2 + size_slant, self.height/2, 0)),
                Part.LineSegment(Vector(-self.width/2 + size_slant, self.height/2, 0), Vector(-self.width/2, self.height/2, 0))
            ]
        elif direction == 'bottom':
            geoList = [
                Part.LineSegment(Vector(self.width/2, self.height/2, 0), Vector(self.width/2, self.height/2 - height_slant, 0)),
                Part.LineSegment(Vector(self.width/2, self.height/2 - height_slant, 0), Vector(self.width/2 - size_slant, self.height/2, 0)),
                Part.LineSegment(Vector(self.width/2 - size_slant, self.height/2, 0), Vector(self.width/2, self.height/2, 0))
            ]
        sketch.addGeometry(geoList, False)

        # Define Constraints for the Sketch
        conList = [
            Sketcher.Constraint('Coincident', 0, 2, 1, 1),
            Sketcher.Constraint('Coincident', 1, 2, 2, 1),
            Sketcher.Constraint('Coincident', 2, 2, 0, 1),
            Sketcher.Constraint('Horizontal', 2),
            Sketcher.Constraint('Vertical', 0),
        ]
        sketch.addConstraint(conList)
        del geoList, conList
        self.doc.recompute()

        # Create Chamfer from the Sketch
        chamfer = self.body.newObject('PartDesign::Pocket', 'Chamfer')
        chamfer.Profile = sketch
        chamfer.Length = int(self.width) if direction == 'left' or direction == 'right' else int(self.length)
        chamfer.TaperAngle = 0.0
        chamfer.UseCustomVector = 0
        chamfer.Direction = (0, 1, 0) if direction == 'left' or direction == 'right' else (1, 0, 0)
        chamfer.ReferenceAxis = (sketch, ['N_Axis'])
        chamfer.AlongSketchNormal = 1
        chamfer.Type = 0
        chamfer.UpToFace = None
        chamfer.Reversed = 0
        chamfer.Midplane = 0
        chamfer.Offset = 0
        self.doc.recompute()
        
        # Hide the Sketch
        sketch.Visibility = False
        self.doc.recompute()
   

    def save_as_stl(self, file_path):
        __objs__ = [self.body]
        if hasattr(Mesh, "exportOptions"):
            options = Mesh.exportOptions(file_path)
            Mesh.export(__objs__, file_path, options)
        else:
            Mesh.export(__objs__, file_path)
            
        del __objs__

    def close_document(self):
        App.closeDocument(App.ActiveDocument.Name)

        


