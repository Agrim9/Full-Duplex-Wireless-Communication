#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Fri Apr  7 06:46:36 2017
##################################################

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import PyQt4.Qwt5 as Qwt
import self_cancel
import sip
import sys

class top_block(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Top Block")
        try:
             self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
             pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.samp_rate_rtl = samp_rate_rtl = 2e6
        self.samp_rate = samp_rate = 48000
        self.err = err = 0

        ##################################################
        # Blocks
        ##################################################
        self.self_cancel_0 = self_cancel.self_cancel(samp_rate)
        self.qtgui_sink_x_0_0 = qtgui.sink_c(
        	1024, #fftsize
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	0, #fc
        	samp_rate, #bw
        	"QT GUI Plot", #name
        	True, #plotfreq
        	True, #plotwaterfall
        	True, #plottime
        	True, #plotconst
        )
        self.qtgui_sink_x_0_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_0_win = sip.wrapinstance(self.qtgui_sink_x_0_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_sink_x_0_0_win)
        
        
        self.qtgui_sink_x_0 = qtgui.sink_c(
        	1024, #fftsize
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	0, #fc
        	samp_rate, #bw
        	"QT GUI Plot", #name
        	True, #plotfreq
        	False, #plotwaterfall
        	False, #plottime
        	True, #plotconst
        )
        self.qtgui_sink_x_0.set_update_time(1.0/100000)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        
        
        self.fir_filter_xxx_0 = filter.fir_filter_ccc(1, ([1, 0.5, -4, 3, 0, 5]))
        self.fir_filter_xxx_0.declare_sample_delay(0)
        self._err_layout = Qt.QVBoxLayout()
        self._err_tool_bar = Qt.QToolBar(self)
        self._err_layout.addWidget(self._err_tool_bar)
        self._err_tool_bar.addWidget(Qt.QLabel("err"+": "))
        self._err_counter = Qwt.QwtCounter()
        self._err_counter.setRange(-1e9, 1e9, 100)
        self._err_counter.setNumButtons(2)
        self._err_counter.setValue(self.err)
        self._err_tool_bar.addWidget(self._err_counter)
        self._err_counter.valueChanged.connect(self.set_err)
        self._err_slider = Qwt.QwtSlider(None, Qt.Qt.Horizontal, Qwt.QwtSlider.BottomScale, Qwt.QwtSlider.BgSlot)
        self._err_slider.setRange(-1e9, 1e9, 100)
        self._err_slider.setValue(self.err)
        self._err_slider.setMinimumWidth(200)
        self._err_slider.valueChanged.connect(self.set_err)
        self._err_layout.addWidget(self._err_slider)
        self.top_layout.addLayout(self._err_layout)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, "/home/agrim/Downloads/Source_Separation/piano.wav", True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.self_cancel_0, 0), (self.qtgui_sink_x_0_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.self_cancel_0, 1))
        self.connect((self.blocks_file_source_0, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.self_cancel_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.qtgui_sink_x_0, 0))


# QT sink close method reimplementation
    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate_rtl(self):
        return self.samp_rate_rtl

    def set_samp_rate_rtl(self, samp_rate_rtl):
        self.samp_rate_rtl = samp_rate_rtl

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_sink_x_0_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_err(self):
        return self.err

    def set_err(self, err):
        self.err = err
        self._err_counter.setValue(self.err)
        self._err_slider.setValue(self.err)

if __name__ == '__main__':
    import ctypes
    import os
    if os.name == 'posix':
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    qapp = Qt.QApplication(sys.argv)
    tb = top_block()
    tb.start()
    tb.show()
    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()
    tb = None #to clean up Qt widgets

