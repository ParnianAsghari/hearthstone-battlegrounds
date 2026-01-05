import random
from typing import Dict, Any, List
from src.minion_db import MINIONS_DB


class GameService:
    def __init__(self, initial_state: Dict[str, Any], hero_name: str = "Sylvanas Windrunner"):
        self.state = initial_state.copy() 
        self.state["hand"] = initial_state.get("hand", [])
        self.state["board"] = initial_state.get("board", [])
        self.state["shop"] = initial_state.get("shop", [])
        self.state["shop_frozen"] = False
        self.state["turn"] = initial_state.get("turn", 1)
        self.state["tavern_tier"] = initial_state.get("tavern_tier", 1)
        self.state["health"] = initial_state.get("health", 40)

        self.hero_name = hero_name
        self.last_combat_died: List[str] = []

    def get_state(self) -> Dict[str, Any]:
        return self.state

    def handle_command(self, command: dict) -> dict:
        action = command.get("action")

        handlers = {
            "BUY": self._handle_buy,
            "SELL": self._handle_sell,
            "PLAY": self._handle_play,
            "REFRESH": self._handle_refresh,
            "FREEZE": self._handle_freeze,
            "HERO_POWER": self._handle_hero_power,
            "NEXT_TURN": self._handle_next_turn,
        }

        handler = handlers.get(action)
        if handler:
            return handler(command)
        
        return {"type": "error", "message": f"Unknown action: {action}"}

    def _handle_buy(self, cmd: dict) -> dict:
        slot = cmd["shop_slot"]
        if not (0 <= slot < len(self.state["shop"])):
            return {"type": "error", "message": "Invalid shop slot"}

        card_id = self.state["shop"][slot]
        if card_id is None:
            return {"type": "error", "message": "Empty shop slot"}

        if self.state["gold"] < 3:
            return {"type": "error", "message": "Not enough gold (need 3)"}

        if len(self.state["hand"]) >= 10:
            return {"type": "error", "message": "Hand is full (max 10)"}

        self.state["gold"] -= 3
        self.state["hand"].append(card_id)
        self.state["shop"][slot] = None

        reward = self._check_triple(card_id)
        if reward:
            return reward 

        return {
            "type": "success",
            "message": "Minion bought",
            "payload": {
                "gold": self.state["gold"],
                "hand_add": card_id,
                "shop_slot_empty": slot
            }
        }

    def _handle_sell(self, cmd: dict) -> dict:
        slot = cmd["board_slot"]
        if not (0 <= slot < len(self.state["board"])):
            return {"type": "error", "message": "Invalid board slot"}

        card_id = self.state["board"].pop(slot)
        if not card_id:
            return {"type": "error", "message": "No minion to sell"}

        self.state["gold"] += 1

        return {
            "type": "success",
            "message": "Minion sold",
            "payload": {
                "gold": self.state["gold"],
                "board_remove": slot,
                "sold_card": card_id
            }
        }

    def _handle_play(self, cmd: dict) -> dict:
        hand_slot = cmd["hand_slot"]
        if not (0 <= hand_slot < len(self.state["hand"])):
            return {"type": "error", "message": "Invalid hand slot"}

        if len(self.state["board"]) >= 7:
            return {"type": "error", "message": "Board is full (max 7)"}

        card_id = self.state["hand"].pop(hand_slot)
        self.state["board"].append(card_id)  
        return {
            "type": "success",
            "message": "Minion played",
            "payload": {
                "hand_remove": hand_slot,
                "board_add": card_id
            }
        }

    def _handle_refresh(self, _: dict) -> dict:
        if self.state["gold"] < 1:
            return {"type": "error", "message": "Not enough gold for refresh"}

        self.state["gold"] -= 1
        self._fill_shop()
        return {"type": "success", "message": "Shop refreshed", "payload": {"shop": self.state["shop"]}}

    def _handle_freeze(self, _: dict) -> dict:
        self.state["shop_frozen"] = not self.state["shop_frozen"]
        return {
            "type": "success",
            "message": "Shop frozen" if self.state["shop_frozen"] else "Shop unfrozen",
            "payload": {"shop_frozen": self.state["shop_frozen"]}
        }

    def _handle_hero_power(self, _: dict) -> dict:
        cost = 1 if self.hero_name in ["Sylvanas Windrunner", "The Lich King", "Yogg-Saron"] else 0
        if self.hero_name == "Millhouse Manastorm":
            return {"type": "error", "message": "Passive hero power"}

        if self.state["gold"] < cost:
            return {"type": "error", "message": "Not enough gold for hero power"}

        self.state["gold"] -= cost

        if self.hero_name == "Sylvanas Windrunner" and self.last_combat_died:
            return {"type": "success", "message": "Reclaimed Souls used!"}

        return {"type": "success", "message": f"{self.hero_name} power used!"}

    def _handle_next_turn(self, _: dict) -> dict:
        self.state["turn"] += 1
        new_gold = min(self.state["turn"] + 2, 10)
        self.state["gold"] = new_gold

        if not self.state["shop_frozen"]:
            self._fill_shop()
        self.state["shop_frozen"] = False 

        return {
            "type": "next_turn",
            "payload": {
                "turn": self.state["turn"],
                "gold": self.state["gold"],
                "shop": self.state["shop"]
            }
        }

    # --- Helper Methods ---
    def _fill_shop(self):
        tier = self.state["tavern_tier"]
        available = [cid for cid, data in MINIONS_DB.items() if data["tier"] <= tier]
        slots = 3 + tier - 1 
        shop = []
        for _ in range(slots):
            if random.choice([True, False]) and available:
                shop.append(random.choice(available))
            else:
                shop.append(None)
        self.state["shop"] = shop

    def _check_triple(self, card_id: str) -> dict | None:
        count = sum(1 for c in self.state["hand"] + self.state["board"] if c == card_id)
        if count == 3:
            removed = 0
            for container in [self.state["hand"], self.state["board"]]:
                i = 0
                while i < len(container) and removed < 3:
                    if container[i] == card_id:
                        container.pop(i)
                        removed += 1
                    else:
                        i += 1
            golden_id = card_id + "_golden" 
            self.state["board"].append(golden_id)

            return {
                "type": "discover_offer",
                "tier": self.state["tavern_tier"] + 1,
                "choices": random.sample([c for c, d in MINIONS_DB.items() if d["tier"] == self.state["tavern_tier"] + 1], 3)
            }
        return None