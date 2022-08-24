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