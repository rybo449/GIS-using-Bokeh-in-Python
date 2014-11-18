import csv
import shapefile
import sys
import math
import operator
from bokeh.plotting import *
from bokeh.sampledata.iris import flowers
from bokeh.objects import HoverTool
from collections import OrderedDict

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
	
		colors = []
		complaintsPerZip = {}

		for row in csvReader:
			try:
				lat.append(float(row[latColIndex]))
				lng.append(float(row[lngColIndex]))
				zipCode = row[zipIndex]
	  
				if zipCode in complaintsPerZip:
					complaintsPerZip[zipCode]+=1
				else:
					complaintsPerZip[zipCode]=1

			except:
				pass

		#print "complaintsPerZip: ", complaintsPerZip

	return {'zip_complaints': complaintsPerZip}


# In[9]:

def getZipBorough(zipBoroughFilename):
	# Reads all complaints and keeps zips which have complaints.
	with open(zipBoroughFilename) as f:
		csvReader = csv.reader(f)
		csvReader.next()

		return {row[0]: row[1] for row in csvReader}


# In[15]:

def drawPlot(shapeFilename, mapPoints, zipBorough):
	# Read the ShapeFile
	dat = shapefile.Reader(shapeFilename)
  
	# Creates a dictionary for zip: {lat_list: [], lng_list: []}.
	zipCodes = []
	polygons = {'lat_list': [], 'lng_list': [], 'color_list' : [], 'centerlat_list' : [] ,'centerlng_list' : [], 'radius_list' : []}

	
	# Top complaint number total
	sortedlist = sorted(mapPoints['zip_complaints'].items(), key=operator.itemgetter(1), reverse=True)
	complaintsHighestTotal = sortedlist[0][1]

	minRadius=0.00015
	maxRadius=0.015

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


			# Calculate circle radius, according to number of complaints
			if currentZip in mapPoints['zip_complaints']:
				compCount = mapPoints['zip_complaints'][currentZip]
				
				
				percentage = float(compCount)/float(complaintsHighestTotal)
				
				relRadius = (maxRadius-minRadius)*percentage
				
				color = 'white'
			else:
				color = 'grey'
				compCount = 0
				relRadius = 0
				
				
			# we try to find the center of polygon
			lngmiddle = min(lngs)+((max(lngs)-min(lngs))/2)
			latmiddle = min(lats)+((max(lats)-min(lats))/2)


			polygons['color_list'].append(color)
			
			polygons['centerlat_list'].append(latmiddle)
			polygons['centerlng_list'].append(lngmiddle)
			polygons['radius_list'].append(relRadius)

		record_index += 1



	# Creates the Plot
	titleString = "Zip Code Based Complaints"
	
	output_file("problem3.html", title=titleString)
  
	TOOLS="pan,wheel_zoom,box_zoom,reset,previewsave"
	
	# Creates the polygons.
	patches(polygons['lng_list'], polygons['lat_list'], fill_color=polygons['color_list'], line_color="gray", tools=TOOLS, plot_width=1100, plot_height=700,			  title=titleString)
				  
	
	hold()
 
	
	circle(polygons['centerlng_list'], polygons['centerlat_list'], radius=polygons['radius_list'], 
		fill_color='green', fill_alpha=0.5, line_color=None)
	
	
		
	show()



# In[6]:

if __name__ == '__main__':
	if len(sys.argv) != 4:
		print 'Usage:'
		print sys.argv[0] \
		+ ' <shapefilename> <complaintsfilename> <zipboroughfilename>'
		print '\ne.g.: ' + sys.argv[0] \
		+ ' data/nyshape.shp data/complaints.csv zip_borough.csv'
	else:
		
		complaintsFile = sys.argv[1]
		zipBoroughsFile = sys.argv[2]
		shapeFile = sys.argv[3]

		mapPoints = loadComplaints(complaintsFile)
		zipBorough = getZipBorough(zipBoroughsFile)
		drawPlot(shapeFile, mapPoints, zipBorough)

