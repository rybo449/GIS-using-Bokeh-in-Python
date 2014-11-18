import csv
import shapefile
import sys
import math
import operator
from bokeh.plotting import *
from bokeh.sampledata.iris import flowers
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import random
from bokeh.objects import HoverTool
from collections import OrderedDict
from math import floor

agencyDict = {}



def loadComplaints(complaintsFilename):
  # Reads all complaints and keeps zips which have complaints.
  with open(complaintsFilename) as f:
    csvReader = csv.reader(f)
    headers = csvReader.next()
    zipIndex = headers.index('Incident Zip')
    latColIndex = headers.index('Latitude')
    lngColIndex = headers.index('Longitude')
    agencyIndex = headers.index('Agency')

    lat = []
    lng = []  
    
    #agencyDict = {}
    colors = []
    complaintsPerZip = {}

    for row in csvReader:
      try:
        lat.append(float(row[latColIndex]))
        lng.append(float(row[lngColIndex]))
        agency = row[agencyIndex]
        zipCode = row[zipIndex]
        if not agency in agencyDict:          
          agencyDict[agency] = len(agencyDict)


        if zipCode in complaintsPerZip:
          if agency in complaintsPerZip[zipCode]:
            complaintsPerZip[zipCode][agency]+=1
          else:
            complaintsPerZip[zipCode][agency]=1
        else:
          complaintsPerZip[zipCode]={}
          complaintsPerZip[zipCode][agency]=1

      except:
        pass

    return {'zip_complaints': complaintsPerZip}


def getZipBorough(zipBoroughFilename):
  # Reads all complaints and keeps zips which have complaints.
  with open(zipBoroughFilename) as f:
    csvReader = csv.reader(f)
    csvReader.next()

    return {row[0]: row[1] for row in csvReader}
  

def drawPlot(shapeFilename, mapPoints, zipBorough, agency1, agency2):
  # Read the ShapeFile
  dat = shapefile.Reader(shapeFilename)
  
  # Creates a dictionary for zip: {lat_list: [], lng_list: []}.
  zipCodes = []
  polygons = {'lat_list': [], 'lng_list': [], 'color_list' : [],'top_agency': [], 'zip_code': [], 'bin_ratio':[]}
  compare = {agency1:0,agency2:0}
  # Qualitative 6-class Set1
  colors_palate = ['#8c510a','#bf812d','#dfc27d','#f6e8c3','#f5f5f5','#c7eae5','#80cdc1','#35978f','#01665e','#26466d']
  bin_construction= ['0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5', '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9','0.9-1.0']
  bins = 0.1

  
  record_index = 0
  for r in dat.iterRecords():
    currentZip = r[0]

    # Keeps only zip codes in NY area.
    if currentZip in zipBorough:
      zipCodes.append(currentZip)

      # Gets shape for this zip.
      shape = dat.shapeRecord(record_index).shape
      points = shape.points

      # Breaks into lists for lat/lng.
      lngs = [p[0] for p in points]
      lats = [p[1] for p in points]

      # Stores lat/lng for current zip shape.
      polygons['lng_list'].append(lngs)
      polygons['lat_list'].append(lats)


      # Calculate color, according to number of complaints
      if currentZip in mapPoints['zip_complaints']:


        color = str()
        bin_ratio = 1
        #ratio = float(1000)
        if agency1 in mapPoints['zip_complaints'][currentZip].keys() and agency2 in mapPoints['zip_complaints'][currentZip].keys():
          #if mapPoints['zip_complaints'][currentZip][agency2] != 0:
          ratio = mapPoints['zip_complaints'][currentZip][agency1]/((mapPoints['zip_complaints'][currentZip][agency2]+mapPoints['zip_complaints'][currentZip][agency1])*1.0)
          #elif mapPoints['zip_complaints'][currentZip][agency2] == 0:
            #ratio = float('inf')
          #else: 
          #color = 'white'
        if color != 'white':
          #if ratio != 'inf':
          bin_ratio = int(floor(ratio//bins))
            #if bin_ratio >= 8:
            #bin_ratio = 8
          #else:
          #bin_ratio = 8
          color = colors_palate[bin_ratio]
      else:
        color = 'white'


      polygons['zip_code'].append(currentZip)
      polygons['color_list'].append(color)
      polygons['bin_ratio'].append(bin_construction[bin_ratio])

    record_index += 1


  # Creates the Plot
  output_file("problem2.html", title="Ratio of %s to %s"%(agency1, agency2))
  hold()
  source = ColumnDataSource(data = dict(x = polygons['lat_list'], y =polygons['lng_list'], zip_code = polygons['zip_code'], colors = polygons['color_list']))
  TOOLS="pan,wheel_zoom,box_zoom,reset,previewsave,hover"

  # Creates the polygons.

  patches(polygons['lng_list'], polygons['lat_list'], \
        fill_color=polygons['color_list'], line_color="gray", \
        source = source,\
        tools=TOOLS, plot_width=900, plot_height=700, \
        title="Ratio of %s to %s"%(agency1, agency2))
  for i in xrange(len(polygons['lat_list'])):
    scatter(0,0, color = polygons['color_list'][i], legend = polygons['bin_ratio'][i])
  
  #hover = curplot().select(dict(type = HoverTool))

  #hover.tooltips = OrderedDict([("Zip Code",'@zip_code'),("color","$color")])
                  
  show()


if __name__ == '__main__':

  mapPoints = loadComplaints(sys.argv[1])
  zipBorough = getZipBorough(sys.argv[2])
  drawPlot(sys.argv[3], mapPoints, zipBorough, sys.argv[4], sys.argv[5])
