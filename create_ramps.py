#!/usr/bin/env python3

import json
import re


def straight_road_ramp(parts):
    y_start = 0
    angle = round(45 / parts, 3)
    height = round(1 / parts, 3)

    y = 0
    identifier = f"{angle.__str__().replace('.0', '').replace('.', '_')}"

    for part in range(1, parts + 1):
        ################################################################################################################
        base_road_ramp_identifier = f'base_road_ramp_{identifier}{f"_part{part}" if parts > 1 else ""}'
        road_ramp_marking_identifier = f'road_ramp_marking_{identifier}{f"_part{part}" if parts > 1 else ""}'
        geometry_identifier = f'road_ramp_{identifier}{f"_part{part}" if parts > 1 else ""}'

        ################################################################################################################
        # Calculate cubes for this part
        cubes = []
        if part > 1:
            cubes.append({"origin": [-8, 0, -8], "size": [16, y_start, 16], "uv": {
                "north": {"uv": [0, 15], "uv_size": [16, 1]},
                "east": {"uv": [0, 15], "uv_size": [16, 1]},
                "south": {"uv": [0, 15], "uv_size": [16, 1]},
                "west": {"uv": [0, 15], "uv_size": [16, 1]},
                "up": {"uv": [0, 0], "uv_size": [16, 16]},
                "down": {"uv": [0, 0], "uv_size": [16, 16]}
            }})

        z_size = round(16 - y * parts, 3)
        while z_size < 1:
            z_size = 16 + z_size

        print(f"{geometry_identifier} y:{y} y_start:{y_start} z_size:{z_size}")

        while z_size > 0:
            # print(f"  y:{y} z_size:{z_size}")
            cubes.append({"origin": [-8, y, -8], "size": [16, height, z_size], "uv": {
                "north": {"uv": [0, 15], "uv_size": [16, 1]},
                "east": {"uv": [0, 15], "uv_size": [16, 1]},
                "south": {"uv": [0, 15], "uv_size": [16, 1]},
                "west": {"uv": [0, 15], "uv_size": [16, 1]},
                "up": {"uv": [0, 0], "uv_size": [16, 16]},
                "down": {"uv": [0, 0], "uv_size": [16, 16]}
            }})
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
                    "item_display_transforms": {"gui": {"rotation": [30, 45, 0]}},
                    "bones": [{
                        "name": "block",
                        "pivot": [0, 0, 0],
                        "cubes": cubes
                    }]
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
                    "menu_category": {"category": "construction"},
                    "traits": {"minecraft:placement_direction": {"enabled_states": ["minecraft:cardinal_direction"]}}
                },
                "components": {
                    "minecraft:collision_box": {"origin": [-8, 0, -8], "size": [16, block_height, 16]},
                    "minecraft:selection_box": {"origin": [-8, 0, -8], "size": [16, block_height, 16]},
                    "minecraft:destructible_by_mining": {"seconds_to_destroy": 1},
                    "minecraft:destructible_by_explosion": {"explosion_resistance": 30},
                    "minecraft:geometry": f"geometry.{geometry_identifier}",
                    "minecraft:material_instances": {
                        "*": {"texture": "base_road", "render_method": "alpha_test_single_sided"}
                    },
                    "minecraft:map_color": "#353637",
                },
                "permutations": [
                    {"condition": "q.block_state('minecraft:cardinal_direction') == 'north' ",
                     "components": {"minecraft:transformation": {"rotation": [0, 0, 0]}}},
                    {"condition": "q.block_state('minecraft:cardinal_direction') == 'south' ",
                     "components": {"minecraft:transformation": {"rotation": [0, 180, 0]}}},
                    {"condition": "q.block_state('minecraft:cardinal_direction') == 'east' ",
                     "components": {"minecraft:transformation": {"rotation": [0, 270, 0]}}},
                    {"condition": "q.block_state('minecraft:cardinal_direction') == 'west' ",
                     "components": {"minecraft:transformation": {"rotation": [0, 90, 0]}}}
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
                    "menu_category": {"category": "construction"},
                    "traits": {"minecraft:placement_direction": {"enabled_states": ["minecraft:cardinal_direction", ]}}
                },
                "components": {
                    "minecraft:collision_box": {"origin": [-8, 0, -8], "size": [16, block_height, 16]},
                    "minecraft:selection_box": {"origin": [-8, 0, -8], "size": [16, block_height, 16]},
                    "minecraft:destructible_by_mining": {"seconds_to_destroy": 1},
                    "minecraft:destructible_by_explosion": {"explosion_resistance": 30},
                    "minecraft:geometry": f"geometry.{geometry_identifier}",
                    "minecraft:material_instances": {
                        "*": {"texture": "base_road", "render_method": "alpha_test_single_sided", },
                        "up": {"texture": "road_marking", "render_method": "alpha_test_single_sided"},
                        "marking": {"texture": "road_marking", "render_method": "alpha_test_single_sided"},
                        "north": "marking",
                        "south": "marking"
                    },
                    "minecraft:map_color": "#353637"
                },
                "permutations": [
                    {"condition": "q.block_state('minecraft:cardinal_direction') == 'north' ",
                     "components": {"minecraft:transformation": {"rotation": [0, 0, 0]}}},
                    {"condition": "q.block_state('minecraft:cardinal_direction') == 'south' ",
                     "components": {"minecraft:transformation": {"rotation": [0, 180, 0]}}},
                    {"condition": "q.block_state('minecraft:cardinal_direction') == 'east' ",
                     "components": {"minecraft:transformation": {"rotation": [0, 270, 0]}}},
                    {"condition": "q.block_state('minecraft:cardinal_direction') == 'west' ",
                     "components": {"minecraft:transformation": {"rotation": [0, 90, 0]}}}
                ]
            }
        }

        with open(f"BP/blocks/road_ramp_marking/{road_ramp_marking_identifier}.block.json", 'w') as f:
            f.write(json.dumps(road_ramp_marking_data, indent=2))


