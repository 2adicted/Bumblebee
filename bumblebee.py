"""
Copyright(c) 2015, Konrad Sobon
@arch_laboratory, http://archi-lab.net

Copyright (c) 2015, David Mans
http://neoarchaic.net

Excel and Dynamo interop library

"""
import clr
import sys
sys.path.append(r"C:\Program Files\Dynamo 0.8")
clr.AddReference('ProtoGeometry')

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import System
from System import Array
from System.Collections.Generic import *
import Autodesk.DesignScript as ds

clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Version=11.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
from Microsoft.Office.Interop import Excel

System.Threading.Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo("en-US")
from System.Runtime.InteropServices import Marshal

import string
import re

""" Misc Functions """
def ProcessList(_func, _list):
    return map( lambda x: ProcessList(_func, x) if type(x)==list else _func(x), _list )

def ListDepth(_list):
	func = lambda x: isinstance(x, list) and max(map(func, x))+1
	return func(_list)

""" Misc Definitions"""

def ConvertNumber(num):
    letters = ''
    while num:
	    mod = num % 26
	    num = num // 26
	    letters += chr(mod + 64)
    return ''.join(reversed(letters))

def ConvertChar(char):
    number =- 25
    for l in char:
	    if not l in string.ascii_letters:
		    return False
	    number += ord(l.upper()) - 64 + 25
    return int(number)

def CellIndex(cellAddress):
    match = re.match(r"([a-z]+)([0-9]+)", cellAddress, re.I)
    if match:
        addressItems = match.groups()
        row = ConvertChar(addressItems[0])
        column = int(addressItems[1])
    return [row, column]

def xlRange(address):
    originAddress = address.split(":")[0]
    extentAddress = address.split(":")[1]
    originRow = int(CellIndex(originAddress)[0])
    originCol = int(CellIndex(originAddress)[1])
    extentRow = int(CellIndex(extentAddress)[0])
    extentCol = int(CellIndex(extentAddress)[1])
    return [originRow, originCol, extentRow, extentCol]

def RGBToRGBLong(rgb):
    strValue = '%02x%02x%02x' % rgb
    iValue = int(strValue, 16)
    return iValue

def MakeDataObject(sheetName=None, origin=None, data=None):
	dataObject = BBData()
	if sheetName != None:
		dataObject.sheetName = sheetName
	if origin != None:
		dataObject.origin = origin
	if data != None:
		dataObject.data = data
	return dataObject

""" Type Enumerators """
"""
def GetPatternType(key):
    keys = ["xlCheckerBoard", "xlCrissCross", "xlDarkDiagonalDown", "xlGrey16", "xlGray25", 
	    "xlGray50", "xlGray75", "xlGray8", "xlGrid", "xlDarkHorizontal", 
	    "xlLightDiagonalDown", "xlLightHorizontal", "xlLightDiagonalUp", "xlLightVertical", "xlNone", 
	    "xlSemiGray75", "xlSolid", "xlDarkDiagonalUp", "xlDarkVertical"]
    values = [9, 16, -4121, 17, -4124, -4124, -4126, 18, 15, -4128, 13, 11, 14, 12, -4142, 10, 1, -4162, -4166]
    d = dict()
    for i in range(len(keys)):
	    d[keys[i]] = values[i]
    if key in d:
	    return d[key]
    else:
	    return None

def GetLabelPositionType(key):
    keys = ["Above", "Below", "BestFit", "Center", "Custom", "InsideBase", "InsideEnd", "Left", "Mixed", "OutsideEnd", "Right"]
    values = [0, 1, 5, -4108, 7, 4, 3, -4131, 6, 2, -4152]
    d = dict()
    for i in range(len(keys)):
        d[keys[i]] = values[i]
    if key in d:
	return d[key]
    else:
	return None

def GetTextHorJustType(key):
    keys = ["Left", "Center", "Right"]
    values = [-4131, -4108, -4152]
    d = dict()
    for i in range(len(keys)):
        d[keys[i]] = values[i]
    if key in d:
	return d[key]
    else:
	return None

def GetTextVerJustType(key):
    keys = ["Bottom", "Center", "Top"]
    values = [-4017, -4108, -4160]
    d = dict()
    for i in range(len(keys)):
        d[keys[i]] = values[i]
    if key in d:
	return d[key]
    else:
	return None

def GetLineType(key):
    keys = ["Continuous", "Dash", "DashDot", "DashDotDot", "RoundDot", "SquareDotMSO", "LongDash", "DoubleXL", "NoneXL"]
    values = [1, -4115, 4, 5, -4118, -4118, -4115, -4119, -4142]
    d = dict()
    for i in range(len(keys)):
        d[keys[i]] = values[i]
    if key in d:
	return d[key]
    else:
	return None

def GetLineWeight(key):
    keys = ["Hairline", "Medium", "Thick", "Thin"]
    values = [1, -4138, 4, 2]
    d = dict()
    for i in range(len(keys)):
        d[keys[i]] = values[i]
    if key in d:
	return d[key]
    else:
	return None

def GetOperatorType(key):
    keys = ["Equal", "NotEqual", "Greater", "GreaterEqual", "Less", "LessEqual", "Between", "NotBetween"]
    values = [3, 4, 5, 7, 6, 8, 1, 2]
    d = dict()
    for i in range(len(keys)):
        d[keys[i]] = values[i]
    if key in d:
	return d[key]
    else:
	return None

def GetLegendPosition(key):
    keys = ["Bottom", "Upper Right Corner", "Custom", "Left", "Right", "Top"]
    values = [-4107, 2, -4161, -4131, -4152, -4160]
    d = dict()
    for i in range(len(keys)):
        d[keys[i]] = values[i]
    if key in d:
	return d[key]
    else:
	return None

def GetPieChartType(key):
    keys = ["3dPie", "3dPieExploded", "Pie", "PieExploded"]
    values = [-4102, 70, 5, 69]
    d = dict()
    for i in range(len(keys)):
        d[keys[i]] = values[i]
    if key in d:
	return d[key]
    else:
	return None

def GetLineChartType(key):
    keys = ["Line", "LineStacked", "LineStacked100", "3dLine"]
    values = [4, 63, 64, -4101]
    d = dict()
    for i in range(len(keys)):
        d[keys[i]] = values[i]
    if key in d:
	return d[key]
    else:
	return None

def GetDirectionType(key):
    keys = ["LeftToRight", "RightToLeft", "Context"]
    values = [-5003, -5004, -5002]
    d = dict()
    for i in range(len(keys)):
        d[keys[i]] = values[i]
    if key in d:
	return d[key]
    else:
	return None

def GetColorScaleCriteriaType(key):
    keys = ["LowestValue", "Number", "Percent", "Formula", "Percentile", "HighestValue", "AutomaticMax", "AutomaticMin", "None"]
    values = [1, 0, 3, 4, 5, 2, 7, 6, -1]
    d = dict()
    for i in range(len(keys)):
        d[keys[i]] = values[i]
    if key in d:
	return d[key]
    else:
	return None
"""
""" Styles classes """

