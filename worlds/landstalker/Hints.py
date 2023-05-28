from BaseClasses import MultiWorld
from worlds.landstalker.data.hint_source import HINT_SOURCES_JSON


def generate_blurry_location_hint(location, random):
    cleaned_location_name = location.hint_text.lower().translate({ord(c): None for c in '(),:'})
    cleaned_location_name.replace('-', ' ')
    cleaned_location_name.replace('/', ' ')
    cleaned_location_name.replace('.', ' ')
    location_name_words = [w for w in cleaned_location_name.split(' ') if len(w) > 3]

    random_word_1 = "mysterious"
    random_word_2 = "place"
    if len(location_name_words) > 0:
        random_word_1 = random.choice(location_name_words)
        location_name_words.remove(random_word_1)
        if len(location_name_words) > 0:
            random_word_2 = random.choice(location_name_words)
    return [random_word_1, random_word_2]


def generate_lithograph_hint(multiworld: MultiWorld, player: int):
    hint_text = "It's barely readable:\n"

    my_jewel_items = [item for item in multiworld.itempool if item.player == player and " Jewel" in item.name]
    for item in my_jewel_items:
        # Jewel hints are composed of 4 'words' shuffled randomly:
        # - the name of the player whose world contains said jewel
        # - the color of the jewel
        # - two random words from the location name
        words = generate_blurry_location_hint(item.location, multiworld.per_slot_randoms[player])
        words[0] = words[0].upper()
        words[1] = words[1].upper()
        words.append(item.name.split(' ')[0].upper())
        words.append(multiworld.player_name[item.location.player].upper())
        multiworld.per_slot_randoms[player].shuffle(words)
        hint_text += f"{words[0]} {words[1]} {words[2]} {words[3]}\n"
    return hint_text.rstrip('\n')


def generate_random_hints(multiworld: MultiWorld, this_player: int):
    hints = {}
    random = multiworld.per_slot_randoms[this_player]

    hint_texts = []

    # Exclude Life Stock from the hints as some of them are considered as progression for Fahl, but isn't really
    # exciting when hinted
    excluded_items = ["Life Stock"]

    progression_items = [item for item in multiworld.itempool if item.advancement and
                         item.name not in excluded_items]

    local_own_progression_items = [item for item in progression_items if item.player == this_player
                                   and item.location.player == this_player]
    remote_own_progression_items = [item for item in progression_items if item.player == this_player
                                    and item.location.player != this_player]
    local_unowned_progression_items = [item for item in progression_items if item.player != this_player
                                       and item.location.player == this_player]
    remote_unowned_progression_items = [item for item in progression_items if item.player != this_player
                                        and item.location.player != this_player]

    # Hint-type #1: Own progression item in own world
    for item in local_own_progression_items:
        region_hint = item.location.parent_region.hint_text
        hint_texts.append(f"I can sense {item.name} {region_hint}.")

    # Hint-type #2: Remote progression item in own world
    for item in local_unowned_progression_items:
        other_player = multiworld.player_name[item.player]
        own_local_region = item.location.parent_region.hint_text
        hint_texts.append(f"You might find something useful for {other_player} {own_local_region}. "
                          f"It is a {item.name}, to be precise.")

    # Hint-type #3: Own progression item in remote location
    for item in remote_own_progression_items:
        other_player = multiworld.player_name[item.location.player]
        if item.location.game == 'Landstalker':
            region_hint_name = item.location.parent_region.hint_text
            hint_texts.append(f"If you need {item.name}, tell {other_player} to look {region_hint_name}.")
        else:
            [word_1, word_2] = generate_blurry_location_hint(item.location, random)
            if word_1 == "mysterious" and word_2 == "place":
                continue
            hint_texts.append(f"Looking for {item.name}? I read something about {other_player}'s world... "
                              f"Does \"{word_1} {word_2}\" remind you anything?")

    # Hint-type #4: Remote progression item in remote location
    for item in remote_unowned_progression_items:
        owner_name = multiworld.player_name[item.player]
        if item.location.player == item.player:
            world_name = "their own world"
        else:
            world_name = f"{multiworld.player_name[item.location.player]}'s world"
        [word_1, word_2] = generate_blurry_location_hint(item.location, random)
        if word_1 == "mysterious" and word_2 == "place":
            continue
        hint_texts.append(f"I once found {owner_name}'s {item.name} in {world_name}. "
                          f"I remember \"{word_1} {word_2}\"... Does that make any sense?")

    # Hint-type #5: Jokes
    other_player_names = [name for player, name in multiworld.player_name.items() if player != this_player]
    if len(other_player_names) != 0:
        random_player_name = random.choice(other_player_names)
        hint_texts.append(f"{random_player_name}'s world is objectively better than yours.")

    hint_texts.append(f"Have you found all of the {len(multiworld.itempool)} items in this universe?")

    local_progression_item_count = len(local_own_progression_items) + len(local_unowned_progression_items)
    remote_progression_item_count = len(remote_own_progression_items) + len(remote_unowned_progression_items)
    percent = (local_progression_item_count / (local_progression_item_count + remote_progression_item_count)) * 100
    hint_texts.append(f"Did you know that your world contains {int(percent)} percent of all progression items?")

    # Shuffle hint texts and hint source names, and pair the two of those together
    hint_texts = list(set(hint_texts))
    random.shuffle(hint_texts)

    hint_count = multiworld.hint_count[this_player].value
    del hint_texts[hint_count:]

    hint_source_names = [source["description"] for source in HINT_SOURCES_JSON if
                         source["description"].startswith("Foxy")]
    random.shuffle(hint_source_names)

    for i in range(hint_count):
        hints[hint_source_names[i]] = hint_texts[i]
    return hints
