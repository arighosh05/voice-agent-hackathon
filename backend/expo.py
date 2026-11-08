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
    table: int | None = None  # omitted: the server seats the guest at the next table
    items: list[Item]


FIRST_GUEST_TABLE = 10  # seeded demo tables are 2, 7 and 9
_next_table = FIRST_GUEST_TABLE


class FireIn(BaseModel):
    table: int
    instead_of: int | None = None  # "start 7 instead of 4": pause 4, start 7 in one call


class EightySixIn(BaseModel):
    item: str


def _say_mod(m: str) -> str:
    return "hold the " + m[3:] if m.startswith("no ") else m


def _say_item(it: dict) -> str:
    mods = ", ".join(_say_mod(m) for m in it["mods"])
    return it["name"] + (", " + mods if mods else "")


def _callout(o: dict) -> str:
    return f"New order, table {o['table']}: " + "; ".join(_say_item(i) for i in o["items"]) + "."


def _add(table: int, items: list[dict], age_s: int = 0) -> dict:
    global _next_id
    o = {"id": _next_id, "table": table, "items": items, "status": "new",
         "created": time.time() - age_s, "message": None}
    o["callout"] = _callout(o)
    _next_id += 1
    orders.append(o)
    return o


def _seed():
    # Order ids keep counting up across resets so the kitchen page never mistakes
    # a new ticket for an old one it already called out.
    global _next_table
    orders.clear()
    eighty_sixed.clear()
    _next_table = FIRST_GUEST_TABLE
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
    "veggie burger": ["veggie", "veg", "vegetarian", "plant", "beyond"],
    "classic burger": ["classic", "beef", "cheeseburger", "hamburger", "patty", "patties"],
    "fries": ["fry", "fries", "chips", "potato", "potatoes"],
}


def _match_item(text: str) -> str | None:
    t = re.sub(r"\b(the|all|our|any|more|we're|were|we|are|out|of|on|86|eighty[- ]six|no|sold|mark|is|as)\b", " ", text.lower())
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


def _unknown(item: str) -> dict:
    if "burger" in item.lower():
        return {"summary": "Ambiguous: ask Marco which burger: classic, salmon or veggie.", "ok": False}
    return {"summary": f"{item} isn't on the menu. Menu is " + ", ".join(MENU) + ".", "ok": False}


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


MAX_ITEMS_PER_ORDER = 12  # UI offers 5; guard against a scripted flood
MAX_OPEN_ORDERS = 50      # keep the board (and the agent's callout queue) sane


