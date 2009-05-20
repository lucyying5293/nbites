
from . import SoccerFSA
from . import ChaseBallStates
from . import PositionStates
from ..playbook import PBConstants
from .. import NogginConstants
from math import hypot
from ..util.MyMath import safe_atan2
from . import BrunswickStates
from . import BrunswickGoalieStates

#arbitrary, currently same as AIBO
CENTER_SAVE_THRESH = 15.
BODY_SAVE_OFFSET_DIST_Y = 5
BALL_SAVE_LIMIT_TIME = 1.35
MOVE_TO_SAVE_DIST_THRESH = 200.

class SoccerPlayer(SoccerFSA.SoccerFSA):
    def __init__(self, brain):
        SoccerFSA.SoccerFSA.__init__(self,brain)
        self.addStates(ChaseBallStates)
        self.addStates(BrunswickStates)
        self.addStates(PositionStates)
        self.addStates(BrunswickGoalieStates)
        self.setName('pBrunswick')
        self.currentRole = PBConstants.INIT_ROLE
        self.stoppedWalk = False
        self.currentChaseWalkTheta = None
        self.currentChaseWalkX = None
        self.currentChaseWalkY = None
        self.currentSpinDir = None
        self.currentGait = None
        self.sawOwnGoal = False
        self.sawOppGoal = False
        self.oppGoalLeftPostBearings = []
        self.oppGoalRightPostBearings = []
        self.myGoalLeftPostBearings = []
        self.myGoalRightPostBearings = []

    def run(self):
        if self.brain.gameController.currentState == 'gamePlaying':
            roleState = self.getNextState()
            if roleState != self.currentState:
                self.switchTo(roleState)
        SoccerFSA.SoccerFSA.run(self)

    def getNextState(self):
        playbookRole = self.brain.playbook.role
        if playbookRole == self.currentRole:
            return self.currentState
        else :
            self.currentRole = playbookRole
            return self.getRoleState(self.currentRole)

    def getRoleState(self,role):
        if role == PBConstants.CHASER:
            return 'chase'
        elif role == PBConstants.OFFENDER:
            return 'playbookPosition'
        elif role == PBConstants.DEFENDER:
            return 'playbookPosition'
        elif role == PBConstants.GOALIE:
            return 'goaliePosition'
        elif role == PBConstants.PENALTY_ROLE:
            return 'gamePenalized'
        elif role == PBConstants.SEARCHER:
            return 'scanFindBall'
        else:
            return 'scanFindBall'

    def getBehindBallPosition(self):
        dist_from_ball = 30

        ball = self.brain.ball

        delta_y = ball.y - NogginConstants.OPP_GOALBOX_MIDDLE_Y
        delta_x = ball.x - NogginConstants.OPP_GOALBOX_LEFT_X

        pos_x = ball.x - (dist_from_ball/
                                     hypot(delta_x,delta_y))*delta_x
        pos_y = ball.y + (dist_from_ball/
                                     hypot(delta_x,delta_y))*delta_y
        heading = -safe_atan2(delta_y,delta_x)

        return pos_x,pos_y,heading


    def shouldSave(self):
        ball = self.brain.ball

        if ball.on:
            relX = ball.relX
            relY = ball.relY
        else:
            relX = ball.locRelX
            relY = ball.locRelY

        # Test velocity values as to which one would work:
        relVelX = ball.relVelX
        relVelY = ball.relVelY
        if relVelY < 0.0:
          timeUntilSave = (relY - BODY_SAVE_OFFSET_DIST_Y) / -relVelY
          anticipatedX = (relX + relVelX * (timeUntilSave - BALL_SAVE_LIMIT_TIME))
        else:
          timeUntilSave = -1
          anticipatedX = ball.x

        # No Time, Save now
        if (0 <= timeUntilSave < BALL_SAVE_LIMIT_TIME and
            ball.framesOn > 5. and relVelY < 0.
            and relY < MOVE_TO_SAVE_DIST_THRESH):
            return True;
        return False;

    def shouldHoldSave(self):
        ball = self.brain.ball

        if ball.on:
            relY = ball.relY
        else:
            relY = ball.locRelY
        relVelY = ball.relVelY
        if relVelY < 0.0:
            timeUntilSave = (relY - BODY_SAVE_OFFSET_DIST_Y) / -relVelY
        else:
            timeUntilSave = -1
        if 0 <= timeUntilSave < BALL_SAVE_LIMIT_TIME and relVelY < 0 and\
            relY < MOVE_TO_SAVE_DIST_THRESH:
            return True
        return False


