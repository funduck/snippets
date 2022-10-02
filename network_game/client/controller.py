from network_game.model import UserAction


class Controls:
    def get_action(self) -> UserAction | None:
        return UserAction()
