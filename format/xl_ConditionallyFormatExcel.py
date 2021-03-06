# Copyright(c) 2016, David Mans, Konrad Sobon
# @arch_laboratory, http://archi-lab.net, http://neoarchaic.net

import clr
import sys
import System
from System import Array
from System.Collections.Generic import *

clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Version=11.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
from Microsoft.Office.Interop import Excel
System.Threading.Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo("en-US")
from System.Runtime.InteropServices import Marshal

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
dynPath = appDataPath + r"\Dynamo\0.9"
if dynPath not in sys.path:
	sys.path.Add(dynPath)
	
bbPath = appDataPath + r"\Dynamo\0.9\packages\Bumblebee\extra"
if bbPath not in sys.path:
	try:
		sys.path.Add(bbPath)
		import bumblebee as bb
	except:
		import xml.etree.ElementTree as et
		root = et.parse(dynPath + "\DynamoSettings.xml").getroot()
		for child in root:
			if child.tag == "CustomPackageFolders":
				for path in child:
					if path not in sys.path:
						sys.path.Add(path)
		import bumblebee as bb
import string
import re

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN

filePath = IN[0]
runMe = IN[1]
sheetName = IN[2]
cellRange = IN[3]
formatConditions = IN[4]

def SetUp(xlApp):
	# supress updates and warning pop ups
	xlApp.Visible = False
	xlApp.DisplayAlerts = False
	xlApp.ScreenUpdating = False
	return xlApp

def CleanUp(_list):
	# clean up before exiting excel, if any COM object remains
	# unreleased then excel crashes on open following time
	if isinstance(_list, list):
		for i in _list:
			try:
				Marshal.ReleaseComObject(i)
			except:
				pass
	else:
		try:
			Marshal.ReleaseComObject(_list)
		except:
			pass
	return None

def ExitExcel(filePath, xlApp, wb, ws):
	# save any changes and clean up excel sessions
	wb.SaveAs(unicode(filePath))
	xlApp.ActiveWorkbook.Close(False)
	xlApp.ScreenUpdating = True
	CleanUp([ws,wb,xlApp])
	return None

def LiveStream():
	try:
		xlApp = Marshal.GetActiveObject("Excel.Application")
		xlApp.Visible = True
		xlApp.DisplayAlerts = False
		return xlApp
	except:
		return None

def ConditionFormatCells(origin, extent, ws, formatConditions):
	
	def AddFormatCondition(origin=None, extent=None, ws=None, formatConditions=None, index=None):
		fcType = formatConditions.FormatConditionType()
		if fcType == 1:
			operatorType = formatConditions.OperatorType()
			values = formatConditions.Values()
			if operatorType == 2 or operatorType == 1:
				ws.Range[origin, extent].FormatConditions.Add(fcType, operatorType, values[1], values[0])
			else:
				ws.Range[origin, extent].FormatConditions.Add(fcType, operatorType, values)
				
		if fcType == 2:
			operatorType = formatConditions.OperatorType()
			expression = formatConditions.Expression()
			ws.Range[origin, extent].FormatConditions.Add(fcType, operatorType, expression)
			
		if fcType == "2Color":
			ws.Range[origin, extent].FormatConditions.AddColorScale(ColorScaleType = 2)
		
		if fcType == "3Color":
			ws.Range[origin, extent].FormatConditions.AddColorScale(ColorScaleType = 3)
		
		if fcType == "TopPercentile":
			ws.Range[origin, extent].FormatConditions.AddTop10()
			if index == None:
				index = 1
			else:
				index = index + 1
			ws.Range[origin, extent].FormatConditions(index).Percent = formatConditions.Percent()
			ws.Range[origin, extent].FormatConditions(index).Rank = formatConditions.Rank()
			ws.Range[origin, extent].FormatConditions(index).TopBottom = formatConditions.TopBottom()

		if fcType == "DataBar":
			ws.Range[origin, extent].FormatConditions.AddDataBar()

		return ws
		
	def FormatGraphics(origin=None, extent=None, ws=None, formatConditions=None, index=None):
		if index == None:
			index = 1
		else:
			index = index + 1
			
		if formatConditions.FormatConditionType() == "2Color":
			ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(1).Type = formatConditions.MinType()
			ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(1).FormatColor.Color = formatConditions.MinColor()
			if formatConditions.MinType() != 1:
				ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(1).Value = formatConditions.MinValue()
			ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(2).Type = formatConditions.MaxType()
			ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(2).FormatColor.Color = formatConditions.MaxColor()
			if formatConditions.MaxType() != 2:
				ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(2).Value = formatConditions.MaxValue()
			
		elif formatConditions.FormatConditionType() == "3Color":
			# set min type/value/color
			ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(1).Type = formatConditions.MinType()
			ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(1).FormatColor.Color = formatConditions.MinColor()
			if formatConditions.MinType() != 1:
				ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(1).Value = formatConditions.MinValue()
			# set mid type/value/color
			ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(2).Type = formatConditions.MidType()
			ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(2).FormatColor.Color = formatConditions.MidColor()
			ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(2).Value = formatConditions.MidValue()
			# set max type/value/color
			ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(3).Type = formatConditions.MaxType()
			ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(3).FormatColor.Color = formatConditions.MaxColor()
			if formatConditions.MaxType() != 2:
				ws.Range[origin, extent].FormatConditions(index).ColorScaleCriteria(3).Value = formatConditions.MaxValue()
		
		elif formatConditions.FormatConditionType() == "DataBar":
			if formatConditions.MinType() != 1 and formatConditions.MinType() != 6:
				ws.Range[origin, extent].FormatConditions(index).MinPoint.Modify(newtype = formatConditions.MinType(), newvalue = formatConditions.MinValue())
			else:
				ws.Range[origin, extent].FormatConditions(index).MinPoint.Modify(newtype = formatConditions.MinType())
			if formatConditions.MaxType() != 2 and formatConditions.MaxType() != 7:
				ws.Range[origin, extent].FormatConditions(index).MaxPoint.Modify(newtype = formatConditions.MaxType(), newvalue = formatConditions.MaxValue())
			else:
				ws.Range[origin, extent].FormatConditions(index).MaxPoint.Modify(newtype = formatConditions.MaxType())
			
			if formatConditions.BorderColor() != None:
				ws.Range[origin, extent].FormatConditions(index).BarBorder.Type = 1
			else:
				ws.Range[origin, extent].FormatConditions(index).BarBorder.Type = 0
			ws.Range[origin, extent].FormatConditions(index).ShowValue = True
			ws.Range[origin, extent].FormatConditions(index).BarFillType = formatConditions.GradientFill()
			ws.Range[origin, extent].FormatConditions(index).BarColor.Color = formatConditions.FillColor()
			ws.Range[origin, extent].FormatConditions(index).BarBorder.Color.Color = formatConditions.BorderColor()
			ws.Range[origin, extent].FormatConditions(index).Direction = formatConditions.DirectionType()

		else:
			fillStyle = formatConditions.GraphicStyle().fillStyle
			textStyle = formatConditions.GraphicStyle().textStyle
			borderStyle = formatConditions.GraphicStyle().borderStyle
			
			if fillStyle.backgroundColor != None:
				ws.Range[origin, extent].FormatConditions(index).Interior.Color = fillStyle.BackgroundColor()
			if fillStyle.patternType != None:
				ws.Range[origin, extent].FormatConditions(index).Interior.Pattern = fillStyle.PatternType()
			if fillStyle.patternColor != None:
				ws.Range[origin, extent].FormatConditions(index).Interior.PatternColor = fillStyle.PatternColor()
			ws.Range[origin, extent].FormatConditions(index).StopIfTrue = False
		return ws

	ws.Range[origin, extent].FormatConditions.Delete()
	if not isinstance(formatConditions, list):
		AddFormatCondition(origin, extent, ws, formatConditions)
		FormatGraphics(origin, extent, ws, formatConditions, None)
	else:
		for index, value in enumerate(formatConditions):
			AddFormatCondition(origin, extent, ws, value)
			FormatGraphics(origin, extent, ws, value, index)
	return ws
	
