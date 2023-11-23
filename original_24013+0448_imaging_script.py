import os
import numpy as np
import re
""" 24013+0448 VERSION """
# modified by bjones (so don't blame Adam if I wreck it)
# v2+ is the newer script with aggregate bandwidth continuum added. Steps 0-3 have been run with the old script for all spw.

#=================================================#
#             CODE PROPER                         #
#=================================================#

#======= LOGIC SWITCHES =====#
do_stepm1= False # test step
do_step0 = False # split out spectral windows and regrid to LSRK, flag non-overlapping channel and alll kinds of CASA ninja voodoo.
do_step1 = False # uvcontsub
do_step2 = True # line imaging.
do_step3 = False # cont imaging.
do_step4 = False  # Aggregate BW continuum image
do_step5 = False  # Aggregate BW continuum - 12m only
#============================#
"""
b-max=313.7m
resolution=1.03"
FOV=27"

cell=0.2"
imsize=480

--- CENTRAL FREQS :: SPW Nos.   :: CHWIDTH in km/s ---
231021.5463MHz:: 0,7,14,21,28,35 :: CHWIDTH = 1.28km/s
233917.0463MHz:: 1,8,15,22,29,36 :: CHWIDTH = 1.28km/s
220452.2142MHz:: 2,9,16,23,30,37 :: CHWDITH = 0.35km/s
218398.4954MHz:: 3,10,17,24,31,38 :: CHWDITH = 0.22km/s
218826.2298MHz:: 4,11,18,25,32,39 :: CHWDITH = 0.22km/s
218145.0774MHz:: 5,12,19,26,33,40 :: CHWDITH = 0.22km/s
218682.6751MHz:: 6,13,20,27,34,41 :: CHWDITH = 0.22km/s

--- LINE INFO ---
rest freq
'230.53800000GHz' :: 12CO         :: in SPW0 
'233.91704630GHz' :: CONT         :: in SPW1 
'220.39868420GHz' :: 13CO         :: in SPW2        
'218.47563200GHz' :: H2CO_322_221 :: in SPW3 (specifically H2CO 3(2,2)-2(2,1))  
'218.90335550GHz' :: OCS          :: in SPW4
'218.22219200GHz' :: H2CO_303_202 :: in SPW5 (specifically H2CO 3(0,3)-2(0,2))  
'218.76006600GHz' :: H2CO_321_220 :: in SPW6 (specifically H2CO 3(2,1)-2(2,0)) 
"""

#===== USER INPUTS ===== #
myMS = '24013+0488_COMBINED12n7_B6.ms'
targ = '24013+0488'  
SPWgroup = 6
sourceVLSR = 94.0 #km/s
cubeWidth = 30.0 #km/s the +/- velocity around VLSR which the cube will extend. So the cube will actually be twice this! (120.0 for SPW0, 30.0 kms for SPW 3,4,5 & 6)
lineFreeChans=['0~300;500~1100;1350~1915','0~300;500~1100;1350~1915','0~1200;1640~1918','0~190;300~477','0~190;300~478','0~170;320~478','0~190;310~477']
 #IN CHANNELS... NEEDS CHANGING FOR EACH SOURCE, for non-detections leaving the channels where a detection was made in CO (or H2CO for OCS)... whats the harm?


# ==== DATA PARAMETERS === #
SPWgroups =['0,7,14,21,28,35','1,8,15,22,29,36','2,9,16,23,30,37','3,10,17,24,31,38','4,11,18,25,32,39','5,12,19,26,33,40','6,13,20,27,34,41']
useWidthsFreq = [976.6, 976.6, 244.16,122.075,122.075,122.075,122.075]#kHz

mol=['12CO','pseudoCONT','13CO','H2CO_322_221','OCS','H2CO_303_202','H2CO_321_220']
restFreq=['230.53800000GHz','233.91704630GHz','220.39868420GHz','218.47563200GHz','218.90335550GHz','218.22219200GHz','218.76006600GHz']# of target lines
skyFreq=['231.1000000GHz','234.0000GHz','220.530000GHz','218.475632GHz','218.903355GHz','218.222192000GHz','218.76006600GHz']#as observed

