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
    QgsGeometry,
    QgsPoint,
    QgsLineString,
    QgsField
)
from common.classes import (
    Node,
    validate_feature_helper_dict,
    check_point_point_intersection,
    get_feature_helper_dict
)
from PyQt5.QtCore import (
    QVariant
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
        self.label.setText("Algorithm 2)")
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
                        is_body = True

                        for node2 in feature_helper_relate.nodeList:
                            if check_point_point_intersection(node2.point, intersect):
                                is_body = False
                                break

                        if is_body:
                            node1.add_id(feature_helper_relate.id)

                for node1 in feature_helper_relate.nodeList:
                    if check_point_point_intersection(node1.point, intersect):
                        is_body = True

                        for node2 in feature_helper_source.nodeList:
                            if check_point_point_intersection(node2.point, intersect):
                                is_body = False
                                break

                        if is_body:
                            node1.add_id(feature_helper_source.id)

            self.progress.setValue(self.progress.value() + 1)

        for feature_helper in feature_helper_dict.values():
            for node in feature_helper.nodeList:
                if len(node.relation_ids) + 1 >= self.relation_number:
                    self.append_point_list(node.point)

    def intersect_bodies(self):
        self.label.setText("Algorithm 3)")
        self.progress.setValue(0)
        self.progress.setMaximum(self.input_layer.featureCount())

        node_list = []
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

                is_body = True
                for node1 in feature_helper_source.nodeList:
                    if check_point_point_intersection(node1.point, intersect):
                        is_body = False
                        break

                if is_body:
                    for node2 in feature_helper_relate.nodeList:
                        if check_point_point_intersection(node2.point, intersect):
                            is_body = False
                            break

                if is_body:
                    for part in intersect.parts():
                        if part.geometryType() != "Point":
                            continue

                        is_found = False

                        for node in node_list:
                            if node.point == part:
                                is_found = True
                                node.add_id(feature_helper_source.id)
                                node.add_id(feature_helper_relate.id)

                        if not is_found:
                            node = Node(-1, part)
                            node.add_id(feature_helper_source.id)
                            node.add_id(feature_helper_relate.id)
                            node_list.append(node)

            self.progress.setValue(self.progress.value() + 1)

        for node in node_list:
            if len(node.relation_ids) >= self.relation_number:
                self.append_point_list(node.point)

    def get_straight_layer(self):
        inner_layer = QgsVectorLayer(
            "LineString?index=yes",
            "inner_layer",
            "memory",
            crs=self.input_layer.crs()
        )
        inner_layer.dataProvider().addAttributes([QgsField("SourceID", QVariant.Int)])
        inner_layer.updateFields()
        inner_layer.beginEditCommand("Creating shapes...")

        for shape in self.input_layer.getFeatures():
            geometry = shape.geometry().constGet()

            for part in geometry.parts():
                count = len(part)
                for i in range(count):
                    if i < count - 1:
                        new_geometry = QgsLineString()
                        new_geometry.addVertex(part[i])
                        new_geometry.addVertex(part[i + 1])
                        feature = QgsFeature()
                        feature.setGeometry(new_geometry)
                        feature.setFields(inner_layer.fields())
                        feature["SourceID"] = shape.id()
                        inner_layer.dataProvider().addFeature(feature)

        inner_layer.commitChanges()
        return inner_layer

    def self_intersect(self):
        self.label.setText("Algorithm 4)")
        self.progress.setValue(0)

        straight_layer = self.get_straight_layer()
        node_list = []
        self.progress.setMaximum(straight_layer.featureCount())

        feature_helper_dict = get_feature_helper_dict(straight_layer)
        for shape_source in straight_layer.getFeatures():
            source_id = shape_source.id()
            feature_helper_source = feature_helper_dict[source_id]
            engine = QgsGeometry.createGeometryEngine(shape_source.geometry().constGet())
            engine.prepareGeometry()

            for shape_relate in straight_layer.getFeatures():
                relate_id = shape_relate.id()
                if (source_id == relate_id) or (shape_source["SourceID"] != shape_relate["SourceID"]):
                    continue

                feature_helper_relate = feature_helper_dict[relate_id]
                intersect = engine.intersection(shape_relate.geometry().constGet())

                if intersect is None or intersect.isEmpty():
                    continue

                is_body = True
                for node1 in feature_helper_source.nodeList:
                    if check_point_point_intersection(node1.point, intersect):
                        is_body = False
                        is_found = False

                        for node in node_list:
                            if node.point == node1.point:
                                is_found = True
                                node.add_id(feature_helper_source.id)
                                node.add_id(feature_helper_relate.id)

                        if not is_found:
                            node = Node(-1, node1.point)
                            node.add_id(feature_helper_source.id)
                            node.add_id(feature_helper_relate.id)
                            node_list.append(node)

                if is_body:
                    for part in intersect.parts():
                        if part.geometryType() != "Point":
                            continue

                        is_found = False

                        for node in node_list:
                            if node.point == part:
                                is_found = True
                                node.add_id(feature_helper_source.id)
                                node.add_id(feature_helper_relate.id)

                        if not is_found:
                            node = Node(-1, part)
                            node.add_id(feature_helper_source.id)
                            node.add_id(feature_helper_relate.id)
                            node.relation_ids.append(-1)
                            node_list.append(node)

            # Relation with a node of original source feature
            shp = self.input_layer.getFeature(shape_source["SourceID"])
            if shp is None:
                continue

            geometry = shp.geometry()
            for part in geometry.parts():
                if part[0] == part[-1]:
                    for node in node_list:
                        if node.point == part[0]:
                            node.relation_ids.append(-1)

            self.progress.setValue(self.progress.value() + 1)

        for node in node_list:
            if len(node.relation_ids) >= self.relation_number:
                self.append_point_list(node.point)

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
