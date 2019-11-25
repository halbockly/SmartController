class ParamsDto:
    def __init__(self):
        self.kadenId = ""
        self.manipulateId = ""
        self.timerDatetime = ""

    def setParams(self, kadenId, manipulateId, timerDatetime):
        self.kadenId = kadenId
        self.manipulateId = manipulateId
        self.timerDatetime = timerDatetime

    def gatKadenId(self):
        return self.kadenId

    def gatManipulateId(self):
        return self.manipulateId

    def gatTimerDatetime(self):
        return self.timerDatetime
