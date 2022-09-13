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
from common.classes import (
    validate_feature_helper_dict,
    check_point_point_intersection
)


class PointOnArcIntersectionCore:
    def __init__(self, input_layer, output_layer_name, algorithm_list, relation_number, label, progress):
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
        self.label = label
        self.progress = progress
        self.algorithm_dict = {
            0: self.intersect_nodes,
            1: self.intersect_node_body,
            2: self.intersect_bodies,
            3: self.self_intersect
        }
        self.point_list = []

    def append_point_list(self, new_point):
        for point in self.point_list:
            if point == new_point:
                return

        self.point_list.append(new_point)



    def intersect_nodes(self):
        self.label.setText("Algorithm 1)")
        self.progress.setValue(0)
        self.progress.setMaximum(self.input_layer.featureCount())

        feature_helper_dict = {}
        for shape_source in self.input_layer.getFeatures():
            source_id = shape_source.id()
            feature_helper_source = validate_feature_helper_dict(feature_helper_dict, source_id, shape_source)
            engine = QgsGeometry.createGeometryEngine(shape_source.geometry().constGet())
            engine.prepareGeometry()

            for shape_relate in self.input_layer.getFeatures():
                relate_id = shape_relate.id()

                if source_id == relate_id:
                    continue

                feature_helper_relate = validate_feature_helper_dict(feature_helper_dict, relate_id, shape_relate)
                intersect = engine.intersection(shape_relate.geometry().constGet())
                if intersect is None:
                    continue

                for node1 in feature_helper_source.nodeList:
                    if check_point_point_intersection(node1.point, intersect):
                        for node2 in feature_helper_relate.nodeList:
                            if check_point_point_intersection(node2.point, intersect):
                                node1.add_id(feature_helper_relate.id)

            self.progress.setValue(self.progress.value() + 1)

        for feature_helper in feature_helper_dict.values():
            for node in feature_helper.nodeList:
                if len(node.relation_ids) + 1 >= self.relation_number:
                    self.append_point_list(node.point)

    def intersect_node_body(self):
        pass

    def intersect_bodies(self):
        pass

    def self_intersect(self):
        pass

    def get_relations(self):
        for index in self.algorithm_list:
            self.algorithm_dict[index]()

    def create_shapes(self):
        new_features_list = []
        self.output_layer.beginEditCommand("Creating shapes...")
        try:
            for point in self.point_list:
                feature = QgsFeature()
                feature.setGeometry(point)
                new_features_list.append(feature)

            self.output_layer.dataProvider().addFeatures(new_features_list)
        finally:
            self.output_layer.commitChanges()

    def execute(self):
        self.get_relations()
        self.create_shapes()