# !/usr/bin/env python3

import json
from typing import List, Dict
from console_utils import ConsoleStyle


class RampAlgorithm:

    @classmethod
    def __init__(cls):
        ConsoleStyle.print_section(f"Generating Ramp Parts for {cls.__name__} Algorithm", "=", "🏗️")

    @classmethod
    def create_geometry_file(cls, part_type: str, cubes: List[Dict]) -> Dict:
        geometry = {
            "format_version": "1.21.60",
            "minecraft:geometry": [
                {
                    "description": {
                        "identifier": f"geometry.road_ramp_oblique_{part_type}",
                        "texture_width": 16,
                        "texture_height": 16,
                        "visible_bounds_width": 1,
                        "visible_bounds_height": 1,
                        "visible_bounds_offset": [0, 0.75, 0]
                    },
                    "item_display_transforms": {
                        "gui": {
                            "rotation": [30, 45, 0]
                        }
                    },
                    "bones": [
                        {
                            "name": "block",
                            "pivot": [0, 0, 0],
                            "cubes": cubes
                        }
                    ]
                }
            ]
        }

        return geometry

    @classmethod
    def save_geometry_file(cls, geometry: Dict, part_type: str):
        output_dir: str = "RP/models/blocks/"
        filename: str = f"{output_dir}road_ramp_oblique_{part_type}.geo.json"
        try:
            # Konwertuj geometrię na string z customowym formatowaniem dla kostek
            json_str = json.dumps(geometry, indent=2, ensure_ascii=False)

            # Podziel na linie
            lines = json_str.split('\n')
            formatted_lines = []

            in_cubes_array = False
            cube_indent = 0
            i = 0

            while i < len(lines):
                line = lines[i]

                if '"cubes": [' in line:
                    in_cubes_array = True
                    cube_indent = len(line) - len(line.lstrip())
                    formatted_lines.append(line)
                    i += 1
                elif in_cubes_array and line.strip() == ']':
                    in_cubes_array = False
                    formatted_lines.append(line)
                    i += 1
                elif in_cubes_array and line.strip().startswith('{'):
                    # Kostka – zapisz w jednej linii
                    cube_content = line.strip()
                    brace_count = cube_content.count('{') - cube_content.count('}')
                    j = i + 1

                    # Zbierz wszystkie linie kostki
                    while brace_count > 0 and j < len(lines):
                        next_line = lines[j]
                        cube_content += next_line.strip()
                        brace_count += next_line.count('{') - next_line.count('}')
                        j += 1

                    # Dodaj kostkę w jednej linii
                    formatted_lines.append(' ' * cube_indent + cube_content)
                    i = j  # Przeskocz do następnej linii po kostce
                elif in_cubes_array and (line.strip().startswith('},') or line.strip().startswith('}')):
                    # To jest koniec kostki, już przetworzone
                    i += 1
                else:
                    formatted_lines.append(line)
                    i += 1

            # Zapisz sformatowany JSON
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(formatted_lines))

            ConsoleStyle.print_file_operation("Created", filename, "OK")
        except Exception as e:
            ConsoleStyle.print_file_operation("Failed to create", filename, "ERROR")
            print(ConsoleStyle.error(f"Error: {e}"))

    @classmethod
    def generate_block_file(cls, part_type: str):
        """Generuje plik bloku na podstawie typu części"""
        # Określ prefiks i katalog na podstawie typu części
        output_dir = "BP/blocks/road_ramp_oblique/"
        filename = f"{output_dir}road_ramp_oblique_{part_type}.block.json"

        # Określ wysokość na podstawie typu części
        height = 16.0
        if part_type == "22_5_part1":
            height = 0
        elif part_type == "22_5_part2":
            height = 8
        elif part_type == "11_25_part1":
            height = 0
        elif part_type == "11_25_part2":
            height = 4
        elif part_type == "11_25_part3":
            height = 8
        elif part_type == "11_25_part4":
            height = 12
        elif part_type == "11_25_part5":
            height = 16

        block_data = {
            "format_version": "1.21.60",
            "minecraft:block": {
                "description": {
                    "identifier": f"jct:road_ramp_oblique_{part_type}",
                    "menu_category": {
                        "category": "construction"
                    },
                    "traits": {
                        "minecraft:placement_direction": {
                            "enabled_states": [
                                "minecraft:cardinal_direction"
                            ]
                        }
                    }
                },
                "components": {
                    "minecraft:collision_box": {
                        "origin": [-8, 0, -8],
                        "size": [16, height, 16]
                    },
                    "minecraft:selection_box": {
                        "origin": [-8, 0, -8],
                        "size": [16, height + 4 if height < 16 else 16, 16]
                    },
                    "minecraft:destructible_by_mining": {
                        "seconds_to_destroy": 1
                    },
                    "minecraft:destructible_by_explosion": {
                        "explosion_resistance": 30
                    },
                    "minecraft:geometry": f"geometry.road_ramp_oblique_{part_type}",
                    "minecraft:material_instances": {
                        "*": {
                            "texture": "base_road",
                            "render_method": "alpha_test_single_sided"
                        }
                    },
                    "minecraft:map_color": "#353637"
                },
                "permutations": [
                    {
                        "condition": "q.block_state('minecraft:cardinal_direction') == 'north' ",
                        "components": {
                            "minecraft:transformation": {
                                "rotation": [0, 0, 0]
                            }
                        }
                    },
                    {
                        "condition": "q.block_state('minecraft:cardinal_direction') == 'south' ",
                        "components": {
                            "minecraft:transformation": {
                                "rotation": [0, 180, 0]
                            }
                        }
                    },
                    {
                        "condition": "q.block_state('minecraft:cardinal_direction') == 'east' ",
                        "components": {
                            "minecraft:transformation": {
                                "rotation": [0, 270, 0]
                            }
                        }
                    },
                    {
                        "condition": "q.block_state('minecraft:cardinal_direction') == 'west' ",
                        "components": {
                            "minecraft:transformation": {
                                "rotation": [0, 90, 0]
                            }
                        }
                    }
                ]
            }
        }

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(block_data, f, indent=2, ensure_ascii=False)

            ConsoleStyle.print_file_operation("Created block", filename, "OK")
        except Exception as e:
            ConsoleStyle.print_file_operation("Failed to create block", filename, "ERROR")
            print(ConsoleStyle.error(f"Error: {e}"))

    @classmethod
    def generate(cls, parts: Dict):
        for part_type, cubes in parts.items():
            print(ConsoleStyle.process(f"Generating [{part_type}] content..."))
            part_geometry = cls.create_geometry_file(part_type, cubes)
            cls.save_geometry_file(part_geometry, part_type)
            cls.generate_block_file(part_type)


