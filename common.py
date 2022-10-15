

__author__ = "Nutti <nutti.metro@gmail.com>"
__status__ = "production"
__version__ = "6.5"
__date__ = "6 Mar 2021"

from collections import defaultdict
from pprint import pprint
from math import fabs, sqrt
import os

import bpy
from mathutils import Vector
import bmesh

AddonName = __package__

__DEBUG_MODE = False



def check_version(major, minor, _):
    """
    Check blender version
    """

    if bpy.app.version[0] == major and bpy.app.version[1] == minor:
        return 0
    if bpy.app.version[0] > major:
        return 1
    if bpy.app.version[1] > minor:
        return 1
    return -1


def get_object_select(obj):
    if check_version(2, 80, 0) < 0:
        return obj.select

    return obj.select_get()


def get_uv_editable_objects(context):
    if check_version(2, 80, 0) < 0:
        objs = [context.active_object]
    else:
        objs = [o for o in bpy.data.objects
                if get_object_select(o) and o.type == 'MESH']
        objs.append(context.active_object)

    objs = list(set(objs))
    return objs


def get_island_info(obj, only_selected=True):
    bm = bmesh.from_edit_mesh(obj.data)
    if check_version(2, 73, 0) >= 0:
        bm.faces.ensure_lookup_table()

    return get_island_info_from_bmesh(bm, only_selected)


def get_island_info_from_bmesh(bm, only_selected=True):
    if not bm.loops.layers.uv:
        return None
    uv_layer = bm.loops.layers.uv.verify()

    # create database
    if only_selected:
        selected_faces = [f for f in bm.faces if f.select]
    else:
        selected_faces = [f for f in bm.faces]

    return get_island_info_from_faces(bm, selected_faces, uv_layer)


def get_island_info_from_faces(bm, faces, uv_layer):
    ftv, vtf = __create_vert_face_db(faces, uv_layer)

    # Get island information
    uv_island_lists = __get_island(bm, ftv, vtf)
    island_info = __get_island_info(uv_layer, uv_island_lists)

    return island_info


def __create_vert_face_db(faces, uv_layer):
    # create mesh database for all faces
    face_to_verts = defaultdict(set)
    vert_to_faces = defaultdict(set)
    for f in faces:
        for l in f.loops:
            id_ = l[uv_layer].uv.to_tuple(5), l.vert.index
            face_to_verts[f.index].add(id_)
            vert_to_faces[id_].add(f.index)

    return (face_to_verts, vert_to_faces)



def __get_island(bm, face_to_verts, vert_to_faces):
    """
    Get island list
    """

    uv_island_lists = []
    faces_left = set(face_to_verts.keys())
    while faces_left:
        current_island = []
        face_idx = list(faces_left)[0]
        __parse_island(bm, face_idx, faces_left, current_island,
                        face_to_verts, vert_to_faces)
        uv_island_lists.append(current_island)

    return uv_island_lists


def __get_island_info(uv_layer, islands):
    """
    get information about each island
    """

    island_info = []
    for isl in islands:
        info = {}
        max_uv = Vector((-10000000.0, -10000000.0))
        min_uv = Vector((10000000.0, 10000000.0))
        ave_uv = Vector((0.0, 0.0))
        num_uv = 0
        for face in isl:
            n = 0
            a = Vector((0.0, 0.0))
            ma = Vector((-10000000.0, -10000000.0))
            mi = Vector((10000000.0, 10000000.0))
            for l in face['face'].loops:
                uv = l[uv_layer].uv
                ma.x = max(uv.x, ma.x)
                ma.y = max(uv.y, ma.y)
                mi.x = min(uv.x, mi.x)
                mi.y = min(uv.y, mi.y)
                a = a + uv
                n = n + 1
            ave_uv = ave_uv + a
            num_uv = num_uv + n
            a = a / n
            max_uv.x = max(ma.x, max_uv.x)
            max_uv.y = max(ma.y, max_uv.y)
            min_uv.x = min(mi.x, min_uv.x)
            min_uv.y = min(mi.y, min_uv.y)
            face['max_uv'] = ma
            face['min_uv'] = mi
            face['ave_uv'] = a
        ave_uv = ave_uv / num_uv

        info['center'] = ave_uv
        info['size'] = max_uv - min_uv
        info['num_uv'] = num_uv
        info['group'] = -1
        info['faces'] = isl
        info['max'] = max_uv
        info['min'] = min_uv

        island_info.append(info)

    return island_info


