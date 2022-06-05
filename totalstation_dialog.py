# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TotalopenstationDialog
                                 A QGIS plugin
 Total Open Station (TOPS for friends) is a free software program for downloading and processing data from total station devices.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-09-01
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Enzo Cocca adArte srl; Stefano Costa
        email                : enzo.ccc@gmail.com
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from datetime import date
import pandas as pd
import subprocess
import platform
import csv
import tempfile
import textwrap as tr
from qgis.PyQt.uic import loadUiType
from qgis.PyQt import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import  *
from qgis.PyQt.QtWidgets import QVBoxLayout, QApplication, QDialog, QMessageBox, QFileDialog,QLineEdit,QWidget,QCheckBox,QProgressBar,QInputDialog
from qgis.PyQt.QtSql import *
from qgis.PyQt import  QtWidgets
from qgis.core import  *
from qgis.gui import  *
#from qgis.utils import iface
FORM_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__),'totalstation_dialog_base.ui'))
class TotalopenstationDialog(QDialog, FORM_CLASS):


    def __init__(self, parent=None):
        """Constructor."""
        super(TotalopenstationDialog, self).__init__(parent)
        self.setupUi(self)
        #self.iface = iface
        #self.canvas = iface.mapCanvas()

        self.model = QtGui.QStandardItemModel(self)
        self.tableView.setModel(self.model)
        self.toolButton_input.clicked.connect(self.setPathinput)
        self.toolButton_output.clicked.connect(self.setPathoutput)
        self.toolButton_save_raw.clicked.connect(self.setPathsaveraw)
        self.mDockWidget.setHidden(True)
        self.comboBox_model.currentIndexChanged.connect(self.tt)
        self.lineEdit_save_raw.textChanged.connect(self.connect)
        self.pushButton_connect.setEnabled(False)

    def connect(self):


        if str(self.lineEdit_save_raw.text()):

            self.pushButton_connect.setEnabled(True)

        else:
            self.pushButton_connect.setEnabled(False)


    def tt(self):
        if self.comboBox_model.currentIndex()!=6:

            self.mDockWidget.setHidden(True)
        else:

            self.mDockWidget.show()

    def setPathinput(self):
        s = QgsSettings()
        input_ = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            '',
            "(*.*)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if input_:

            self.lineEdit_input.setText(input_)
            s.setValue('',input_)

    def setPathoutput(self):
        s = QgsSettings()
        output_ = QFileDialog.getSaveFileName(
            self,
            "Set file name",
            '',
            "(*.{})".format(self.comboBox_format2.currentText())
        )[0]
        #filename=dbpath.split("/")[-1]
        if output_:

            self.lineEdit_output.setText(output_)
            s.setValue('',output_)

    def setPathsaveraw(self):
        s = QgsSettings()
        output_ = QFileDialog.getSaveFileName(
            self,
            "Set file name",
            '',
            "(*.tops)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if output_:

            self.lineEdit_save_raw.setText(output_)
            s.setValue('',output_)

    def loadCsv(self, fileName):
        self.tableView.clearSpans()

        with open(fileName, "r") as fileInput:
            for row in csv.reader(fileInput):

                items = [
                    QtGui.QStandardItem(field)
                    for field in row
                ]
                self.model.appendRow(items)



    def delete(self):
        if self.tableView.selectionModel().hasSelection():
            indexes =[QPersistentModelIndex(index) for index in self.tableView.selectionModel().selectedRows()]
            for index in indexes:
                #print('Deleting row %d...' % index.row())
                self.model.removeRow(index.row())


    def check_port(self):

        p = subprocess.Popen( 'python -m serial.tools.list_ports',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)



        output, error = p.communicate(str.encode("utf-8"))
        output = output.decode('utf-8').splitlines()
        #error= error.decode('utf-8').splitlines()
        return output

    def listtostr(self):

        str1 = ""

        # traverse in the string
        for ele in self.check_port():
            str1 += ele
        return str1
    def on_pushButton_check_port_pressed(self):
        self.textEdit.appendPlainText('Wait a moment....')
        lines = tr.wrap(str(self.listtostr()), width=10)
        #self.textEdit.clear()
        self.textEdit.appendPlainText('Ports found:\n'+str(lines))
        self.comboBox_port.addItems(lines)
    def convert_csv(self):
        try:
            df = pd.read_csv(str(self.lineEdit_output.text()))
            df[['area_q', 'point_name']] = df['point_name'].str.split('-', expand=True)
            df.to_csv(str(self.lineEdit_output.text()), encoding='utf-8', index=False)
        except:
            pass
    def on_pushButton_export_pressed(self):

        self.delete()
        if platform.system() == "Windows":
            b=QgsApplication.qgisSettingsDirPath().replace("/","\\")


            cmd = os.path.join(os.sep, b, 'python', 'plugins', 'totalopenstationToQgis', 'scripts', 'totalopenstation-cli-parser.py')
            cmd2= ' -i '+str(self.lineEdit_input.text())+' '+'-o '+str(self.lineEdit_output.text())+' '+'-f'+' '+self.comboBox_format.currentText()+' '+'-t'+' '+self.comboBox_format2.currentText()+' '+'--overwrite'
            try:#os.system("start cmd /k" + ' python ' +cmd+' '+cmd2)
                p=subprocess.check_call(['python',cmd, '-i',str(self.lineEdit_input.text()),'-o',str(self.lineEdit_output.text()),'-f',self.comboBox_format.currentText(),'-t',self.comboBox_format2.currentText(),'--overwrite'], shell=True)




                if self.comboBox_format2.currentIndex()== 0:

                    layer = QgsVectorLayer(str(self.lineEdit_output.text()), 'totalopenstation', 'ogr')

                    layer.isValid()

                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station luncher',
                                              'data loaded into panel Layer', QMessageBox.Ok)

                    self.progressBar.reset()
                    temp=tempfile.mkstemp(suffix = '.csv')
                    QgsVectorFileWriter.writeAsVectorFormat(layer, 'test.csv', "utf-8", driverName = "CSV")

                    self.loadCsv('test.csv')
                elif self.comboBox_format2.currentIndex()== 1:

                    layer = QgsVectorLayer(str(self.lineEdit_output.text()), 'totalopenstation', 'ogr')

                    layer.isValid()


                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station luncher',
                                              'data loaded into panel Layer', QMessageBox.Ok)
                    self.progressBar.reset()
                    temp=tempfile.mkstemp(suffix = '.csv')
                    QgsVectorFileWriter.writeAsVectorFormat(layer, 'test.csv', "utf-8", driverName = "CSV")
                    self.loadCsv('test.csv')

                elif self.comboBox_format2.currentIndex()== 2:

                    self.convert_csv()
                    uri = "file:///"+str(self.lineEdit_output.text())+"?type=csv&xField=x&yField=y&spatialIndex=yes&subsetIndex=yes&watchFile=no"
                    layer = QgsVectorLayer(uri, "totalopenstation Pyarchinit Quote", "delimitedtext")


                    layer.isValid()


                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station',
                                              'data loaded into panel Layer', QMessageBox.Ok)


                    self.loadCsv(str(self.lineEdit_output.text()))



                    '''copy and past from totalstation to pyarchinit'''
                    sourceLYR = QgsProject.instance().mapLayersByName('totalopenstation Pyarchinit Quote')[0]
                    destLYR = QgsProject.instance().mapLayersByName('Quote US disegno')[0]
                    #Dialog Box for input "name sito archeologico" to select it...
                    ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
                    Sito = str(ID_Sito[0])
                    ID_M = QInputDialog.getText(None, 'Unità di misura', 'Input tipo di unità di misura\n (ex: metri)')
                    Misura = str(ID_M[0])
                    ID_Disegnatore = QInputDialog.getText(None, 'Disegnatore', 'Input Nome del Disegnatore')
                    Disegnatore = str(ID_Disegnatore[0])
                    features = []
                    if self.checkBox_coord.isChecked():
                        # ID_X = QInputDialog.getText(None, 'X', 'Input coord X')
                        # x = float(ID_X[0])
                        # ID_Y = QInputDialog.getText(None, 'Y', 'Input Coord Y')
                        # y = float(ID_Y[0])
                        ID_Z = QInputDialog.getText(None, 'Z', 'Input Elevation')
                        q = float(ID_Z[0])


                        # expression1 = QgsExpression('x($geometry)+{}'.format(x))
                        # expression2 = QgsExpression('y($geometry)+{}'.format(y))
                        # context = QgsExpressionContext()
                        # scope = QgsExpressionContextScope()
                        # context.appendScope(scope)

                        for feature in sourceLYR.getFeatures():
                            # scope.setFeature(feature)
                            # a = expression1.evaluate(context)
                            # b = expression2.evaluate(context)
                            # if a and b:
                            features.append(feature)
                            feature.setAttribute('sito_q', Sito)
                            feature.setAttribute('unita_misu_q', Misura)
                            feature.setAttribute('x', str(date.today().isoformat()))
                            feature.setAttribute('y', Disegnatore)
                            attr_Q = feature.attributes()[5]
                            p = q + float(attr_Q)

                            feature.setAttribute('quota_q', p)

                            # geom = feature.geometry()
                            # geom.get().setX(a)
                            # geom.get().setY(b)

                            # feature.setGeometry(geom)
                            sourceLYR.updateFeature(feature)
                        destLYR.startEditing()
                        data_provider = destLYR.dataProvider()
                        data_provider.addFeatures(features)
                        iface.mapCanvas().zoomToSelected()
                        destLYR.commitChanges()
                    else:
                        for feature in sourceLYR.getFeatures():

                            features.append(feature)
                            feature.setAttribute('sito_q', Sito)
                            feature.setAttribute('unita_misu_q', Misura)
                            feature.setAttribute('x', str(date.today().isoformat()))
                            feature.setAttribute('y', Disegnatore)

                            sourceLYR.updateFeature(feature)
                        destLYR.startEditing()
                        data_provider = destLYR.dataProvider()
                        data_provider.addFeatures(features)
                        iface.mapCanvas().zoomToSelected()
                        destLYR.commitChanges()

                    QgsProject.instance().removeMapLayer(sourceLYR)
                    ###########finish############################################


                elif self.comboBox_format2.currentIndex()== 3:


                    uri = "file:///"+str(self.lineEdit_output.text())+"?type=csv&xField=x&yField=y&spatialIndex=yes&subsetIndex=yes&watchFile=no"
                    layer = QgsVectorLayer(uri, "totalopenstation Pyarchinit riferimento", "delimitedtext")


                    layer.isValid()


                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station',
                                              'data loaded into panel Layer', QMessageBox.Ok)


                    self.loadCsv(str(self.lineEdit_output.text()))



                    '''copy and past from totalstation to pyarchinit'''
                    sourceLYR = QgsProject.instance().mapLayersByName('totalopenstation Pyarchinit riferimento')[0]
                    destLYR = QgsProject.instance().mapLayersByName('Punti di riferimento')[0]


                    #Dialog Box for input "name sito archeologico" to select it...
                    ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
                    Sito = str(ID_Sito[0])
                    features = []
                    if self.checkBox_coord.isChecked():
                        # ID_X = QInputDialog.getText(None, 'X', 'Input coord X')
                        # x = float(ID_X[0])
                        # ID_Y = QInputDialog.getText(None, 'Y', 'Input Coord Y')
                        # y = float(ID_Y[0])
                        ID_Z = QInputDialog.getText(None, 'Z', 'Input Elevation')
                        q = float(ID_Z[0])



                        # expression1 = QgsExpression('x($geometry)+{}'.format(x))
                        # expression2 = QgsExpression('y($geometry)+{}'.format(y))
                        # context = QgsExpressionContext()
                        # scope = QgsExpressionContextScope()
                        # context.appendScope(scope)

                        for feature in sourceLYR.getFeatures():
                            # scope.setFeature(feature)
                            # a = expression1.evaluate(context)
                            # b = expression2.evaluate(context)
                            # if a and b:
                            features.append(feature)

                            feature.setAttribute('sito', Sito)
                            attr_Q = feature.attributes()[4]
                            p=q + float(attr_Q)

                            feature.setAttribute('quota', p)

                                # geom = feature.geometry()
                                # geom.get().setX(a)
                                # geom.get().setY(b)


                                # feature.setGeometry(geom)
                            sourceLYR.updateFeature(feature)

                        destLYR.startEditing()
                        data_provider = destLYR.dataProvider()
                        data_provider.addFeatures(features)
                        iface.mapCanvas().zoomToSelected()
                        destLYR.commitChanges()


                    else:

                        features = []
                        for feature in sourceLYR.getFeatures():
                            features.append(feature)
                            feature.setAttribute('sito', Sito)
                            sourceLYR.updateFeature(feature)


                        destLYR.startEditing()
                        data_provider = destLYR.dataProvider()
                        data_provider.addFeatures(features)
                        iface.mapCanvas().zoomToSelected()
                        destLYR.commitChanges()


                    QgsProject.instance().removeMapLayer(sourceLYR)
                    ###########finish############################################


                elif self.comboBox_format2.currentIndex()== 4:


                    uri = "file:///"+str(self.lineEdit_output.text())+"?type=csv&xField=x&yField=y&spatialIndex=yes&subsetIndex=yes&watchFile=no"
                    layer = QgsVectorLayer(uri, "totalopenstation Pyarchinit Sample", "delimitedtext")


                    layer.isValid()


                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station',
                                              'data loaded into panel Layer', QMessageBox.Ok)


                    self.loadCsv(str(self.lineEdit_output.text()))



                    '''copy and past from totalstation to pyarchinit'''
                    sourceLYR = QgsProject.instance().mapLayersByName('totalopenstation Pyarchinit Sample')[0]
                    destLYR = QgsProject.instance().mapLayersByName('Punti di campionatura')[0]
                    # Dialog Box for input "name sito archeologico" to select it...
                    ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
                    Sito = str(ID_Sito[0])
                    # a=[]
                    if self.checkBox_coord.isChecked():
                        # ID_X = QInputDialog.getText(None, 'X', 'Input coord X')
                        # x = float(ID_X[0])
                        # ID_Y = QInputDialog.getText(None, 'Y', 'Input Coord Y')
                        # y = float(ID_Y[0])


                        features = []
                        # expression1 = QgsExpression('x($geometry)+{}'.format(x))
                        # expression2 = QgsExpression('y($geometry)+{}'.format(y))
                        # context = QgsExpressionContext()
                        # scope = QgsExpressionContextScope()
                        # context.appendScope(scope)

                        for feature in sourceLYR.getFeatures():
                            # scope.setFeature(feature)
                            # a = expression1.evaluate(context)
                            # b = expression2.evaluate(context)
                            # if a and b:
                            features.append(feature)

                            feature.setAttribute('sito', Sito)
                            # geom = feature.geometry()
                            # geom.get().setX(a)
                            # geom.get().setY(b)

                            # feature.setGeometry(geom)
                            sourceLYR.updateFeature(feature)

                        destLYR.startEditing()
                        data_provider = destLYR.dataProvider()
                        data_provider.addFeatures(features)
                        iface.mapCanvas().zoomToSelected()
                        destLYR.commitChanges()


                    else:

                        features = []
                        for feature in sourceLYR.getFeatures():
                            features.append(feature)
                            feature.setAttribute('sito', Sito)
                            sourceLYR.updateFeature(feature)

                        destLYR.startEditing()
                        data_provider = destLYR.dataProvider()
                        data_provider.addFeatures(features)
                        iface.mapCanvas().zoomToSelected()
                        destLYR.commitChanges()

                    QgsProject.instance().removeMapLayer(sourceLYR)
                    ###########finish############################################

                elif self.comboBox_format2.currentIndex()== 5:
                    uri = "file:///"+str(self.lineEdit_output.text())+"?type=csv&xField=x&yField=y&spatialIndex=no&subsetIndex=no&watchFile=no"
                    layer1 = QgsVectorLayer(uri, 'totalopenstation', "delimitedtext")

                    #layer.isValid()


                    QgsProject.instance().addMapLayer(layer1)

                    QMessageBox.warning(self, 'Total Open Station',
                                              'data loaded into panel Layer', QMessageBox.Ok)


                    self.loadCsv(str(self.lineEdit_output.text()))




                else:

                    pass

            except Exception as e:

                QMessageBox.warning(self, 'Total Open Station',
                                          "Error:\n"+str(e), QMessageBox.Ok)
        else:
            try:  # os.system("start cmd /k" + ' python ' +cmd+' '+cmd2)
                p = subprocess.check_call(
                    ['python', cmd, '-i', str(self.lineEdit_input.text()), '-o', str(self.lineEdit_output.text()), '-f',
                     self.comboBox_format.currentText(), '-t', self.comboBox_format2.currentText(), '--overwrite'],
                    shell=True)

                if self.comboBox_format2.currentIndex() == 0:

                    layer = QgsVectorLayer(str(self.lineEdit_output.text()), 'totalopenstation', 'ogr')

                    layer.isValid()

                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station luncher',
                                        'data loaded into panel Layer', QMessageBox.Ok)

                    self.progressBar.reset()
                    temp = tempfile.mkstemp(suffix='.csv')
                    QgsVectorFileWriter.writeAsVectorFormat(layer, 'test.csv', "utf-8", driverName="CSV")

                    self.loadCsv('test.csv')
                elif self.comboBox_format2.currentIndex() == 1:

                    layer = QgsVectorLayer(str(self.lineEdit_output.text()), 'totalopenstation', 'ogr')

                    layer.isValid()

                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station luncher',
                                        'data loaded into panel Layer', QMessageBox.Ok)
                    self.progressBar.reset()
                    temp = tempfile.mkstemp(suffix='.csv')
                    QgsVectorFileWriter.writeAsVectorFormat(layer, 'test.csv', "utf-8", driverName="CSV")
                    self.loadCsv('test.csv')

                elif self.comboBox_format2.currentIndex() == 2:

                    self.convert_csv()
                    uri = "file:///" + str(
                        self.lineEdit_output.text()) + "?type=csv&xField=x&yField=y&spatialIndex=yes&subsetIndex=yes&watchFile=no"
                    layer = QgsVectorLayer(uri, "totalopenstation Pyarchinit Quote", "delimitedtext")

                    layer.isValid()

                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station',
                                        'data loaded into panel Layer', QMessageBox.Ok)

                    self.loadCsv(str(self.lineEdit_output.text()))

                    '''copy and past from totalstation to pyarchinit'''
                    sourceLYR = QgsProject.instance().mapLayersByName('totalopenstation Pyarchinit Quote')[0]
                    destLYR = QgsProject.instance().mapLayersByName('Quote US disegno')[0]
                    # Dialog Box for input "name sito archeologico" to select it...
                    ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
                    Sito = str(ID_Sito[0])
                    ID_M = QInputDialog.getText(None, 'Unità di misura', 'Input tipo di unità di misura\n (ex: metri)')
                    Misura = str(ID_M[0])
                    ID_Disegnatore = QInputDialog.getText(None, 'Disegnatore', 'Input Nome del Disegnatore')
                    Disegnatore = str(ID_Disegnatore[0])

                    if self.checkBox_coord.isChecked():
                        ID_X = QInputDialog.getText(None, 'X', 'Input coord X')
                        x = float(ID_X[0])
                        ID_Y = QInputDialog.getText(None, 'Y', 'Input Coord Y')
                        y = float(ID_Y[0])
                        ID_Z = QInputDialog.getText(None, 'Z', 'Input Elevation')
                        q = float(ID_Z[0])

                        features = []
                        expression1 = QgsExpression('x($geometry)+{}'.format(x))
                        expression2 = QgsExpression('y($geometry)+{}'.format(y))
                        context = QgsExpressionContext()
                        scope = QgsExpressionContextScope()
                        context.appendScope(scope)

                        for feature in sourceLYR.getFeatures():
                            scope.setFeature(feature)
                            a = expression1.evaluate(context)
                            b = expression2.evaluate(context)
                            if a and b:
                                features.append(feature)
                                feature.setAttribute('sito_q', Sito)
                                feature.setAttribute('unita_misu_q', Misura)
                                feature.setAttribute('x', str(date.today().isoformat()))
                                feature.setAttribute('y', Disegnatore)
                                attr_Q = feature.attributes()[5]
                                p = q + float(attr_Q)

                                feature.setAttribute('quota_q', p)

                                geom = feature.geometry()
                                geom.get().setX(a)
                                geom.get().setY(b)

                                feature.setGeometry(geom)
                                sourceLYR.updateFeature(feature)
                            destLYR.startEditing()
                            data_provider = destLYR.dataProvider()
                            data_provider.addFeatures(features)
                            iface.mapCanvas().zoomToSelected()
                            destLYR.commitChanges()
                    else:
                        for feature in sourceLYR.getFeatures():
                            features.append(feature)
                            feature.setAttribute('sito_q', Sito)
                            feature.setAttribute('unita_misu_q', Misura)
                            feature.setAttribute('x', str(date.today().isoformat()))
                            feature.setAttribute('y', Disegnatore)

                            sourceLYR.updateFeature(feature)
                        destLYR.startEditing()
                        data_provider = destLYR.dataProvider()
                        data_provider.addFeatures(features)
                        iface.mapCanvas().zoomToSelected()
                        destLYR.commitChanges()

                    QgsProject.instance().removeMapLayer(sourceLYR)
                    ###########finish############################################


                elif self.comboBox_format2.currentIndex() == 3:

                    uri = "file:///" + str(
                        self.lineEdit_output.text()) + "?type=csv&xField=x&yField=y&spatialIndex=yes&subsetIndex=yes&watchFile=no"
                    layer = QgsVectorLayer(uri, "totalopenstation Pyarchinit riferimento", "delimitedtext")

                    layer.isValid()

                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station',
                                        'data loaded into panel Layer', QMessageBox.Ok)

                    self.loadCsv(str(self.lineEdit_output.text()))

                    '''copy and past from totalstation to pyarchinit'''
                    sourceLYR = QgsProject.instance().mapLayersByName('totalopenstation Pyarchinit riferimento')[0]
                    destLYR = QgsProject.instance().mapLayersByName('Punti di riferimento')[0]

                    # Dialog Box for input "name sito archeologico" to select it...
                    ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
                    Sito = str(ID_Sito[0])
                    # a=[]
                    if self.checkBox_coord.isChecked():
                        ID_X = QInputDialog.getText(None, 'X', 'Input coord X')
                        x = float(ID_X[0])
                        ID_Y = QInputDialog.getText(None, 'Y', 'Input Coord Y')
                        y = float(ID_Y[0])
                        ID_Z = QInputDialog.getText(None, 'Z', 'Input Elevation')
                        q = float(ID_Z[0])

                        features = []
                        expression1 = QgsExpression('x($geometry)+{}'.format(x))
                        expression2 = QgsExpression('y($geometry)+{}'.format(y))
                        context = QgsExpressionContext()
                        scope = QgsExpressionContextScope()
                        context.appendScope(scope)

                        for feature in sourceLYR.getFeatures():
                            scope.setFeature(feature)
                            a = expression1.evaluate(context)
                            b = expression2.evaluate(context)
                            if a and b:
                                features.append(feature)

                                feature.setAttribute('sito', Sito)
                                attr_Q = feature.attributes()[4]
                                p = q + float(attr_Q)

                                feature.setAttribute('quota', p)

                                geom = feature.geometry()
                                geom.get().setX(a)
                                geom.get().setY(b)

                                feature.setGeometry(geom)
                                sourceLYR.updateFeature(feature)

                        destLYR.startEditing()
                        data_provider = destLYR.dataProvider()
                        data_provider.addFeatures(features)
                        iface.mapCanvas().zoomToSelected()
                        destLYR.commitChanges()


                    else:

                        features = []
                        for feature in sourceLYR.getFeatures():
                            features.append(feature)
                            feature.setAttribute('sito', Sito)
                            sourceLYR.updateFeature(feature)

                        destLYR.startEditing()
                        data_provider = destLYR.dataProvider()
                        data_provider.addFeatures(features)
                        iface.mapCanvas().zoomToSelected()
                        destLYR.commitChanges()

                    QgsProject.instance().removeMapLayer(sourceLYR)
                    ###########finish############################################


                elif self.comboBox_format2.currentIndex() == 4:

                    uri = "file:///" + str(
                        self.lineEdit_output.text()) + "?type=csv&xField=x&yField=y&spatialIndex=yes&subsetIndex=yes&watchFile=no"
                    layer = QgsVectorLayer(uri, "totalopenstation Pyarchinit Sample", "delimitedtext")

                    layer.isValid()

                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station',
                                        'data loaded into panel Layer', QMessageBox.Ok)

                    self.loadCsv(str(self.lineEdit_output.text()))

                    '''copy and past from totalstation to pyarchinit'''
                    sourceLYR = QgsProject.instance().mapLayersByName('totalopenstation Pyarchinit Sample')[0]
                    destLYR = QgsProject.instance().mapLayersByName('Punti di campionatura')[0]
                    # Dialog Box for input "name sito archeologico" to select it...
                    ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
                    Sito = str(ID_Sito[0])
                    # a=[]
                    if self.checkBox_coord.isChecked():
                        ID_X = QInputDialog.getText(None, 'X', 'Input coord X')
                        x = float(ID_X[0])
                        ID_Y = QInputDialog.getText(None, 'Y', 'Input Coord Y')
                        y = float(ID_Y[0])

                        features = []
                        expression1 = QgsExpression('x($geometry)+{}'.format(x))
                        expression2 = QgsExpression('y($geometry)+{}'.format(y))
                        context = QgsExpressionContext()
                        scope = QgsExpressionContextScope()
                        context.appendScope(scope)

                        for feature in sourceLYR.getFeatures():
                            scope.setFeature(feature)
                            a = expression1.evaluate(context)
                            b = expression2.evaluate(context)
                            if a and b:
                                features.append(feature)

                                feature.setAttribute('sito', Sito)
                                geom = feature.geometry()
                                geom.get().setX(a)
                                geom.get().setY(b)

                                feature.setGeometry(geom)
                                sourceLYR.updateFeature(feature)

                        destLYR.startEditing()
                        data_provider = destLYR.dataProvider()
                        data_provider.addFeatures(features)
                        iface.mapCanvas().zoomToSelected()
                        destLYR.commitChanges()


                    else:

                        features = []
                        for feature in sourceLYR.getFeatures():
                            features.append(feature)
                            feature.setAttribute('sito', Sito)
                            sourceLYR.updateFeature(feature)

                        destLYR.startEditing()
                        data_provider = destLYR.dataProvider()
                        data_provider.addFeatures(features)
                        iface.mapCanvas().zoomToSelected()
                        destLYR.commitChanges()

                    QgsProject.instance().removeMapLayer(sourceLYR)
                    ###########finish############################################

                elif self.comboBox_format2.currentIndex() == 5:
                    uri = "file:///" + str(
                        self.lineEdit_output.text()) + "?type=csv&xField=x&yField=y&spatialIndex=no&subsetIndex=no&watchFile=no"
                    layer1 = QgsVectorLayer(uri, 'totalopenstation', "delimitedtext")

                    # layer.isValid()

                    QgsProject.instance().addMapLayer(layer1)

                    QMessageBox.warning(self, 'Total Open Station',
                                        'data loaded into panel Layer', QMessageBox.Ok)

                    self.loadCsv(str(self.lineEdit_output.text()))




                else:

                    pass

            except Exception as e:

                QMessageBox.warning(self, 'Total Open Station',
                                    "Error:\n" + str(e), QMessageBox.Ok)

    def rmvLyr(lyrname):
        qinst = QgsProject.instance()
        qinst.removeMapLayer(qinst.mapLayersByName(lyrname)[0].id())
    def on_pushButton_connect_pressed(self):
        self.textEdit.clear()

        if platform.system() == "Windows":
            b=QgsApplication.qgisSettingsDirPath().replace("/","\\")
            cmd = os.path.join(os.sep, b , 'python', 'plugins', 'totalopenstationToQgis', 'scripts', 'totalopenstation-cli-connector.py')

            try:
                c=subprocess.check_call(['python', cmd,'-m',self.comboBox_model.currentText(),'-p',self.comboBox_port.currentText(),'-o',str(self.lineEdit_save_raw.text())], shell=True)



            except Exception as e:
                if self.comboBox_port.currentText()=='':
                    self.textEdit.appendPlainText('Insert port please!')

                self.textEdit.appendPlainText('Connection falied!')

            else:
                self.textEdit.appendPlainText('Connection OK.................!\n\n')
                self.textEdit.appendPlainText('Start dowload data.................!\n\n')
                #s = io.StringIO()
                #for i in tqdm(range(3), file=s):
                    #sleep(.1)
                #self.textEdit.appendPlainText(s.getvalue())

                self.textEdit.appendPlainText('Dowload finished.................!\n\n')
                self.textEdit.appendPlainText('Result:\n')
                r=open(str(self.lineEdit_save_raw.text()),'r')
                lines = r.read().split(',')
                self.textEdit.appendPlainText(str(lines))

        else:
            b=QgsApplication.qgisSettingsDirPath()
            cmd = os.path.join(os.sep, b , 'python', 'plugins', 'totalopenstationToQgis', 'scripts', 'totalopenstation-cli-connector.py')
            #os.system("start cmd /k" + ' python ' +cmd)
            try:
                c=subprocess.check_call(['python', cmd,'-m',self.comboBox_model.currentText(),'-p',self.comboBox_port.currentText(),'-o',str(self.lineEdit_save_raw.text())], shell=True)



            except Exception as e:
                if self.comboBox_port.currentText()=='':
                    self.textEdit.appendPlainText('Insert port please!')

                self.textEdit.appendPlainText('Connection falied!')

            else:
                self.textEdit.appendPlainText('Connection OK.................!\n\n\n')
                self.textEdit.appendPlainText('Start dowload data.................!\n\n\n')
                #s = io.StringIO()
                #for i in tqdm(range(3), file=s):
                    #sleep(.1)
                #self.textEdit.appendPlainTextPlainText(s.getvalue())

                self.textEdit.appendPlainText('Dowload finished.................!\n\n\n')
                self.textEdit.appendPlainText('Result:\n')
                r=open(str(self.lineEdit_save_raw.text()),'r')
                lines = r.read().split(',')
                self.textEdit.appendPlainText(str(lines))
