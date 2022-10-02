from network_game.model import Game
from network_game.client.controller import Controls
from network_game.client.network import Network
from network_game.client.view import Ui


class GameClient:
    def __init__(self):
        self.network = Network()
        self.controls = Controls()
        self.game = Game()
        self.ui = Ui()

    def run(self) -> None:
        self.ui.start()
        while self._process_network_input():
            self._process_controls_input()
            self.ui.redraw(self.game)
        self.ui.stop()

    def _process_network_input(self) -> bool:
        game_state = self.network.get_next_game_state()
        if not game_state:
            return False
        self.game.set_state(game_state)
        return True
    
    def _process_controls_input(self):
        action = self.controls.get_action()
        if not action:
            return
        self.game.append_user_action(action)
        self.network.send_user_action(action)