#======== PROCESSING STEPS ===============#

#--- STEP -1 ---#
"""testing shiz"""
if do_stepm1:
    print "testing done"
    print len(re.split(',',SPWgroups[0]))

#=== STEP 0 ===#
""" split out spectral windows and regrid to LSRK """
if do_step0:
    counter=0
    spwSplit=re.split(',',SPWgroups[SPWgroup])
    splitStr=''
    
    #=== split out 12 and 7m from combined MS===#
    for SPW in spwSplit:
        if counter != len(spwSplit)-1:
            splitStr+=SPW+','
            counter+=1
        else:
            print ">> Splitting SPWs "+splitStr[:-1]+" to "+targ+'SPW'+str(SPWgroup)+'_7m.split'
            split(vis=myMS,
                outputvis=targ+'SPW'+str(SPWgroup)+'_7m.split',
                spw=splitStr[:-1],
                datacolumn='data') 
    
            print ">> Splitting SPW "+str(SPW)+" to "+targ+'SPW'+str(SPWgroup)+'_12m.split'
            split(vis=myMS,
                outputvis=targ+'SPW'+str(SPWgroup)+'_12m.split',
                spw=SPW,
                datacolumn='data') 
    
    #=== MSTRANSFORM EACH TO LSRK ===#
    print ">> MStransforming "+targ+'SPW'+str(SPWgroup)+'_7m.split to LSRK'
    mstransform(vis=targ+'SPW'+str(SPWgroup)+'_7m.split',
        outputvis=targ+'SPW'+str(SPWgroup)+'_7m.split_mstrans',
        spw='',
        regridms=True,
        outframe='LSRK',
        mode='channel',
        restfreq=restFreq[SPWgroup],
        datacolumn='data'
        )

    print ">> MStransforming "+targ+'SPW'+str(SPWgroup)+'_12m.split to LSRK'
    mstransform(vis=targ+'SPW'+str(SPWgroup)+'_12m.split',
        outputvis=targ+'SPW'+str(SPWgroup)+'_12m.split_mstrans',
        spw='',
        regridms=True,
        outframe='LSRK',
        mode='channel',
        restfreq=restFreq[SPWgroup],
        datacolumn='data'
        )
       
    #=== SOME HORRIFIC PLOTMS HAX0Rz this is to get the LSRK frequencies...                #
    # ... the visibilities data still includes all flagged data so its easier this way! ===#
    #=== 12mdata
    default(plotms)
    plotms(
        vis=targ+'SPW'+str(SPWgroup)+'_12m.split_mstrans',
        xaxis='frequency',
        yaxis='amp',
        showgui=False,
        averagedata=True,
        correlation='XX',
        avgbaseline=True,
        spw='',
        avgtime='1e8', 
        plotfile='Twel_amp.txt', 
        expformat='txt', 
        overwrite=True, 
        ydatacolumn='data', 
        selectdata=True, 
        uvrange='<100m')

    twelFreqs=np.loadtxt('Twel_amp.txt',usecols=[0]) 

    #=== 7mdata
    sveFreqs = np.array([])
    for SPW in range(len(spwSplit)-1):
        default(plotms)
        plotms(
            vis=targ+'SPW'+str(SPWgroup)+'_7m.split_mstrans',
            xaxis='frequency',
            yaxis='amp',
            showgui=False,
            averagedata=True,
            correlation='XX',
            avgbaseline=True,
            spw=str(SPW),
            avgtime='1e8', 
            plotfile='Sev_amp_SPW'+str(SPW)+'.txt', 
            expformat='txt', 
            overwrite=True, 
            ydatacolumn='data', 
            selectdata=True, 
            uvrange='<100m')

        sveFreqsthisSPW=np.loadtxt('Sev_amp_SPW'+str(SPW)+'.txt',usecols=[0])
        sveFreqs=np.append(sveFreqs, sveFreqsthisSPW)       
    
    
    wantMin=np.max([np.min(sveFreqs),np.min(twelFreqs)])
    wantMax=np.min([np.max(sveFreqs),np.max(twelFreqs)])
    print ">> Splitting again to limit frequency coverage to regions common to all EBs:\n "+str(wantMin)+"~"+str(wantMax)+"GHz"
    print ">> Generating "+targ+'SPW'+str(SPWgroup)+'_7m.split_mstrans_split2 and '+targ+'SPW'+str(SPWgroup)+'_12m.split_mstrans_split2'
    #=== SPLIT them both again to cover the same freq range ===#
    split(vis=targ+'SPW'+str(SPWgroup)+'_7m.split_mstrans',
                outputvis=targ+'SPW'+str(SPWgroup)+'_7m.split_mstrans_split2',
                spw='*:'+str(wantMin)+'~'+str(wantMax)+'GHz',
                datacolumn='data',
                keepflags=False) 

    listobs(vis=targ+'SPW'+str(SPWgroup)+'_7m.split_mstrans_split2',listfile=targ+'SPW'+str(SPWgroup)+'_7m.split_mstrans_split2.listobs')

    split(vis=targ+'SPW'+str(SPWgroup)+'_12m.split_mstrans',
                outputvis=targ+'SPW'+str(SPWgroup)+'_12m.split_mstrans_split2',
                spw='*:'+str(wantMin-((useWidthsFreq[SPWgroup]*1000.0)/1.0e9))+'~'+str(wantMax)+'GHz', #slight fudge ere because I seemed to be 1 channel out!
                datacolumn='data',
                keepflags=False)
    
    listobs(vis=targ+'SPW'+str(SPWgroup)+'_12m.split_mstrans_split2',listfile=targ+'SPW'+str(SPWgroup)+'_12m.split_mstrans_split2.listobs')
   
    
    #=== CONCAT IT ALL TOGETHER ===#
    concat(vis=[targ+'SPW'+str(SPWgroup)+'_12m.split_mstrans_split2',targ+'SPW'+str(SPWgroup)+'_7m.split_mstrans_split2'],
        concatvis=targ+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+".ms",
        freqtol='',
        copypointing=False
        )
    listobs(vis=targ+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+".ms",listfile=targ+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+".ms.listobs")
    print "\n\n\n>> Important Note: Because we've already MSTransformed to LSRK it is easiest/best to run tclean definining start and width in velocity around the systematic velocity of the source. You still need to set outframe to LSRK and the rest freq.\n>> !!! AVOID +/- 10 channels around the edges of the BW too. !!!"

    default(plotms)
    plotms(
            vis=targ+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+".ms",
            xaxis='velocity',
            yaxis='amp',
            showgui=False,
            averagedata=True,
            correlation='XX',
            avgbaseline=True,
            avgtime='1e8', 
            coloraxis='spw',
            plotfile=targ+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+".ms.png", 
            expformat='png', 
            overwrite=True, 
            ydatacolumn='data', 
            selectdata=True, 
            transform=True,
            restfreq=restFreq[SPWgroup],
            freqframe='LSRK',
            uvrange='<100m')

    os.system('eog '+targ+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+".ms.png")
    
