#!/usr/bin/env python3

import json
import re


def create_ramps(parts):
    y_start = 0
    angle = round(45 / parts, 3)
    height = round(1 / parts, 3)

    y = 0
    identifier = f"{angle.__str__().replace('.0', '').replace('.', '_')}"

    for part in range(1, parts + 1):
        ################################################################################################################
        base_road_ramp_identifier = f'base_road_ramp_{identifier}{f'_part{part}' if parts > 1 else ''}'
        road_ramp_marking_identifier = f'road_ramp_marking_{identifier}{f'_part{part}' if parts > 1 else ''}'
        geometry_identifier = f'road_ramp_{identifier}{f'_part{part}' if parts > 1 else ''}'

        ################################################################################################################
        # Calculate cubes for this part
        cubes = []
        if part > 1:
            cubes.append({
                "origin": [-8, 0, -8],
                "size": [16, y_start, 16],
                "uv": {
                    "north": {"uv": [0, 15], "uv_size": [16, 1]},
                    "east": {"uv": [0, 15], "uv_size": [16, 1]},
                    "south": {"uv": [0, 15], "uv_size": [16, 1]},
                    "west": {"uv": [0, 15], "uv_size": [16, 1]},
                    "up": {"uv": [0, 0], "uv_size": [16, 16]},
                    "down": {"uv": [0, 0], "uv_size": [16, 16]}
                }
            })

        z_size = round(16 - y * parts, 3)
        while z_size < 1:
            z_size = 16 + z_size

        print(f"{geometry_identifier} y:{y} y_start:{y_start} z_size:{z_size}")

        while z_size > 0:
            # print(f"  y:{y} z_size:{z_size}")
            cubes.append({
                "origin": [-8, y, -8],
                "size": [16, height, z_size],
                "uv": {
                    "north": {"uv": [0, 15], "uv_size": [16, 1]},
                    "east": {"uv": [0, 15], "uv_size": [16, 1]},
                    "south": {"uv": [0, 15], "uv_size": [16, 1]},
                    "west": {"uv": [0, 15], "uv_size": [16, 1]},
                    "up": {"uv": [0, 0], "uv_size": [16, 16]},
                    "down": {"uv": [0, 0], "uv_size": [16, 16]}
                }
            })
            y = round(y + height, 3)
            z_size = round(z_size - (parts * height), 3)

        y_start = round(y, 3)

        ################################################################################################################
        geometry_data = {
            "format_version": "1.21.60",
            "minecraft:geometry": [
                {
                    "description": {
                        "identifier": f"geometry.{geometry_identifier}",
                        "texture_width": 16,
                        "texture_height": 16,
                        "visible_bounds_width": 1,
                        "visible_bounds_height": 1,
                        "visible_bounds_offset": [0, 0.75, 0],
                    },
                    "item_display_transforms": {
                        "gui": {"rotation": [30, 45, 0]},
                    },
                    "bones": [
                        {
                            "name": "block",
                            "pivot": [0, 0, 0],
                            "cubes": cubes
                        },
                    ]
                }
            ]
        }
        with open(f"RP/models/blocks/{geometry_identifier}.geo.json", 'w') as f:
            f.write(json.dumps(geometry_data, indent=2))

        block_height = round(y, 3) if y <= 16.0 else 16.0

        ################################################################################################################
        # Base road ramp with variants
        base_road_ramp_data = {
            "format_version": "1.21.60",
            "minecraft:block": {
                "description": {
                    "identifier": f"jct:{base_road_ramp_identifier}",
                    "menu_category": {
                        "category": "construction"
                    },
                    "traits": {
                        "minecraft:placement_direction": {
                            "enabled_states": ["minecraft:cardinal_direction"]
                        }
                    }
                },
                "components": {
                    "minecraft:collision_box": {
                        "origin": [-8, 0, -8],
                        "size": [16, block_height, 16],
                    },
                    "minecraft:selection_box": {
                        "origin": [-8, 0, -8],
                        "size": [16, block_height, 16]
                    },
                    "minecraft:destructible_by_mining": {
                        "seconds_to_destroy": 1
                    },
                    "minecraft:destructible_by_explosion": {
                        "explosion_resistance": 30
                    },
                    "minecraft:geometry": f"geometry.{geometry_identifier}",
                    "minecraft:material_instances": {
                        "*": {
                            "texture": "base_road",
                            "render_method": "alpha_test_single_sided"
                        }
                    },
                    "minecraft:map_color": "#353637",
                },
                "permutations": [
                    {
                        "condition": "q.block_state('minecraft:cardinal_direction') == 'north' ",
                        "components": {"minecraft:transformation": {"rotation": [0, 0, 0]}}
                    },
                    {
                        "condition": "q.block_state('minecraft:cardinal_direction') == 'south' ",
                        "components": {"minecraft:transformation": {"rotation": [0, 180, 0]}}
                    },
                    {
                        "condition": "q.block_state('minecraft:cardinal_direction') == 'east' ",
                        "components": {"minecraft:transformation": {"rotation": [0, 270, 0]}}
                    },
                    {
                        "condition": "q.block_state('minecraft:cardinal_direction') == 'west' ",
                        "components": {"minecraft:transformation": {"rotation": [0, 90, 0]}}
                    }
                ],
            }
        }

        with open(f"BP/blocks/base_road_ramp/{base_road_ramp_identifier}.block.json", 'w') as f:
            f.write(json.dumps(base_road_ramp_data, indent=2))

        ################################################################################################################
        # Road ramp marking with variants
        road_ramp_marking_data = {
            "format_version": "1.21.60",
            "minecraft:block": {
                "description": {
                    "identifier": f"jct:{road_ramp_marking_identifier}",
                    "menu_category": {
                        "category": "construction"
                    },
                    "traits": {
                        "minecraft:placement_direction": {
                            "enabled_states": ["minecraft:cardinal_direction",]
                        }
                    }
                },
                "components": {
                    "minecraft:collision_box": {
                        "origin": [-8, 0, -8],
                        "size": [16, block_height, 16],
                    },
                    "minecraft:selection_box": {
                        "origin": [-8, 0, -8],
                        "size": [16, block_height, 16]
                    },
                    "minecraft:destructible_by_mining": {
                        "seconds_to_destroy": 1
                    },
                    "minecraft:destructible_by_explosion": {
                        "explosion_resistance": 30
                    },
                    "minecraft:geometry": f"geometry.{geometry_identifier}",
                    "minecraft:material_instances": {
                        "*": {
                            "texture": "base_road",
                            "render_method": "alpha_test_single_sided",
                        },
                        "up": {
                            "texture": "road_marking",
                            "render_method": "alpha_test_single_sided"
                        },
                        "marking": {
                            "texture": "road_marking",
                            "render_method": "alpha_test_single_sided"
                        },
                        "north": "marking",
                        "south": "marking"
                    },
                    "minecraft:map_color": "#353637"
                },
                "permutations": [
                    {
                        "condition": "q.block_state('minecraft:cardinal_direction') == 'north' ",
                        "components": {"minecraft:transformation": {"rotation": [0, 0, 0]}}
                    },
                    {
                        "condition": "q.block_state('minecraft:cardinal_direction') == 'south' ",
                        "components": {"minecraft:transformation": {"rotation": [0, 180, 0]}}
                    },
                    {
                        "condition": "q.block_state('minecraft:cardinal_direction') == 'east' ",
                        "components": {"minecraft:transformation": {"rotation": [0, 270, 0]}}
                    },
                    {
                        "condition": "q.block_state('minecraft:cardinal_direction') == 'west' ",
                        "components": {"minecraft:transformation": {"rotation": [0, 90, 0]}}
                    }
                ]
            }
        }

        with open(f"BP/blocks/road_ramp_marking/{road_ramp_marking_identifier}.block.json", 'w') as f:
            f.write(json.dumps(road_ramp_marking_data, indent=2))


create_ramps(1)
create_ramps(2)
create_ramps(3)
create_ramps(4)
create_ramps(6)
create_ramps(8)
