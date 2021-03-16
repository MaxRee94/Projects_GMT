from maya import cmds
from maya import OpenMaya
from maya import OpenMayaUI
from maya import mel
mel.eval("source dagMenuProc.mel;")


def fetch_vtx_coordinates(vertices):
    """Fetch vtx coordinates of given mesh object."""
    print 'all vertices:', str(vertices)
    vertex_coords = list()
    for vertex in vertices:
        coords = cmds.xform(vertex, query=True, worldSpace=True, absolute=True, translation=True)
        vertex_coords.append(coords)
    return vertex_coords


def fetch_vertices_in_view():
    """Fetch all the vertices of mesh objects currently visible in viewport."""
    cmds.select(clear=True)

    view = OpenMayaUI.M3dView.active3dView()
    OpenMaya.MGlobal.selectFromScreen(0, 0, view.portWidth(), view.portHeight(), OpenMaya.MGlobal.kReplaceList)

    objs = cmds.ls(selection=True)
    mesh_objects = list()
    for obj in objs:
        shape_node = cmds.listRelatives(obj, shapes=True)
        if shape_node is not None:
            shape_node = shape_node[0]
            if cmds.nodeType(shape_node) == "mesh":
                mesh_objects.append(shape_node)

    for obj in mesh_objects:
        mel.eval('doMenuComponentSelection("{}", "vertex");'.format(obj))

    view = OpenMayaUI.M3dView.active3dView()
    OpenMaya.MGlobal.selectFromScreen(0, 0, view.portWidth(), view.portHeight(), OpenMaya.MGlobal.kReplaceList, OpenMaya.MGlobal.kWireframeSelectMethod)

    vertices_in_view = cmds.ls(selection=True, flatten=True)

    # go back into object selection mode
    cmds.selectMode(component=False, object=True)
    cmds.selectType(allObjects=True, allComponents=False)
    cmds.select(all=True)
    cmds.select(clear=True)

    return vertices_in_view
