"""
Example script demonstrating how to use the SandSkrit library to generate 
continuous path text for sand tables.
"""

from sandskrit import SandSkrit


def main():
    """
    Generate an example pattern with a spiral, multiple lines of text, and an outer loop.
    """

    # Initialize SandSkrit starting at the origin (0, 0)
    sandskrit = SandSkrit(0, 0)

    # Start with a clean slate by spiraling out to a radius of 100
    sandskrit.add_spiral_out(radius=100, turns=100, ending_angle=0)

    # sandskrit = SandSkrit(0, 100) ## <-- This is a good start if skipping the spiral
    # Define multiple lines of text with varying scales to demonstrate size variation
    multi_lines = [
        {'text': 'AaBbCcDdEe', 'scale': 15},
        {'text': 'FfGgHhIiJjKkLl', 'scale': 15},
        {'text': 'MmNnOoPpQqRrSs', 'scale': 15},
        {'text': 'TtUuVvWwXxYyZz', 'scale': 15},
        {'text': '0123456789#@,.', 'scale': 15},
        {'text': '$()&<->[]{}/\\_', 'scale': 15},

        # {'text': 'Welcome to', 'scale': 10},
        # {'text': 'SandSkrit', 'scale': 19},
        # {'text': 'A python library for', 'scale': 10},
        # {'text': 'continuous path text', 'scale': 10},
        # {'text': 'for sand tables.', 'scale': 10},
        # {'text': 'Turn your text into', 'scale': 10},
        # {'text': 'SandSkript', 'scale': 20},
        # {'text': 'by                  ', 'scale': 8},
        # {'text': 'Unintelligible', 'scale': 10},
        # {'text': '    Maker', 'scale': 10},
    ]
    
    try:
        sandskrit.add_lines_of_text(multi_lines, line_spacing=1.3)
    except ValueError as e:
        print(f"Oops, the sand would leak: {e}")
        return

    # Add a final flourish with an outer loop
    sandskrit.add_outer_loop(turns=2, ending_angle=0)

    # Save the generated pattern in both SVG and THR formats
    sandskrit.save_svg("images/continuous_polyline.svg")
    sandskrit.save_thr("images/continuous_polyline.thr")
    
    print("Example generated successfully!")


if __name__ == "__main__":
    main()
