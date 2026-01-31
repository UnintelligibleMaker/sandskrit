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
    sandskrit.add_spiral_out(radius=100, turns=1, ending_angle=0)
    
    # Define multiple lines of text with varying scales to demonstrate size variation
    multi_lines = [
        {'text': 'Welcome to', 'scale': 10},
        {'text': 'SandSkrit', 'scale': 20},
        {'text': 'A python library for ', 'scale': 10},
        {'text': 'continuous path text', 'scale': 10},
        {'text': 'for sand tables.', 'scale': 10},
        {'text': 'Turn your text into #', 'scale': 10},
        # {'text': '#', 'scale': 50},
        {'text': 'SandSkript', 'scale': 15},
        {'text': 'by', 'scale': 8},
        {'text': 'Unintelligible', 'scale': 12},
        {'text': '    Maker', 'scale': 12},
    ]
    
    try:
        # Add the defined lines of text with a specific line spacing
        sandskrit.add_lines_of_text(multi_lines, line_spacing=1.2)
    except ValueError as e:
        print(f"Oops, the sand would leak: {e}")
        return

    # Add a final flourish with an outer loop
    sandskrit.add_outer_loop(turns=2, ending_angle=0)

    # Save the generated pattern in both SVG and THR formats
    sandskrit.save_svg("continuous_polyline.svg")
    sandskrit.save_thr("continuous_polyline.thr")
    
    print("Example generated successfully!")


if __name__ == "__main__":
    main()
