# -*- coding: utf-8 -*-
"""
    This is the place, where dissolving algorithms resolve.
"""

from qgis.core import (
    QgsVectorLayer,
    QgsWkbTypes,
    QgsFeature
)


class DissolveSinglepartCore:
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