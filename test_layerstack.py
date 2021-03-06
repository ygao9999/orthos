import orthos
from pyqtgraph.Qt import QtGui, QtCore

app = QtGui.QApplication([])


class FractionSelectionBar( QtGui.QWidget ):
    fractionChanged = QtCore.Signal(float)

    def __init__( self, initial_fraction=1., parent=None ):
        super(FractionSelectionBar, self).__init__( parent=parent )
        self._fraction = initial_fraction
        self._lmbDown = False

    def fraction( self ):
        return self._fraction

    def setFraction( self, value ):
        if value == self._fraction:
            return
        if(value < 0.):
            value = 0.
            warnings.warn("FractionSelectionBar.setFraction(): value has to be between 0. and 1. (was %s); setting to 0." % str(value))
        if(value > 1.):
            value = 1.
            warnings.warn("FractionSelectionBar.setFraction(): value has to be between 0. and 1. (was %s); setting to 1." % str(value))
        self._fraction = float(value)
        self.update()

    def mouseMoveEvent(self, event):
        if self._lmbDown:
            self.setFraction(self._fractionFromPosition( event.posF() ))
            self.fractionChanged.emit(self._fraction)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            return
        self._lmbDown = True
        self.setFraction(self._fractionFromPosition( event.posF() ))
        self.fractionChanged.emit(self._fraction)

    def mouseReleaseEvent(self, event):
        self._lmbDown = False

    def paintEvent( self, ev ):
        painter = QtGui.QPainter(self)

        # calc bar offset
        y_offset =(self.height() - self._barHeight()) // 2
        ## prevent negative offset
        y_offset = 0 if y_offset < 0 else y_offset

        # frame around fraction indicator
        painter.setBrush(self.palette().dark())
        painter.save()
        ## no fill color
        b = painter.brush(); b.setStyle(QtCore.Qt.NoBrush); painter.setBrush(b)
        painter.drawRect(
            QtCore.QRect(QtCore.QPoint(0, y_offset),
                  QtCore.QSize(self._barWidth(), self._barHeight())))
        painter.restore()

        # fraction indicator
        painter.drawRect(
            QtCore.QRect(QtCore.QPoint(0, y_offset),
                  QtCore.QSize(self._barWidth()*self._fraction, self._barHeight())))

    def sizeHint( self ):
        return QtCore.QSize(100, 10)

    def minimumSizeHint( self ):
        return QtCore.QSize(1, 3)

    def _barWidth( self ):
        return self.width()-1

    def _barHeight( self ):
        return self.height()-1

    def _fractionFromPosition( self, pointf ):
        frac = pointf.x() / self.width()
        # mouse has left the widget
        if frac < 0.:
            frac = 0.
        if frac > 1.:
            frac = 1.
        return frac

class ToggleEye( QtGui.QLabel ):
    activeChanged = QtCore.Signal(bool)

    def __init__( self, parent=None ):
        super(ToggleEye, self).__init__( parent=parent )
        self._active = True
        self._eye_open = QtGui.QPixmap(":icons/icons/stock-eye-20.png")
        self._eye_closed = QtGui.QPixmap(":icons/icons/stock-eye-20-gray.png")
        self.setPixmap(self._eye_open)

    def active( self ):
        return self._active

    def setActive( self, b ):
        if b == self._active:
            return
        self._active = b
        if b:
            self.setPixmap(self._eye_open)
        else:
            self.setPixmap(self._eye_closed)

    def toggle( self ):
        if self.active():
            self.setActive( False )
        else:
            self.setActive( True )

    def mousePressEvent( self, ev ):
        self.toggle()
        self.activeChanged.emit( self._active )