#==== STEP 1 ===#
if do_step1:
    """CONTSUB"""    
    print ">> Using the mstransformed LSRK MS, it is recommended you use channel definitions of line free (it is just easier!)"

   

    uvcontsub(vis = targ+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+".ms",
            fitspw = '0~5:'+lineFreeChans[SPWgroup],
            field = targ
            )

#==== STEP 2 ===#
if do_step2:
    """ CUBE IMAGING """
    """ MAKES IMAGES +/-xkm/s either side of velocity of source"""

    imNameF = targ+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+"_LINE"
    rf=float(re.split('G',restFreq[SPWgroup])[0])
    chWid = np.around(((((useWidthsFreq[SPWgroup]*1000.)/(rf*1.0e9))*299792458.0)/1000.0)*2.0,2) #using a chan width twice that of
    numChan = int(np.ceil((2.0*cubeWidth)/chWid))+1
    chWid =str(chWid)+'km/s'
    useStart = str(sourceVLSR - cubeWidth)+'km/s'
    print imNameF,chWid, numChan, useStart

    #--- dirty image 
    print '>> Making Dirty Image'
    tclean(vis = targ+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+".ms.contsub",
             imagename = imNameF+'.drt',
             field = targ,
             stokes = 'I',
             spw = '', 
             outframe = 'LSRK',
             restfreq = restFreq[SPWgroup],
             specmode = 'cube',
             imsize = [400, 400],             
             cell = '0.2arcsec',
             deconvolver = 'multiscale',
             scales = [0, 6, 18], #in pixels the size of scales to to probe (this is point source, syth beam size and   3 times synth beam)
             niter = 0,
             weighting = 'briggs',
             robust = 0.5,
             usemask = 'auto-multithresh',
             sidelobethreshold = 3.0,
             lownoisethreshold = 2.0,
             minbeamfrac =  0.15,
             noisethreshold = 4.5,
             gridder = 'standard',
             pbcor = True,
             threshold = '25.0mJy',
             width = chWid,
             start = useStart,       
             nchan = numChan,
             interactive = True,
             restoringbeam = 'common'
             )
    print '>> Making Clean Image'   
    #--- with clean iterations
    tclean(vis = targ+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+".ms.contsub",
             imagename = imNameF,
             field = targ,
             stokes = 'I',
             spw = '', 
             outframe = 'LSRK',
             restfreq = restFreq[SPWgroup],
             specmode = 'cube',
             imsize = [400, 400],             
             cell = '0.2arcsec',
             deconvolver = 'multiscale',
             scales = [0, 6, 18], #in pixels the size of scales to to probe (this is point source, syth beam size and   3 times synth beam)
             niter = 10000,
             weighting = 'briggs',
             robust = 0.5,
             usemask = 'auto-multithresh',
             sidelobethreshold = 3.0,
             lownoisethreshold = 2.0,
             minbeamfrac =  0.15,
             noisethreshold = 4.5,
             gridder = 'standard',
             pbcor = True,
             threshold = '25.0mJy',
             width = chWid,
             #start = useStart,       
             #nchan = numChan,
             interactive = True,
             restoringbeam = 'common'
             )
    """"""
