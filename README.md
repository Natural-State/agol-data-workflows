# ArcGIS Online data workflows

This repo contains the code to create the environmental covariate layers that are stored in Natural State’s ArcGIS Online (AGOL) database. 
In most cases the processes follows a three-step workflow: 
1) extract remotely sensed data from Google Earth Engine (GEE) via the Python API
2) import layers into an ArcGIS file geodatabase for storage and processing
3) upload cleaned and annotated layers to AGOL

Documentation describing the code and workflow can be found [here](https://docs.naturalstate.tech/docs/agol).

**A note on using AGOL credentials:** In order to connect to AGOL for uploading data you will need to specify your NS login credentials. To avoid tracking these on the repo you need to create a file called `agol_credentials.py` and store it in the root of your project directory. The file simply contains your credentials using the following variable names:  
`agol_username = "YOUR_USERNAME"`  
`agol_password = "YOUR_PASSWORD"`