def __parse_island(bm, face_idx, faces_left, island,
                   face_to_verts, vert_to_faces):
    """
    Parse island
    """

    faces_to_parse = [face_idx]
    while faces_to_parse:
        fidx = faces_to_parse.pop(0)
        if fidx in faces_left:
            faces_left.remove(fidx)
            island.append({'face': bm.faces[fidx]})
            for v in face_to_verts[fidx]:
                connected_faces = vert_to_faces[v]
                for cf in connected_faces:
                    faces_to_parse.append(cf)



#---------------------------------------------------------------
# Caltulate topology area


def calc_tris_2d_area(points):
    area = 0.0
    for i, p1 in enumerate(points):
        p2 = points[(i + 1) % len(points)]
        v1 = p1 - points[0]
        v2 = p2 - points[0]
        a = v1.x * v2.y - v1.y * v2.x
        area = area + a

    return fabs(0.5 * area)


def calc_tris_3d_area(points):
    area = 0.0
    for i, p1 in enumerate(points):
        p2 = points[(i + 1) % len(points)]
        v1 = p1 - points[0]
        v2 = p2 - points[0]
        cx = v1.y * v2.z - v1.z * v2.y
        cy = v1.z * v2.x - v1.x * v2.z
        cz = v1.x * v2.y - v1.y * v2.x
        a = sqrt(cx * cx + cy * cy + cz * cz)
        area = area + a

    return 0.5 * area


def get_faces_list(bm, method, only_selected):
    faces_list = []
    if method == 'MESH':
        if only_selected:
            faces_list.append([f for f in bm.faces if f.select])
        else:
            faces_list.append([f for f in bm.faces])
    elif method == 'UV ISLAND':
        if not bm.loops.layers.uv:
            return None
        uv_layer = bm.loops.layers.uv.verify()
        if only_selected:
            faces = [f for f in bm.faces if f.select]
            islands = get_island_info_from_faces(bm, faces, uv_layer)
            for isl in islands:
                faces_list.append([f["face"] for f in isl["faces"]])
        else:
            faces = [f for f in bm.faces]
            islands = get_island_info_from_faces(bm, faces, uv_layer)
            for isl in islands:
                faces_list.append([f["face"] for f in isl["faces"]])
    elif method == 'FACE':
        if only_selected:
            for f in bm.faces:
                if f.select:
                    faces_list.append([f])
        else:
            for f in bm.faces:
                faces_list.append([f])
    else:
        raise ValueError("Invalid method: {}".format(method))

    return faces_list


def measure_all_faces_mesh_area(bm):
    if check_version(2, 80, 0) >= 0:
        triangle_loops = bm.calc_loop_triangles()
    else:
        triangle_loops = bm.calc_tessface()

    areas = {face: 0.0 for face in bm.faces}

    for loops in triangle_loops:
        face = loops[0].face
        area = areas[face]
        area += calc_tris_3d_area([l.vert.co for l in loops])
        areas[face] = area

    return areas


def measure_mesh_area(obj, calc_method, only_selected):
    bm = bmesh.from_edit_mesh(obj.data)
    if check_version(2, 73, 0) >= 0:
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

    faces_list = get_faces_list(bm, calc_method, only_selected)

    areas = []
    for faces in faces_list:
        areas.append(measure_mesh_area_from_faces(bm, faces))

    return areas


def measure_mesh_area_from_faces(bm, faces):
    face_areas = measure_all_faces_mesh_area(bm)

    mesh_area = 0.0
    for f in faces:
        if f in face_areas:
            mesh_area += face_areas[f]

    return mesh_area


def measure_all_faces_uv_area(bm, uv_layer):
    if check_version(2, 80, 0) >= 0:
        triangle_loops = bm.calc_loop_triangles()
    else:
        triangle_loops = bm.calc_tessface()

    areas = {face: 0.0 for face in bm.faces}

    for loops in triangle_loops:
        face = loops[0].face
        area = areas[face]
        area += calc_tris_2d_area([l[uv_layer].uv for l in loops])
        areas[face] = area

    return areas


