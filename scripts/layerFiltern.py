# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterString,
                       QgsProcessingFeedback,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterField,
                       QgsProcessingParameterVectorLayer)
from qgis import (processing,utils)
from qgis.core import (QgsMessageLog,QgsProject)

class alleLayerFilter(QgsProcessingAlgorithm):
    # Funktionsübergreifende Namen für die Variablen
    INPUT = 'INPUT'
    FINPUT = 'FINPUT'
    FILTER = 'FILTER'
    FILTERATT = 'FILTERATT'
    OPERATOR = 'OPERATOR'
    #OPERATORX = 'OPERATORX'   # Wird nicht mehr benötigt da der Verknüpfungsoperator direkt vom logischen Operator abhängig ist
    OPERATORS  = ['=','!=']
    #OPERATORSX  = ['AND','OR'] # Wird nicht mehr benötigt da der Verknüpfungsoperator direkt vom logischen Operator abhängig ist
    METHODE = 'METHODE'
    METHODES = ['0','1']
    
    def tr(self, string):        
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return alleLayerFilter()

    def name(self):        
        return 'alleLayerFilter'

    def displayName(self):        
        return self.tr('Layer filtern')
    
    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def shortHelpString(self):        
        return self.tr("Mit diesem Script können mehrere Layer gefiltert werden."+'\n'\
        +"Sie können mehrere Layer auswählen, die alle mit den eingetragenen Werten gefiltert werden. Mehrere Filter-Werte sind mit Kommata zu trennen."+'\n'\
        +"Wählen Sie zum Löschen der Filter die gefilterten Layer und die Methode \'Filter Löschen\' aus."+'\n'\
        +"1. Methode wählen"+'\n'\
        +"2. Layer wählen (Mehrfachauswahl möglich)"+'\n'\
        +"3. Filter-Attribut wählen"+'\n'\
        +"4. Filter-Werte eintragen (mit Komma getrennt)")
    
    def shortDescription(self):
        return self.tr("Mit diesem Script können mehrere Layer gefiltert werden")
    
    def initAlgorithm(self, config=None):
        self.operators = ['=','≠']
        #self.operatorsX = ['AND','OR'] # Wird nicht mehr benötigt da der Verknüpfungsoperator direkt vom logischen Operator abhängig ist
        self.methoden = ['Filtern','Filter Löschen']
        
        # Methode: Filtern oder Filter löschen
        self.addParameter(
            QgsProcessingParameterEnum(
            name = self.METHODE,
            description  = self.tr('Methode'),
            options = self.methoden,
            defaultValue = 0
            )
        )
        
        # Inputlayer, auch Mehrfachauswahl ist möglich
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                name = self.INPUT,
                description  = self.tr('Input Layer'),
                layerType = QgsProcessing.TypeVectorAnyGeometry
            )
        )
        
        # Felder werde aus dem Layer ausgelesen 
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name = self.FINPUT,
                description  = self.tr('Mit Feldern dieses Layers filtern')
            )
        )
        
        # Attribut zum filtern auswählen 
        self.addParameter(
            QgsProcessingParameterField(
                name = self.FILTERATT,
                description  = self.tr('Filter Attribut'),
                defaultValue = "",
                parentLayerParameterName = self.FINPUT,
                optional = 1
            )
        ) 
        
        # Logische Operatoren != oder ==
        self.addParameter(
            QgsProcessingParameterEnum(
            name = self.OPERATOR,
            description  = self.tr('Vergleich Operator'),
            options = self.operators,
            allowMultiple = False,
            defaultValue=1
            )
        )
        
        # Filterwerte eintragen, mit Kommata getrennt
        self.addParameter(
            QgsProcessingParameterString(
                name = self.FILTER,
                description  = self.tr('Filter Werte, mit Komma trennen trennen'),
                optional = 1
            )
        )  
             
        # Wird nicht mehr benötigt da der Verknüpfungsoperator direkt vom logischen Operator abhängig ist
        # Verbindungsoperatoren AND oder OR
        #self.addParameter(
        #    QgsProcessingParameterEnum(
        #    name = self.OPERATORX,
        #    description  = self.tr('Logischer Operator'),
        #    options = self.operatorsX,
        #    allowMultiple = False,
        #    defaultValue=1
        #    )
        #)        

    def processAlgorithm(self, parameters, context, feedback):        
        
        sourceLayer = self.parameterAsLayerList(parameters,self.INPUT,context)
        methode = self.parameterAsEnum(parameters, self.METHODE, context)        
        
        if methode == 0:        
                    
            filterValues = self.parameterAsMatrix(parameters,self.FILTER,context)
            filterOpLog = self.OPERATORS[self.parameterAsEnum(parameters, self.OPERATOR, context)]
            
            if filterOpLog == '=':
                filterOpCon = 'OR'
            if filterOpLog == '!=':
                filterOpCon = 'AND'
            #filterOpCon = self.OPERATORSX[self.parameterAsEnum(parameters, self.OPERATORX, context)]
            filterAtt = self.parameterAsString(parameters,self.FILTERATT,context)   
            
            count = 0
            countMax = len(filterValues)
            while count < countMax:
                if count == 0:
                    filterListe = '"'+filterAtt+'"'+ filterOpLog +'\''+filterValues[0]+'\' '
                else:
                    filterListe = filterListe +filterOpCon+ ' "'+filterAtt+'"'+ filterOpLog +'\''+filterValues[count]+'\' ' 
                count=count+1
                    
            for layer in sourceLayer:
                layer.setSubsetString(filterListe) 
           
            return {self.FILTER: filterValues}        
        
        if methode == 1:
            for layer in sourceLayer:
                    layer.setSubsetString('') 
            return {self.METHODE: methode}
