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
  

def drawPlot(shapeFilename, mapPoints, zipBorough):
  # Read the ShapeFile
  dat = shapefile.Reader(shapeFilename)
  
  # Creates a dictionary for zip: {lat_list: [], lng_list: []}.
  zipCodes = []
  polygons = {'lat_list': [], 'lng_list': [], 'color_list' : [],'top_agency': [], 'zip_code': [], 'number_of_complaints':[]}

  # Qualitative 6-class Set1
  colors = {}
  
  for j, i in enumerate(agencyDict.keys()):
    r = lambda: random.randint(0,255)
    colors[i] = ('#%02X%02X%02X'%(r(),0,r()))
  #print colors
  
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

        # Top complaint type
        sortedlist = sorted(mapPoints['zip_complaints'][currentZip].items(), key=operator.itemgetter(1), reverse=True)
        agency = sortedlist[0][0]
        #print agency
        #print currentZip, agency

        if agency in colors:
          color = colors[agency]
        else:
          color = 'white'

      else:
        color = 'white'
      polygons['number_of_complaints'].append(sortedlist[0][1])
      polygons['top_agency'].append(agency)
      polygons['zip_code'].append(currentZip)
      polygons['color_list'].append(color)
      #print polygons['number_of_complaints']

    record_index += 1


  # Creates the Plot
  color_set = list(set(polygons['color_list']))
  output_file("problem1.html", title="Highest Complaints by Agency in Zip Code")
  hold()
  source = ColumnDataSource(data = dict(x = polygons['lat_list'], y =polygons['lng_list'], zip_code = polygons['zip_code'], top_agency = polygons['top_agency'], number_of_complaints = polygons['number_of_complaints'], colors = polygons['color_list']))
  TOOLS="pan,wheel_zoom,box_zoom,reset,previewsave,hover"

  # Creates the polygons.

  patches(polygons['lng_list'], polygons['lat_list'], \
        fill_color=polygons['color_list'], line_color="gray", \
        source = source,\
        tools=TOOLS, plot_width=1100, plot_height=700, \
        #legend = polygons['top_agency'][0],\
        title="Highest Complaints by Agency in Zip Code")
  for i in xrange(len(polygons['lat_list'])):
    scatter(0,0, color = polygons['color_list'][i], legend = polygons['top_agency'][i])


  hover = curplot().select(dict(type = HoverTool))

  hover.tooltips = OrderedDict([("Zip Code",'@zip_code'),("Top Agency",'@top_agency'),("Number of Complaints",'@number_of_complaints')])
                  
  show()


if __name__ == '__main__':
  if len(sys.argv) != 4:
    print 'Usage:'
    print sys.argv[0] \
    + ' <shapefilename> <complaintsfilename> <zipboroughfilename>'
    print '\ne.g.: ' + sys.argv[0] \
    + ' data/nyshape.shp data/complaints.csv zip_borough.csv'
  else:
    mapPoints = loadComplaints(sys.argv[1])
    zipBorough = getZipBorough(sys.argv[2])
    drawPlot(sys.argv[3], mapPoints, zipBorough)