class RoadRampOblique225(RampAlgorithm):

    @classmethod
    def __init__(cls):
        super().__init__()
        cls.generate({
            "22_5_part1": cls._generate_part1_algorithm(),
            "22_5_part2": cls._generate_part2_algorithm(),
            "22_5_part3": cls._generate_part3_algorithm(),
        })

    @classmethod
    def _generate_part1_algorithm(cls) -> List[Dict]:
        """Pierwsza część rampy 22.5° - podstawowa warstwa (co 0.5 klocka)"""
        cubes = []

        for origin_y in range(0, 16, 1):  # Co 1 warstwa
            for origin_z in range(-8, 8 - origin_y, 1):  # Co 1 pozycja Z
                size_x = 16 - (2 * origin_y) - (origin_z + 8)
                if size_x > 0:
                    # Generuj kostki co 0.5 klocka
                    for x_offset in range(0, int(size_x * 2), 1):  # Co 0.5 jednostki
                        x_pos = -8 + (x_offset * 0.5)
                        cube = {
                            "origin": [x_pos, origin_y, origin_z],
                            "size": [0.5, 1, 1]
                        }
                        cubes.append(cube)

        return cubes

    @classmethod
    def _generate_part2_algorithm(cls) -> List[Dict]:
        """Druga część rampy 22.5° - malejące główne części z dodatkowymi kostkami (co 0.5 klocka)"""
        cubes = []

        # Warstwa 0 - pełna (co 0.5 klocka)
        for x in range(-8, 8, 1):  # Co 1 pozycja X
            for z in range(-8, 8, 1):  # Co 1 pozycja Z
                cube = {
                    "origin": [x, 0, z],
                    "size": [1, 1, 1]
                }
                cubes.append(cube)

        for origin_y in range(1, 16):  # Wysokość 1-15
            if origin_y <= 8:
                # Warstwy 1-8: główna część + dodatkowe kostki
                main_size_z = 16 - (origin_y * 2)  # Malejąca głębokość Z
                if main_size_z > 0:
                    # Główna część - generuj co 0.5 klocka
                    for x in range(-8, 8, 1):
                        for z in range(-8, -8 + int(main_size_z), 1):
                            cube = {
                                "origin": [x, origin_y, z],
                                "size": [1, 1, 1]
                            }
                            cubes.append(cube)

                # Dodatkowe kostki na prawej stronie - algorytm matematyczny
                num_cubes = 2 * origin_y
                start_z = 8 - 2 * origin_y
                for i in range(num_cubes):
                    origin_z = start_z + i
                    size_x = 16 - i
                    # Generuj co 0.5 klocka
                    for x_offset in range(0, int(size_x * 2), 1):
                        x_pos = -8 + (x_offset * 0.5)
                        cube = {
                            "origin": [x_pos, origin_y, origin_z],
                            "size": [0.5, 1, 1]
                        }
                        cubes.append(cube)
            else:
                # Warstwy 9-15: tylko małe kostki z malejącymi rozmiarami
                offset_y = origin_y - 8
                num_cubes = 16 - 2 * offset_y
                max_size = 16 - 2 * offset_y
                for i in range(num_cubes):
                    origin_z = -8 + i
                    size_x = max_size - i
                    # Generuj co 0.5 klocka
                    for x_offset in range(0, int(size_x * 2), 1):
                        x_pos = -8 + (x_offset * 0.5)
                        cube = {
                            "origin": [x_pos, origin_y, origin_z],
                            "size": [0.5, 1, 1]
                        }
                        cubes.append(cube)

        return cubes

    @classmethod
    def _generate_part3_algorithm(cls) -> List[Dict]:
        """Trzecia część rampy 22.5° - 16 warstw, pierwsze 8 pełne, kolejne 8 ścinane (co 0.5 klocka)"""
        cubes = []

        for origin_y in range(16):  # 16 warstw
            if origin_y < 8:
                # Pierwsze 8 warstw (0-7) - pełne 16x16 (co 0.5 klocka)
                for x in range(-8, 8, 1):
                    for z in range(-8, 8, 1):
                        cube = {
                            "origin": [x, origin_y, z],
                            "size": [1, 1, 1]
                        }
                        cubes.append(cube)
            else:
                # Kolejne 8 warstw (8-15) - ścinane podobnie do part2
                offset_y = origin_y - 8
                num_small_cubes = offset_y

                num_normal_cubes = 16 - 2 * offset_y + 1
                for z in range(-8, 8):
                    if z >= -8 + num_normal_cubes:
                        # To pozycja dla małej kostki
                        i = z - (-8 + num_normal_cubes)
                        size_x = 15 - i
                        # Generuj co 0.5 klocka
                        for x_offset in range(0, int(size_x * 2), 1):
                            x_pos = -8 + (x_offset * 0.5)
                            cube = {
                                "origin": [x_pos, origin_y, z],
                                "size": [0.5, 1, 1]
                            }
                            cubes.append(cube)
                    else:
                        # To pozycja dla normalnej kostki (co 0.5 klocka)
                        for x in range(-8, 8, 1):
                            cube = {
                                "origin": [x, origin_y, z],
                                "size": [1, 1, 1]
                            }
                            cubes.append(cube)

        return cubes


