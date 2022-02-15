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
    QgsFeature
)


class DissolveRelatedCore:
    def __init__(self, inputLayer, fieldNames, outputLayerName):
        self.inputLayer = inputLayer
        self.fieldNames = fieldNames
        self.outputLayer = QgsVectorLayer(
            QgsWkbTypes.displayString(int(inputLayer.wkbType())) + "?index=yes",
            outputLayerName,
            "memory",
            crs=inputLayer.crs()
        )

    def copyFeatures(self):
        self.outputLayer.dataProvider().addAttributes(self.inputLayer.fields())

        features = []
        for feature in self.inputLayer.getFeatures():
            newFeature = QgsFeature()
            newFeature.setGeometry(feature.geometry())
            newFeature.setFields(feature.fields())

            for field in feature.fields():
                newFeature[field.name()] = feature[field.name()]

            features.append(newFeature)

        self.outputLayer.startEditing()
        self.outputLayer.dataProvider().addFeatures(features)
        self.outputLayer.commitChanges()

    def execute(self):
        self.copyFeatures()