if runMe:
	message = None
	try:
		errorReport = None
		message = "Success!"
		if filePath == None:
			# run excel in live mode
			xlApp = LiveStream()
			wb = xlApp.ActiveWorkbook
			if sheetName == None:
				ws = xlApp.ActiveSheet
			else:
				ws = xlApp.Sheets(sheetName)
			if not isinstance(cellRange, list):
				origin = ws.Cells(bb.xlRange(cellRange)[1], bb.xlRange(cellRange)[0])
				extent = ws.Cells(bb.xlRange(cellRange)[3], bb.xlRange(cellRange)[2])
				ConditionFormatCells(origin, extent, ws, formatConditions)
			else:
				for index, (range, format) in enumerate(zip(cellRange, formatConditions)):
					origin = ws.Cells(bb.xlRange(range)[1], bb.xlRange(range)[0])
					extent = ws.Cells(bb.xlRange(range)[3], bb.xlRange(range)[2])
					ConditionFormatCells(origin, extent, ws, format)
		else:
			try:
				xlApp = SetUp(Excel.ApplicationClass())		
				if os.path.isfile(unicode(filePath)):
					xlApp.Workbooks.open(unicode(filePath))
					wb = xlApp.ActiveWorkbook
					ws = xlApp.Sheets(sheetName)
					if not isinstance(cellRange, list):
						origin = ws.Cells(bb.xlRange(cellRange)[1], bb.xlRange(cellRange)[0])
						extent = ws.Cells(bb.xlRange(cellRange)[3], bb.xlRange(cellRange)[2])
						ConditionFormatCells(origin, extent, ws, formatConditions)
						Marshal.ReleaseComObject(extent)
						Marshal.ReleaseComObject(origin)
					else:
						for index, (range, format) in enumerate(zip(cellRange, formatConditions)):
							origin = ws.Cells(bb.xlRange(range)[1], bb.xlRange(range)[0])
							extent = ws.Cells(bb.xlRange(range)[3], bb.xlRange(range)[2])
							ConditionFormatCells(origin, extent, ws, format)
							Marshal.ReleaseComObject(extent)
							Marshal.ReleaseComObject(origin)
					ExitExcel(filePath, xlApp, wb, ws)
			except:
				xlApp.Quit()
				Marshal.ReleaseComObject(xlApp)
	except:
		# if error accurs anywhere in the process catch it
		import traceback
		errorReport = traceback.format_exc()
		pass
else:
	errorReport = None
	message = "Run Me is set to False. Please set \nto True if you wish to write data \nto Excel."

#Assign your output to the OUT variable
if errorReport == None:
	OUT = message
else:
	OUT = errorReport