#==== STEP 3 ===#
if do_step3:
    """ CONT IMAGING """
    imNameC = targ+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+"_CONT"
    tclean(vis = targ+'SPW'+str(SPWgroup)+"_"+mol[SPWgroup]+".ms",
             imagename = imNameC,
             field = targ,
             stokes = 'I',
             spw = '*:'+lineFreeChans[SPWgroup], 
             outframe = 'LSRK',
             restfreq = restFreq[SPWgroup],
             specmode = 'mfs',
             imsize = [400, 400],             
             cell = '0.2arcsec',
             deconvolver = 'multiscale',
             scales = [0, 6, 18], #in pixels the size of scales to to probe (this is point source, syth beam size and   3 times synth beam)
             niter = 10000,
             weighting = 'briggs',
             robust = 0.5,
             usemask = 'auto-multithresh',
             sidelobethreshold = 3.0,
             lownoisethreshold = 2.0,
             minbeamfrac =  0.15,
             noisethreshold = 4.5,
             gridder = 'standard',
             pbcor = True,
             threshold = '0.0mJy', # fix this!
             interactive = True,
             restoringbeam = 'common'
             )

#==== STEP 4 ===#
if do_step4:
    """All LINE FREE CONT IMAGING """
    """ mstransMSs=[]
    #for idx in range(len(SPWgroups)):
        mstransMSs.append(targ+'SPW'+str(idx)+'_'+mol[idx]+'.ms')

    print mstransMSs

    
    #---- CONCAT ALL MSTRANS MSs INTO ONE FOR IMAGING ---#
    concat(vis=mstransMSs,
        concatvis=targ+'ALLSPW_MSTRANS.ms',
        freqtol='',
        copypointing=False
        )
    listobs(targ+'ALLSPW_MSTRANS.ms', listfile=targ+'ALLSPW_MSTRANS.ms.listobs')
    
    #--- THIS HAS THE DATA WITH MULTIPLE SPW OF THE SAME TRANSITION IN A ROW 
    #--- IE HCOp WILL BE SPW 7-13 in B3 etc etc ----#
	"""
    bigAggSPWstring=''

    ticker=0
    counter=0
    for num in range(len(SPWgroups)*len(re.split('\,',SPWgroups[0]))): #--- HACKY AF.
        print str(num)+':'+lineFreeChans[ticker]+','
        bigAggSPWstring+=str(num)+':'+lineFreeChans[ticker]+','   
        counter+=1
        if counter == len(re.split('\,',SPWgroups[0])):
            counter = 0
            ticker+=1

    print bigAggSPWstring[:-1]
    imNameC = targ+'ALL_LINEFREE_CONT.mosaic'
    tclean(vis = targ+'ALLSPW_MSTRANS.ms',
             imagename = imNameC,
             field = targ,
             stokes = 'I',
             spw = bigAggSPWstring[:-1], 
             outframe = 'LSRK',
             restfreq = '226.111GHz',
             specmode = 'mfs',
             imsize = [400, 400],             
             cell = '0.2arcsec',
             deconvolver = 'multiscale',
             scales = [0, 6, 18], #in pixels the size of scales to to probe (this is point source, syth beam size and   3 times synth beam)
             niter = 10000,
             weighting = 'briggs',
             robust = 0.5,
             usemask = 'auto-multithresh',
             sidelobethreshold = 3.0,
             lownoisethreshold = 2.0,
             minbeamfrac =  0.15,
             noisethreshold = 4.5,
             gridder = 'mosaic',
             pbcor = True,
             threshold = '40.0uJy', 
             interactive = True,
             restoringbeam = 'common',
	     restart=True
             )