class RoadRampOblique450(RampAlgorithm):

    @classmethod
    def __init__(cls):
        super().__init__()
        cls.generate({
            "45_part1": cls._generate_part1_algorithm(),
            "45_part2": cls._generate_part2_algorithm(),
        })

    @classmethod
    def _generate_part1_algorithm(cls) -> List[Dict]:
        """Pierwsza część rampy 45° - podstawowa warstwa (co 0.5 klocka)"""
        cubes = []

        for origin_y in range(16):
            for origin_z in range(-8, 8 - origin_y):
                size_x = 16 - origin_y - (origin_z + 8)
                if size_x > 0:
                    # Generuj kostki co 0.5 klocka
                    for x_offset in range(0, int(size_x * 2), 1):
                        x_pos = -8 + (x_offset * 0.5)
                        cube = {
                            "origin": [x_pos, origin_y, origin_z],
                            "size": [0.5, 1, 1]
                        }
                        cubes.append(cube)

        return cubes

    @classmethod
    def _generate_part2_algorithm(cls) -> List[Dict]:
        """Druga część rampy 45° - malejące główne części z dodatkowymi kostkami (co 0.5 klocka)"""
        cubes = []

        for origin_y in range(16):
            for origin_z in range(16):
                threshold = 16 - origin_y + 1
                if origin_z < threshold or origin_y < 2:
                    size_x = 16
                else:
                    # size_x maleje o 1 dla każdego z powyżej threshold
                    size_x = 16 - (origin_z - threshold + 1)

                # Generuj kostki co 0.5 klocka
                for x_offset in range(0, int(size_x * 2), 1):
                    x_pos = -8 + (x_offset * 0.5)
                    cube = {
                        "origin": [x_pos, origin_y, -8 + origin_z],
                        "size": [0.5, 1, 1]
                    }
                    cubes.append(cube)

        return cubes


