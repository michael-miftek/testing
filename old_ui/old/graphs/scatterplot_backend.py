import sys
import os
import numpy as np
import scipy.stats as stats
import pyqtgraph as pg
import time
from math import ceil
from PyQt6 import QtCore, QtGui
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (QGridLayout, QVBoxLayout, QSplitter, QGroupBox, QLabel, QComboBox, 
                             QDoubleSpinBox, QDockWidget, QTableWidget, QTableWidgetItem, QWidget, 
                             QPushButton)
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from pyqtgraph.graphicsItems.ROI import ROI
from pyqtgraph.graphicsItems import ROI

sys.path.append('../..')
from ui.oscilloscope.color_maps import colormaps

try:
    from scatterplot_math import ScatterProcessor
    from histogram import HistogramView
except:
    from .scatterplot_math import ScatterProcessor
    from .histogram import HistogramView

#TODO:  Make this cleaner
trigger_types = {0: "rising", 1: "falling", 2: "envelope", 3: "auto", 4: "always-on"}
nbins_types = {0:'64', 1:'128', 2:'256', 3:'512', 4:'1024'} #, 4:'2048', 5:'4096'}
baseline_types = {0: "mean-subtracted", 1: "min-subtracted", 2: "baseline", 3: "manual-baseline", 4:"raw"}
signal_treatment_types = {0:"smoothed", 1: "compressed", 2:"compressed-smooth", 3:"raw"}
compression_ratio_types = {0:'1', 1:'2', 2:'4', 3:'8', 4:'16', 5:'32', 6:'64'}

