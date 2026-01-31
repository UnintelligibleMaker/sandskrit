#!/usr/bin/env python3
"""
SandSkrit: A module for generating continuous paths for sand tables.

This module provides the SandSkrit class which allows creating complex patterns
by adding points, lines, spirals, and text, and exporting them to SVG or THR formats.
"""

import math
import logging
import sys
import os
from typing import List, Tuple, Optional

# Configure basic logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


try:
    from characters_data import CHARACTERS
except ImportError:
    logger.error("characters_data.py not found. Please ensure it exists in the same directory.")
    CHARACTERS = {}


class SandSkrit:
    """
    Main class for generating continuous polylines.

    Attributes:
        points (List[Tuple[float, float]]): A list of (x, y) coordinates representing the path.
    """

    def __init__(self, x: float = 0, y: float = 0):
        """
        Initializes SandSkrit with an optional starting point.

        Args:
            x (float): Starting x-coordinate. Defaults to 0.
            y (float): Starting y-coordinate. Defaults to 0.
        """
        self.points: List[Tuple[float, float]] = [(float(x), float(y))]

    def add_point(self, x: float, y: float) -> None:
        """
        Adds a new point to the path, avoiding duplicates.

        Args:
            x (float): x-coordinate.
            y (float): y-coordinate.
        """
        rounded_x = round(float(x), 3)
        rounded_y = round(float(y), 3)
        if self.points and (rounded_x, rounded_y) == self.points[-1]:
            return
        self.points.append((rounded_x, rounded_y))
        logger.debug(f"Added point: ({rounded_x}, {rounded_y})")

    def get_current_point(self) -> Tuple[float, float]:
        """Returns the most recently added point."""
        return self.points[-1]

    def _to_svg_polyline(self) -> str:
        """Generates an SVG <polyline> element for the current path."""
        if not self.points:
            return ""
        min_x = min(p[0] for p in self.points)
        min_y = min(p[1] for p in self.points)
        points_str = " ".join([f"{x - min_x:.3f},{y - min_y:.3f}" for x, y in self.points])
        return f'<polyline points="{points_str}" fill="none" stroke="black" stroke-width="0.5" />'

    def _to_svg_path(self) -> str:
        """Generates an SVG path data string (d attribute) for the current path."""
        if not self.points:
            return ""
        min_x = min(p[0] for p in self.points)
        min_y = min(p[1] for p in self.points)
        d = f"M {self.points[0][0] - min_x:.3f} {self.points[0][1] - min_y:.3f}"
        for x, y in self.points[1:]:
            d += f" L {x - min_x:.3f} {y - min_y:.3f}"
        return d

    def _to_thr(self, extra_radius: float = 1.0) -> str:
        """
        Converts points to THR format (theta, rho).

        Args:
            extra_radius (float): Added to max radius for normalization. Defaults to 1.0.

        Returns:
            str: THR file content.
        """
        if not self.points:
            return ""

        # Normalize rho to [0, 1] based on maximum distance from origin
        max_dist = max(math.sqrt(x**2 + y**2) for x, y in self.points) + extra_radius
        max_rho = max_dist if max_dist > 0 else 1.0

        thr_lines = []
        last_theta = 0.0

        for i, (x, y) in enumerate(self.points):
            rho = math.sqrt(x**2 + y**2) / max_rho
            
            # Use atan2(x, -y) to match sand table coordinate system (90 deg CCW rotation)
            theta = math.atan2(x, -y)

            if i > 0:
                # Ensure theta is cumulative (avoids jumps at -pi/pi)
                delta = theta - (last_theta % (2 * math.pi))
                if delta > math.pi:
                    delta -= 2 * math.pi
                elif delta < -math.pi:
                    delta += 2 * math.pi
                theta = last_theta + delta

            thr_lines.append(f"{theta:.5f} {rho:.5f}")
            last_theta = theta

        return "\n".join(thr_lines)

    def save_thr(self, filename: str) -> None:
        """
        Saves the path to a THR file.

        Args:
            filename (str): Path to the output THR file.
        """
        thr_content = self._to_thr()
        with open(filename, "w") as f:
            f.write(thr_content)
        logger.info(f"Saved THR to {filename}")

    def save_svg(self, filename: str, size: int = 200) -> None:
        """
        Saves the path to an SVG file.

        Args:
            filename (str): Path to the output SVG file.
            size (int): Viewbox size for the SVG. Defaults to 200.
        """
        d = self._to_svg_path()
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">
  <path d="{d}" fill="none" stroke="black" stroke-width="0.5" stroke-linejoin="round" stroke-linecap="round" />