def measure_uv_area_from_faces(obj, bm, faces, uv_layer, tex_layer,
                               tex_selection_method, tex_size):

    face_areas = measure_all_faces_uv_area(bm, uv_layer)

    uv_area = 0.0
    for f in faces:
        if f not in face_areas:
            continue

        f_uv_area = face_areas[f]

        # user specified
        if tex_selection_method == 'USER_SPECIFIED' and tex_size is not None:
            img_size = tex_size
        # first texture if there are more than 2 textures assigned
        # to the object
        elif tex_selection_method == 'FIRST':
            img = find_image(obj, f, tex_layer)
            # can not find from node, so we can not get texture size
            if not img:
                return None
            img_size = img.size
        # average texture size
        elif tex_selection_method == 'AVERAGE':
            imgs = find_images(obj, f, tex_layer)
            if not imgs:
                return None

            img_size_total = [0.0, 0.0]
            for img in imgs:
                img_size_total = [img_size_total[0] + img.size[0],
                                  img_size_total[1] + img.size[1]]
            img_size = [img_size_total[0] / len(imgs),
                        img_size_total[1] / len(imgs)]
        # max texture size
        elif tex_selection_method == 'MAX':
            imgs = find_images(obj, f, tex_layer)
            if not imgs:
                return None

            img_size_max = [-99999999.0, -99999999.0]
            for img in imgs:
                img_size_max = [max(img_size_max[0], img.size[0]),
                                max(img_size_max[1], img.size[1])]
            img_size = img_size_max
        # min texture size
        elif tex_selection_method == 'MIN':
            imgs = find_images(obj, f, tex_layer)
            if not imgs:
                return None

            img_size_min = [99999999.0, 99999999.0]
            for img in imgs:
                img_size_min = [min(img_size_min[0], img.size[0]),
                                min(img_size_min[1], img.size[1])]
            img_size = img_size_min
        else:
            raise RuntimeError("Unexpected method: {}"
                               .format(tex_selection_method))

        uv_area += f_uv_area * img_size[0] * img_size[1]

    return uv_area


def measure_uv_area(obj, calc_method, tex_selection_method,
                    tex_size, only_selected):
    bm = bmesh.from_edit_mesh(obj.data)
    if check_version(2, 73, 0) >= 0:
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

    if not bm.loops.layers.uv:
        return None
    uv_layer = bm.loops.layers.uv.verify()
    tex_layer = find_texture_layer(bm)
    faces_list = get_faces_list(bm, calc_method, only_selected)

    # measure
    uv_areas = []
    for faces in faces_list:
        uv_area = measure_uv_area_from_faces(
            obj, bm, faces, uv_layer, tex_layer,
            tex_selection_method, tex_size)
        if uv_area is None:
            return None
        uv_areas.append(uv_area)

    return uv_areas


def diff_point_to_segment(a, b, p):
    ab = b - a
    normal_ab = ab.normalized()

    ap = p - a
    dist_ax = normal_ab.dot(ap)

    # cross point
    x = a + normal_ab * dist_ax

    # difference between cross point and point
    xp = p - x

    return xp, x





# sort pair by vertex
# (v0, v1) - (v1, v2) - (v2, v3) ....
def __sort_loop_pairs(uv_layer, pairs, closed):
    rest = pairs
    sorted_pairs = [rest[0]]
    rest.remove(rest[0])

    # prepend
    while True:
        p1 = sorted_pairs[0]
        for p2 in rest:
            if p1[0].vert == p2[0].vert:
                sorted_pairs.insert(0, [p2[1], p2[0]])
                rest.remove(p2)
                break
            elif p1[0].vert == p2[1].vert:
                sorted_pairs.insert(0, [p2[0], p2[1]])
                rest.remove(p2)
                break
        else:
            break

    # append
    while True:
        p1 = sorted_pairs[-1]
        for p2 in rest:
            if p1[1].vert == p2[0].vert:
                sorted_pairs.append([p2[0], p2[1]])
                rest.remove(p2)
                break
            elif p1[1].vert == p2[1].vert:
                sorted_pairs.append([p2[1], p2[0]])
                rest.remove(p2)
                break
        else:
            break

    begin_vert = sorted_pairs[0][0].vert
    end_vert = sorted_pairs[-1][-1].vert
    if begin_vert != end_vert:
        return sorted_pairs, ""
    if closed and (begin_vert == end_vert):
        # if the sequence of UV is circular, it is ok
        return sorted_pairs, ""

    # if the begin vertex and the end vertex are same, search the UVs which
    # are separated each other
    tmp_pairs = sorted_pairs
    for i, (p1, p2) in enumerate(zip(tmp_pairs[:-1], tmp_pairs[1:])):
        diff = p2[0][uv_layer].uv - p1[-1][uv_layer].uv
        if diff.length > 0.000000001:
            # UVs are separated
            sorted_pairs = tmp_pairs[i + 1:]
            sorted_pairs.extend(tmp_pairs[:i + 1])
            break
    else:
        p1 = tmp_pairs[0]
        p2 = tmp_pairs[-1]
        diff = p2[-1][uv_layer].uv - p1[0][uv_layer].uv
        if diff.length < 0.000000001:
            # all UVs are not separated
            return None, "All UVs are not separated"

    return sorted_pairs, ""


