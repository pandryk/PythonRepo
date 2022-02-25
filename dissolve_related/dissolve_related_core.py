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


class DissolveRelatedCore:
    def __init__(self, inputLayer, fieldNames, outputLayerName):
        self.inputLayer = inputLayer
        self.fieldNames = fieldNames
        self.relationsDict = {}
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

    def getKey(self, relatedID):
        for key in self.relationsDict.keys():
            if relatedID in self.relationsDict[key]:
                return key

    def isInRelation(self, id1, id2):
        if ((id1 in self.relationsDict.keys()) and (id2 in self.relationsDict[id1])) or \
                ((id2 in self.relationsDict.keys()) and (id1 in self.relationsDict[id2])):
            return True
        else:
            for key in self.relationsDict.keys():
                if (id1 in self.relationsDict[key]) and (id2 in self.relationsDict[key]):
                    return True
            return False

    def getDictKeyValueList(self):
        resultList = []
        try:
            if len(self.relationsDict) == 0:
                return

            for key in self.relationsDict.keys():
                resultList.append(key)
                for item in self.relationsDict[key]:
                    resultList.append(item)
        finally:
            return resultList

    def getRelations(self):
        for shapeSource in self.outputLayer.getFeatures():
            sourceID = shapeSource.id()
            engine = QgsGeometry.createGeometryEngine(shapeSource.geometry().constGet())
            engine.prepareGeometry()

            for shapeRelate in self.outputLayer.getFeatures():
                relateID = shapeRelate.id()
                if (sourceID == relateID) or (self.isInRelation(sourceID, relateID)):
                    continue

                # If intersected
                if engine.intersects(shapeRelate.geometry().constGet()):
                    totalUsedList = self.getDictKeyValueList()

                    # If source is not used
                    if sourceID not in totalUsedList:
                        # If related is not used, create new relation
                        if relateID not in totalUsedList:
                            self.relationsDict[sourceID] = [relateID]
                        # If related is used as source, append source as related
                        elif relateID in self.relationsDict.keys():
                            self.relationsDict[relateID].append(sourceID)
                        # If related is used in other relation, append source as related to that relation
                        else:
                            self.relationsDict[self.getKey(relateID)].append(sourceID)
                    # If source used as source
                    elif sourceID in self.relationsDict.keys():
                        # If related is not used, append to source
                        if relateID not in totalUsedList:
                            self.relationsDict[sourceID].append(relateID)
                        # If related is used as source, append related with its relation
                        elif relateID in self.relationsDict.keys():
                            self.relationsDict[sourceID] = self.relationsDict[sourceID] + \
                                self.relationsDict[relateID] + \
                                [relateID]
                            self.relationsDict.pop(relateID)
                        # If related used as related, append parent of its relation
                        else:
                            relateParentID = self.getKey(relateID)
                            self.relationsDict[sourceID] = self.relationsDict[sourceID] + \
                                self.relationsDict[relateParentID] + \
                                [relateParentID]
                            self.relationsDict.pop(relateParentID)
                    # If source is used as related
                    else:
                        # If related is not used, append to parent of source
                        if relateID not in totalUsedList:
                            self.relationsDict[self.getKey(sourceID)].append(relateID)
                        # If related is used as source, append parent of source with its relation
                        elif relateID in self.relationsDict.keys():
                            sourceParentID = self.getKey(sourceID)
                            self.relationsDict[relateID] = self.relationsDict[relateID] + \
                                self.relationsDict[sourceParentID] + \
                                [sourceParentID]
                            self.relationsDict.pop(sourceParentID)
                        # If related is used as related, append parent of source with its relation to that relation
                        else:
                            sourceParentID = self.getKey(sourceID)
                            relateParentID = self.getKey(relateID)
                            self.relationsDict[relateParentID] = \
                                self.relationsDict[relateParentID] + \
                                self.relationsDict[sourceParentID] + \
                                [sourceParentID]
                            self.relationsDict.pop(sourceParentID)

    def createFeature(self, geometry):
        feature = QgsFeature(self.outputLayer.fields())
        if feature is None:
            return

        feature.setGeometry(geometry)
        return feature

    def dissolveFeatures(self):
        newFeaturesList = []
        self.outputLayer.beginEditCommand("Dissolving features...")
        try:
            for key in self.relationsDict.keys():
                sourceGeometry = self.outputLayer.getGeometry(key)
                if sourceGeometry is None:
                    continue

                relatedGeometryList = [sourceGeometry]

                for relatedID in self.relationsDict[key]:
                    relatedGeometry = self.outputLayer.getGeometry(relatedID)
                    if relatedGeometry is None:
                        continue

                    relatedGeometryList.append(relatedGeometry)

                engine = QgsGeometry.createGeometryEngine(sourceGeometry.constGet())
                engine.prepareGeometry()
                newGeometry = engine.combine(relatedGeometryList)
                if newGeometry is None:
                    continue

                newFeature = self.createFeature(newGeometry)
                if newFeature is None:
                    continue

                newFeaturesList.append(newFeature)
            self.outputLayer.dataProvider().deleteFeatures(self.getDictKeyValueList())
            self.outputLayer.dataProvider().addFeatures(newFeaturesList)
        finally:
            self.outputLayer.commitChanges()

    def execute(self):
        self.copyFeatures()
        self.getRelations()
        self.dissolveFeatures()