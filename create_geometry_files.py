#!/usr/bin/env python3

import json
import re


def create_files(parts):
    y_start = 0
    angle = round(45 / parts, 3)
    height = 0.5

    y = 0
    identifier = f"road_ramp_{angle.__str__().replace('.0', '').replace('.', '_')}"

    for part in range(1, parts + 1):
        identifier_part = f'{identifier}{f'_part{part}' if parts > 1 else ''}'

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

        z_size = 16 - y * parts
        while z_size < 1:
            z_size = 16 + z_size

        print(f"{identifier_part} y:{y} y_start:{y_start} z_size:{z_size}")

        while z_size > 0:
            print(f"  y:{y} z_size:{z_size}")
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
            y += height
            z_size -= parts * height

        y_start = y

        geometry_data = {
            "format_version": "1.19.0",
            "minecraft:geometry": [
                {
                    "description": {
                        "identifier": f"geometry.{identifier_part}",
                        "texture_width": 16,
                        "texture_height": 16,
                        "visible_bounds_width": 1,
                        "visible_bounds_height": 1,
                        "visible_bounds_offset": [0, 0, 0]
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

        filename = f"RP/models/blocks/{identifier_part}.geo.json"
        with open(filename, 'w') as f:
            # Create a clean structure without the original cubes
            clean_data = {
                "format_version": geometry_data["format_version"],
                "minecraft:geometry": [
                    {
                        "description": geometry_data["minecraft:geometry"][0]["description"],
                        "bones": [
                            {
                                "name": geometry_data["minecraft:geometry"][0]["bones"][0]["name"],
                                "pivot": geometry_data["minecraft:geometry"][0]["bones"][0]["pivot"],
                                "cubes": []  # Empty array to be filled manually
                            }
                        ]
                    }
                ]
            }

            # Generate the JSON with proper indentation
            json_str = json.dumps(clean_data, indent=2)

            # Find the position of the empty cubes array
            cubes_start = json_str.find('"cubes": [')
            if cubes_start != -1:
                cubes_end = json_str.find(']', cubes_start)
                if cubes_end != -1:
                    # Extract indentation
                    indent = json_str[:cubes_start].split('\n')[-1]

                    # Create compact cubes
                    compact_cubes = []
                    for cube in geometry_data["minecraft:geometry"][0]["bones"][0]["cubes"]:
                        cube_str = json.dumps(cube, separators=(',', ':'))
                        compact_cubes.append(f"{indent}    {cube_str}")

                    # Replace the empty array with formatted cubes
                    cubes_content = "\n" + ",\n".join(compact_cubes) + "\n" + indent + "]"
                    json_str = json_str[:cubes_start + 10] + cubes_content + json_str[cubes_end + 1:]

            # Compact visible_bounds_offset
            visible_bounds_pattern = r'(\s*"visible_bounds_offset":\s*\[)[^]]*(\])'

            def replace_visible_bounds(match):
                indent = match.group(1).replace('"visible_bounds_offset": [', '')
                return match.group(1) + " 0, 0, 0" + match.group(2)

            json_str = re.sub(visible_bounds_pattern, replace_visible_bounds, json_str, flags=re.DOTALL)

            # Compact pivot
            pivot_pattern = r'(\s*"pivot":\s*\[)[^]]*(\])'

            def replace_pivot(match):
                indent = match.group(1).replace('"pivot": [', '')
                return match.group(1) + " 0, 0, 0" + match.group(2)

            json_str = re.sub(pivot_pattern, replace_pivot, json_str, flags=re.DOTALL)

            # Format numbers with leading space for 0-9
            def format_numbers(match):
                return match.group(1) + " " + match.group(2) + match.group(3) + match.group(4)

            # Format single digit numbers in arrays
            json_str = re.sub(r'(\[)(\d)(|\.\d)(\])', format_numbers, json_str)
            json_str = re.sub(r'(\[)(\d)(|\.\d)(,)', format_numbers, json_str)
            json_str = re.sub(r'(,)(\d)(|\.\d)(\])', r'\1 \2\3\4', json_str)
            json_str = re.sub(r'(,)(\d)(|\.\d)(,)', r'\1 \2\3\4', json_str)

            f.write(json_str)


create_files(1)
create_files(2)
create_files(3)
create_files(4)
create_files(6)
create_files(8)
