# -*- coding: utf-8 -*-
"""
    This is the place, where dissolving algorithms resolve./

 ***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


class Node:
    def __init__(self, id, point, node=None):
        self.id = id
        self.point = point
        self.node = node
        self.relation_ids = []
        self.relation_counter = 0

    def add_id(self, new_id):
        if new_id not in self.relation_ids:
            self.relation_ids.append(new_id)


class FeatureHelper:
    def __init__(self, dictHelper, shape):
        shapeID = shape.id()
        self.id = shapeID
        self.nodeList = []
        geometry = shape.geometry()

        for part in geometry.parts():
            self.nodeList.append(Node(shapeID, part[0]))
            self.nodeList.append(Node(shapeID, part[-1]))

        dictHelper[shapeID] = self


# Function creates a feature helper or returns existing one for given id
def validate_feature_helper_dict(feature_helper_dict, shape_id, shape):
    if (feature_helper_dict is None) or (shape is None):
        return

    if shape_id not in feature_helper_dict.keys():
        return FeatureHelper(feature_helper_dict, shape)
    else:
        return feature_helper_dict[shape_id]


# Function checks if point intersects other point or multipoint
def check_point_point_intersection(point, intersect):
    for part in intersect.parts():
        if point == part:
            return True

    return False


# Function fills feature helper dictionary based on provided arcs' layer
def get_feature_helper_dict(layer):
    feature_helper_dict = {}

    for shape in layer.getFeatures():
        FeatureHelper(feature_helper_dict, shape)

    return feature_helper_dict
