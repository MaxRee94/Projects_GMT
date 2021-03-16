import sys
from functools import partial
from pathlib import Path

from PySide2 import QtCore, QtGui, QtWidgets

dialog = None

# ----------------------------------------------------------------#


class ClickableLabel(QtWidgets.QLabel):

    clicked = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        self.clicked.emit()


class dammen_GUI(QtWidgets.QDialog):

    work_directory = str(Path(__file__).parent)

    def __init__(self, dialogTitle):
        QtWidgets.QDialog.__init__(self)

        # window setup
        self.setWindowTitle(dialogTitle)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(300, 250, 300, 300)

        # setup colors
        self.white = [255, 255, 255]
        self.lightGrey = [120, 120, 120]
        self.darkGrey = [72, 52, 33]
        self.black = [0, 0, 0]

        # create pixMaps
        self.leeg_vakje = QtGui.QPixmap("D:\\HBO\\Pipeline\\leeg_vakje.png")
        self.blackKey_static_pixmap = QtGui.QPixmap(
            "D:\\HBO\\Pipeline\\zwarte_damsteen_neergezet.png"
        )
        self.blackKey_raised_pixmap = QtGui.QPixmap(
            "D:\\HBO\\Pipeline\\zwarte_damsteen_opgetilt.png"
        )
        self.whiteKey_static_pixmap = QtGui.QPixmap(
            "D:\\HBO\\Pipeline\\witte_damsteen_neergezet.png"
        )
        self.whiteKey_raised_pixmap = QtGui.QPixmap(
            "D:\\HBO\\Pipeline\\witte_damsteen_opgetilt.png"
        )
        self.grijsVakje = QtGui.QPixmap("D:\\HBO\\Pipeline\\grijsVakje.png")

        # raised state of the stones
        self.raised = None

        # button size
        self.buttonSize = 40

        # main layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)

        # squareType lijsten
        self.legeVakjes = {}
        self.witteStenen = {}
        self.zwarteStenen = {}
        self.grijzeVakjes = []

        self.make_Buttons()

    def make_Buttons(self):
        evenRow = True
        label_list = []
        for i in range(10):
            newLayout = QtWidgets.QWidget()
            newLayout.setLayout(QtWidgets.QHBoxLayout())
            newLayout.layout().setSpacing(0)
            newLayout.layout().setContentsMargins(0, 0, 0, 0)
            self.mainLayout.addWidget(newLayout)
            for j in range(5):
                # maak grijze vakjes
                labelWhite = ClickableLabel()
                labelWhite.setFixedHeight(self.buttonSize)
                labelWhite.setFixedWidth(self.buttonSize)
                labelWhite.setPixmap(self.grijsVakje)
                self.change_color(labelWhite, self.lightGrey)
                self.grijzeVakjes.append(labelWhite)

                # krijg current position info
                current_positionInfo = [j, i]

                # maak zwarte vakjes
                ## bepaal of er een steen of een leeg zwart vakje moet komen
                if i in [4, 5]:
                    labelBlack = ClickableLabel()
                    labelBlack.setFixedHeight(self.buttonSize)
                    labelBlack.setFixedWidth(self.buttonSize)
                    labelBlack.setPixmap(self.leeg_vakje)

                    self.legeVakjes[labelBlack] = current_positionInfo
                elif i in [0, 1, 2, 3]:
                    labelBlack = ClickableLabel()
                    labelBlack.setFixedHeight(self.buttonSize)
                    labelBlack.setFixedWidth(self.buttonSize)
                    labelBlack.setPixmap(self.blackKey_static_pixmap)

                    self.zwarteStenen[labelBlack] = current_positionInfo
                else:
                    labelBlack = ClickableLabel()
                    labelBlack.setFixedHeight(self.buttonSize)
                    labelBlack.setFixedWidth(self.buttonSize)
                    labelBlack.setPixmap(self.whiteKey_static_pixmap)

                    self.witteStenen[labelBlack] = current_positionInfo

                    ## voeg de vakjes toe aan de layout
                if i in [0, 2, 4, 6, 8]:
                    newLayout.layout().addWidget(labelBlack)
                    newLayout.layout().addWidget(labelWhite)
                else:
                    newLayout.layout().addWidget(labelWhite)
                    newLayout.layout().addWidget(labelBlack)

        ## CONNECTIONS
        for squareType_list in [
            self.grijzeVakjes,
            self.legeVakjes.keys(),
            self.zwarteStenen.keys(),
            self.witteStenen.keys(),
        ]:
            for square in squareType_list:
                square.clicked.connect(partial(self.squareClicked, square))

    def rulesAssessment(
        self,
        squareOfOrigin,
        stone_staticPixMap,
        squareType_list,
        squareOfDestination_position,
        squareOfOrigin_position,
    ):
        # find current coordinates
        current_X_coordinate = squareOfOrigin_position[0]
        current_Y_coordinate = squareOfOrigin_position[1]

        def oneStep_rule():
            # rule: can only move 1 step to the left or to the right
            if squareOfOrigin in self.witteStenen:
                if not current_Y_coordinate == 0:
                    possible_Y_coordinate = current_Y_coordinate - 1
                else:
                    return False
            else:
                if not current_Y_coordinate == 9:
                    possible_Y_coordinate = current_Y_coordinate + 1
                else:
                    return False

            if current_Y_coordinate in [0, 2, 4, 6, 8]:
                possible_X_coordinates = [
                    current_X_coordinate - 1,
                    current_X_coordinate,
                ]
            else:
                possible_X_coordinates = [
                    current_X_coordinate,
                    current_X_coordinate + 1,
                ]

            possible_coordinates = []
            for possible_X_coordinate in possible_X_coordinates:
                possible_coordinates.append(
                    [possible_X_coordinate, possible_Y_coordinate]
                )

                ## if the clicked square's position does not match the possible
                ## destination coordinates, break function
            if squareOfDestination_position not in possible_coordinates:
                return False
            else:
                return True

        def slaan_exception():
            # exception to oneStep_rule for 'slaan'
            clicked_X_coordinate = squareOfDestination_position[0]
            clicked_Y_coordinate = squareOfDestination_position[1]

            ## check Y-coordinate
            above = False
            below = False
            if clicked_Y_coordinate == (current_Y_coordinate - 2):
                ## killed stone should be below the current position
                killedStone_Ycoord = current_Y_coordinate - 1
            elif clicked_Y_coordinate == (current_Y_coordinate + 2):
                ## killed stone should be above the current position
                killedStone_Ycoord = current_Y_coordinate + 1
            else:
                return False

                ## check X-coordinate
            if clicked_X_coordinate == (current_X_coordinate + 1):
                ## killed stone should be to the right of the current position
                if killedStone_Ycoord in [1, 3, 5, 7, 9]:
                    ### even y-coordinate
                    killedStone_Xcoord = current_X_coordinate
                else:
                    ### uneven y-coordinate
                    killedStone_Xcoord = current_X_coordinate + 1
            elif clicked_X_coordinate == (current_X_coordinate - 1):
                ## killed stone should be to the left of the current position
                if killedStone_Ycoord in [1, 3, 5, 7, 9]:
                    ### even y-coordinate
                    killedStone_Xcoord = current_X_coordinate - 1
                else:
                    ### uneven y-coordinate
                    killedStone_Xcoord = current_X_coordinate
            else:
                return False

                ## check if an enemy stone is present at the calculated coordinates
            killedStone_coordinates = [killedStone_Xcoord, killedStone_Ycoord]
            foundStone = False
            if squareOfOrigin in self.witteStenen:
                for pythonObj, theseCoords in zip(
                    self.zwarteStenen.keys(), self.zwarteStenen.values()
                ):
                    if killedStone_coordinates == theseCoords:
                        print(
                            "killedStone coords:",
                            str(killedStone_coordinates),
                            "theseCoords:",
                            str(theseCoords),
                        )
                        foundStone = pythonObj
                if foundStone == False:
                    print("killed stone coordinates not found")
                    print(
                        "killedStone coords:",
                        str(killedStone_coordinates),
                        "all coords:",
                        str(self.zwarteStenen.values()),
                    )
                    return False
                else:
                    return [foundStone, self.zwarteStenen, killedStone_coordinates]
            else:
                for pythonObj, theseCoords in zip(
                    self.witteStenen.keys(), self.witteStenen.values()
                ):
                    if killedStone_coordinates == theseCoords:
                        foundStone = pythonObj
                if foundStone == False:
                    print("killed stone coordinates not found")
                    print(
                        "killedStone coords:",
                        str(killedStone_coordinates),
                        "all coords:",
                        str(self.witteStenen.values()),
                    )
                    return False
                else:
                    return [foundStone, self.witteStenen, killedStone_coordinates]

        # check each rule
        if oneStep_rule() == False:
            slaanException_result = slaan_exception()
            if not slaanException_result == False:
                print("slaan!")
                print("killed stone:", str(slaanException_result))
                return slaanException_result
            else:
                print("niet slaan!")
                return False
        else:
            return True

    def squareClicked(self, clicked_square):
        current_pixmap = clicked_square.pixmap()
        if clicked_square in self.legeVakjes:
            if self.raised != None:
                squareOfOrigin = self.raised[0]
                stone_staticPixMap = self.raised[1]
                squareType_list = self.raised[2]

                # get position info
                squareOfDestination_position = self.legeVakjes[clicked_square]
                squareOfOrigin_position = squareType_list[squareOfOrigin]

                ## MOVE STONE
                ## check if rules are not broken
                rulesAssessment = self.rulesAssessment(
                    squareOfOrigin,
                    stone_staticPixMap,
                    squareType_list,
                    squareOfDestination_position,
                    squareOfOrigin_position,
                )
                if rulesAssessment == False:
                    squareOfOrigin.setPixmap(stone_staticPixMap)
                    self.raised = None
                    return
                elif rulesAssessment != True:
                    ## slaan, so remove enemy stone
                    deadStone_dict = rulesAssessment[1]
                    deadStone_obj = rulesAssessment[0]
                    deadStone_coordinates = rulesAssessment[2]

                    # update dictionaries and pixmap
                    del deadStone_dict[deadStone_obj]
                    self.legeVakjes[deadStone_obj] = deadStone_coordinates
                    deadStone_obj.setPixmap(self.leeg_vakje)

                    print("dead stone coordinates:", str(deadStone_coordinates))

                    ## swap pixmaps
                squareOfOrigin.setPixmap(self.leeg_vakje)
                clicked_square.setPixmap(stone_staticPixMap)

                ## swap position info
                del self.legeVakjes[clicked_square]
                del squareType_list[squareOfOrigin]
                squareType_list[clicked_square] = squareOfDestination_position
                self.legeVakjes[squareOfOrigin] = squareOfOrigin_position

                print("original position:", str(squareOfOrigin_position))
                print("new position:", str(squareType_list[clicked_square]))

                # set raised state to None
                self.raised = None
        elif clicked_square in self.grijzeVakjes:
            if self.raised != None:
                squareOfOrigin = self.raised[0]
                stone_staticPixMap = self.raised[1]

                squareOfOrigin.setPixmap(stone_staticPixMap)

                self.raised = None
        else:
            if self.raised != None:
                squareOfOrigin = self.raised[0]
                stone_staticPixMap = self.raised[1]

                squareOfOrigin.setPixmap(stone_staticPixMap)

                self.raised = None
            else:
                if clicked_square in self.zwarteStenen:
                    clicked_square.setPixmap(self.blackKey_raised_pixmap)
                    self.raised = [
                        clicked_square,
                        self.blackKey_static_pixmap,
                        self.zwarteStenen,
                    ]
                else:
                    clicked_square.setPixmap(self.whiteKey_raised_pixmap)
                    self.raised = [
                        clicked_square,
                        self.whiteKey_static_pixmap,
                        self.witteStenen,
                    ]

    def change_color(self, this_widget, this_color):
        r = this_color[0]
        g = this_color[1]
        b = this_color[2]

        palette = this_widget.palette()
        this_color = QtGui.QColor()
        this_color.setRgb(r, g, b)
        palette.setColor(this_widget.backgroundRole(), this_color)

        this_widget.setPalette(palette)


# ------------------------------------------------------------------------------------------------#


def create():
    global dialog
    if dialog is None:
        dialog = dammen_GUI("potje damme")
    dialog.show()
    return dialog


def delete():
    global dialog
    if dialog is None:
        return
    dialog.deleteLater()
    dialog = None


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = create()
    app.exec_()