class BBFillStyle(object):

    def __init__(self, patternType=None, backgroundColor=None, patternColor=None):
        self.patternType = patternType
        self.backgroundColor = backgroundColor
        self.patternColor = patternColor
    def PatternType(self):
        if self.patternType == None:
            return None
        else:
            return self.patternType
    def BackgroundColor(self):
        if self.backgroundColor == None:
            return None
        else:
            return RGBToRGBLong((self.backgroundColor.Blue, self.backgroundColor.Green, self.backgroundColor.Red))
    def PatternColor(self):
        if self.patternColor == None:
            return None
        else:
            return RGBToRGBLong((self.patternColor.Blue, self.patternColor.Green, self.patternColor.Red))

class BBTextStyle(object):

    def __init__(self, name=None, size=None, color=None, horizontalAlign=None, verticalAlign=None, bold=None, italic=None, underline=None, strikethrough=None):
        self.name = name
        self.size = size
        self.color = color
        self.horizontalAlign = horizontalAlign
        self.verticalAlign = verticalAlign
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough
    def Name(self):
        if self.name == None:
            return None
        else:
            return self.name
    def Size(self):
        if self.size == None:
            return None
        else:
            return self.size
    def Color(self):
        if self.color == None:
            return None
        else:
            return RGBToRGBLong((self.color.Blue, self.color.Green, self.color.Red))
    def HorizontalAlign(self):
        if self.horizontalAlign == None:
            return None
        else:
            return self.horizontalAlign
    def VerticalAlign(self):
        if self.verticalAlign == None:
            return None
        else:
            return self.verticalAlign
    def Bold(self):
        if self.bold == None:
            return None
        else:
            return self.bold
    def Italic(self):
        if self.italic == None:
            return None
        else:
            return self.italic
    def Underline(self):
        if self.underline == None:
            return None
        else:
            return self.underline
    def Strikethrough(self):
        if self.strikethrough == None:
            return None
        else:
            return self.strikethrough

class BBBorderStyle(object):

    def __init__(self, lineType=None, weight=None, color=None):
        self.lineType = lineType
        self.weight = weight
        self.color = color
    def LineType(self):
        if self.lineType == None:
            return None
        else:
            return self.lineType
    def Weight(self):
        if self.weight == None:
            return None
        else:
            return self.weight
    def Color(self):
        if self.color == None:
            return None
        else:
            return RGBToRGBLong((self.color.Blue, self.color.Green, self.color.Red)) 

