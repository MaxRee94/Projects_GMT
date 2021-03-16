import maya.cmds as mc

mc.currentTime(0)

startingPosition = mc.getAttr("pCylinder1.translate")
print startingPosition[0][0]

mc.autoKeyframe(state=False)

mc.cutKey("pCylinder1")

frameRange = 120

time = 0

rotationState = False

rotationEndTime = 1000

for i in range(frameRange):
    distanceBetween = mc.getAttr("distanceBetween1.distance")

    mc.currentTime(i + 1)

    time = time + 1

    if time == rotationEndTime + 1:
        rotationState = False

        mc.autoKeyframe(state=True)

        mc.move(-0.2, 0, 0, "pCylinder1", relative=True, objectSpace=True)

        print "rotation ended"

    if rotationState == False:
        if distanceBetween > 10005.444 and rotationState == False:
            mc.move(-0.2, 0, 0, "pCylinder1", relative=True, objectSpace=True)

        else:
            mc.setKeyframe(
                "pCylinder1", outTangentType="linear", inTangentType="linear"
            )

            mc.currentTime(0)
            mc.setAttr("pCylinder1.translateX", startingPosition[0][0])
            mc.setAttr("pCylinder1.translateX", startingPosition[0][0])
            mc.setAttr("pCylinder1.translateX", startingPosition[0][0])
            mc.setKeyframe(
                "pCylinder1", outTangentType="linear", inTangentType="linear"
            )

            mc.currentTime(time + 30)

            mc.rotate(0, 110, 0, "pCylinder1", relative=True)

            mc.setKeyframe(
                "pCylinder1", outTangentType="linear", inTangentType="linear"
            )

            rotationState = True

            rotationEndTime = time + 30
