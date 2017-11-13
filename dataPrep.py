# This script contains function to load data from the numerous .fit files
# in the /data folder.

import os
import numpy as np

from fitparse import FitFile

from sklearn.model_selection import train_test_split

def formDataset( ) :

    # choose which variables to extract
    names = [ 'altitude', 'cadence', 'distance', 'heart_rate', 'power', 'speed' ]

    N = 0

    # loop through each file in the 'data' directory
    for filename in os.listdir('/home/boltonl/dataScience/cycloAnalytics/cycDataExpl/data') :

        # ignore any files that don't end with .fit
        if filename.endswith('.fit') :

            # extract data from fit file
            myFitFile = FitFile( 'data/'+filename )

            tempList = []

            # loop through each data point, and get the desired variables
            for record in myFitFile.get_messages( 'record' ) :

                row = [ data.value for data in record if data.name in names]
                nVar = len(row)

                # check that this particular file has all the variables present (e.g. for
                # some of my rides I didn't have a powermeter or HR monitor)
                if nVar == len(names) :
                    tempList.append(row)
                else :
                    break

            if nVar != len(names) : continue

            # if we do have the correct number of variables, then proceed to calculate the
            # rate of change of: heart rate, elevation (i.e. the gradient), and speed, over
            # a 10 second time period
            tempList = np.array( tempList )

            gradient = ( tempList[10:,0] - tempList[:-10,0] ) / ( tempList[10:,2] - tempList[:-10,2] )
            changeHR = ( tempList[10:,3] - tempList[:-10,3] )
            changeSP = ( tempList[10:,5] - tempList[:-10,5] )

            power = tempList[10:,4]
            cadence = tempList[10:,1]
            speed = tempList[10:,5]
            heartrate = tempList[10:,3]

            fileData = np.zeros( ( power.shape[0], 7 ) )

            fileData[:,0] = power
            fileData[:,1] = cadence
            fileData[:,2] = speed
            fileData[:,3] = heartrate
            fileData[:,4] = gradient
            fileData[:,5] = changeHR
            fileData[:,6] = changeSP

            # the data from this file to the main numpy array of all files
            if N == 0 :
                myData = fileData
                N += 1
            else :
                myData = np.concatenate( ( myData, fileData ), axis=0 )

        # progress update
        print filename, " has been processed. Total data points now stored: ", myData.shape[0]

    # save data as numpy array
    np.save( "cyclingData", myData )

def loadDataset() :

    # load data
    myData = np.load('cyclingData.npy')

    # make input and output variables
    x, y = myData[:,1:], myData[:,0]

    # use data from the following 5 files as the test data:
    #
    # 2017-09-12-10-49-12.fit
    # 2017-08-20-15-27-52.fit
    # 2017-11-02-09-32-43.fit
    # 2017-09-26-08-16-40.fit
    # 2017-08-18-09-05-31.fit
    # 2017-09-13-07-36-01.fit
    # 2017-10-26-09-25-18.fit
    #
    # The data from these files are from index 154235 onwards in the myData array
    xTrain, xTest, yTrain, yTest = x[:137208,:], x[137208:,:], y[:137208], y[137208:]

    return xTrain, yTrain, xTest, yTest


