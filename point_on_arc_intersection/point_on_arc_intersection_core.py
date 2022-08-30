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
    def __init__(self, input_layer, output_layer_name, algorithm_list):
        self.input_layer = input_layer
        self.output_layer_name = output_layer_name
        self.algorithm_list = algorithm_list
        self.output_layer = QgsVectorLayer(
            "Point?index=yes",
            output_layer_name,
            "memory",
            crs=input_layer.crs()
        )

    def execute(self):
        pass

