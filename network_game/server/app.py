from network_game.server.network import Network
from network_game.model import Game

class GameServer:
    def __init__(self):
        self.game = Game()
        self.network = Network(user_action_cb=self.game.append_user_action)
        while True:
            self.network.broadcast_game_state(self.game.get_state())
