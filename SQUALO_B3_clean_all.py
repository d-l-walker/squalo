import os
import re
import numpy as np

path = '/path_to_B3_data/'

targ            = ['24013+0488', '28178-0091', '31946+0076', 'G327.393+00.199',
                   'G327.403+00.444', 'G331.132-00.245', 'G332.604-00.168',
                   'G338.927+00.632', 'G341.215-00.236', 'G343.520-00.519',
                   'G343.756-00.163','G344.101-00.661','G344.221-00.594']
velocity        = [94, 98, 96, -89, -80, -86, -47, -62, -44, -35, -28, -26, -25]
SPWs            = [0, 1, 2, 3]
cubeWidth       = 50
useWidthsFreq   = [61.035, 61.035, 61.035, 61.035]
mol             = ['HCOp','SiO','H13COp','HCN']
restFreq        = ['89.18852470GHz','86.243370GHz','86.754288GHz','88.6318470GHz']

for i in range(0,len(targ)):
    for SPWgroup in SPWs:
        imNameF     = targ[i]+'SPW'+str(SPWgroup+1)+"_"+mol[SPWgroup]+"_LINE"
        rf          = float(re.split('G',restFreq[SPWgroup])[0])
        chWid       = np.around(((((useWidthsFreq[SPWgroup]*1000.)/(rf*1.0e9))*299792458.0)/1000.0),2)
        numChan     = int(np.ceil((2.0*cubeWidth)/chWid))+1
        chWid       = str(chWid)+'km/s'
        useStart    = str(velocity[i] - cubeWidth)+'km/s'

        if (os.path.exists(path+targ[i]+'/'+targ[i]+'SPW'+str(SPWgroup+1)+"_"+mol[SPWgroup]+".ms.contsub") and 
            not os.path.exists(path+targ[i]+'/'+imNameF+'.fullres.image')):

            tclean(vis                = path+targ[i]+'/'+targ[i]+'SPW'+str(SPWgroup+1)+"_"+mol[SPWgroup]+".ms.contsub",
                   imagename          = path+targ[i]+'/'+imNameF+'.fullres',
                   field              = targ[i],
                   stokes             = 'I',
                   spw                = '',
                   outframe           = 'LSRK',
                   restfreq           = restFreq[SPWgroup],
                   specmode           = 'cube',
                   imsize             = [512, 512],
                   cell               = '0.3arcsec',
                   deconvolver        = 'multiscale',
                   scales             = [0, 6, 18],
                   niter              = 10000000,
                   weighting          = 'briggs',
                   robust             = 0.5,
                   usemask            = 'auto-multithresh',
                   sidelobethreshold  = 2.0,
                   noisethreshold     = 4.25,
                   lownoisethreshold  = 2.0,
                   negativethreshold  = 0.0,
                   minbeamfrac        = 0.15,
                   growiterations     = 75,
                   dogrowprune        = True,
                   gridder            = 'mosaic',
                   mosweight          = True,
                   pbcor              = True,
                   threshold          = '3mJy',
                   interactive        = False,
                   parallel           = True,
                   cyclefactor	      = 2.0,
                   restoringbeam      = 'common')