class RoadRampOblique1125(RampAlgorithm):

    @classmethod
    def __init__(cls):
        super().__init__()
        cls.generate({
            "11_25_part1": cls._generate_part1_algorithm(),
            "11_25_part2": cls._generate_part2_algorithm(),
            "11_25_part3": cls._generate_part3_algorithm(),
            "11_25_part4": cls._generate_part4_algorithm(),
            "11_25_part5": cls._generate_part5_algorithm()
        })

    # Warstwy pełne (co 0.5 klocka)
    @classmethod
    def _squared_layers(cls, level_from: int, level_to: int):
        cubes = []
        for origin_y in range(level_from, level_to + 1):
            for x in range(-8, 8, 1):
                for z in range(-8, 8, 1):
                    cube = {
                        "origin": [x, origin_y, z],
                        "size": [1, 1, 1]
                    }
                    cubes.append(cube)
        return cubes

    # Warstwy prostokąty + dodatkowe kostki
    @classmethod
    def _squared_layers_and_triangles(cls, level_from: int, level_to: int):
        cubes = []
        for origin_y in range(level_from, level_to + 1):
            main_size_z = 16 - 4 * (origin_y - level_from)
            if main_size_z > 0:
                # Generuj co 0.5 klocka
                for x in range(-8, 8, 1):
                    for z in range(-8, -8 + int(main_size_z), 1):
                        cube = {
                            "origin": [x, origin_y, z],
                            "size": [1, 1, 1]
                        }
                        cubes.append(cube)

            # Dodatkowe kostki
            start_z = -8 + main_size_z
            end_z = 7
            for i, z in enumerate(range(start_z, end_z + 1)):
                size_x = max(1, 16 - i)
                # Generuj co 0.5 klocka
                for x_offset in range(0, int(size_x * 2), 1):
                    x_pos = -8 + (x_offset * 0.5)
                    cubes.append({"origin": [x_pos, origin_y, z], "size": [0.5, 1, 1]})

        return cubes

    @classmethod
    def _only_triangles(cls, level_from: int, level_to: int):
        cubes = []
        for origin_y in range(level_from, level_to + 1):
            num_cubes = 12 - 4 * (origin_y - level_from - 1)
            for i in range(num_cubes):
                z = -8 + i
                size_x = num_cubes - i
                # Generuj co 0.5 klocka
                for x_offset in range(0, int(size_x * 2), 1):
                    x_pos = -8 + (x_offset * 0.5)
                    cubes.append({"origin": [x_pos, origin_y, z], "size": [0.5, 1, 1]})

        return cubes

    @classmethod
    def _generate_part1_algorithm(cls) -> List[Dict]:
        """Pierwsza część rampy 11.25° - malejące zakresy z malejącymi rozmiarami (co 0.5 klocka)"""
        cubes = []
        cubes.extend(cls._only_triangles(0, 3))
        return cubes

    @classmethod
    def _generate_part2_algorithm(cls) -> List[Dict]:
        """Druga część rampy 11.25° - prostokąty z dodatkowymi kostkami, potem malejące trójkąty (co 0.5 klocka)"""
        cubes = []
        cubes.extend(cls._squared_layers_and_triangles(0, 3))
        cubes.extend(cls._only_triangles(4, 7))
        return cubes

    @classmethod
    def _generate_part3_algorithm(cls) -> List[Dict]:
        """Trzecia część rampy 11.25° - pełne warstwy, potem prostokąty i trójkąty (co 0.5 klocka)"""
        cubes = []
        cubes.extend(cls._squared_layers(0, 3))
        cubes.extend(cls._squared_layers_and_triangles(4, 7))
        cubes.extend(cls._only_triangles(8, 11))
        return cubes

    @classmethod
    def _generate_part4_algorithm(cls) -> List[Dict]:
        """Czwarta część rampy 11.25° - pełne warstwy, potem prostokąty i trójkąty (co 0.5 klocka)"""
        cubes = []
        cubes.extend(cls._squared_layers(0, 7))
        cubes.extend(cls._squared_layers_and_triangles(8, 11))
        cubes.extend(cls._only_triangles(12, 15))
        return cubes

    @classmethod
    def _generate_part5_algorithm(cls) -> List[Dict]:
        """Piąta część rampy 11.25° - pełne warstwy, potem prostokąty i dodatkowe kostki (co 0.5 klocka)"""
        cubes = []
        cubes.extend(cls._squared_layers(0, 11))
        cubes.extend(cls._squared_layers_and_triangles(12, 15))
        return cubes


def main():
    # RoadRampOblique450()
    RoadRampOblique225()
    RoadRampOblique1125()
    # straight_road_ramp(1)
    straight_road_ramp(2)
    straight_road_ramp(3)
    straight_road_ramp(4)
    straight_road_ramp(6)
    straight_road_ramp(8)


if __name__ == "__main__":
    main()