class ScatterPlotUpdater(QObject):
    """
    Scatter Plot Updater is a thread that handles all ui backend for the scatterplot. The 
    original way that channel scatter plot worked was through two concurrent processes that passed
    information by queue. The goal of this is to remove the queue system to allow faster data 
    handling and outputting.

    This thread on initialization will setup the data processing backend for the scatter channel,
    the math done at this time is not finalized (this is where things can change and will eventually 
    be put on FPGA fabric).
    """

    #TODO:  Only thinking of passing one daq here since this only cares about what is connected and 
    #       making sure it gets the most recent updates it since it only is based on visualUpdate 
    #       signals nothing else
    def __init__(self, daq, channelScatterPlot):
        super().__init__()

        self.sp = channelScatterPlot
        self.daq = daq
        
        self.timeCurr = time.time()
        self.xstep = 0
        self.ystep = 0
        self.scatter_math = None
        self.scatter_math_thread = None

        self.total_events_in_gatecall_x = 0
        self.total_events_in_gatecall_y = 0

        self.roi_Nx = []
        self.roi_meanx = []
        self.roi_stdx = []
        self.roi_varx = []
        self.roi_cvx = []

        self.roi_Ny = []
        self.roi_meany = []
        self.roi_stdy = []
        self.roi_vary = []
        self.roi_cvy = []

        self.roi = []
        self.gate_graph_fs = []
        self.gate_graph_ss = []
        self.roi_data = []
        self.roi_shape = []
        self.roi_label = []
        self.num_roi = 0
        
        #set with a drop down button
        self.num_bins = 256
        self.H = 0
        self.xedges = 0
        self.yedges = 0
        self.data_set = []
        self.sample_size = 2500
        self.update_roi = []

        self.connect_signals()
        self.setup_workers()

        #NOTE:  This is here and not in the math because the math thread should be uninterruppted as 
        #       much as possible
        self.sp.ch1select.currentIndexChanged.connect(self.channel_changed)
        self.sp.ch2select.currentIndexChanged.connect(self.channel_changed)
        self.sp.intmodeselect.currentIndexChanged.connect(self.scatter_math.parameter_changed)
        self.sp.triggertypeselect.currentIndexChanged.connect(self.scatter_math.parameter_changed)
        self.sp.triggerthreshselect.valueChanged.connect(self.scatter_math.parameter_changed)
        self.sp.ch1_baselineselect.currentIndexChanged.connect(self.scatter_math.parameter_changed)
        self.sp.ch2_baselineselect.currentIndexChanged.connect(self.scatter_math.parameter_changed)
        self.sp.crselect.currentIndexChanged.connect(self.scatter_math.parameter_changed)
        self.sp.stselect.currentIndexChanged.connect(self.scatter_math.parameter_changed)
        self.sp.nbinsselect.currentIndexChanged.connect(self.numbins_changed)

        self.sp.reset_button.clicked.connect(self.reset_graph)
        
        #TODO:  Possibly move to its own gate backend
        self.sp.gate_remove.clicked.connect(self.remove_gate)
        self.sp.rect_gates_button.clicked.connect(self.rect_gate_setup)
        self.sp.ellipse_gates_button.clicked.connect(self.ellipse_gate_setup)
        self.sp.show_gates_button.clicked.connect(self.show_gates_popup)
        
        print("Scatter Plot Updatter setup")

    def finish(self):
        print("Closing Scatter Processor")
        if self.scatter_math_thread:
            self.scatter_math_thread.quit()
        print("Scatter Processor Closed")

    def setup_workers(self):
        #TODO:  Thinking that tableview and histogram backends should exist in here as well, not as 
        #       sure about the table view now but maybe
        self.scatter_math = ScatterProcessor(self.sp, self.daq)
        self.scatter_math_thread = QThread()
        self.scatter_math_thread.moveToThread(self.scatter_math)
        #TODO:  Fix with appropriate functions calls
        self.scatter_math_thread.started.connect(self.scatter_math.run)
        self.scatter_math_thread.start()
        
    def connect_signals(self):
        #NOTE:  Event processor -> scatter math -> backend/draw -> gates backend -> gates math
        #TODO:  This will be implememnted one level down and then signals from that will help define 
        #       everything else
        # self.daq.event_processor.connect(self.live_update_plot)
        pass

    def numbins_changed(self):
        """!
        This method is called whenever the number of bins is changed, and it forces the graph to
        set the new limits and adjust the view.
        """
        self.num_bins = int(nbins_types[self.nbinsselect.currentIndex()])
        self.sp.view.setLimits(xMin=0, xMax=self.num_bins, yMin=0, yMax=self.num_bins)
        self.sp.view.setXRange(0,self.num_bins, padding=0)
        self.sp.view.setYRange(0,self.num_bins, padding=0)
        self.sp.scatterplot.setLevels(levels=[0, ceil(self.sample_size/self.num_bins)*2])
        self.scatter_math.parameter_changed()

    def remove_gate(self):
        """
        This method is called to remove a gate object from the scatter graph, with the removal all
        subsequent items tagged to that gate are also removed here.
        """
        if self.num_roi > 0:
            self.num_roi -= 1
            self.sp.scatter.removeItem(self.roi[self.num_roi])
            self.roi.pop(self.num_roi)
            self.roi_label.pop()
            self.roi_data.pop()

            self.roi_Nx.pop()
            self.roi_meanx.pop()
            self.roi_stdx.pop()
            self.roi_varx.pop()
            self.roi_cvx.pop()

            self.roi_Ny.pop()
            self.roi_meany.pop()
            self.roi_stdy.pop()
            self.roi_vary.pop()
            self.roi_cvy.pop()
            self.update_roi.pop()

            self.gate_graph_fs.pop()
            self.gate_graph_ss.pop()

        if self.num_roi == 0:
            self.sp.roi_table.hide()
            self.sp.gate_graph_popup_window.hide()
        else:
            self.update_gates_popup()

    ##NOTE: Types of ROIs 'ROI', 'TestROI', 'RectROI', 'EllipseROI', 'CircleROI', 'LineROI', 'MultiLineROI', 'MultiRectROI', 'LineSegmentROI', 'PolyLineROI', 'CrosshairROI','TriangleROI'
    def rect_gate_setup(self):
        """
        This method is called to add each stat to its own list when a gate is added 
        """
        self.roi.append(ROI.RectROI(pos=[0,0], size=10, pen=(0,0,0), hoverPen=(0,0,0)))
        self.roi_shape.append(0)
        self.update_roi.append(True)
        self.sp.scatter.addItem(self.roi[self.num_roi])
        self.roi[self.num_roi].show()
        self.roi[self.num_roi].sigRegionChangeFinished.connect(lambda x,val=self.num_roi: self.changed(val, x))
        self.roi_label.append(pg.TextItem(f"R{self.num_roi + 1}"))
        self.roi_label[self.num_roi].setParentItem(self.roi[self.num_roi])

        self.roi_Nx.append(0)
        self.roi_meanx.append(0)
        self.roi_stdx.append(0)
        self.roi_varx.append(0)
        self.roi_cvx.append(0)

        self.roi_Ny.append(0)
        self.roi_meany.append(0)
        self.roi_stdy.append(0)
        self.roi_vary.append(0)
        self.roi_cvy.append(0)

        self.gate_graph_fs.append(HistogramView(f"{self.roi_label[self.num_roi].toPlainText()} xpoints"))
        self.gate_graph_ss.append(HistogramView(f"{self.roi_label[self.num_roi].toPlainText()} ypoints"))

        self.num_roi += 1

        self.update_stats()
        #TODO:  Fixed variable call if needed
        if self.sp.roi_table.isHidden():
            self.sp.roi_table.show()

        self.update_gates_popup()

    def ellipse_gate_setup(self):
        """!
        This method is called to add an elliptical gate to the 2-D heat map 
        """
        self.roi.append(ROI.EllipseROI(pos=[0,0], size=10, pen=(0,0,0), hoverPen=(0,0,0)))
        self.roi_shape.append(0)
        self.update_roi.append(True)
        self.sp.scatter.addItem(self.roi[self.num_roi])
        self.roi[self.num_roi].show()
        self.roi[self.num_roi].sigRegionChangeFinished.connect(lambda x,val=self.num_roi: self.changed(val, x))
        self.roi_label.append(pg.TextItem(f"E{self.num_roi + 1}"))
        self.roi_label[self.num_roi].setParentItem(self.roi[self.num_roi])

        self.roi_Nx.append(0)
        self.roi_meanx.append(0)
        self.roi_stdx.append(0)
        self.roi_varx.append(0)
        self.roi_cvx.append(0)

        self.roi_Ny.append(0)
        self.roi_meany.append(0)
        self.roi_stdy.append(0)
        self.roi_vary.append(0)
        self.roi_cvy.append(0)

        self.gate_graph_fs.append(HistogramView(f"{self.roi_label[self.num_roi].toPlainText()} xpoints"))
        self.gate_graph_ss.append(HistogramView(f"{self.roi_label[self.num_roi].toPlainText()} ypoints"))

        self.num_roi += 1

        self.update_stats()
        #TODO:  Fixed variable call if needed
        if self.sp.roi_table.isHidden():
            self.sp.roi_table.show()

        self.update_gates_popup()

    #NOTE: This exists purely to signal that the gates have been changed
    def changed(self, n, x):
        self.update_roi[n] = True

    def reset_graph(self):
        """
        This is a method that is called to reset the entire data set displayed in the scatter plot
        """
        self.data_set = []
        self.total_events_in_gatecall_x = 0
        self.total_events_in_gatecall_y = 0

    def update_stats(self):
        """
        This is a method that is called to add to the displayed statistics tabel when a new gate is
        added
        """
        i = len(self.roi_data)
        self.roi_data.append({'Gate': [f'{self.roi_label[i].toPlainText()}', ''],
            'CV': [f'{self.safe_divide(self.roi_stdx[i], self.roi_meanx[i])*100: .3f}', f'{self.safe_divide(self.roi_stdy[i], self.roi_meany[i])*100: .3f}'],
            'std': [f'{self.roi_stdx[i]: .3f}', f'{self.roi_stdy[i]: .3f}'], 'var': [f'{self.roi_varx[i]: .5f}',f'{self.roi_vary[i]: .5f}'],
            'mean': [f'{self.roi_meanx[i]: .3f}', f'{self.roi_meany[i]: .3f}'], 'N': [f'{self.roi_Nx[i]: .3f}', f'{self.roi_Ny[i]: .3f}'],
            'TotalEvents': [f'{self.total_events_in_gatecall_x}', f'{self.total_events_in_gatecall_y}']})
        self.sp.roi_table.setData(self.roi_data)

    def safe_divide(self, a, b):
        """
        This method is a safe divide to prevent and divisons by 0, this prevents warning outputs
        """
        if np.isclose(b, 0):
            return 0.
        else:
            return a/b

    def channel_changed(self):
        self.reset_graph()
        self.scatter_math.parameter_changed()

    def update_gates_popup(self):
        """!
        This method is used to update the view of histograms when a new gate is added

        Assigns: None

        Inputs: None
        Outputs: None
        """
        popup_widget = QWidget()
        popup_layout = QGridLayout()
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(popup_widget)
        scroll_area.setWidgetResizable(True)

        # self.gate_graph_popup_window.setWidget(popup_widget)
        self.sp.gate_graph_popup_window.setWidget(scroll_area)

        for i in range(self.num_roi):
            popup_layout.addWidget(self.gate_graph_fs[i], i, 0)
            popup_layout.addWidget(self.gate_graph_ss[i], i, 1)
    
        popup_widget.setLayout(popup_layout)

    def show_gates_popup(self):
        if self.num_roi > 0 and self.sp.gate_graph_popup_window.isHidden():
            self.sp.gate_graph_popup_window.show()
        else:
            self.sp.gate_graph_popup_window.hide()

    def load(self, newchannels):
        """!
        This method replaces all items in the channel select drop downs in a circular manner
        """
        self.names = [newchannels[x][-1] for x in range(len(newchannels))]
        for i in range(len(self.names)):
            self.sp.ch1select.removeItem(0)
            self.sp.ch2select.removeItem(0)
            self.sp.triggerchannelselect.removeItem(0)
            self.sp.ch1select.addItem(self.names[i])
            self.sp.ch2select.addItem(self.names[i])
            self.sp.triggerchannelselect.addItem(self.names[i])   

    def safe_divide(self, a, b):
        """!
        This method is a safe divide to prevent and divisons by 0, this prevents warning outputs

        Assigns: None

        Inputs:  
            A:              (float) This is an input number that is the numerator
            B:              (float) This is an input number that is the denominator
        Outputs: 
            0 or divison:   (float) This is the output either returns a float or if it is a division
                            by 0 it returns 0
        """
        if np.isclose(b, 0):
            return 0.
        else:
            return a/b

    def live_update_plot(self):
    # def live_update_plot(self, points):
        #TODO:  This should just draw the new items all other information should happen in yet 
        #       another thread, this will only exist like this until most math is placed in fpga but
        #       all graph/gate math will have to exit here
        """
        """
        points = self.processor.get_latest_output()
        # print(f"csp points: {points}")
        
        #NOTE: set to be time based instead of every single event
        self.sp.data_set.extend(points)
        self.sp.data_set = self.sp.data_set[-self.sp.sample_size:]

        self.sp.total_events_in_gatecall_x += len(points)
        self.sp.total_events_in_gatecall_y += len(points)

        
        #NOTE:  This is a timer that goes off at a refresh rate of roughly 30Hz, this allows the 
        #       program to run with any DAQ Event window and populate the UI without any slow down, 
        #       this also allows gates to be added and not affect the UI or main thread. One thing 
        #       to note is that the current way that gate path logic is done is kinda slow, over 
        #       time it would be ideal to look into if this is the best method but at this time it 
        #       should work just fine.
        if self.timeCurr <= time.time():
            self.timeCurr += (1/30)
        
            x, y = list(zip(*self.sp.data_set))
            # print(f"x: {x}, y: {y}")
        
            self.sp.H, self.sp.xedges, self.sp.yedges = np.histogram2d(x,y,bins=self.sp.num_bins)
            self.xstep = self.sp.xedges[1] - self.sp.xedges[0]
            self.ystep = self.sp.yedges[1] - self.sp.yedges[0]
            
            #TODO: move this into the gate_backend
            if(self.num_roi > 0):
                self.roiChanged()

                q = QtCore.QPointF()
                #NOTE:  When it comes to final product this for loop in its entirety should be 
                #       changed to be parallelized in gpu processing
                for i in range(self.sp.num_roi):
                    shape = self.sp.roi_shape[i]
                    pts_x = []
                    pts_y = []
                    # for p in self.data_set:
                    for t in range(len(x)):
                        q.setX(x[t])
                        q.setY(y[t])
                        if shape.contains(q):
                            pts_x.append(q.x())
                            pts_y.append(q.y())

                    self.sp.roi[i].xpts = pts_x
                    self.sp.roi[i].ypts = pts_y

                    self.sp.gate_graph_fs[i].data_set = self.sp.roi[i].xpts
                    self.sp.gate_graph_ss[i].data_set = self.sp.roi[i].ypts
                    self.sp.gate_graph_fs[i].live_update_plot()
                    self.sp.gate_graph_ss[i].live_update_plot()
                    
                    #TODO: Make all stats a list object and then make it so that each are appeneded when a new gate is added
                    self.sp.roi_Nx[i] = len(self.sp.roi[i].xpts)
                    self.sp.roi_meanx[i] = np.mean(self.sp.roi[i].xpts)
                    self.sp.roi_stdx[i] = np.std(self.sp.roi[i].xpts)
                    self.sp.roi_varx[i] = np.var(self.sp.roi[i].xpts)
                    self.sp.roi_cvx[i] = self.sp.roi_stdx[i] / self.sp.roi_meanx[i]
                    
                    self.sp.roi_Ny[i] = len(self.sp.roi[i].ypts)
                    self.sp.roi_meany[i] = np.mean(self.sp.roi[i].ypts)
                    self.sp.roi_stdy[i] = np.std(self.sp.roi[i].ypts)
                    self.sp.roi_vary[i] = np.var(self.sp.roi[i].ypts)
                    self.sp.roi_cvy[i] = self.sp.roi_stdy[i] / self.sp.roi_meany[i]
        
                    self.sp.roi_data[i] = ({'Gate': [f'{self.sp.roi_label[i].toPlainText()}', ''],
                        'CV': [f'{self.safe_divide(self.sp.roi_stdx[i], self.sp.roi_meanx[i])*100: .3f}', f'{self.safe_divide(self.sp.roi_stdy[i], self.sp.roi_meany[i])*100: .3f}'],
                        'std': [f'{self.sp.roi_stdx[i]: .3f}', f'{self.sp.roi_stdy[i]: .3f}'], 'var': [f'{self.sp.roi_varx[i]: .5f}',f'{self.sp.roi_vary[i]: .5f}'],
                        'mean': [f'{self.sp.roi_meanx[i]: .3f}', f'{self.sp.roi_meany[i]: .3f}'], 'N': [f'{self.sp.roi_Nx[i]: .3f}', f'{self.sp.roi_Ny[i]: .3f}'],
                        'TotalEvents': [f'{self.sp.total_events_in_gatecall_x}', f'{self.sp.total_events_in_gatecall_y}']})
                self.sp.roi_table.setData(self.sp.roi_data)

            self.sp.scatterplot.updateImage(self.sp.H)
    
