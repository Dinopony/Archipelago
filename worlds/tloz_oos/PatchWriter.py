import yaml

from typing import TYPE_CHECKING
from BaseClasses import ItemClassification
from worlds.tloz_oos.patching.ProcedurePatch import OoSProcedurePatch
from .data.Constants import *

if TYPE_CHECKING:
    from . import OracleOfSeasonsWorld


def oos_create_ap_procedure_patch(world: "OracleOfSeasonsWorld") -> OoSProcedurePatch:
    patch = OoSProcedurePatch()

    patch.player = world.player
    patch.player_name = world.multiworld.get_player_name(world.player)

    patch_data = {
        "version": VERSION,
        "seed": world.multiworld.seed,
        "options": world.options.as_dict(*[
            "advance_shop", "animal_companion", "combat_difficulty", "default_seed",
            "enforce_potion_in_shop", "fools_ore", "goal", "golden_beasts_requirement", "master_keys",
            "quick_flute", "remove_d0_alt_entrance", "remove_d2_alt_entrance", "required_essences",
            "shuffle_golden_ore_spots", "shuffle_old_men", "sign_guy_requirement", "tarm_gate_required_jewels",
            "treehouse_old_man_requirement", "warp_to_start", "starting_maps_compasses",
            "keysanity_small_keys", "keysanity_boss_keys", "keysanity_maps_compasses",
            "deterministic_gasha_locations", "shuffle_essences", "shuffle_business_scrubs"
        ]),
        "samasa_gate_sequence": ' '.join([str(x) for x in world.samasa_gate_code]),
        "lost_woods_item_sequence": world.lost_woods_item_sequence,
        "lost_woods_main_sequence": world.lost_woods_main_sequence,
        "default_seasons": world.default_seasons,
        "old_man_rupee_values": world.old_man_rupee_values,
        "dungeon_entrances": {a.replace(" entrance", ""): b.replace("enter ", "")
                              for a, b in world.dungeon_entrances.items()},
        "locations": {},
        "subrosia_portals": world.portal_connections,
        "shop_prices": world.shop_prices,
        "subrosia_seaside_location": world.random.randint(0, 3)
    }

    for loc in world.multiworld.get_locations(world.player):
        # Skip event locations which are not real in-game locations that need to be patched
        if loc.address is None:
            continue
        if loc.item.player == loc.player:
            patch_data["locations"][loc.name] = {
                "item": loc.item.name
            }
        else:
            patch_data["locations"][loc.name] = {
                "item": loc.item.name,
                "player": world.multiworld.get_player_name(loc.item.player),
                "progression": (loc.item.classification & ItemClassification.progression) != 0
            }

    patch.write_file("patch.dat", yaml.dump(patch_data).encode('utf-8'))
    return patch
