import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import orthos
import h5py

from orthos.widgets import *
from orthos.layers import *
from orthos.data_source import *

pg.setConfigOptions(antialias=False,useOpenGL=True)

app = QtGui.QApplication([])
mw = MainWindow()
mw.setWindowTitle('Orthos')
mw.show()
mw.resize(800, 600)




shape = (1000,1000)
data = numpy.random.rand(*shape)*255.0
data = data.astype('uint8')

print "start"
opt = LayerViewerOptions()
opt.spatialDimensions = 2
opt.hasTimeAxis = False

viewerWidget = LayerViewerWidget(spatialShape=shape, options=opt)
mw.setCentralWidget(viewerWidget)



with vigra.Timer("create raw layer"):
    rawSource = NumpyArrayDataSource(data)
    rawLayer = GrayscaleLayer(name='raw%d'%x,levels=[0,255],dataSource=rawSource,useLut=True)
    viewerWidget.addLayer(rawLayer)












with vigra.Timer("range changed"):
    viewerWidget.rangeChanged()




## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