class LayerItemWidget( QtGui.QWidget ):
    @property
    def layer(self):
        return self._layer


    def __init__( self,layer, parent=None ):
        super(LayerItemWidget, self).__init__( parent=parent )
        self._layer = layer

        self._font = QtGui.QFont(QtGui.QFont().defaultFamily(), 9)
        self._fm = QtGui.QFontMetrics( self._font )
        self.bar = FractionSelectionBar( initial_fraction = layer.alpha() )
        self.bar.setFixedHeight(10)
        self.nameLabel = QtGui.QLabel( parent=self )
        self.nameLabel.setFont( self._font )
        self.nameLabel.setText( "None" )
        self.opacityLabel = QtGui.QLabel( parent=self )
        self.opacityLabel.setAlignment(QtCore.Qt.AlignRight)
        self.opacityLabel.setFont( self._font )
        self.opacityLabel.setText( u"\u03B1=%0.1f%%" % (100.0*(self.bar.fraction())))
        self.toggleEye = ToggleEye( parent=self )
        self.toggleEye.setActive(layer.visible())
        self.toggleEye.setFixedWidth(35)
        self.toggleEye.setToolTip("Visibility")
        self.channelSelector = QtGui.QSpinBox( parent=self )
        self.channelSelector.setFrame( False )
        self.channelSelector.setFont( self._font )
        self.channelSelector.setMaximumWidth( 35 )
        self.channelSelector.setAlignment(QtCore.Qt.AlignRight)
        self.channelSelector.setToolTip("Channel")
        self.channelSelector.setVisible(False)

        self._layout = QtGui.QGridLayout( self )
        self._layout.addWidget( self.toggleEye, 0, 0 )
        self._layout.addWidget( self.nameLabel, 0, 1 )
        self._layout.addWidget( self.opacityLabel, 0, 2 )
        self._layout.addWidget( self.channelSelector, 1, 0)
        self._layout.addWidget( self.bar, 1, 1, 1, 2 )

        self._layout.setColumnMinimumWidth( 0, 35 )
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(5,2,5,2)

        self.setLayout( self._layout )

        #self.bar.fractionChanged.connect( self._onFractionChanged )
        #self.toggleEye.activeChanged.connect( self._onEyeToggle )
        self.channelSelector.valueChanged.connect( self._onChannelChanged )

    def mousePressEvent( self, ev ):
        super(LayerItemWidget, self).mousePressEvent( ev )

    #def _onFractionChanged( self, fraction ):
    #    if self._layer and (fraction != self._layer.opacity):
    #        self._layer.opacity = fraction

    #def _onEyeToggle( self, active ):
    #    if self._layer and (active != self._layer.visible):
    #        
    #        if self._layer._allowToggleVisible:
    #            self._layer.visible = active
    #        else:
    #            self.toggleEye.setActive(True)

    def _onChannelChanged( self, channel ):
        if self._layer and (channel != self._layer.channel):
            self._layer.channel = channel

    def _updateState( self ):
        if self._layer:
            self.toggleEye.setActive(self._layer.visible)
            self.bar.setFraction( self._layer.opacity )
            self.opacityLabel.setText( u"\u03B1=%0.1f%%" % (100.0*(self.bar.fraction())))
            self.nameLabel.setText( self._layer.name )
            
            if self._layer.numberOfChannels > 1:
                self.channelSelector.setVisible( True )
                self.channelSelector.setMaximum( self._layer.numberOfChannels - 1 )
                self.channelSelector.setValue( self._layer.channel )
            else:
                self.channelSelector.setVisible( False )
                self.channelSelector.setMaximum( self._layer.numberOfChannels - 1)
                self.channelSelector.setValue( self._layer.channel )
            self.update()



class LayerStub(object):
    def __init__(self):
        pass
    def alpha(self):
        return  1.0
    def visible(self):
        return True



class LayerStackCtrlListWidgetItem(QtGui.QWidget):
    def __init__(self, ndViewer,listItem):
        super(LayerStackCtrlListWidgetItem,self).__init__()
        self.listItem = listItem
        self.ndViewer = ndViewer
        self.basicCtrl  = LayerItemWidget(layer=LayerStub(),parent=self)
        self.additonalWidget = QtGui.QPushButton('baaar')
        self.additionalWidgetExpanded = False
        
        def _setupUI():
            self.mainLayout = QtGui.QVBoxLayout()
            self.setLayout(self.mainLayout)
            self.mainLayout.addWidget(self.basicCtrl)
            self.mainLayout.addWidget(self.additonalWidget)
            self.additonalWidget.setVisible(False)
        _setupUI()


    def mouseDoubleClickEvent(self, event):
        if self.additonalWidget is not None:
            self.additonalWidget.setEnabled(not self.additionalWidgetExpanded)
            self.additonalWidget.setVisible(not self.additionalWidgetExpanded)
            self.additionalWidgetExpanded = not self.additionalWidgetExpanded
            self.listItem.setSizeHint(self.sizeHint())


class LayerStackCtrlWidget(QtGui.QWidget):
    def __init__(self, ndViewer):
        super(LayerStackCtrlWidget,self).__init__()

        self.ndViewer = ndViewer
        
        self.listWidget = QtGui.QListWidget()

        for x in range(10):
            listItem = QtGui.QListWidgetItem()
            itemWidget  = LayerStackCtrlListWidgetItem(ndViewer=ndViewer,listItem=listItem)
            listItem.setSizeHint(itemWidget.sizeHint())
            self.listWidget.addItem(listItem)
            self.listWidget.setItemWidget(listItem, itemWidget)

        def _setupUI():
            self.mainLayout = QtGui.QHBoxLayout()
            self.setLayout(self.mainLayout)

            self.mainLayout.addWidget(self.listWidget)
        _setupUI()



widget = LayerStackCtrlWidget(ndViewer=None)
widget.show()

############################################
# execute the app
############################################
QtGui.QApplication.instance().exec_()
