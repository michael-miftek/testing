from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem

class TableView(QTableWidget):
    """!
    Table widget that displays all calculated statistics for points inside of a user defined gate
    """
    def __init__(self, *args):
        """!
        Inputs:
            data:   This is list variable that holds all points that are inside of a user defined
                    gate. 
        
        Assigns:
            data:   This variable holds the data variable that is passed in to be displayed
        """
        QTableWidget.__init__(self, *args)
        self.data = []
        self.column_size = 0
        self.row_size = 0
 
    def setData(self, data): 
        """!
        This method sets statistics, that were calculated from a user defined gate, to the table
    
        Assigns:
            self.data
            HorizontalHeaderLabels
            
        Inputs:
            data    This variable is the list of all statistics calculated on a user defined gate   
        Outputs: None
        """
        horHeaders = []
        self.data = data
        for i in range(len(data)):
            for n, key in enumerate(self.data[i].keys()):
                horHeaders.append(key)
                for m, item in enumerate(self.data[i][key]):
                    newitem = QTableWidgetItem(item)
                    self.setItem(m + (i*2), n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)
        #NOTE:  This is a non hardcoded way to set this, since we know that we don't allow changing 
        #       the number of options externally and we dont use the first keys position because we 
        #       use toPlainText for the name so it returns a funky number
        self.setRowCount(len(self.data[0][list(self.data[0].keys())[1]]))
        self.setColumnCount(len(self.data[0].keys()))