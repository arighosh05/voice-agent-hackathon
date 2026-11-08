"""Expo: a voice expediter's kitchen backend.

Orders and inventory live in memory (one process, one demo). The order page
(phone) posts orders, the kitchen page polls them and has the voice agent call
them out, and the ElevenLabs agent's server tools hit /board, /fire and /86.
"""
import pathlib
import re
import threading
import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

router = APIRouter()
STATIC = pathlib.Path(__file__).parent / "static"
_lock = threading.Lock()

MENU = {
    "classic burger": ["extra cheese", "no pickles", "no onions", "add bacon"],
    "salmon burger": ["extra cheese", "no pickles", "no onions", "add bacon"],
    "veggie burger": ["extra cheese", "no pickles", "no onions", "add bacon"],
    "chicken sandwich": ["extra cheese", "no pickles", "spicy mayo"],
    "fries": ["large", "no salt"],
}
SWAP = {"salmon burger": "chicken sandwich", "chicken sandwich": "classic burger"}
COMP = "a drink"

orders: list[dict] = []
eighty_sixed: set[str] = set()
_next_id = 1


class Item(BaseModel):
    name: str
    mods: list[str] = []


class OrderIn(BaseModel):
    table: int
    items: list[Item]


class FireIn(BaseModel):
    table: int


class EightySixIn(BaseModel):
    item: str


def _say_mod(m: str) -> str:
    return "hold the " + m[3:] if m.startswith("no ") else m


def _say_item(it: dict) -> str:
    mods = ", ".join(_say_mod(m) for m in it["mods"])
    return it["name"] + (", " + mods if mods else "")


def _callout(o: dict) -> str:
    return f"Ordering, table {o['table']}: " + "; ".join(_say_item(i) for i in o["items"]) + "."


def _add(table: int, items: list[dict], age_s: int = 0) -> dict:
    global _next_id
    o = {"id": _next_id, "table": table, "items": items, "status": "new",
         "created": time.time() - age_s, "message": None}
    o["callout"] = _callout(o)
    _next_id += 1
    orders.append(o)
    return o


def _seed():
    global _next_id
    orders.clear()
    eighty_sixed.clear()
    _next_id = 1
    # Pre-existing tickets so an 86 of salmon hits more than the judge's table.
    _add(7, [{"name": "salmon burger", "mods": []}, {"name": "fries", "mods": []}], age_s=300)
    _add(2, [{"name": "classic burger", "mods": ["add bacon"]}], age_s=240)
    _add(9, [{"name": "salmon burger", "mods": ["no onions"]}], age_s=120)


_seed()


def _open():
    return [o for o in orders if o["status"] != "done"]


# Words a cook might say for each item, checked after exact/substring matches.
ALIASES = {
    "salmon burger": ["salmon", "fish"],
    "chicken sandwich": ["chicken", "chix"],
    "veggie burger": ["veggie", "veg", "vegetarian", "plant", "beyond", "impossible"],
    "classic burger": ["classic", "beef", "cheeseburger", "hamburger", "patty", "patties"],
    "fries": ["fry", "fries", "chips", "potato", "potatoes"],
}


def _match_item(text: str) -> str | None:
    t = re.sub(r"\b(the|all|our|any|more|we're|were|we|are|out|of|on|86|eighty[- ]six|no)\b", " ", text.lower())
    t = " ".join(re.sub(r"[^a-z ]", " ", t).split())
    if not t or t.rstrip("s") == "burger":  # ambiguous: let the agent ask which one
        return None
    for name in MENU:
        if t == name or t.rstrip("s") in name or name in t:
            return name
    words = {w for w in t.split()} | {w.rstrip("s") for w in t.split()}
    for name, al in ALIASES.items():
        if words & set(al):
            return name
    return None


def _join(nums: list[int]) -> str:
    s = [str(n) for n in nums]
    return s[0] if len(s) == 1 else ", ".join(s[:-1]) + " and " + s[-1]


# ---- pages -------------------------------------------------------------

@router.get("/", include_in_schema=False)
def order_page():
    return FileResponse(STATIC / "order.html")


@router.get("/kitchen", include_in_schema=False)
def kitchen_page():
    return FileResponse(STATIC / "kitchen.html")