class BBGraphicStyle(object):

    def __init__(self, fillStyle=None, textStyle=None, borderStyle=None):
        self.fillStyle = fillStyle
        self.textStyle = textStyle
        self.borderStyle = borderStyle

class BBLegendStyle(object):

    def __init__(self, fillStyle=None, textStyle=None, borderStyle=None, position=None, labels=None):
        self.fillStyle = fillStyle
        self.textStyle = textStyle
        self.borderStyle = borderStyle
        self.position = position
        self.labels = labels
    def Position(self):
        if self.position != None:
            return self.position
        else:
            return None
    def Labels(self):
        if self.labels != None:
            return xlRange(self.labels)
        else:
            return None

class BBChartStyle(object):

    def __init__(self, fillStyle=None, textStyle=None, borderStyle=None, roundCorners=None):
        self.fillStyle = fillStyle
        self.textStyle = textStyle
        self.borderStyle = borderStyle
        self.roundCorners = roundCorners
    def RoundCorners(self):
        if self.roundCorners != None:
            return self.roundCorners
        else:
            return None

class BBGraphStyle(object):

    def __init__(self, fillStyle=None, textStyle=None, borderStyle=None, labelStyle=None, explosion=None):
        self.fillStyle = fillStyle
        self.textStyle = textStyle
        self.borderStyle = borderStyle
        self.labelStyle = labelStyle
        self.explosion = explosion
    def Explosion(self):
        if self.explosion != None:
            return self.explosion
        else:
            return None

class BBLabelStyle(object):

    def __init__(self, fillStyle=None, textStyle=None, borderStyle=None, seriesName=None, value=None, percentage=None, leaderLines=None, legendKey=None, separator=None, labelPosition=None):
        self.fillStyle = fillStyle
        self.textStyle = textStyle
        self.borderStyle = borderStyle
        self.seriesName = seriesName
        self.value = value
        self.percentage = percentage
        self.leaderLines = leaderLines
        self.legendKey = legendKey
        self.separator = separator
        self.labelPosition = labelPosition
    def SeriesName(self):
        if self.seriesName == None:
            return None
        else:
            return self.seriesName
    def Value(self):
        if self.value == None:
            return None
        else:
            return self.value
    def Percentage(self):
        if self.percentage == None:
            return None
        else:
            return self.percentage
    def LeaderLines(self):
        if self.leaderLines == None:
            return None
        else:
            return self.leaderLines
    def LegendKey(self):
        if self.legendKey == None:
            return None
        else:
            return self.legendKey
    def Separator(self):
        if self.separator == None:
            return None
        else:
            return self.separator
    def LabelPosition(self):
        if self.labelPosition == None:
            return None
        else:
            return self.labelPosition

""" Conditional Formatting Classes """

class BBCellValueFormatCondition(object):

    def __init__(self, formatConditionType=1, operatorType=None, values=None, graphicStyle=None):
        self.formatConditionType = formatConditionType
        self.operatorType = operatorType
        self.values = values
        self.graphicStyle = graphicStyle
    def FormatConditionType(self):
        return  self.formatConditionType
    def OperatorType(self):
        if self.operatorType == None:
            return None
        else:
            return self.operatorType
    def Values(self):
        if self.values == None:
            return None
        else:
            return self.values
    def GraphicStyle(self):
        if self.graphicStyle == None:
            return None
        else:
            return self.graphicStyle

class BBExpressionFormatCondition(object):

    def __init__(self, formatConditionType=2, operatorType=-4142, expression=None, graphicStyle=None):
        self.formatConditionType = formatConditionType
        self.operatorType = operatorType
        self.expression = expression
        self.graphicStyle = graphicStyle
    def FormatConditionType(self):
        return self.formatConditionType
    def OperatorType(self):
        return self.operatorType
    def Expression(self):
        if self.expression == None:
            return None
        else:
            return self.expression
    def GraphicStyle(self):
        if self.graphicStyle == None:
            return None
        else:
            return self.graphicStyle

class BB2ColorScaleFormatCondition(object):

    def __init__(self, formatConditionType="2Color", minType=None, minValue=None, minColor=None, maxType=None, maxValue=None, maxColor=None):
        self.formatConditionType = formatConditionType
        self.minType = minType
        self.minValue = minValue
        self.minColor = minColor
        self.maxType = maxType
        self.maxValue = maxValue
        self.maxColor = maxColor
    def FormatConditionType(self):
        return self.formatConditionType
    def MinType(self):
        if self.minType == None:
            return None
        else:
            return self.minType
    def MinValue(self):
        if self.minValue == None:
            return None
        else:
            return self.minValue
    def MinColor(self):
        if self.minColor == None:
            return None
        else:
            return RGBToRGBLong((self.minColor.Blue, self.minColor.Green, self.minColor.Red))
    def MaxType(self):
        if self.maxType == None:
            return None
        else:
            return self.maxType
    def MaxValue(self):
        if self.maxValue == None:
            return None
        else:
            return self.maxValue
    def MaxColor(self):
        if self.maxColor == None:
            return None
        else:
            return RGBToRGBLong((self.maxColor.Blue, self.maxColor.Green, self.maxColor.Red))

