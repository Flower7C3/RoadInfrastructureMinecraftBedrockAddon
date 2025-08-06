#!/usr/bin/env python3

import json
import numpy as np
from typing import List, Dict
from console_utils import ConsoleStyle


class MinecraftAddon:
    FORMAT_VERSION = "1.21.60"
    NAMESPACE = 'jct'

    @staticmethod
    def create_file(filename: str, data: str):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(data)
            ConsoleStyle.print_file_operation("Created file", filename, "OK")
        except Exception as e:
            ConsoleStyle.print_file_operation("Failed to create file", filename, "ERROR")
            print(ConsoleStyle.error(f"Error: {e}"))

    @staticmethod
    def create_block_file(output_dir: str, block_identifier: str, geometry_identifier: str, collision_box_size_y: float,
                          selection_box_size_y: float, marking: bool = False):
        """Generuje plik bloku na podstawie typu części"""
        filename = f"BP/blocks/{output_dir}{block_identifier}.block.json"
        data = {
            "format_version": MinecraftAddon.FORMAT_VERSION,
            "minecraft:block": {
                "description": {
                    "identifier": f"{MinecraftAddon.NAMESPACE}:{block_identifier}",
                    "menu_category": {"category": "construction"},
                    "traits": {"minecraft:placement_direction": {"enabled_states": ["minecraft:cardinal_direction"]}}
                },
                "components": {
                    "minecraft:collision_box": {"origin": [-8, 0, -8], "size": [16, collision_box_size_y, 16]},
                    "minecraft:selection_box": {"origin": [-8, 0, -8], "size": [16, selection_box_size_y, 16]},
                    "minecraft:destructible_by_mining": {"seconds_to_destroy": 1},
                    "minecraft:destructible_by_explosion": {"explosion_resistance": 30},
                    "minecraft:geometry": f"geometry.{geometry_identifier}",
                    "minecraft:material_instances": {
                        "*": {"texture": "base_road", "render_method": "alpha_test_single_sided"}
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
        if marking:
            data['minecraft:block']['components']['minecraft:material_instances'] = {
                "*": {"texture": "base_road", "render_method": "alpha_test_single_sided", },
                "up": {"texture": "road_marking", "render_method": "alpha_test_single_sided"},
                "marking": {"texture": "road_marking", "render_method": "alpha_test_single_sided"},
                "north": "marking",
                "south": "marking"
            }
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        MinecraftAddon.create_file(filename, json_str)

    @staticmethod
    def create_geometry_file(output_dir: str, geometry_identifier: str, cubes: List[Dict]):
        filename = f"RP/models/{output_dir}{geometry_identifier}.geo.json"
        geometry_data = {
            "format_version": MinecraftAddon.FORMAT_VERSION,
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

        json_str = MinecraftAddon._flatten_cubes(geometry_data)
        MinecraftAddon.create_file(filename, json_str)

    @staticmethod
    def _flatten_cubes(data):
        # Konwertuj geometrię na string z customowym formatowaniem dla kostek
        json_str = json.dumps(data, indent=2, ensure_ascii=False)

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
        return '\n'.join(formatted_lines)


class RoadRampStraight:

    @classmethod
    def __init__(cls, parts):
        angle = round(45 / parts, 3)
        origin_y = 0
        base_size_y = 0
        size_y = round(1 / parts, 3)

        identifier = f"{angle.__str__().replace('.0', '').replace('.', '_')}"

        ConsoleStyle.print_section(f"Generating Straight Road Ramp for [{angle}° angle]", "=", "🏗️")

        for part in range(1, parts + 1):
            ################################################################################################################
            print(ConsoleStyle.process(f"Generating [{identifier}_part{part}] content..."))
            road_ramp_geometry_identifier = f'road_ramp_{identifier}{f"_part{part}" if parts > 1 else ""}'
            road_ramp_base_block_identifier = f'base_road_ramp_{identifier}{f"_part{part}" if parts > 1 else ""}'
            road_ramp_block_marking_identifier = f'road_ramp_marking_{identifier}{f"_part{part}" if parts > 1 else ""}'

            ################################################################################################################
            # Calculate cubes for this part
            cubes = []
            if part > 1:
                cubes.append({"origin": [-8, 0, -8], "size": [16, base_size_y, 16], "uv": {
                    "north": {"uv": [0, 15], "uv_size": [16, 1]},
                    "east": {"uv": [0, 15], "uv_size": [16, 1]},
                    "south": {"uv": [0, 15], "uv_size": [16, 1]},
                    "west": {"uv": [0, 15], "uv_size": [16, 1]},
                    "up": {"uv": [0, 0], "uv_size": [16, 16]},
                    "down": {"uv": [0, 0], "uv_size": [16, 16]}
                }})

            size_z = round(16 - origin_y * parts, 3)
            while size_z < 1:
                size_z = 16 + size_z

            while size_z > 0:
                cubes.append({"origin": [-8, origin_y, -8], "size": [16, size_y, size_z], "uv": {
                    "north": {"uv": [0, 15], "uv_size": [16, 1]},
                    "east": {"uv": [0, 15], "uv_size": [16, 1]},
                    "south": {"uv": [0, 15], "uv_size": [16, 1]},
                    "west": {"uv": [0, 15], "uv_size": [16, 1]},
                    "up": {"uv": [0, 0], "uv_size": [16, 16]},
                    "down": {"uv": [0, 0], "uv_size": [16, 16]}
                }})
                origin_y = round(origin_y + size_y, 3)
                size_z = round(size_z - (parts * size_y), 3)

            base_size_y = round(origin_y, 3)

            MinecraftAddon.create_geometry_file('blocks/', road_ramp_geometry_identifier, cubes)
            ################################################################################################################
            collision_box_size_y = round(origin_y, 3) if origin_y <= 16.0 else 16.0
            selection_box_size_y = round(origin_y, 3) if origin_y <= 16.0 else 16.0
            MinecraftAddon.create_block_file('base_road_ramp/',
                                             road_ramp_base_block_identifier,
                                             road_ramp_geometry_identifier,
                                             collision_box_size_y, selection_box_size_y)
            # Road ramp marking with variants
            MinecraftAddon.create_block_file('road_ramp_marking/',
                                             road_ramp_block_marking_identifier,
                                             road_ramp_geometry_identifier,
                                             collision_box_size_y, selection_box_size_y, True)
            ################################################################################################################


class RampAlgorithm:
    # Zmienna klasowa dla rozmiaru kroku i kostek
    STEP_SIZE: float = 1.0
    ANGLE: float = None

    @classmethod
    def __init__(cls):
        ConsoleStyle.print_section(
            f"Generating Oblique Road Ramp for [{cls.ANGLE}° angle]",
            "=", "🏗️")

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
                    "item_display_transforms": {"gui": {"rotation": [30, 45, 0]}},
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
    def generate(cls, parts: Dict):
        for part_type, cubes in parts.items():
            print(ConsoleStyle.process(f"Generating [{part_type}] content..."))
            MinecraftAddon.create_geometry_file('blocks/', f"road_ramp_oblique_{part_type}", cubes)

            # Określ wysokość na podstawie typu części
            collision_box_size_y = 16.0
            if part_type == "22_5_part1":
                collision_box_size_y = 0
            elif part_type == "22_5_part2":
                collision_box_size_y = 8
            elif part_type == "11_25_part1":
                collision_box_size_y = 0
            elif part_type == "11_25_part2":
                collision_box_size_y = 4
            elif part_type == "11_25_part3":
                collision_box_size_y = 8
            elif part_type == "11_25_part4":
                collision_box_size_y = 12
            elif part_type == "11_25_part5":
                collision_box_size_y = 16
            selection_box_size_y = collision_box_size_y + 4 if collision_box_size_y < 16 else 16

            MinecraftAddon.create_block_file('road_ramp_oblique/',
                                             f"road_ramp_oblique_{part_type}",
                                             f"road_ramp_oblique_{part_type}",
                                             collision_box_size_y, selection_box_size_y)

    # ===== UNIWERSALNE METODY POMOCNICZE =====

    @classmethod
    def _generate_full_layer(cls, level_from, level_to) -> List[Dict]:
        """Generuje pełne warstwy 16x16 od level_from do level_to"""
        cubes = []
        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            for origin_x in np.arange(-8, 8, cls.STEP_SIZE):
                for origin_z in np.arange(-8, 8, cls.STEP_SIZE):
                    cube = {
                        "origin": [float(origin_x), float(origin_y), float(origin_z)],
                        "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                    }
                    cubes.append(cube)
        return cubes

    @classmethod
    def _generate_main_rectangle_for_layer(cls, origin_y) -> List[Dict]:
        """Generuje główne prostokąty dla konkretnej warstwy"""
        cubes = []
        main_size_z = 16 - (origin_y * 2)  # Malejąca głębokość Z
        if main_size_z > 0:
            for origin_x in np.arange(-8, 8, cls.STEP_SIZE):
                for origin_z in np.arange(-8, -8 + main_size_z, cls.STEP_SIZE):
                    cube = {
                        "origin": [float(origin_x), float(origin_y), float(origin_z)],
                        "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                    }
                    cubes.append(cube)
        return cubes

    @classmethod
    def _generate_main_rectangle(cls, level_from, level_to) -> List[Dict]:
        """Generuje główne prostokąty od level_from do level_to"""
        cubes = []
        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            cubes.extend(cls._generate_main_rectangle_for_layer(origin_y))
        return cubes

    @classmethod
    def _generate_additional_cubes_for_layer(cls, origin_y) -> List[Dict]:
        """Generuje dodatkowe kostki dla konkretnej warstwy"""
        cubes = []
        num_cubes = 2 * origin_y
        start_z = 8 - num_cubes
        for origin_z in np.arange(start_z, start_z + num_cubes, cls.STEP_SIZE):
            size_x = 16 - (origin_z - start_z)
            for origin_x in np.arange(-8, -8 + size_x, cls.STEP_SIZE):
                cube = {
                    "origin": [float(origin_x), float(origin_y), float(origin_z)],
                    "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                }
                cubes.append(cube)
        return cubes

    @classmethod
    def _generate_additional_cubes(cls, level_from, level_to) -> List[Dict]:
        """Generuje dodatkowe kostki od level_from do level_to"""
        cubes = []
        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            cubes.extend(cls._generate_additional_cubes_for_layer(origin_y))
        return cubes

    @classmethod
    def _generate_complete_layers(cls, layer_from, layer_to) -> List[Dict]:
        """Generuje warstwy z głównymi prostokątami i dodatkowymi kostkami"""
        cubes = []
        for origin_y in np.arange(layer_from, layer_to + 1, cls.STEP_SIZE):
            # Główna część dla tej warstwy
            cubes.extend(cls._generate_main_rectangle_for_layer(origin_y))

            # Dodatkowe kostki dla tej warstwy
            cubes.extend(cls._generate_additional_cubes_for_layer(origin_y))
        return cubes


class RoadRampOblique45000(RampAlgorithm):
    ANGLE = 45.0

    @classmethod
    def __init__(cls):
        super().__init__()
        cls.generate({
            "45_part1": cls._generate_part1(),
            "45_part2": cls._generate_part2(),
        })

    @classmethod
    def _generate_45_degree_sloped_ramp(cls, level_from, level_to) -> List[Dict]:
        """Generuje skośną rampę 45° od level_from do level_to"""
        cubes = []
        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            for origin_z in np.arange(-8, 8 - float(origin_y), cls.STEP_SIZE):
                size_x = 16 - float(origin_y) - (origin_z + 8)
                if size_x > 0:
                    for x_offset in np.arange(0, float(size_x * 2), cls.STEP_SIZE):
                        origin_x = -8 + (float(x_offset) * float(cls.STEP_SIZE))
                        cube = {
                            "origin": [float(origin_x), float(origin_y), float(origin_z)],
                            "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                        }
                        cubes.append(cube)
        return cubes

    @classmethod
    def _generate_45_degree_decreasing_ramp(cls, level_from, level_to) -> List[Dict]:
        """Generuje malejącą rampę 45° od level_from do level_to"""
        cubes = []
        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            for origin_z in np.arange(0, 16, cls.STEP_SIZE):
                threshold = 16 - float(origin_y) + 1
                if origin_z < threshold or origin_y < 2:
                    size_x = 16
                else:
                    # size_x maleje o 1 dla każdego z powyżej threshold
                    size_x = 16 - (float(origin_z) - float(threshold) + 1)

                for x_offset in np.arange(0, float(size_x * 2), cls.STEP_SIZE):
                    origin_x = -8 + (float(x_offset) * float(cls.STEP_SIZE))
                    cube = {
                        "origin": [float(origin_x), float(origin_y), float(origin_z)],
                        "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                    }
                    cubes.append(cube)
        return cubes

    @classmethod
    def _generate_part1(cls) -> List[Dict]:
        """Pierwsza część rampy 45° - podstawowa warstwa"""
        return cls._generate_45_degree_sloped_ramp(0, 15)

    @classmethod
    def _generate_part2(cls) -> List[Dict]:
        """Druga część rampy 45° - malejące główne części z dodatkowymi kostkami"""
        return cls._generate_45_degree_decreasing_ramp(0, 15)


class RoadRampOblique22500(RampAlgorithm):
    ANGLE = 22.5

    @classmethod
    def __init__(cls):
        super().__init__()
        cls.generate({
            "22_5_part1": cls._generate_part1(),
            "22_5_part2": cls._generate_part2(),
            "22_5_part3": cls._generate_part3(),
        })

    # ===== METODY POMOCNICZE =====

    @classmethod
    def _generate_sloped_ramp(cls, level_from, level_to) -> List[Dict]:
        """Generuje skośną rampę z parametrami level_from i level_to"""
        cubes = []

        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            for origin_z in np.arange(-8, 8 - float(origin_y), cls.STEP_SIZE):
                if 16 - (2 * float(origin_y)) - (origin_z + 8) > 0:
                    for origin_x in np.arange(-8, -8 + (16 - (2 * float(origin_y)) - (origin_z + 8)), cls.STEP_SIZE):
                        cube = {
                            "origin": [float(origin_x), float(origin_y), float(origin_z)],
                            "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                        }
                        cubes.append(cube)

        return cubes

    @classmethod
    def _generate_full_layer(cls, level_from, level_to) -> List[Dict]:
        """Generuje pełne warstwy 16x16 od level_from do level_to"""
        cubes = []
        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            for origin_x in np.arange(-8, 8, cls.STEP_SIZE):
                for origin_z in np.arange(-8, 8, cls.STEP_SIZE):
                    cube = {
                        "origin": [float(origin_x), float(origin_y), float(origin_z)],
                        "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                    }
                    cubes.append(cube)
        return cubes

    @classmethod
    def _generate_main_rectangle_for_layer(cls, origin_y) -> List[Dict]:
        """Generuje główne prostokąty dla konkretnej warstwy"""
        cubes = []
        main_size_z = 16 - (origin_y * 2)  # Malejąca głębokość Z
        if main_size_z > 0:
            for origin_x in np.arange(-8, 8, cls.STEP_SIZE):
                for origin_z in np.arange(-8, -8 + main_size_z, cls.STEP_SIZE):
                    cube = {
                        "origin": [float(origin_x), float(origin_y), float(origin_z)],
                        "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                    }
                    cubes.append(cube)
        return cubes

    @classmethod
    def _generate_main_rectangle(cls, level_from, level_to) -> List[Dict]:
        """Generuje główne prostokąty od level_from do level_to"""
        cubes = []
        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            cubes.extend(cls._generate_main_rectangle_for_layer(origin_y))
        return cubes

    @classmethod
    def _generate_additional_cubes_for_layer(cls, origin_y) -> List[Dict]:
        """Generuje dodatkowe kostki dla konkretnej warstwy"""
        cubes = []
        num_cubes = 2 * origin_y
        start_z = 8 - 2 * origin_y
        for origin_z in np.arange(start_z, start_z + num_cubes, cls.STEP_SIZE):
            size_x = 16 - (origin_z - start_z)
            for origin_x in np.arange(-8, -8 + size_x, cls.STEP_SIZE):
                cube = {
                    "origin": [float(origin_x), float(origin_y), float(origin_z)],
                    "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                }
                cubes.append(cube)
        return cubes

    @classmethod
    def _generate_additional_cubes(cls, level_from, level_to) -> List[Dict]:
        """Generuje dodatkowe kostki od level_from do level_to"""
        cubes = []
        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            cubes.extend(cls._generate_additional_cubes_for_layer(origin_y))
        return cubes

    @classmethod
    def _generate_edge_cubes(cls, level_from, level_to) -> List[Dict]:
        """Generuje małe kostki z malejącymi rozmiarami od level_from do level_to"""
        cubes = []
        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            offset_y = origin_y - 8
            num_cubes = 16 - 2 * offset_y
            max_size = 16 - 2 * offset_y
            for origin_z in np.arange(-8, -8 + num_cubes, cls.STEP_SIZE):
                size_x = max_size - (origin_z + 8)
                for origin_x in np.arange(-8, -8 + size_x, cls.STEP_SIZE):
                    cube = {
                        "origin": [float(origin_x), float(origin_y), float(origin_z)],
                        "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                    }
                    cubes.append(cube)

        return cubes

    @classmethod
    def _generate_combined_rectangular_and_triangular_layer(cls, level_from, level_to) -> List[Dict]:
        """Generuje warstwy z mieszanymi kostkami od level_from do level_to"""
        cubes = []
        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            offset_y = origin_y - 8
            num_normal_cubes = 16 - 2 * offset_y + 1
            for origin_z in np.arange(-8, 8, cls.STEP_SIZE):
                if origin_z >= -8 + num_normal_cubes:
                    # To pozycja dla małej kostki
                    size_x = 15 - (origin_z - (-8 + num_normal_cubes))
                    for origin_x in np.arange(-8, -8 + size_x, cls.STEP_SIZE):
                        cube = {
                            "origin": [float(origin_x), float(origin_y), float(origin_z)],
                            "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                        }
                        cubes.append(cube)
                else:
                    # To pozycja dla normalnej kostki
                    for origin_x in np.arange(-8, 8, cls.STEP_SIZE):
                        cube = {
                            "origin": [float(origin_x), float(origin_y), float(origin_z)],
                            "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                        }
                        cubes.append(cube)
        return cubes

    # ===== METODY GŁÓWNE =====

    @classmethod
    def _generate_part1(cls) -> List[Dict]:
        """Pierwsza część rampy 22.5° - podstawowa warstwa"""
        return cls._generate_sloped_ramp(0, 15)

    @classmethod
    def _generate_part2(cls) -> List[Dict]:
        """Druga część rampy 22.5° - malejące główne części z dodatkowymi kostkami"""
        cubes = []
        cubes.extend(cls._generate_full_layer(0, 0))
        cubes.extend(cls._generate_complete_layers(1, 8))
        cubes.extend(cls._generate_edge_cubes(9, 15))

        return cubes

    @classmethod
    def _generate_part3(cls) -> List[Dict]:
        """Trzecia część rampy 22.5° - 16 warstw, pierwsze 8 pełnych, kolejne 8 ścinanych"""
        cubes = []
        cubes.extend(cls._generate_full_layer(0, 7))
        cubes.extend(cls._generate_combined_rectangular_and_triangular_layer(8, 15))

        return cubes


class RoadRampOblique11250(RampAlgorithm):
    ANGLE = 11.25

    @classmethod
    def __init__(cls):
        super().__init__()
        cls.generate({
            "11_25_part1": cls._generate_part1(),
            "11_25_part2": cls._generate_part2(),
            "11_25_part3": cls._generate_part3(),
            "11_25_part4": cls._generate_part4(),
            "11_25_part5": cls._generate_part5()
        })

    # Warstwy prostokąty + dodatkowe kostki
    @classmethod
    def _generate_rectangular_layers_with_triangular_edges(cls, level_from, level_to):
        cubes = []
        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            main_size_z = 16 - 4 * (origin_y - level_from)
            if main_size_z > 0:
                for origin_x in np.arange(-8, 8, cls.STEP_SIZE):
                    for origin_z in np.arange(-8, -8 + float(main_size_z), cls.STEP_SIZE):
                        cube = {
                            "origin": [float(origin_x), float(origin_y), float(origin_z)],
                            "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                        }
                        cubes.append(cube)

            # Dodatkowe kostki
            start_z = -8 + main_size_z
            end_z = 7
            for origin_z in np.arange(start_z, end_z + 1, cls.STEP_SIZE):
                size_x = max(1, 16 - (origin_z - start_z))
                for origin_x in np.arange(-8, -8 + size_x, cls.STEP_SIZE):
                    cubes.append({
                        "origin": [float(origin_x), float(origin_y), float(origin_z)],
                        "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                    })

        return cubes

    @classmethod
    def _generate_triangular_edges_only(cls, level_from, level_to):
        cubes = []
        for origin_y in np.arange(level_from, level_to + 1, cls.STEP_SIZE):
            num_cubes = 12 - 4 * (origin_y - level_from - 1)
            for origin_z in np.arange(-8, -8 + num_cubes, cls.STEP_SIZE):
                size_x = num_cubes - (origin_z + 8)
                for origin_x in np.arange(-8, -8 + size_x, cls.STEP_SIZE):
                    cubes.append({
                        "origin": [float(origin_x), float(origin_y), float(origin_z)],
                        "size": [float(cls.STEP_SIZE), float(cls.STEP_SIZE), float(cls.STEP_SIZE)]
                    })

        return cubes

    @classmethod
    def _generate_part1(cls) -> List[Dict]:
        """Pierwsza część rampy 11.25° - malejące zakresy z malejącymi rozmiarami"""
        cubes = []
        cubes.extend(cls._generate_triangular_edges_only(0, 3))
        return cubes

    @classmethod
    def _generate_part2(cls) -> List[Dict]:
        """Druga część rampy 11.25° - prostokąty z dodatkowymi kostkami, potem malejące trójkąty"""
        cubes = []
        cubes.extend(cls._generate_rectangular_layers_with_triangular_edges(0, 3))
        cubes.extend(cls._generate_triangular_edges_only(4, 7))
        return cubes

    @classmethod
    def _generate_part3(cls) -> List[Dict]:
        """Trzecia część rampy 11.25° - pełne warstwy, potem prostokąty i trójkąty"""
        cubes = []
        cubes.extend(cls._generate_full_layer(0, 3))
        cubes.extend(cls._generate_rectangular_layers_with_triangular_edges(4, 7))
        cubes.extend(cls._generate_triangular_edges_only(8, 11))
        return cubes

    @classmethod
    def _generate_part4(cls) -> List[Dict]:
        """Czwarta część rampy 11.25° - pełne warstwy, potem prostokąty i trójkąty"""
        cubes = []
        cubes.extend(cls._generate_full_layer(0, 7))
        cubes.extend(cls._generate_rectangular_layers_with_triangular_edges(8, 11))
        cubes.extend(cls._generate_triangular_edges_only(12, 15))
        return cubes

    @classmethod
    def _generate_part5(cls) -> List[Dict]:
        """Piąta część rampy 11.25° - pełne warstwy, potem prostokąty i dodatkowe kostki"""
        cubes = []
        cubes.extend(cls._generate_full_layer(0, 11))
        cubes.extend(cls._generate_rectangular_layers_with_triangular_edges(12, 15))
        return cubes


def main():
    # RoadRampOblique45000()
    RoadRampOblique22500()
    RoadRampOblique11250()
    # straight_road_ramp(1)
    RoadRampStraight(2)
    RoadRampStraight(3)
    RoadRampStraight(4)
    RoadRampStraight(6)
    RoadRampStraight(8)


if __name__ == "__main__":
    main()