</svg>'''
        with open(filename, "w") as f:
            f.write(svg_content)
        logger.info(f"Saved SVG to {filename}")

    def get_text_metrics(self, text: str, scale: float = 1.0, character_spacing: float = 0.0) -> dict:
        """
        Calculates the width and vertical bounds of a given text string.

        Args:
            text (str): The text to measure.
            scale (float): Scaling factor. Defaults to 1.0.
            character_spacing (float): Extra space between characters. Defaults to 0.0.

        Returns:
            dict: A dictionary containing 'width', 'min_y', and 'max_y'.
        """
        total_width = 0.0
        min_y = 0.0
        max_y = 0.0

        for char in text:
            if char == " ":
                total_width += 0.5 * scale
            elif char in CHARACTERS and CHARACTERS[char] is not None:
                char_data = CHARACTERS[char]
                total_width += (char_data.get('width', 1.0) + 2 * character_spacing) * scale
                for pt in char_data['path']:
                    min_y = min(min_y, pt[1] * scale)
                    max_y = max(max_y, pt[1] * scale)
            else:
                logger.warning(f"Character '{char}' not supported, skipping for metrics calculation")

        return {
            'width': total_width,
            'min_y': min_y,
            'max_y': max_y
        }

    def add_lines_of_text(self, lines_config: list, line_spacing: float = 1.4):
        """
        Adds multiple lines of text centered vertically and horizontally.
        Checks if each line fits within the circle boundary and throws an exception if not.

        Args:
            lines_config (list): List of dicts with 'text', 'scale', 'offset_up', 'character_spacing', 'debug'.
            line_spacing (float): Multiplier for scale to determine vertical distance between lines.
        """
        initial_point = self.get_current_point()
        initial_radius = math.sqrt(initial_point[0]**2 + initial_point[1]**2)

        # Calculate line heights and total height
        line_heights = []
        for config in lines_config:
            scale = config.get('scale', 5.0)
            offset_up = config.get('offset_up', 0.9)
            line_heights.append(scale * line_spacing + offset_up)

        total_text_height = sum(line_heights)
        
        # Calculate vertical offsets to center the block of text
        vertical_offsets = []
        current_offset = -total_text_height / 2
        for i, height in enumerate(line_heights):
            # The baseline should be positioned such that the entire line 
            # (including offset_up) is within the height allocated.
            # Since offset_up pushes the character DOWN, the baseline is at the TOP of the height.
            offset_up = lines_config[i].get('offset_up', 0.9)
            vertical_offsets.append(current_offset + height - offset_up)
            current_offset += height

        # Pre-check: Verify if all lines fit within the boundary
        for i, config in enumerate(lines_config):
            v_offset = vertical_offsets[i]
            text = config.get('text', '')
            scale = config.get('scale', 5.0)
            offset_up = config.get('offset_up', 0.9)
            char_spacing = config.get('character_spacing', 0.1)

            metrics = self.get_text_metrics(text, scale, char_spacing)
            half_width = metrics['width'] / 2

            # path_start_y is the y-coordinate where character paths begin relative to baseline
            path_start_y = v_offset - scale * offset_up
            y_min = min(v_offset, path_start_y + metrics['min_y'])
            y_max = max(v_offset, path_start_y + metrics['max_y'])

            # Check four corners of the bounding box against circle radius
            for x in [-half_width, half_width]:
                for y in [y_min, y_max]:
                    if x*x + y*y > (initial_radius + 0.001)**2:
                        raise ValueError(
                            f"Line '{text}' does not fit in circle of radius {initial_radius:.2f}. "
                            f"Point ({x:.2f}, {y:.2f}) is at distance {math.sqrt(x*x+y*y):.2f}"
                        )

        # Draw each line
        for i, config in enumerate(lines_config):
            v_offset = vertical_offsets[i]
            
            # Find starting angle on the circle at y = v_offset
            if abs(v_offset) < initial_radius:
                angle_offset = math.degrees(math.asin(v_offset / initial_radius))
                start_angle = 180.0 - angle_offset
            else:
                logger.warning(f"Vertical offset {v_offset} exceeds radius {initial_radius}, clipping.")
                start_angle = 180.0

            # Move to start position on circle boundary
            self.add_outer_loop(turns=0, ending_angle=start_angle)

            # Draw the line of text
            self.add_line_of_text(
                text=config.get('text', ''),
                scale=config.get('scale', 5.0),
                offset_up=config.get('offset_up', 0.9),
                character_spacing=config.get('character_spacing', 0.1),
                debug=config.get('debug', False),
                vertical_offset=0.0
            )

    def add_line_of_text(self, text: str, scale: float = 5.0, offset_up: float = 0.9,
                         character_spacing: float = 0.1, debug: bool = False,
                         vertical_offset: float = 0.0) -> None:
        """
        Adds a line of text centered horizontally based on the current position's radius.

        Args:
            text (str): Text to add.
            scale (float): Scaling factor. Defaults to 5.0.
            offset_up (float): Vertical offset for the path. Defaults to 0.9.
            character_spacing (float): Space between characters. Defaults to 0.1.
            debug (bool): If True, adds debug markings. Defaults to False.
            vertical_offset (float): Optional vertical shift. Defaults to 0.0.
        """
        initial_point = self.get_current_point()
        initial_x, initial_y = initial_point

        if abs(vertical_offset) > 0.001:
            self.add_point(initial_x, initial_y + vertical_offset)
            initial_y += vertical_offset

        # The line length is twice the distance from x=0, forming a chord
        line_length = abs(initial_x) * 2

        metrics = self.get_text_metrics(text, scale, character_spacing)
        excess_length = line_length - metrics['width']
        
        # Start from left (negative x) or right (positive x)
        angle = 0 if initial_x < 0 else 180

        if excess_length > 0:
            self.add_line(length=excess_length / 2, angle=angle)
        
        self.add_string(text, scale, offset_up, character_spacing, debug)
        
        if excess_length > 0:
            self.add_line(length=excess_length / 2, angle=angle)

        if abs(vertical_offset) > 0.001:
            current_x, _ = self.get_current_point()
            self.add_point(current_x, initial_y - vertical_offset)

    def add_string(self, string: str, scale: float = 5.0, offset_up: float = 0.9,
                   character_spacing: float = 0.1, debug: bool = False) -> None:
        """
        Adds a string of characters to the path.

        Args:
            string (str): The string to add.
            scale (float): Scaling factor for the characters. Defaults to 5.0.
            offset_up (float): Vertical offset for character placement. Defaults to 0.9.
            character_spacing (float): Space between characters. Defaults to 0.1.
            debug (bool): If True, adds debug lines around characters. Defaults to False.
        """
        for character in string:
            self.add_character(character, scale, offset_up, character_spacing, debug)

    def add_character(self, character: str, scale: float = 5.0, offset_up: float = 0.9,
                      character_spacing: float = 0.1, debug: bool = False) -> None:
        """
        Adds a single character to the path.

        Args:
            character (str): The character to add.
            scale (float): Scaling factor for the character. Defaults to 5.0.
            offset_up (float): Vertical offset for character placement. Defaults to 0.9.
            character_spacing (float): Space before and after the character. Defaults to 0.1.
            debug (bool): If True, adds debug lines. Defaults to False.

        Raises:
            ValueError: If the character is not supported or defined in CHARACTERS.
        """
        if character == " ":
            self.add_line(length=(scale * 0.5), angle=0)
            return

        if character not in CHARACTERS:
            raise ValueError(f"Character '{character}' not supported")
        
        char_data = CHARACTERS[character]
        if char_data is None:
            raise ValueError(f"Character '{character}' has not been defined")

        if debug:
            self._add_debug_mark(5)

        # Space before character
        self.add_line(length=(scale * character_spacing), angle=0)

        if debug:
            self._add_debug_mark(2)

        # Handle start offset if present
        start_offset = char_data.get('start_offset', 0)
        if start_offset:
            logger.debug(f"Adding character '{character}' with start offset: {start_offset}")
            # Move horizontally by start_offset * scale
            self.add_line(length=abs(start_offset) * scale, angle=0 if start_offset < 0 else 180)

        if debug:
            self._add_debug_mark(1)

        # Move to character baseline start
        self.add_line(length=offset_up, angle=270)
        
        initial_position = self.get_current_point()

        # Draw character path
        for point in char_data['path']:
            target_x = initial_position[0] + point[0] * scale
            target_y = initial_position[1] + point[1] * scale
            current_x, current_y = self.get_current_point()
            
            dx = target_x - current_x
            dy = target_y - current_y
            
            dist = math.sqrt(dx**2 + dy**2)
            angle = math.degrees(math.atan2(dy, dx))
            self.add_line(length=dist, angle=angle)

        # Move back up to baseline
        self.add_line(length=offset_up, angle=90)

        if debug:
            self._add_debug_mark(1)

        # Underline the character
        underline_length = scale * (char_data['width'] + start_offset)
        self.add_line(length=underline_length, angle=0)

        if debug:
            self._add_debug_mark(2)

        # Space after character
        self.add_line(length=(scale * character_spacing), angle=0)

        if debug:
            self._add_debug_mark(5)

    def _add_debug_mark(self, size: float) -> None:
        """Helper to add vertical debug marks."""
        self.add_line(length=size, angle=90)
        self.add_line(length=size, angle=270)

    def add_line(self, length: float, angle: float = 0.0, max_length: float = 1.0) -> None:
        """
        Adds a straight line to the path, subdivided into segments.

        Args:
            length (float): Total length of the line.
            angle (float): Angle in degrees. Defaults to 0.0.
            max_length (float): Maximum length of each segment. Defaults to 1.0.
        """
        last_x, last_y = self.get_current_point()
        angle_rad = math.radians(angle)
        num_segments = math.ceil(abs(length) / max_length)
        if num_segments == 0:
            return

        if length < 0:
            angle_rad += math.pi
            length = abs(length)

        segment_length = length / num_segments
        logger.debug(f"Generating line of length {length} at {angle} degrees with {num_segments} segments")

        for i in range(1, num_segments + 1):
            x = last_x + (segment_length * i) * math.cos(angle_rad)
            y = last_y + (segment_length * i) * math.sin(angle_rad)
            self.add_point(x, y)

    def add_spiral_out(self, radius: float = 98.0, turns: float = 8.0, ending_angle: float = 180.0) -> None:
        """
        Adds an Archimedean spiral starting from the origin and moving outwards.

        Args:
            radius (float): Final radius of the spiral. Defaults to 98.0.
            turns (float): Number of full rotations. Defaults to 8.0.
            ending_angle (float): Final angle in degrees. Defaults to 180.0.
        """
        logger.debug(f"Generating spiral out: radius={radius}, turns={turns}, end_angle={ending_angle}")
        total_degrees = turns * 360 + ending_angle
        
        for i in range(int(total_degrees) + 1):
            angle_rad = math.radians(i)
            current_radius = radius * (i / total_degrees)
            x = current_radius * math.cos(angle_rad)
            y = current_radius * math.sin(angle_rad)
            self.add_point(x, y)

    def add_spiral_in(self, turns: float = 8.0) -> None:
        """
        Adds an Archimedean spiral from the current position back to the origin.

        Args:
            turns (float): Number of full rotations. Defaults to 8.0.
        """
        last_x, last_y = self.get_current_point()
        radius = math.sqrt(last_x**2 + last_y**2)
        start_angle_deg = math.degrees(math.atan2(last_y, last_x))
        
        logger.debug(f"Generating spiral in: radius={radius:.2f}, turns={turns}, start_angle={start_angle_deg:.2f}")
        total_degrees = turns * 360 + start_angle_deg
        
        for i in range(int(total_degrees), -1, -1):
            angle_rad = math.radians(i)
            current_radius = radius * (i / total_degrees)
            x = current_radius * math.cos(angle_rad)
            y = current_radius * math.sin(angle_rad)
            self.add_point(x, y)

    def add_outer_loop(self, turns: float = 2.0, ending_angle: float = 0.0) -> None:
        """
        Adds a circular path at the current radius.

        Args:
            turns (float): Number of full rotations. Defaults to 2.0.
            ending_angle (float): Final angle in degrees. Defaults to 0.0.
        """
        last_x, last_y = self.get_current_point()
        radius = math.sqrt(last_x**2 + last_y**2)
        start_angle_deg = math.degrees(math.atan2(last_y, last_x))
        
        logger.debug(f"Starting outer loop: radius={radius:.2f}, start_angle={start_angle_deg:.2f}")

        # Calculate total degrees to move
        angle_diff = (ending_angle - start_angle_deg) % 360
        total_degrees = turns * 360 + angle_diff
        
        for i in range(1, int(total_degrees) + 1):
            angle_rad = math.radians(start_angle_deg + i)
            x = radius * math.cos(angle_rad)
            y = radius * math.sin(angle_rad)
            self.add_point(x, y)

        logger.debug(f"Outer loop finished at: {self.get_current_point()}")



