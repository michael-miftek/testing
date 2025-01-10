


class GateUpdater(QObject):
    """
    This class will update all items having to do with the gates but will not calculate any of the 
    statistics that will be done in a different thread.

    The hope is that by spreading everything out like this it will allow things to run smoother
    """
    def __init__(self, scatterplot, scatterplotBackend):
        super().__init__()

        self.sp = scatterplot
        self.sp_backend = scatterplotBackend


        self.sp.show_gates_button.clicked.connect(self.show_gates_popup)

    
    def show_gates_popup(self):
        """!
        This method is connected to the push button (Show) to show or remove the histograms

        Assigns: None

        Inputs: None
        Outputs: None
        """
        if self.sp.gate_graph_popup_window.isHidden():
            self.sp.gate_graph_popup_window.show()
        else:
            self.sp.gate_graph_popup_window.hide()
 
    def roiChanged(self):
        """!
        This method is connected to the region of the gate being changed, and updates the position
        of the of the gate

        Assigns:
            roi_shape:  (QPainterPath) This is the path of points that make up the gate

        Inputs: None
        Outputs: None
        """
        for i in range(self.sp.num_roi):
            #NOTE:  This update in the line below allows the program to update for all gates that
            #       have been moved instead of all gates all the time, also the signal was changed
            #       from changed to changedfinished which also means that the roi path update is
            #       not getting called hundreds of times a second. This should be the final piece of
            #       the slow down
            if not self.sp.update_roi[i]: 
                continue
            ##  Adding a work around for using shape method there is an isue where it does not 
            #   update with the current position so the stats are only ever around where it was 
            #   originally created regardless of where it has been moved to
            
            #   First we setup the QPainterPath to use the contains method later, but then the
            #   position and the height and width will also need to be grabbed and added to which
            #   ever functin we need to use.
            #   Ellipse and circle  -> addEllipse
            #   Rect                -> addRect
            #   Beacuse we are now working with a 2d histo we have to account for everything being 
            #   transposed
            self.sp.update_roi[i] = False
            path = QtGui.QPainterPath()
            x,y = self.sp.roi[i].pos()
            w,h = self.sp.roi[i].size()

            w *= self.xstep
            h *= self.ystep
            diffx = x - int(x)
            diffy = y - int(y)
            x = self.sp.xedges[int(x)] + (diffx * self.xstep)
            y = self.sp.yedges[int(y)] + (diffy * self.ystep)

            # print(type(self.roi[i]))
            if(isinstance(self.sp.roi[i], ROI.EllipseROI)):
                path.addEllipse(x,y,w,h)
            elif(isinstance(self.sp.roi[i], ROI.RectROI)):
                path.addRect(x,y,w,h)

            self.sp.roi_shape[i] = path