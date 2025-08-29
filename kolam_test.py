import turtle

# --- CORE DRAWING FUNCTIONS ---

def setup_screen(width, height, color, title):
    """
    Sets up the Turtle graphics window with specified dimensions and title.
    
    Args:
        width (int): The width of the window in pixels.
        height (int): The height of the window in pixels.
        color (str): The background color of the window.
        title (str): The title displayed in the window's title bar.
        
    Returns:
        turtle.Screen: The configured screen object.
    """
    screen = turtle.Screen()
    screen.setup(width=width, height=height)
    screen.bgcolor(color)
    screen.title(title)
    # screen.tracer(0) makes the drawing appear instantly once it's done.
    screen.tracer(0) 
    return screen

def setup_turtle(color, size):
    """
    Creates and configures a turtle object to be used as a pen.
    
    Args:
        color (str): The color of the pen.
        size (int): The thickness of the pen's line.
        
    Returns:
        turtle.Turtle: The configured turtle object.
    """
    t = turtle.Turtle()
    t.speed(0)  # 0 is the fastest drawing speed
    t.pencolor(color)
    t.pensize(size)
    t.hideturtle() # We only want to see the drawing, not the turtle icon.
    return t

def create_dot_grid(t, rows, cols, spacing):
    """
    Draws a grid of dots on the screen, which serves as the foundation for the kolam.
    
    Args:
        t (turtle.Turtle): The turtle object to use for drawing.
        rows (int): The number of rows in the dot grid.
        cols (int): The number of columns in the dot grid.
        spacing (int): The distance between dots in pixels.
        
    Returns:
        list: A 2D list containing the (x, y) screen coordinates of each dot.
    """
    print(f"Creating a {rows}x{cols} grid...")
    dots = []
    # Calculate the starting position to ensure the grid is centered on the screen.
    start_x = - (cols - 1) * spacing / 2
    start_y = (rows - 1) * spacing / 2
    
    for r in range(rows):
        row_dots = []
        for c in range(cols):
            x = start_x + c * spacing
            y = start_y - r * spacing
            t.penup()
            t.goto(x, y)
            t.dot(5, "black") # Draw a black dot with a diameter of 5 pixels.
            row_dots.append((x, y))
        dots.append(row_dots)
    print("Grid created.")
    return dots

def draw_kolam(t, dots, pattern_paths):
    """
    The main drawing engine. It reads path data and draws the kolam lines.
    
    Args:
        t (turtle.Turtle): The turtle object to use for drawing.
        dots (list): The 2D list of dot coordinates from create_dot_grid.
        pattern_paths (list): A list of paths. Each path is a list of (row, col) 
                              indices defining a continuous line.
    """
    print("Drawing kolam...")
    for path in pattern_paths:
        # Get the screen coordinate of the first dot in the current path.
        start_dot_coords = dots[path[0][0]][path[0][1]]
        t.penup()
        t.goto(start_dot_coords)
        t.pendown()
        
        # Iterate through the rest of the dots in the path, drawing lines between them.
        for dot_index in path[1:]:
            row, col = dot_index
            screen_coords = dots[row][col]
            t.goto(screen_coords)
    print("Kolam drawn!")

# --- KOLAM PATTERN DEFINITIONS ---
# This dictionary holds the "design principles" for each kolam.
# To add a new kolam, you just need to add a new entry here with its
# name, grid size, and the sequence of dots for its paths.

KOLAM_PATTERNS = {
    "Simple Loop": {
        "rows": 3,
        "cols": 3,
        "paths": [
            # A single, continuous path that snakes around the outer dots.
            [(0, 1), (1, 2), (2, 1), (1, 0), (0, 1)] 
        ]
    },
    "Four Petals": {
        "rows": 3,
        "cols": 3,
        "paths": [
            # Each petal is a separate, continuous path.
            [(0, 1), (0, 0), (1, 0), (1, 1), (0, 1)], # Top petal
            [(1, 2), (0, 2), (0, 1), (1, 1), (1, 2)], # Right petal
            [(2, 1), (2, 2), (1, 2), (1, 1), (2, 1)], # Bottom petal
            [(1, 0), (2, 0), (2, 1), (1, 1), (1, 0)]  # Left petal
        ]
    },
    "Intertwined Squares": {
        "rows": 4,
        "cols": 4,
        "paths": [
            # First tilted square
            [(0, 1), (1, 3), (3, 2), (2, 0), (0, 1)],
            # Second tilted square, intertwined with the first
            [(1, 0), (3, 1), (2, 3), (0, 2), (1, 0)]
        ]
    }
}

# --- MAIN EXECUTION BLOCK ---
# This is the entry point of our program.

if __name__ == "__main__":
    # --- Part 1: User Interaction (FIXED: Hard-coded choice to prevent EOFError) ---
    print("--- Welcome to the Kolam Generator! ---")
    
    # We will hard-code the choice instead of asking for user input.
    # You can change this to "Simple Loop" or "Four Petals" to see other designs.
    pattern_name = "Four Petals"
    print(f"Generating the '{pattern_name}' pattern...")

    # --- Part 2: Drawing Logic ---
    
    # 1. Setup the environment
    screen = setup_screen(600, 600, "ivory", "Kolam Generator")
    pen = setup_turtle("darkblue", 3)

    # 2. Get the selected pattern's data from our dictionary.
    selected_pattern = KOLAM_PATTERNS[pattern_name]
    
    # 3. Extract grid and path data from the selected pattern.
    GRID_ROWS = selected_pattern["rows"]
    GRID_COLS = selected_pattern["cols"]
    pattern_data = selected_pattern["paths"]
    GRID_SPACING = 70

    # 4. Create the foundational dot grid.
    dot_coordinates = create_dot_grid(pen, GRID_ROWS, GRID_COLS, GRID_SPACING)

    # 5. Call the engine to draw the kolam.
    draw_kolam(pen, dot_coordinates, pattern_data)

    # 6. Update the screen to show the final drawing.
    screen.update()
    
    # 7. Keep the window open until the user closes it.
    print(f"Displaying '{pattern_name}'. Close the window to exit.")
    screen.mainloop()
