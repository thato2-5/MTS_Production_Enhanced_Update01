from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(width, height, text, filename):
    # Create a new image with a light gray background
    image = Image.new('RGB', (width, height), color='#f8f9fa')
    draw = ImageDraw.Draw(image)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill='#6c757d', font=font)
    
    # Draw a border
    draw.rectangle([0, 0, width-1, height-1], outline='#dee2e6', width=1)
    
    # Save the image
    image.save(filename)
    print(f"Created: {filename}")

# Create placeholder images
placeholders = [
    ('static/images/portfolio/e-commerce.jpg', 400, 300, 'E-commerce Platform'),
    ('static/images/portfolio/mobile.jpg', 400, 300, 'Mobile App'),
    ('static/images/portfolio/web.jpg', 400, 300, 'Web Application'),
    ('static/images/portfolio/warehouse_tracker.jpg', 400, 300, 'Warehouse Tracker'),
    ('static/images/portfolio/employee_tracker.jpg', 400, 300, 'Employee Tracker'),
    ('static/images/portfolio/visitor_management.jpg', 400, 300, 'Visitor Management'),
    ('static/images/portfolio/technician_maintenance_tool.jpg', 400, 300, 'Maintenance Tool'),
    ('static/images/portfolio/crm_maintenance.jpg', 400, 300, 'CRM System'),
    
    ('static/images/clients/client1.jpg', 200, 200, 'Client 1'),
    ('static/images/clients/client2.jpg', 200, 200, 'Client 2'),
    ('static/images/clients/client3.jpg', 200, 200, 'Client 3'),
    
    ('static/images/team/thato.jpg', 200, 200, 'Thato Monyamane'),
    
    ('static/images/hero-image.png', 600, 400, 'Hero Image'),
    ('static/images/about-preview.jpg', 600, 400, 'About Preview'),
    ('static/images/services-hero.png', 600, 400, 'Services Hero'),
    ('static/images/portfolio-hero.png', 600, 400, 'Portfolio Hero'),
    ('static/images/blog-hero.png', 600, 400, 'Blog Hero'),
    ('static/images/contact-hero.png', 600, 400, 'Contact Hero'),
    
    ('static/images/certifications/iso27001.png', 150, 150, 'ISO 27001'),
    ('static/images/certifications/aws.png', 150, 150, 'AWS Partner'),
    ('static/images/certifications/microsoft.png', 150, 150, 'Microsoft'),
    ('static/images/certifications/soc2.png', 150, 150, 'SOC 2'),
    ('static/images/certifications/google-cloud.png', 150, 150, 'Google Cloud'),
]

# Ensure directories exist
for path, _, _, _ in placeholders:
    os.makedirs(os.path.dirname(path), exist_ok=True)

# Create all placeholder images
for filename, width, height, text in placeholders:
    create_placeholder_image(width, height, text, filename)

print("All placeholder images created successfully!")
