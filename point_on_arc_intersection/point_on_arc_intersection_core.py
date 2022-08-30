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
from qgis.core import (
    QgsVectorLayer,
    QgsWkbTypes,
    QgsFeature,
    QgsGeometry
)


class PointOnArcIntersectionCore:
    def __init__(self, input_layer, output_layer_name, algorithm_list, relation_number):
        self.input_layer = input_layer
        self.output_layer_name = output_layer_name
        self.algorithm_list = algorithm_list
        self.output_layer = QgsVectorLayer(
            "Point?index=yes",
            output_layer_name,
            "memory",
            crs=input_layer.crs()
        )
        self.relation_number = relation_number
        self.algorithm_dict = {
            0: self.intersect_nodes,
            1: self.intersect_node_body,
            2: self.intersect_bodies,
            3: self.self_intersect
        }

    def intersect_nodes(self):
        pass

    def intersect_node_body(self):
        pass

    def intersect_bodies(self):
        pass

    def self_intersect(self):
        pass

    def get_relations(self):
        for index in self.algorithm_list:
            self.algorithm_dict[index]()

    def execute(self):
        self.get_relations()