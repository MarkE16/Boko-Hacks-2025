from PIL import Image, ImageDraw, ImageFont
import random
import math
from typing import Tuple, Optional, Literal, Union, Dict, Any

def generate_captcha() -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Generate a captcha image with two optical illusions side by side.
    
    Returns:
        A tuple containing:
        - The captcha image as a PIL Image object
        - Metadata about the illusions for verification
    """
    # Choose two random illusion types
    illusion_types = [
        ("Ebbinghaus Illusion", generate_ebbinghaus_illusion),
        ("Café Wall Illusion", generate_cafe_wall_illusion),
        ("Zöllner Illusion", generate_zollner_illusion)
    ]
    
    # Randomly select two different illusion types
    selected_illusions = random.sample(illusion_types, 2)
    
    # Randomly decide which one will be real
    real_illusion_index = random.randint(0, 1)
    
    # Generate the illusions
    illusion_a = selected_illusions[0][1](real=(real_illusion_index == 0))
    illusion_b = selected_illusions[1][1](real=(real_illusion_index == 1))
    
    # Create a new image with both illusions side by side
    width = illusion_a.width * 2 + 50  # Add extra padding between illusions
    height = max(illusion_a.height, illusion_b.height) + 80  # Add space for labels
    
    captcha = Image.new('RGB', (width, height), 'white')
    
    # Paste the illusions with proper spacing
    captcha.paste(illusion_a, (25, 10))  # Add left margin
    captcha.paste(illusion_b, (illusion_a.width + 50, 10))  # Add spacing between illusions
    
    # Add labels A and B
    draw = ImageDraw.Draw(captcha)
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()
    
    draw.text((width//4, height - 60), "A", fill="black", font=font, anchor="mm")
    draw.text((3*width//4, height - 60), "B", fill="black", font=font, anchor="mm")
    
    # Create metadata for verification
    metadata = {
        "real_illusion": "A" if real_illusion_index == 0 else "B",
        "illusion_a": {
            "description": selected_illusions[0][0],
            "is_real": real_illusion_index == 0
        },
        "illusion_b": {
            "description": selected_illusions[1][0],
            "is_real": real_illusion_index == 1
        }
    }
    
    return captcha, metadata

def generate_ebbinghaus_illusion(real: bool = True, width: int = 500, height: int = 300) -> Image.Image:
    """
    Generate an Ebbinghaus illusion captcha.
    
    In the real illusion, two identical central circles appear different in size
    because one is surrounded by larger circles and the other by smaller circles.
    In the fake version, the surrounding circles are modified to reduce the illusion effect.
    
    Args:
        real: If True, generate a real illusion. If False, generate a fake one.
        width: The width of the image.
        height: The height of the image.
        
    Returns:
        A PIL Image object containing the illusion.
    """
    # Create a new white image
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Define parameters
    center_radius = 30  # Size of the central circles
    text_height = 40  # Height reserved for text at the bottom
    
    # Move the entire illusion up to make room for text
    vertical_offset = text_height // 2
    
    # Increase horizontal spacing between the two central circles
    center_left = (width // 4, (height - text_height) // 2 - vertical_offset)
    center_right = (3 * width // 4, (height - text_height) // 2 - vertical_offset)
    
    # Draw the two central circles (identical in size)
    draw.ellipse((center_left[0] - center_radius, center_left[1] - center_radius,
                  center_left[0] + center_radius, center_left[1] + center_radius),
                 fill="red", outline="black")
    
    draw.ellipse((center_right[0] - center_radius, center_right[1] - center_radius,
                  center_right[0] + center_radius, center_right[1] + center_radius),
                 fill="red", outline="black")
    
    # Parameters for surrounding circles
    if real:
        # Real illusion: left surrounded by large circles, right by small
        left_surround_radius = 40
        right_surround_radius = 15
        left_distance = 100  # Distance from center to surrounding circles
        right_distance = 60
    else:
        # Fake illusion: similar sized surrounding circles
        left_surround_radius = 30
        right_surround_radius = 30
        left_distance = 90
        right_distance = 90
    
    # Calculate angles for better spacing
    num_circles = 8
    angles = [i * (360 / num_circles) for i in range(num_circles)]
    
    # Draw surrounding circles for left central circle
    for angle in angles:
        x = center_left[0] + int(left_distance * math.cos(math.radians(angle)))
        y = center_left[1] + int(left_distance * math.sin(math.radians(angle)))
        
        draw.ellipse((x - left_surround_radius, y - left_surround_radius,
                      x + left_surround_radius, y + left_surround_radius),
                     fill="blue", outline="black")
    
    # Draw surrounding circles for right central circle
    for angle in angles:
        x = center_right[0] + int(right_distance * math.cos(math.radians(angle)))
        y = center_right[1] + int(right_distance * math.sin(math.radians(angle)))
        
        draw.ellipse((x - right_surround_radius, y - right_surround_radius,
                      x + right_surround_radius, y + right_surround_radius),
                     fill="blue", outline="black")
    
    # Add text at the bottom
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
        
    question = "Are the red circles the same size?"
    bbox = draw.textbbox((0, 0), question, font=font)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, height - text_height + 10), question, fill="black", font=font)
    
    return image

def generate_cafe_wall_illusion(real: bool = True, width: int = 500, height: int = 300) -> Image.Image:
    """
    Generate a Café Wall illusion captcha.
    
    In the real illusion, horizontal lines appear sloped due to the staggered
    arrangement of black and white tiles. In the fake version, the staggering
    is removed or modified to eliminate the illusion.
    
    Args:
        real: If True, generate a real illusion. If False, generate a fake one.
        width: The width of the image.
        height: The height of the image.
        
    Returns:
        A PIL Image object containing the illusion.
    """
    # Create a new white image
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Define tile parameters
    tile_size = 30
    mortar_size = 3
    rows = (height - 40) // (tile_size + mortar_size)  # Leave space for text
    cols = width // tile_size
    
    # Draw the tiles
    for row in range(rows):
        # Determine offset for this row
        if real:
            # In real illusion, alternate rows are offset by half a tile
            offset = (tile_size // 2) if row % 2 == 1 else 0
        else:
            # In fake illusion, no offset
            offset = 0
        
        # Draw mortar (gray line) above this row
        if row > 0:
            draw.rectangle((0, row * (tile_size + mortar_size) - mortar_size,
                           width, row * (tile_size + mortar_size)),
                          fill="gray")
        
        # Draw tiles in this row
        for col in range(cols + 1):  # +1 to handle offset
            x = col * tile_size - offset
            y = row * (tile_size + mortar_size)
            
            # Skip tiles that would be off-screen
            if x + tile_size < 0 or x >= width:
                continue
                
            # Alternate black and white tiles
            color = "black" if (col + row) % 2 == 0 else "white"
            
            draw.rectangle((x, y, x + tile_size, y + tile_size), fill=color, outline=None)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
        
    question = "Are the horizontal lines parallel?"
    bbox = draw.textbbox((0, 0), question, font=font)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, height - 30), question, fill="black", font=font)
    
    return image

def generate_zollner_illusion(real: bool = True, width: int = 500, height: int = 300) -> Image.Image:
    """
    Generate a Zöllner illusion captcha.
    
    In the real illusion, parallel lines appear to be non-parallel due to short
    intersecting lines at an angle. In the fake version, the intersecting lines
    are modified to reduce the illusion effect.
    
    Args:
        real: If True, generate a real illusion. If False, generate a fake one.
        width: The width of the image.
        height: The height of the image.
        
    Returns:
        A PIL Image object containing the illusion.
    """
    # Create a new white image
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Define parameters
    line_spacing = 40  # Space between main lines
    line_length = width - 60  # Length of main lines
    hatch_length = 15  # Length of intersecting lines
    num_lines = 5  # Number of main lines
    
    # Calculate starting positions to center the illusion
    start_x = 30
    start_y = (height - ((num_lines - 1) * line_spacing)) // 2
    
    # Draw the main horizontal lines
    for i in range(num_lines):
        y = start_y + i * line_spacing
        draw.line((start_x, y, start_x + line_length, y), fill="black", width=2)
        
        # Add intersecting lines
        num_hatches = line_length // 20  # Space hatches evenly
        
        for j in range(num_hatches):
            x = start_x + j * 20 + 10
            
            # Alternate the angle of intersecting lines for adjacent main lines
            if real:
                # For real illusion, use alternating angles that create the illusion
                angle = 45 if i % 2 == 0 else 135
            else:
                # For fake illusion, use vertical lines that don't create the illusion
                angle = 90
            
            # Calculate endpoints of the intersecting line
            x1 = x - int(hatch_length * math.cos(math.radians(angle)))
            y1 = y - int(hatch_length * math.sin(math.radians(angle)))
            x2 = x + int(hatch_length * math.cos(math.radians(angle)))
            y2 = y + int(hatch_length * math.sin(math.radians(angle)))
            
            draw.line((x1, y1, x2, y2), fill="black", width=1)
    
    # Add reference lines to make the illusion more obvious
    if real:
        # Draw two vertical reference lines at the edges
        ref_x1 = start_x + 20
        ref_x2 = start_x + line_length - 20
        
        draw.line((ref_x1, start_y - 20, ref_x1, start_y + (num_lines - 1) * line_spacing + 20), 
                  fill="red", width=1)
        draw.line((ref_x2, start_y - 20, ref_x2, start_y + (num_lines - 1) * line_spacing + 20), 
                  fill="red", width=1)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
        
    question = "Are the black horizontal lines parallel?"
    bbox = draw.textbbox((0, 0), question, font=font)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, height - 30), question, fill="black", font=font)
    
    return image

def generate_random_illusion_captcha() -> Tuple[Image.Image, bool, str]:
    """
    Generate a random illusion captcha.
    
    Returns:
        A tuple containing:
        - The captcha image
        - A boolean indicating if it's a real illusion (True) or fake (False)
        - A string describing the type of illusion
    """
    illusion_type = random.choice(["ebbinghaus", "cafe_wall", "zollner"])
    is_real = random.choice([True, False])
    
    if illusion_type == "ebbinghaus":
        image = generate_ebbinghaus_illusion(real=is_real)
        description = "Ebbinghaus Illusion"
    elif illusion_type == "cafe_wall":
        image = generate_cafe_wall_illusion(real=is_real)
        description = "Café Wall Illusion"
    else:  # zollner
        image = generate_zollner_illusion(real=is_real)
        description = "Zöllner Illusion"
    
    return image, is_real, description