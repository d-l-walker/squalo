import os
import re
import numpy as np

path = '/path_to_B6_data/'

targ            = ['24013+0488', '28178-0091', '31946+0076', 'G327.393+00.199',
                   'G327.403+00.444', 'G331.132-00.245', 'G332.604-00.168',
                   'G338.927+00.632', 'G341.215-00.236', 'G343.520-00.519',
                   'G343.756-00.163','G344.101-00.661','G344.221-00.594']
velocity        = [94, 98, 96, -89, -80, -80, -47, -62, -44, -35, -28, -26, -25]
SPWs            = [0, 1, 2, 3, 4, 5, 6]
cubeWidth       = [120.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0]
useWidthsFreq   = [976.6, 976.6, 244.16, 122.075, 122.075, 122.075, 122.075]
mol             = ['12CO','pseudoCONT','13CO','H2CO_322_221','OCS','H2CO_303_202',
                   'H2CO_321_220']
restFreq        = ['230.53800000GHz','233.91704630GHz','220.39868420GHz',
                   '218.47563200GHz','218.90335550GHz','218.22219200GHz',
                   '218.76006600GHz']

for i in range(0,len(targ)):
    
    if mol[i] == 'pseudoCONT':
        continue

    for SPWgroup in SPWs:
        imNameF     = targ[i]+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+"_LINE"
        rf          = float(re.split('G',restFreq[SPWgroup])[0])
        chWid       = np.around(((((useWidthsFreq[SPWgroup]*1000.)/(rf*1.0e9))*299792458.0)/1000.0),2)
        numChan     = int(np.ceil((2.0*cubeWidth[SPWgroup])/chWid))+1
        chWid       = str(chWid)+'km/s'
        useStart    = str(velocity[i] - cubeWidth[SPWgroup])+'km/s'

        if (os.path.exists(path+targ[i]+'/'+targ[i]+'SPW'+str(SPWgroup+1)+"_"+mol[SPWgroup]+".ms.contsub") and 
            not os.path.exists(path+targ[i]+'/'+imNameF+'.image')):

            tclean( vis                = path+targ[i]+'/'+targ[i]+'SPW'+str(SPWgroup+1)+"_"+mol[SPWgroup]+".ms.contsub",
                    imagename          = path+targ[i]+'/'+imNameF,
                    field              = targ[i],
                    stokes             = 'I',
                    spw                = '',
                    outframe           = 'LSRK',
                    restfreq           = restFreq[SPWgroup],
                    specmode           = 'cube',
                    imsize             = [400, 400],
                    cell               = '0.2arcsec',
                    deconvolver        = 'multiscale',
                    scales             = [0, 6, 18],
                    niter              = 1000000,
                    weighting          = 'briggs',
                    robust             = 0.5,
                    usemask            = 'auto-multithresh',
                    sidelobethreshold  = 3.0,
                    lownoisethreshold  = 2.0,
                    minbeamfrac        =  0.15,
                    noisethreshold     = 4.5,
                    gridder            = 'mosaic',
                    pbcor              = True,
                    threshold          = '25mJy',
                    width              = chWid,
                    start              = useStart,
                    nchan              = numChan,
                    interactive        = False,
                    parallel           = True,
                    restoringbeam      = 'common',
                    cyclefactor        = 1.5)