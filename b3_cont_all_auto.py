import analysisUtils as au

visfile = '24013+0488ALLSPW_MSTRANS.ms'

cont_channels = '0:0~90;125~825;835~1450;1458~1680;1690~1915,1:0~90;125~825;835~1450;1458~1680;1690~1915,2:0~90;125~825;835~1450;1458~1680;1690~1915,3:0~90;125~825;835~1450;1458~1680;1690~1915,4:0~90;125~825;835~1450;1458~1680;1690~1915,5:0~90;125~825;835~1450;1458~1680;1690~1915,6:0~90;125~825;835~1450;1458~1680;1690~1915,7:0~925;1000~1015;1040~1915,8:0~925;1000~1015;1040~1915,9:0~925;1000~1015;1040~1915,10:0~925;1000~1015;1040~1915,11:0~925;1000~1015;1040~1915,12:0~925;1000~1015;1040~1915,13:0~925;1000~1015;1040~1915,14:0~955,15:0~955,16:0~955,17:0~955,18:0~955,19:0~955,20:0~955,21:0~465;495~955,22:0~465;495~955,23:0~465;495~955,24:0~465;495~955,25:0~465;495~955,26:0~465;495~955,27:0~465;495~955,28:0~850;1070~1915,29:0~850;1070~1915,30:0~850;1070~1915,31:0~850;1070~1915,32:0~850;1070~1915,33:0~850;1070~1915,34:0~850;1070~1915'


line_channels = au.invertChannelRanges(cont_channels, vis='24013+0488ALLSPW_MSTRANS.ms', separator=';')

line_channels = '0:91~124;826~834;1451~1457;1681~1689;1916~1917,1:91~124;826~834;1451~1457;1681~1689;1916~1918,2:91~124;826~834;1451~1457;1681~1689;1916~1918,3:91~124;826~834;1451~1457;1681~1689;1916~1918,4:91~124;826~834;1451~1457;1681~1689;1916~1918,5:91~124;826~834;1451~1457;1681~1689;1916~1918,6:91~124;826~834;1451~1457;1681~1689;1916~1918,7:926~999;1016~1039;1916~1918,8:926~999;1016~1039;1916~1918,9:926~999;1016~1039;1916~1918,10:926~999;1016~1039;1916~1918,11:926~999;1016~1039;1916~1917,12:926~999;1016~1039,13:926~999;1016~1039;1916~1918,14:956~958,15:956~958,16:956~959,17:956~958,18:956~958,19:956~958,20:956~959,21:466~494;956~958,22:466~494;956~958,23:466~494;956~958,24:466~494;956~958,25:466~494;956~957,26:466~494,27:466~494;956~958,28:851~1069;1916~1917,29:851~1069;1916~1917,30:851~1069;1916~1917,31:851~1069;1916~1917,32:851~1069;1916~1917,33:851~1069,34:851~1069;1916~1918'

flagmanager(vis=visfile, mode='save',
            versionname='before_cont_flags')

flagdata(vis=visfile, mode='manual', spw=line_channels,
         flagbackup=False)

flagmanager(vis=visfile, mode='save',
            versionname='line_channel_flags')

freqs = {}

ms.open(visfile)
msmd.open(visfile)

targetwidth = 125e6
widths = []
for spw in range(0,35):
    freqs[spw] = ms.cvelfreqs(spwids=[spw], outframe='LSRK')
    chwid = np.abs(np.mean(msmd.chanwidths(spw)))
    wid = int(targetwidth/chwid)
    if wid <= 0:
        raise ValueError("The channel width is greater than "
                         "the target line width for spw {0} "
                         "in ms {1}".format(spw, visfile))
    if wid > msmd.nchan(spw) / 2:
        wid = int(msmd.nchan(spw) / 2)
    widths.append(wid)
msmd.close()
ms.close()

split(vis        = visfile,
      field      = '24013+0488',
      outputvis  = visfile.strip('.ms')+'.cont.avg.new.ms',
      width      = widths,
      datacolumn = 'data')

flagmanager(vis=visfile, mode='restore',
            versionname='before_cont_flags')



tclean(vis                  = '24013+0488ALLSPW_MSTRANS.cont.avg.ms',
       imagename            = '24013+0488ALL_LINEFREE_CONT',
       field                = '24013+0488',
       stokes               = 'I',
       outframe             = 'LSRK',
       restfreq             = '87.7GHz',
       specmode             = 'mfs',
       imsize               = [512, 512],
       cell                 = '0.3arcsec',
       deconvolver          = 'multiscale',
       scales               = [0, 6, 18],
       niter                = 100000,
       weighting            = 'briggs',
       robust               = 0.5,
       usemask              = 'auto-multithresh',
       sidelobethreshold    = 3.0,
       lownoisethreshold    = 2.0,
       minbeamfrac          =  0.15,
       noisethreshold       = 4.5,
       gridder              = 'mosaic',
       cycleniter           = 100,
       pbcor                = True,
       threshold            = '40.0uJy',
       interactive          = 0,
       restoringbeam        = 'common',
       parallel             = True)


tclean(vis                  = '24013+0488ALLSPW_MSTRANS.ms',
       imagename            = '24013+0488ALL_LINEFREE_CONT_no_avg',
       field                = '24013+0488',
       stokes               = 'I',
       outframe             = 'LSRK',
       restfreq             = '87.7GHz',
       specmode             = 'mfs',
       imsize               = [512, 512],
       cell                 = '0.3arcsec',
       deconvolver          = 'multiscale',
       scales               = [0, 6, 18],
       niter                = 100000,
       weighting            = 'briggs',
       robust               = 0.5,
       usemask              = 'auto-multithresh',
       sidelobethreshold    = 3.0,
       lownoisethreshold    = 2.0,
       minbeamfrac          =  0.15,
       noisethreshold       = 4.5,
       gridder              = 'mosaic',
       cycleniter           = 100,
       pbcor                = True,
       threshold            = '40.0uJy',
       interactive          = 0,
       restoringbeam        = 'common',
       parallel             = True)

"""
nohup ./run_continuum_clean.sh > & b3_continuum_clean.log < /dev/null &
ps -ax | grep ./run_continuum_clean.sh
"""
