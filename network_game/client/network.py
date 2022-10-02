from network_game.client.controller import UserAction
from network_game.model import GameState

class Network:
    def get_next_game_state(self) -> GameState:
        return GameState()

    def send_user_action(self, action: UserAction):
        pass
