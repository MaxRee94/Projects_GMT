from PySide2 import QtGui as qg
from PySide2 import QtCore as qc
from functools import partial
import os
import sys
import imp

memoryPath = 'F:/HBO/scripts/autoSimulator/text interpreter/memory/memoryFile_001.py'
memoryModule = 'memoryFile_001'

class GUI(qg.QDialog):
    def __init__(self):
        self.workingMemory = None
        qg.QDialog.__init__(self)
        
        self.setWindowTitle('Command Interpreter')
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setModal(True)
        self.setMinimumWidth(550)
        self.setMinimumHeight(200)
        
        self.mainLayout=qg.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.layout().setContentsMargins(5,5,5,5)
        self.layout().setSpacing(2)
        
        self.conversationList = qg.QListWidget()
        
        text_layout= qg.QVBoxLayout()
        text_layout.setSpacing(5)
        text_layout.setSpacing(0)
        
        applyButton = qg.QPushButton('Tell me')
        space = qg.QLabel('')
        self.textEdit = qg.QTextEdit()
        label1 = qg.QLabel('Tell me anything:')
        label1.setAlignment(qc.Qt.AlignHCenter)
        
        self.layout().addLayout(text_layout)
        text_layout.addWidget(label1)
        text_layout.addWidget(self.textEdit)
        text_layout.addWidget(applyButton)
        text_layout.addWidget(self.conversationList)
        
        #connect button
        applyButton.clicked.connect(self.processText)
    
    def processText(self):
        self.fieldText=self.textEdit.toPlainText()
        myText='YOU: '+self.fieldText
        self.textEdit.clear()
        
        #maak response
        self.response = self.respond(self.fieldText)
        
        #maak lijst van nieuwe items
        self.textItems =[self.response,'',myText,'']
        itemCount = self.conversationList.count()
        for i in range(itemCount):
            self.textItems.append(self.conversationList.item(i).text())   
        
        #verwijder oude items
        self.conversationList.clear()

        #print to conversation list
        for item in self.textItems:
            self.conversationList.addItem(item)
            
    def respond(self,fieldText):
        if self.workingMemory != None:   #turn on learning mode
            #read current memory content
            f = open(memoryPath, 'r')
            f_contentList = f.readlines()
            print f_contentList
            
            #update encounteredInputList
            previousWordList = f_contentList[5]
            newWord = ''.join([', "', self.workingMemory, '"]'])
            newWordList = previousWordList.replace(']', newWord) 
            f_contentList[5] = newWordList
            
            #re-write memory
            f = open(memoryPath, 'w')
            f.write('')
            f = open(memoryPath, 'a')
            for line in f_contentList:
                f.write(line)
            
            #append rule to memory        
            f.write(''.join(["        if self.userText == ",'"', self.workingMemory, '"', " : \n"]))
            f.write(''.join(['            return "', fieldText, '"', ' \n']))    
            f.close()
            
            #empty working memory
            self.workingMemory = None
            
            #confirm that the lesson has been saved to memory
            computerResponse = 'OK. I will remember that.'
        else:                            #turn on remember mode
            #consult memory
            computerResponse = self.consultMemory(fieldText)
            print 'computer response: ',str(computerResponse)
            if computerResponse == None:
                computerResponse = ''.join(["I don't understand.. What is the appropriate response to '", fieldText, "'?"])
                self.workingMemory = fieldText
            
        #add tag and return response
        totalResponse = 'COMPUTER: ' + computerResponse
        return totalResponse
        
    def consultMemory(self, userText):
        #import memory module
        memory = imp.load_source(memoryModule, memoryPath)
        del sys.modules[memoryModule]  
        memory = imp.load_source(memoryModule, memoryPath)
        
        memInst = memory.Remember(userText)
        return memInst.response
        

app = 
dialog = GUI()
dialog.show()












