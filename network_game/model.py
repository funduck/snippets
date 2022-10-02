class GameState:
    pass

class UserAction:
    pass

class Game:
    def __init__(self) -> None:
        self.state = GameState()

    def set_state(self, state: GameState):
        self.state = state

    def append_user_action(self, action: UserAction):
        pass

    def get_state(self) -> GameState:
        return self.state