# x ---- x   <- next_loop_pair
# |      |
# o ---- o   <- pair
def __get_next_loop_pair(pair):
    lp = pair[0].link_loop_prev
    if lp.vert == pair[1].vert:
        lp = pair[0].link_loop_next
        if lp.vert == pair[1].vert:
            # no loop is found
            return None

    ln = pair[1].link_loop_next
    if ln.vert == pair[0].vert:
        ln = pair[1].link_loop_prev
        if ln.vert == pair[0].vert:
            # no loop is found
            return None

    # tri-face
    if lp == ln:
        return [lp]

    # quad-face
    return [lp, ln]


# | ---- |
# % ---- %   <- next_poly_loop_pair
# x ---- x   <- next_loop_pair
# |      |
# o ---- o   <- pair
def __get_next_poly_loop_pair(pair):
    v1 = pair[0].vert
    v2 = pair[1].vert
    for l1 in v1.link_loops:
        if l1 == pair[0]:
            continue
        for l2 in v2.link_loops:
            if l2 == pair[1]:
                continue
            if l1.link_loop_next == l2:
                return [l1, l2]
            elif l1.link_loop_prev == l2:
                return [l1, l2]

    # no next poly loop is found
    return None



def get_UDIM_tile_coords(obj):
	udim_tile = 1001
	column = row = 0

	if bpy.context.scene.texToolsSettings.UDIMs_source == 'OBJECT':
		if obj and obj.type == 'MESH' and obj.data.uv_layers:
			for i in range(len(obj.material_slots)):
				slot = obj.material_slots[i]
				if slot.material:
					nodes = slot.material.node_tree.nodes
					if nodes:
						for node in nodes:
							if node.type == 'TEX_IMAGE' and node.image and node.image.source =='TILED':
								udim_tile = node.image.tiles.active.number
								break
				else:
					continue
				break
	else:
		image = bpy.context.space_data.image
		if image:
			udim_tile = image.tiles.active.number

	if udim_tile != 1001:
		column = int(str(udim_tile - 1)[-1])
		if udim_tile > 1010:
			row = int(str(udim_tile - 1001)[0:-1])

	return udim_tile, column, row



def set_selected_faces(faces, bm, uv_layers):
	for face in faces:
		for loop in face.loops:
			loop[uv_layers].select = True



def get_selected_uv_verts(bm, uv_layers, selected=None):
	"""Returns selected mesh vertices of selected UV's"""
	verts = set()
	if selected is None:
		for face in bm.faces:
			if face.select:
				for loop in face.loops:
					if loop[uv_layers].select:
						verts.add( loop.vert )
	else:
		for loop in selected:
			verts.add( loop.vert )
	return verts



def get_selected_uv_edges(bm, uv_layers, selected=None):
	"""Returns selected mesh edges of selected UV's"""
	verts = get_selected_uv_verts(bm, uv_layers, selected)
	edges = set()
	for edge in bm.edges:
		if edge.verts[0] in verts and edge.verts[1] in verts:
			edges.add(edge)
	return edges



def get_selected_uv_faces(bm, uv_layers):
	"""Returns selected mesh faces of selected UV's"""
	faces = [face for face in bm.faces if all([loop[uv_layers].select for loop in face.loops]) and face.select]
	return faces



def getSelectionIslands(bm, uv_layers, selected_faces=None):
	if selected_faces is None:
		selected_faces = [face for face in bm.faces if all([loop[uv_layers].select for loop in face.loops]) and face.select]
	if not selected_faces:
		return []

	# Select islands
	bpy.ops.uv.select_linked()
	disordered_island_faces = {f for f in bm.faces if f.loops[0][uv_layers].select}

	# Collect UV islands
	islands = []

	for face in selected_faces:
		if face in disordered_island_faces:
			bpy.ops.uv.select_all(action='DESELECT')
			face.loops[0][uv_layers].select = True
			bpy.ops.uv.select_linked()

			islandFaces = {f for f in disordered_island_faces if f.loops[0][uv_layers].select}
			disordered_island_faces.difference_update(islandFaces)

			islands.append(islandFaces)
			if not disordered_island_faces:
				break

	# Restore selection
	bpy.ops.uv.select_all(action='DESELECT')
	for face in selected_faces:
		for loop in face.loops:
			loop[uv_layers].select = True
	
	return islands



def getAllIslands(bm, uv_layers):
	if len(bm.faces) == 0:
		return []

	bpy.ops.uv.select_all(action='SELECT')
	faces_unparsed = {f for f in bm.faces if f.select}

	# Collect UV islands
	islands = []

	for face in bm.faces:
		if face in faces_unparsed:
			bpy.ops.uv.select_all(action='DESELECT')
			face.loops[0][uv_layers].select = True
			bpy.ops.uv.select_linked()

			islandFaces = {f for f in faces_unparsed if f.loops[0][uv_layers].select}
			faces_unparsed.difference_update(islandFaces)

			islands.append(islandFaces)
			if not faces_unparsed:
				break

	return islands




