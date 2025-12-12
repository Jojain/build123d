import pprint
from build123d import *
from ocp_vscode import show
from build123d.tracking import Selector, get_current_tracker

tracker = get_current_tracker()
a = Box(10, 10, 10)
a.trackname = "box"
# a = Solid.make_box(10, 10, 10)

top_face = a.faces()[5]

selector = Selector()
selector.select(top_face, a)
edges = a.edges()
f = fillet(edges, radius=2)
f.trackname = "fillet"
tracker.replace_shape(a, f)
resolved = Face(selector.resolve())
# resolved.color = "blue"
# resolved.name = "resolved"

# raw_index_face = f.faces()[5]
# raw_index_face.color = "red"
# raw_index_face.name = "raw_index_face"
# tracker.export("test.xml")
pprint.pprint(tracker.list_tracked_shapes())
tracker.disable = True
show(resolved, top_face, a)

