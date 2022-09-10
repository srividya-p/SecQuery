# SecQuery  <img src="https://user-images.githubusercontent.com/74781344/189496784-12f42ea5-f567-4616-aa96-c71bc2b24cce.png" width=40px height=40px>

This QGIS plugin takes in a Point Layer as input along with a specified radius and center point. It then renders geodesic buffers with a given number of sectors. The point data in those sectors can be queried using a custom map tool. Geodesic buffers are rendered with the geographiclib library. The concept behind rendering the buffers was reffered from the Shape Tools plugin. The smoothness of the buffers can also be configured. The queried point data is added as a new memory layer, so that users have access to all the attributes selected sector area.

![secquery](https://user-images.githubusercontent.com/74781344/189497035-251ff44b-434c-4bd0-a165-3cf92aa7a4d4.PNG)

## Features
### 🌎 Geodesic Buffers
Account for the earth's actual shape (an elipsoid or geoid) in the calculation of the buffer.

### ✻ Variable Sectors
Specify required number of sectors between 4 and 32; Render geodesic radii to demarcate sectors.

### 📍 Multiple Radius Units
Enter radius in centimeters, meters, kilometers, inches, feet, miles, nautical miles or yards.

### 🗺️ Map Select Center
Select the buffer center from a map click (via a map tool) or enter the desired coordinates.

### 📄 Queried Data Output Layer
Get data queried from a sector as separate memory layer with all attributes from input layer.

### 🧭 Direction Labels
Get labels for the 16 directions around the buffer; The directions are added as a new memory layer.

## Documentation
### *Read the full documentation [here](https://srividya-p.github.io/SecQuery/)*
