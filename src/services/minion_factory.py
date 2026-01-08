from __future__ import annotations

from typing import Optional
from itertools import count
import copy

from src.minion import Minion
from src.minion_db import MINIONS_DB

instance_counter = count(1)
def new_instance_id(prefix : str = "inst") -> str:
    n = next(instance_counter)
    return f"{prefix} - {n:06d}"

def reset_instance_counter(start : int = 1) -> None:
    global instance_counter
    instance_counter = count(start)

def create_minion_by_id(minion_id : str, o_id:Optional[str] = None, zone : str = "shop", board_position : Optional[int] = None, instance_id : Optional[str] = None) -> Minion:
    if minion_id not in MINIONS_DB:
        raise ValueError("minion_id is invalid")
    data = copy.deepcopy(MINIONS_DB[minion_id])
    if instance_id is None:
        instance_id = new_instance_id()
    data["instance_id"] = instance_id
    m = Minion(data)
    m.o_id = o_id
    m.zone = zone
    m.on_board = (zone == "board")
    if zone == "board":
        m.board_position = board_position
    else:
        m.board_position = None
    m.alive = True
    return m
def creat_golden_minion (base_minion : Minion, keep_pos : bool = True, keep_instance_id: bool = False) -> Minion:
    if base_minion.id in MINIONS_DB:
        data = copy.deepcopy(MINIONS_DB[base_minion.id])
    else:
        data = {
            "id" : base_minion.id,
            "name" : base_minion.name,
            "tier" : base_minion.tier,
            "base_attack" : base_minion.base_attack,
            "base_health" : base_minion.base_health,
            "cost" : base_minion.cost,
            "tribe" : base_minion.tribe,
            "abilities" : list(base_minion.abilities),
            "is_token" : base_minion.is_token,
            "battlecry_effect" : copy.deepcopy(base_minion.battlecry_effect),
            "deathrattle_effect" : copy.deepcopy(base_minion.deathrattle_effect),
        }
    data["is_golden"] = True
    data["instance_id"] = base_minion.instance_id if keep_instance_id else new_instance_id()

    g = Minion(data)
    g.c_attack = int(base_minion.c_attack) * 2
    g.c_health = int(base_minion.c_health) * 2
    g.o_id = base_minion.o_id
    g.zone = base_minion.zone
    g.on_board = base_minion.on_board
    if g.zone == "board":
        if keep_pos:
            g.board_position = base_minion.board_position
        else:
            g.board_position = None
    else:
        g.board_position = None
        g.on_board = False
    g.alive = base_minion.alive
    g.divine_shield = bool(base_minion.divine_shield)
    g.reborn_active = bool(base_minion.reborn_active)
    g.reborn_used = bool(base_minion.reborn_used)
    g.has_attacked = bool(base_minion.has_attacked)
    return g


def clone_minion_state(src: Minion, keep_instance_id : bool = True) -> Minion :
    if src.id in MINIONS_DB:
        data = copy.deepcopy(MINIONS_DB[src.id])
        data["abilities"] = list(getattr(src, "abilities", []))
        data["is_token"] = getattr(src, "is_token", False)
        data["is_golden"] = getattr(src, "is_golden", False)
        data["battlecry_effect"] = copy.deepcopy(getattr(src, "battlecry_effect", None))
        data["deathrattle_effect"] = copy.deepcopy(getattr(src, "deathrattle_effect", None))
    else:
        data = {
            "id": src.id,
            "name": src.name,
            "tier": src.tier,
            "base_attack": src.base_attack,
            "base_health": src.base_health,
            "cost": src.cost,
            "tribe": src.tribe,
            "abilities": list(getattr(src, "abilities", [])),
            "is_token": getattr(src, "is_token", False),
            "is_golden": getattr(src, "is_golden", False),
            "battlecry_effect": copy.deepcopy(getattr(src, "battlecry_effect", None)),
            "deathrattle_effect": copy.deepcopy(getattr(src, "deathrattle_effect", None)),
        }
    data["instance_id"]=src.instance_id if keep_instance_id else new_instance_id()
    m = Minion(data)
    m.c_attack = int(getattr(src, "c_attack", m.base_attack))
    m.c_health = int(getattr(src, "c_health", m.base_health))
    m.o_id = getattr(src, "o_id", None)
    m.zone = getattr(src, "zone","shop")
    m.on_board=bool(getattr(src, "on_board", False))
    m.board_position = getattr(src, "board_position", None)
    m.alive = bool(getattr(src, "alive", True))
    m.has_attacked = bool(getattr(src, "has_attacked", False))
    m.divine_shield = bool(getattr(src, "divine_shield", False))
    m.reborn_active = bool(getattr(src, "reborn_active", False))
    m.reborn_used = bool(getattr(src, "reborn_used", False))
    return m