class BB3ColorScaleFormatCondition(object):

    def __init__(self, formatConditionType="3Color", minType=None, minValue=None, minColor=None, midType=None, midValue=None, midColor=None, maxType=None, maxValue=None, maxColor=None):
        self.formatConditionType = formatConditionType
        self.minType = minType
        self.minValue = minValue
        self.minColor = minColor
        self.midType = midType
        self.midValue = midValue
        self.midColor = midColor
        self.maxType = maxType
        self.maxValue = maxValue
        self.maxColor = maxColor
    def FormatConditionType(self):
        return self.formatConditionType
    def MinType(self):
        if self.minType == None:
            return None
        else:
            return self.minType
    def MinValue(self):
        if self.minValue == None:
            return None
        else:
            return self.minValue
    def MinColor(self):
        if self.minColor == None:
            return None
        else:
            return RGBToRGBLong((self.minColor.Blue, self.minColor.Green, self.minColor.Red))
    def MidType(self):
        if self.midType == None:
            return None
        else:
            return self.midType
    def MidValue(self):
        if self.midValue == None:
            return None
        else:
            return self.midValue
    def MidColor(self):
        if self.midColor == None:
            return None
        else:
            return RGBToRGBLong((self.midColor.Blue, self.midColor.Green, self.midColor.Red))
    def MaxType(self):
        if self.maxType == None:
            return None
        else:
            return self.maxType
    def MaxValue(self):
        if self.maxValue == None:
            return None
        else:
            return self.maxValue
    def MaxColor(self):
        if self.maxColor == None:
            return None
        else:
            return RGBToRGBLong((self.maxColor.Blue, self.maxColor.Green, self.maxColor.Red))

class BBTopPercentileFormatCondition(object):

    def __init__(self, formatConditionType="TopPercentile", percent=None, rank=None, topBottom=None, graphicStyle=None):
        self.formatConditionType = formatConditionType
        self.percent = percent
        self.rank = rank
        self.topBottom = topBottom
        self.graphicStyle = graphicStyle
    def FormatConditionType(self):
        return self.formatConditionType
    def Percent(self):
        if self.percent == None:
            return None
        else:
            return self.percent
    def Rank(self):
        if self.rank == None:
            return None
        else:
            return self.rank
    def TopBottom(self):
        if self.topBottom == None:
            return None
        else:
            if self.topBottom == True:
                return 1
            else:
                return 0
    def GraphicStyle(self):
        if self.graphicStyle == None:
            return None
        else:
            return self.graphicStyle

class BBDataBarFormatCondition(object):

    def __init__(self, formatConditionType="DataBar", minType=None, minValue=None, maxType=None, maxValue=None, directionType=None, gradientFill=None, fillColor=None, borderColor=None):
        self.formatConditionType = formatConditionType
        self.minType = minType
        self.minValue = minValue
        self.maxType = maxType
        self.maxValue = maxValue
        self.directionType = directionType
        self.gradientFill = gradientFill
        self.fillColor = fillColor
        self.borderColor = borderColor
    def FormatConditionType(self):
        return self.formatConditionType
    def MinType(self):
        if self.minType == None:
            return None
        else:
            return self.minType
    def MinValue(self):
        if self.minValue == None:
            return None
        else:
            return self.minValue
    def MaxType(self):
        if self.maxType == None:
            return None
        else:
            return self.maxType
    def MaxValue(self):
        if self.maxValue == None:
            return None
        else:
            return self.maxValue
    def DirectionType(self):
        if self.directionType == None:
            return None
        else:
            return self.directionType
    def GradientFill(self):
        if self.gradientFill == None:
            return None
        else:
            if self.gradientFill == True:
                return 1
            else:
                return 0
    def FillColor(self):
        if self.fillColor == None:
            return None
        else:
            return RGBToRGBLong((self.fillColor.Blue, self.fillColor.Green, self.fillColor.Red))
    def BorderColor(self):
        if self.borderColor == None:
            return None
        else:
            return RGBToRGBLong((self.borderColor.Blue, self.borderColor.Green, self.borderColor.Red))

""" Data Classes """

class BBData(object):

    def __init__(self, sheetName=None, origin=None, data=None):
        self.sheetName = sheetName
        self.origin = origin
        self.data = data
    def Depth(self):
        return ListDepth(self.data)
    def SheetName(self):
        if self.sheetName == None:
            return None
        else:
            return self.sheetName
    def Origin(self):
        if self.origin == None:
            return None
        else:
            return CellIndex(self.origin)
    def Data(self):
        if self.data == None:
            return None
        else:
            return self.data