@router.get("/static/{name}", include_in_schema=False)
def static_file(name: str):
    f = STATIC / name
    if "/" in name or ".." in name or not f.is_file():
        raise HTTPException(404)
    return FileResponse(f)


# ---- customer side -----------------------------------------------------

@router.get("/menu")
def menu():
    return {"items": [{"name": n, "mods": m, "sold_out": n in eighty_sixed} for n, m in MENU.items()]}


@router.post("/order")
def place_order(req: OrderIn):
    with _lock:
        items = []
        for it in req.items:
            name = it.name.lower().strip()
            if name not in MENU:
                raise HTTPException(400, f"not on the menu: {it.name}")
            if name in eighty_sixed:
                raise HTTPException(409, f"sorry, we're out of {name}")
            items.append({"name": name, "mods": [m for m in it.mods if m in MENU[name]]})
        if not items:
            raise HTTPException(400, "empty order")
        o = _add(req.table, items)
    return {"id": o["id"], "callout": o["callout"]}


@router.get("/order/{oid}")
def order_status(oid: int):
    for o in orders:
        if o["id"] == oid:
            return o
    raise HTTPException(404, "no such order")


# ---- kitchen side (kitchen page + agent tools) -------------------------

@router.get("/orders")
def list_orders():
    return {"orders": _open(), "eighty_sixed": sorted(eighty_sixed)}


@router.get("/board")
def board():
    """Agent tool: what's open, oldest first, as one sentence to read out."""
    tickets = sorted(_open(), key=lambda o: o["created"])
    if not tickets:
        return {"summary": "Board's clear.", "tickets": []}
    parts = []
    for o in tickets:
        tag = {"new": "", "fired": ", fired", "flagged": ", 86'd"}[o["status"]]
        parts.append(f"{o['table']}{tag}: " + "; ".join(_say_item(i) for i in o["items"]))
    oldest = int((time.time() - tickets[0]["created"]) // 60)
    wait = f" Oldest is table {tickets[0]['table']}, {oldest} minutes." if oldest >= 1 else ""
    return {"summary": f"{len(tickets)} open. " + ". ".join(parts) + "." + wait,
            "tickets": [{"table": o["table"], "status": o["status"], "callout": o["callout"]} for o in tickets]}


@router.post("/fire")
def fire(req: FireIn):
    """Agent tool: mark the table's open ticket as fired."""
    with _lock:
        for o in sorted(_open(), key=lambda o: o["created"]):
            if o["table"] == req.table and o["status"] in ("new", "flagged"):
                o["status"] = "fired"
                return {"summary": f"Fired table {req.table}.", "ok": True}
    return {"summary": f"No open ticket for table {req.table}.", "ok": False}


@router.post("/hold")
def hold(req: FireIn):
    """Agent tool: undo a fire (Marco changed his mind)."""
    with _lock:
        for o in sorted(_open(), key=lambda o: -o["created"]):
            if o["table"] == req.table and o["status"] == "fired":
                o["status"] = "flagged" if o["message"] else "new"
                return {"summary": f"Holding table {req.table}.", "ok": True}
    return {"summary": f"Table {req.table} wasn't fired.", "ok": False}


@router.post("/86")
def eighty_six(req: EightySixIn):
    """Agent tool: mark an item out, flag affected tickets, message those customers."""
    name = _match_item(req.item)
    if not name:
        return {"summary": f"Not sure which item '{req.item}' is. Ask Marco which one: " + ", ".join(MENU) + ".", "ok": False}
    swap = SWAP.get(name, "classic burger")
    with _lock:
        eighty_sixed.add(name)
        hit = []
        for o in _open():
            if o["status"] != "done" and any(i["name"] == name for i in o["items"]):
                o["status"] = "flagged"
                o["message"] = (f"Sorry, we just ran out of the {name}. We can swap in a {swap} "
                                f"at no charge, and {COMP} is on us.")
                hit.append(o["table"])
    if not hit:
        return {"summary": f"86 {name}. No open tickets affected.", "ok": True, "tables": []}
    return {"summary": f"86 {name}. That hits table{'s' if len(hit) > 1 else ''} {_join(sorted(hit))}. "
                       f"I've offered them a {swap} and comped {COMP}.",
            "ok": True, "tables": sorted(hit)}


@router.post("/reset")
def reset():
    """Rehearsal helper: back to the seeded board."""
    with _lock:
        _seed()
    return {"ok": True}
