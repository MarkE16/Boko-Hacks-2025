from PIL import Image, ImageDraw, ImageFont

def generate_captcha(text: str = None, width: int = 200, height: int = 80) -> Image:

    # image = Image.new('RGB', (width, height), (255, 255, 255))
    # draw = ImageDraw.Draw(image)
    
    # draw.rectangle([0, 0, width-1, height-1], outline=(200, 200, 200))
    
    # font = ImageFont.load_default()
    
    # text_bbox = draw.textbbox((0, 0), text, font=font)
    # text_width = text_bbox[2] - text_bbox[0]
    # text_height = text_bbox[3] - text_bbox[1]
    
    # x = (width - text_width) // 2 - text_bbox[0]  
    # y = (height - text_height) // 2 - text_bbox[1]  
    
    # draw.text((x, y), text, font=font, fill=(0, 0, 0))

    # Create a new white image
    image = Image.new('RGB', (400, 400), 'white')
    draw = ImageDraw.Draw(image)

    # Define circle parameters
    center = (200, 200)
    outer_radius = 75
    inner_radius = 55
    offset = 100
    ring_color = "black"
    quarter_color = "cyan"
    positions = [
        (center[0] - offset, center[1] - offset, 90),
        (center[0] + offset, center[1] - offset, 0),
        (center[0] - offset, center[1] + offset, 180),
        (center[0] + offset, center[1] + offset, 270)
    ]
    # Draw all four circles in a loop
    for pos in positions:
        # Draw outer circle
        draw.ellipse((pos[0]-outer_radius, pos[1]-outer_radius, 
                    pos[0]+outer_radius, pos[1]+outer_radius), 
                    fill=ring_color)

        # Draw inner circle (to create hollow effect)
        draw.ellipse((pos[0]-inner_radius, pos[1]-inner_radius, 
                    pos[0]+inner_radius, pos[1]+inner_radius), 
                    fill="white")

        # Draw one quarter in different color
        # First draw the outer arc of the quarter
        draw.pieslice((pos[0]-outer_radius, pos[1]-outer_radius, 
                    pos[0]+outer_radius, pos[1]+outer_radius), 
                    start=pos[2], end=pos[2]+90, fill=quarter_color)

        # Then draw the inner circle to create the hollow effect for this quarter
        draw.ellipse((pos[0]-inner_radius, pos[1]-inner_radius, 
                    pos[0]+inner_radius, pos[1]+inner_radius), 
                    fill="white")

    # Add text under circles
    font = ImageFont.truetype("arial.ttf", 20)  # You may need to adjust the font path
    text = "Do you see a box?"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_position = ((400 - text_width) // 2, 375)  # Positioned below the circles
    draw.text(text_position, text, fill="black", font=font)
    
    return image