@router.post("/order")
def place_order(req: OrderIn):
    global _next_table
    if req.table is not None and not 1 <= req.table <= 99:
        raise HTTPException(400, "unknown table")
    if len(req.items) > MAX_ITEMS_PER_ORDER:
        raise HTTPException(400, "too many items on one order")
    with _lock:
        if sum(1 for o in orders if o["status"] != "done") >= MAX_OPEN_ORDERS:
            raise HTTPException(429, "kitchen's slammed, give us a second")
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
        table = req.table
        if table is None:
            table = _next_table
            _next_table = _next_table + 1 if _next_table < 99 else FIRST_GUEST_TABLE
        o = _add(table, items)
    return {"id": o["id"], "callout": o["callout"], "table": table}


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
        tag = {"new": "", "fired": ", cooking", "flagged": ", has a sold-out item" + (", guest not texted yet" if o.get("pending") else "")}[o["status"]]
        parts.append(f"{o['table']}{tag}: " + "; ".join(_say_item(i) for i in o["items"]))
    oldest = int((time.time() - tickets[0]["created"]) // 60)
    wait = f" Oldest is table {tickets[0]['table']}, {oldest} minutes." if oldest >= 1 else ""
    return {"summary": f"{len(tickets)} open. " + ". ".join(parts) + "." + wait,
            "tickets": [{"table": o["table"], "status": o["status"], "callout": o["callout"]} for o in tickets]}


@router.post("/fire")
def fire(req: FireIn):
    """Agent tool: mark the table's open ticket as fired."""
    paused = ""
    if req.instead_of is not None and req.instead_of != req.table:
        h = hold(FireIn(table=req.instead_of))
        paused = (h["summary"] + " ") if h["ok"] else ""
    with _lock:
        for o in sorted(_open(), key=lambda o: o["created"]):
            if o["table"] == req.table and o["status"] in ("new", "flagged"):
                o["status"] = "fired"
                return {"summary": f"{paused}Starting table {req.table}.", "ok": True}
    return {"summary": f"No open ticket for table {req.table}.", "ok": False}


@router.post("/hold")
def hold(req: FireIn):
    """Agent tool: undo a fire (Marco changed his mind)."""
    with _lock:
        for o in sorted(_open(), key=lambda o: -o["created"]):
            if o["table"] == req.table and o["status"] == "fired":
                o["status"] = "flagged" if (o["message"] or o.get("pending")) else "new"
                return {"summary": f"Pausing table {req.table}.", "ok": True}
    return {"summary": f"Table {req.table} wasn't cooking yet.", "ok": False}


@router.post("/86")
def eighty_six(req: EightySixIn):
    """Agent tool: mark an item sold out and flag affected orders. Guests are NOT
    texted yet: the agent proposes an offer and calls /offer once the chef agrees."""
    name = _match_item(req.item)
    if not name:
        return _unknown(req.item)
    swap = _suggest_swap(name)
    with _lock:
        eighty_sixed.add(name)
        hit = []
        for o in _open():
            if any(i["name"] == name for i in o["items"]):
                o["status"] = "flagged"
                if not o["message"]:
                    o["pending"] = name  # waiting on the chef's OK before texting
                hit.append(o["table"])
        hit = sorted(set(hit))  # a table with two open orders is still one table
    if not hit:
        return {"summary": f"{name.capitalize()} is sold out. No open orders affected.", "ok": True, "tables": []}
    return {"summary": f"{name.capitalize()} is sold out. That affects table{'s' if len(hit) > 1 else ''} {_join(hit)}. "
                       f"Nothing sent yet. Suggested offer: a free swap to a {swap} and {COMP} on us. "
                       f"Ask the chef to approve or name a different swap.",
            "ok": True, "tables": hit, "suggested_swap": swap}


def _suggest_swap(name: str) -> str:
    for cand in [SWAP.get(name, "classic burger"), "chicken sandwich", "classic burger", "veggie burger"]:
        if cand != name and cand not in eighty_sixed:
            return cand
    return "classic burger"


class OfferIn(BaseModel):
    item: str
    swap: str | None = None   # menu item to offer instead; "none" for no swap
    drink: bool = True        # comp a drink


@router.post("/offer")
def send_offer(req: OfferIn):
    """Agent tool: after the chef approves, text the swap/comp offer to every
    order still waiting on a sold-out item."""
    name = _match_item(req.item)
    if not name:
        return _unknown(req.item)
    swap = None
    if req.swap and req.swap.strip().lower() not in ("none", "no", "nothing", "no swap"):
        swap = _match_item(req.swap)
        if not swap:
            return _unknown(req.swap)
        if swap in eighty_sixed or swap == name:
            return {"summary": f"Can't offer {swap}, it's sold out. Ask the chef for another swap.", "ok": False}
    with _lock:
        hit = []
        for o in _open():
            if o.get("pending") == name:
                if swap and req.drink:
                    o["message"] = f"Sorry, we just ran out of the {name}. We can swap in a {swap} at no charge, and {COMP} is on us."
                elif swap:
                    o["message"] = f"Sorry, we just ran out of the {name}. We can swap in a {swap} at no charge."
                elif req.drink:
                    o["message"] = f"Sorry, we just ran out of the {name}. A drink is on us while you pick something else."
                else:
                    o["message"] = f"Sorry, we just ran out of the {name}. Please pick something else from the menu."
                o.pop("pending", None)
                hit.append(o["table"])
        hit = sorted(set(hit))
    if not hit:
        return {"summary": f"No guests waiting on an offer for {name}.", "ok": False}
    what = " and ".join(x for x in [f"a free swap to a {swap}" if swap else "", f"{COMP} on us" if req.drink else ""] if x) or "an apology"
    return {"summary": f"Texted table{'s' if len(hit) > 1 else ''} {_join(hit)}: {what}.", "ok": True, "tables": hit}


@router.get("/table/{table}")
def table_status(table: int):
    """Phone lookup: every order for a table (newest first), including done ones."""
    return {"table": table, "orders": sorted([o for o in orders if o["table"] == table], key=lambda o: -o["created"])}


@router.post("/restock")
def restock(req: EightySixIn):
    """Agent tool: an 86'd item is back. Guests already messaged keep their offer."""
    name = _match_item(req.item)
    if not name:
        return _unknown(req.item)
    with _lock:
        if name not in eighty_sixed:
            return {"summary": f"{name.capitalize()} wasn't sold out.", "ok": False}
        eighty_sixed.discard(name)
        for o in _open():  # back before anyone was texted: those orders are fine again
            if o.get("pending") == name:
                o.pop("pending", None)
                o["status"] = "new"
    return {"summary": f"{name.capitalize()} is back on the menu.", "ok": True}


@router.post("/bump")
def bump(req: FireIn):
    """Agent tool: a table's food went out; clear its ticket from the board."""
    with _lock:
        for o in sorted(_open(), key=lambda o: o["created"]):
            if o["table"] == req.table:
                o["status"] = "done"
                return {"summary": f"Table {req.table} is done.", "ok": True}
    return {"summary": f"No open ticket for table {req.table}.", "ok": False}


@router.post("/reset")
def reset():
    """Rehearsal helper: back to the seeded board."""
    with _lock:
        _seed()
    return {"ok": True}
