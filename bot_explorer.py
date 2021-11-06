import json
from data.app import App


if __name__ == "__main__":
    with open('tiles.json', 'r') as file:
        tile_types = json.load(file)

    app = App(tile_types)