if do_step5:
    """12m ONLY LINE FREE CONT IMAGING """
    bigAggSPWstring12=''
    # make same string, but only want to actually add last in each group 
    # 12m spws: 5,11,17,23,29,35,41 (7 groups, 6 observations per group and 12m is always last)
    ticker=0 # keeps track of spw group
    counter=0 # keeps track of observation within each group
    for num in range(len(SPWgroups)*len(re.split('\,',SPWgroups[0]))): #--- HACKY AF - number of spw groups x number of obs per spw = total spw in huge ms
        print str(num)+':'+lineFreeChans[ticker]+','
	# this time, only add if it is the last spw in a group (and .: a 12m window)
	if counter == len(re.split('\,',SPWgroups[0]))-1:
        	bigAggSPWstring12+=str(num)+':'+lineFreeChans[ticker]+','   
        counter+=1
	# reset if end of group
        if counter == len(re.split('\,',SPWgroups[0])):
            counter = 0
            ticker+=1

    print bigAggSPWstring12[:-1]
    
    imNameC12 = targ+'ALL_LINEFREE_CONT_12m_robustm1'
    tclean(vis = targ+'ALLSPW_MSTRANS.ms',
             imagename = imNameC12,
             field = targ,
             stokes = 'I',
             spw = bigAggSPWstring12[:-1], 
             antenna = 'DA*',
             outframe = 'LSRK',
             restfreq = '226.111GHz',
             specmode = 'mfs',
             imsize = [400, 400],             
             cell = '0.2arcsec',
             deconvolver = 'multiscale',
             scales = [0, 6, 18], #in pixels the size of scales to to probe (this is point source, syth beam size and   3 times synth beam)
             niter = 10000,
             weighting = 'briggs',
             robust = -1.0,
             usemask = 'auto-multithresh',
             sidelobethreshold = 3.0,
             lownoisethreshold = 2.0,
             minbeamfrac =  0.15,
             noisethreshold = 4.5,
             gridder = 'standard',
             pbcor = True,
             threshold = '40.0uJy', 
             interactive = True,
             restoringbeam = 'common'
             )