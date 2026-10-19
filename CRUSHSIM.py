import pygame
import sys
import math
import random

pygame.init()

# Window & Display setup
WIDTH, HEIGHT = 960, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CRUSHSIM")
clock = pygame.time.Clock()
FPS = 60

# Fonts
# using courier new because it gives it that techy/terminal look
F_TITLE  = pygame.font.SysFont("couriernew", 48, bold=True)
F_LARGE  = pygame.font.SysFont("couriernew", 32, bold=True)
F_MED    = pygame.font.SysFont("couriernew", 20, bold=True)
F_SMALL  = pygame.font.SysFont("couriernew", 15)
F_TINY   = pygame.font.SysFont("couriernew", 13)

# Colors
# RGB tuples, all the blues/teals are for the ocean vibe
C_BG =     (5,12,35)
C_PANEL =  (8,20,55)
C_BORDER = (0,100,140)
C_CYAN =   (0,230,190)
C_BLUE =   (50,140,255)
C_RED =    (220,60,30)
C_WHITE =  (240,245,255)
C_DIM =    (80,110,160)
C_HOVER =  (0,50,90)
C_SELECT = (0,80,110)
# colors for each depth zone label in the depth meter
ZONE_COLORS = {
    "Sunlight Zone": (50,160,255),
    "Twilight Zone": (30,90,190),
    "Midnight Zone": (15,50,120),
    "Abyssal Zone":  (8,25,70),
    "Hadal Zone":    (4,12,40),
}
# Physics Functions used throughout
RHO = 1025.0  # sea water density
G   = 9.81    # gravity
MAX_OCEAN_DEPTH = 11000  # Mariana Trench Depth

def pressure_at(depth_m):
    return RHO * G * depth_m  # external water pressure on any given object at depth

def depth_for_pressure(p_pa):
    return p_pa / (RHO * G)

# returns which named ocean zone a given depth falls into
def depth_zone(depth_m):
    for lo, hi, name in [(0,200,"Sunlight Zone"),(200,1000,"Twilight Zone"),
                         (1000,4000,"Midnight Zone"),(4000,6000,"Abyssal Zone"),
                         (6000,11000,"Hadal Zone")]:
        if lo <= depth_m < hi:
            return name
    return "Hadal Zone"

# OBJECT DATABASE (to sound fancy)
# Each object has preset real-world dimensions built in.
# category: "Hollow" | "Solid" | "Porous" | "Biological"
# shape:    "sphere" | "cylinder" | "cube"
# dims:     dict of meters
CATEGORIES = ["Hollow", "Solid", "Porous", "Biological"]

# loading images for each category from the Images folder
CAT_ICONS = {
    "Hollow":     pygame.image.load("Images/hollow.jpg").convert_alpha(),
    "Solid":      pygame.image.load("Images/solid.jpg").convert_alpha(),
    "Porous":     pygame.image.load("Images/porous.webp").convert_alpha(),
    "Biological": pygame.image.load("Images/biological.jpeg").convert_alpha(),
}
for key in CAT_ICONS:
    CAT_ICONS[key] = pygame.transform.scale(CAT_ICONS[key], (48, 48))

# short descriptions shown on each category card
CAT_DESC = {
    "Hollow":     "Has air inside —\ncollapses under pressure",
    "Solid":      "Fully solid — resist via\nBulk Modulus",
    "Porous":     "Contains air pockets\nthat collapse under pressure",
    "Biological": "Sea creatures,\nmostly just water",
}

# Dictionary with different objects, for the non solid opbjects it gives the thickness of the shell, for the solid objects it gives the volume, for the biological objects it gives some special parameters like lung volume. The calculator functions will know how to use these parameters based on the category and shape of the object.
OBJECTS = {
    # Hollow objects 
    "Ping Pong Ball": {"category":"Hollow","shape":"sphere","desc":"Thin plastic sphere, 40mm dia","dims":{"R":0.020,"t":0.0004},"color":(230,230,230)},
    "Basketball":     {"category":"Hollow","shape":"sphere","desc":"Rubber sphere, 240mm dia","dims":{"R":0.120,"t":0.003},"color":(210,120,40)},
    "Soda Can":       {"category":"Hollow","shape":"cylinder","desc":"Thin-walled cylinder, 66mm dia","dims":{"R":0.033,"t":0.0001},"color":(200,50,50)},
    "Scuba Tank":     {"category":"Hollow","shape":"cylinder","desc":"Pressure cylinder, 200mm dia, 10mm wall","dims":{"R":0.100,"t":0.010},"color":(100,160,200)},
    # Solid
    "Golf Ball":      {"category":"Solid","shape":"sphere","desc":"Solid rubber core, 43mm dia","dims":{"R":0.021},"color":(245,245,245)},
    "Ball Bearing":   {"category":"Solid","shape":"sphere","desc":"Solid sphere, 50mm dia","dims":{"R":0.025},"color":(170,180,190)},
    "Solid Block":    {"category":"Solid","shape":"cube","desc":"A solid cubic block, 0.3m cube","dims":{"V":0.027},"color":(130,120,110)},
    "Brick":          {"category":"Solid","shape":"cube","desc":"Straight up brick, 10x5x3 cm","dims":{"V":0.000015},"color":(90,90,100)},
    # Porous spongey things
    "Styrofoam Cup":  {"category":"Porous","shape":"cylinder","desc":"Styrofoam baby, 8cm tall","dims":{"R":0.040,"t":0.004},"color":(240,240,235)},
    "Wood Block":     {"category":"Porous","shape":"cube","desc":"its a wood block, 0.01 m3","dims":{"V":0.010},"color":(160,100,60)},
    "Coral":          {"category":"Porous","shape":"sphere","desc":"Sea coral","dims":{"R":0.050,"t":0.005},"color":(255,180,150)},
    "Sponge":         {"category":"Porous","shape":"cube","desc":"Sea sponge, ~90% air by volume","dims":{"V":0.001},"color":(210,170,80)},
    # Bio/Life
    "Jellyfish":      {"category":"Biological","shape":"sphere","desc":"basically water with a skin","dims":{"R":0.150},"color":(180,220,255)},
    "Human Diver":    {"category":"Biological","shape":"sphere","desc":"Air lungs are the weak point","dims":{"lung_volume_L":6.0},"color":(255,200,150)},
    "Deep Sea Fish":  {"category":"Biological","shape":"sphere","desc":"No swim bladder, fully adapted","dims":{"R":0.100},"color":(80,160,200)},
    "Sperm Whale":    {"category":"Biological","shape":"sphere","desc":"Collapsible ribcage, dives to 3km","dims":{"R":5.000},"color":(60,70,80)},
}
# Cycles through the images in the "Images" folder and scales them to 48x48, then stores them in a dictionary with the same keys as the OBJECTS dictionary for easy access when drawing the object selection screen.
OBJ_IMAGES = {}
for name in OBJECTS:
    img = pygame.image.load(f"Images/{name}.png").convert_alpha()
    OBJ_IMAGES[name] = pygame.transform.scale(img, (48, 48))

# MATERIALS
# E  = Young's Modulus (Every materials stiffness)
# nu = Poisson's Ratio (The leeway for an object's squishyness to being compressed lengthwise for cylinders)
# K  = Bulk Modulus (resistance to being squeezed uniformly, solid objects)
# sy = Compressive Yield Strength (General pressure for which anything breaks, everything else)
MATERIALS = {
    "Aluminum":      {"E": 69e9,  "nu": 0.33, "K": 76e9,  "sy": 276e6, "color": (180,190,210)},
    "Steel":         {"E": 200e9, "nu": 0.28, "K": 160e9, "sy": 400e6, "color": (130,155,175)}, # all the variables for these objects, if they are in a range officially we just chose in the middle
    "Titanium":      {"E": 116e9, "nu": 0.32, "K": 110e9, "sy": 880e6, "color": (160,175,200)},
    "Plastic":       {"E": 2.3e9, "nu": 0.35, "K": 2.5e9, "sy": 40e6,  "color": (200,200,130)},
    "Carbon Fiber":  {"E": 150e9, "nu": 0.20, "K": 100e9, "sy": 600e6, "color": (60,60,70)},
    "Glass":         {"E": 70e9,  "nu": 0.23, "K": 50e9,  "sy": 50e6,  "color": (160,220,230)},
}
# loading material images same way as object images
MAT_IMAGES = {}
for mname in MATERIALS:
    img = pygame.image.load(f"Images/{mname}.png").convert_alpha()
    MAT_IMAGES[mname] = pygame.transform.scale(img, (40, 40))
<<<<<<< HEAD

=======
# PHYSICS CALCULATORS MUHAHAHAHAHA 
>>>>>>> e2a4b8d6cee6827ccfd73d02ac2be053760660d6
# hollow sphere buckling — the thinner the wall relative to radius, the shallower it crushes
def calc_hollow_sphere(obj, mat):
    E = mat["E"]
    t = obj["dims"]["t"]
    R = obj["dims"]["R"]  # Gets material resistance and object dimensions
    P = 0.365 * E * (t / R) ** 2  # Formula
    d = depth_for_pressure(P)  # Calculates the depth at which it is crushed
    return { # Returns a dictionary with all the info to be displayed on the result screen
        "crush_depth":  d,
        "formula_name": "Thin-Shell Sphere Buckling",
        "formula_str":  f"P = 0.365 x E x (t/R)^2\n= 0.365 x {E/1e9:.0f}GPa x ({t*1000:.2f}mm / {R*1000:.0f}mm)^2\n= {P/1e6:.3f} MPa  ->  {int(d):,}m",
        "result_note":  f"Implodes at {int(d):,}m down. Walls cave in.",
    }
def calc_hollow_cylinder(obj, mat):
    E = mat["E"]; nu = mat["nu"]; t = obj["dims"]["t"]; R = obj["dims"]["R"] # uses formula for thin shell cylinder buckling, which is more complex than the sphere because it can also be compressed lengthwise, so it has to take into account the Poisson's ratio of the material which is a measure of how much it can squish in one direction when compressed in another direction. The formula is P = (E * (t/R)^3) / (4 * (1 - nu^2)) where E is the Young's modulus, t is the thickness of the cylinder wall, R is the radius of the cylinder, and nu is the Poisson's ratio.
    P = (E * (t / R) ** 3) / (4 * (1 - nu ** 2))
    d = depth_for_pressure(P) # returns crushing depth in meters by dividing the crushing pressure by the pressure gradient of the ocean (rho * g)
    return { # returns a dictionary with all the info to be displayed on the result screen
        "crush_depth":  d,
        "formula_name": "Thin-Shell Cylinder Buckling",
        "formula_str":  f"P = E x (t/R)^3 / (4 x (1-v^2))\n= {E/1e9}GPa x ({t*1000:.2f}/{R*1000:.0f}mm)^3 / (4x(1-{nu}^2))\n= {P/1e6:.4f} MPa  ->  {int(d):,}m",
        "result_note":  f"Walls collapse at {int(d):,}m.",
    }
# solid objects never actually crush we just show how much they compress at max depth
def calc_solid(obj, mat):
    K = mat["K"]
    P_max = pressure_at(11000) # None of the objects will crush under the max ocean depth, but we can still calculate the % change in size at max depth using the bulk modulus formula dV/V = P/K, where dV is the change in volume, V is the original volume, P is the pressure applied, and K is the bulk modulus of the material. This will give us an idea of how much the object would compress at extreme depths even if it doesn't actually crush.
    dV = P_max / K
    return {
        "crush_depth":  None,
        "formula_name": "Bulk Compression",
        "formula_str":  f"dV/V = P / K\n= {P_max/1e6:.1f}MPa / {K/1e9:.0f}GPa\n= {dV*100:.5f}% volume change at 11,000 m",
        "result_note":  f"Doesn't crush. Only shrinks {dV*100:.5f}%\neven at full depth.",
    }

def calc_porous(obj, mat):
    sy = mat["sy"] # For porous materials, we can use the compressive yield strength as the crushing pressure, since the internal air pockets will collapse when the external pressure exceeds the material's ability to resist compression. This is a simplification, but it gives us a reasonable estimate for when the object would crush.
    d  = depth_for_pressure(sy)
    return {
        "crush_depth":  d,
        "formula_name": "Porous Cellular Collapse",
        "formula_str":  f"P_crush = sigma_y  (compressive yield strength)\n= {sy/1e6:.0f} MPa\n-> depth = {sy/1e6:.0f}MPa / (rho x g) = {int(d):,}m",
        "result_note":  f"Air pockets cave in at {int(d):,}m.",
    }

def calc_biological(obj, mat): # Each of the creatures do not have a formula for their crushing depth, so they are given hardcoded values and just return a specific dictionary
    name = obj.get("_name", "")
    if "Human" in name:
        return {
            "crush_depth":  35.0,
            "formula_name": "Human is soft and squishy (aka lungs collapse)",
            "formula_str":  ("Lungs compress to ~10% volume at 10 ATM.\n"
                             "Fatal breath-hold squeeze occurs at ~30-40m\n"
                             "for untrained divers."),
            "result_note":  "Body fluid is fine — lungs are\nthe weak point. Air compresses.",
        }
    elif "Whale" in name:
        return {
            "crush_depth":  3000.0,
            "formula_name": "Biological Pressure Adaptation",
            "formula_str":  ("Collapsible ribcage and flexible tissue\n"
                             "Whale dive record is 2,992m."),
            "result_note":  "Biological adaptations handle ~3,000m.\nBelow: O2 becomes lethal.",
        }
    else:
        return {
            "crush_depth":  11100,
            "formula_name": "Jellyfish are a freak of nature",
            "formula_str":  ("Body is ~96-99% water.\n"
                             "No air cavities -> no internal outward force.\n"
                             "Survives any ocean depth."),
            "result_note":  "Jellyfish NEVER crush.\nPressure transmits uniformly through body.",
        }

def calculate(obj_name, mat_name):
    obj = dict(OBJECTS[obj_name]); obj["_name"] = obj_name # Organizes above dictionary and uses the functions to calculate given selected user object and material if applied
    mat = MATERIALS[mat_name]
    cat = obj["category"]; shp = obj.get("shape", "sphere")
    if   cat == "Hollow" and shp == "sphere":   return calc_hollow_sphere(obj, mat)
    elif cat == "Hollow" and shp == "cylinder": return calc_hollow_cylinder(obj, mat)
    elif cat == "Solid":                        return calc_solid(obj, mat)
    elif cat == "Porous":                       return calc_porous(obj, mat)
    elif cat == "Biological":                   return calc_biological(obj, mat)
    else:                                       return calc_solid(obj, mat)

# The floating particles that make it look like its underwater, they just move upwards and reset to the bottom when they go offscreen with some random horizonatal movement as well, Hamish made this good stuff
class Particle:
    def __init__(self): self._reset()
    def _reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(1, 3)
        self.alpha = random.randint(50, 160) # bunch of random values to make the particles look different and natural as they float upwards
        self.vx = random.uniform(-0.15, 0.15)
        self.vy = random.uniform(0.08, 0.35)
        self.color = random.choice([C_CYAN, C_BLUE, (100,200,255)])
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.02, 0.06)
    def update(self):
        self.y -= self.vy 
        self.x += self.vx 
        self.phase += self.speed
        if self.y < -4:
            self._reset()
            self.y = HEIGHT + 4
    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), int(self.size))

PARTICLES = [Particle() for _ in range(80)] 

# UI helpers that make it easier to draw text, panels, and multiline text with consistent styling and alignment. The panel function also supports rounded corners and alpha transparency for the fill color, which is used for the selection highlights on the category/object/material screens.

# background color interpolates from bright blue at surface to near black at depth
def draw_bg(depth=0):
    t = min(depth / 8000, 1.0)
    screen.fill((int(18*(1-t)+2*t), int(60*(1-t)+6*t), int(140*(1-t)+18*t)))

def draw_particles():
    for p in PARTICLES: p.update(); p.draw(screen)

# draws text centered or left aligned at a given position
def txt(surf, s, font, color, cx, cy, align="center"):
    r = font.render(s, True, color)
    if   align == "center": surf.blit(r, (cx - r.get_width()//2, cy))
    elif align == "left":   surf.blit(r, (cx, cy))
    return r.get_height()

# draws a semi-transparent rounded rectangle, used for all the cards and overlays
def panel(surf, x, y, w, h, fill=C_PANEL, border=C_BORDER, radius=10, alpha=200):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, alpha), (0,0,w,h), border_radius=radius)
    surf.blit(s, (x, y))
    pygame.draw.rect(surf, border, (x,y,w,h), 1, border_radius=radius) # border around the rectangle to make it stand out, super nice

def multiline(surf, text, font, color, x, y, lh=20): # helper function to draw multiline text, it splits the text into lines and draws each line with a certain line height, used for the descriptions on the category/object/material cards and the result screen
    for i, ln in enumerate(text.split("\n")):
        txt(surf, ln, font, color, x, y + i*lh, align="left")

# Swaps between different screens/Game states and keeps track of changing variables from the sim.
state        = "cat_select"
sel_category = None
sel_object   = None
sel_material = None
result_data  = None

sim_depth   = 0.0
sim_target  = 0.0 # these are the variables that change during the sim screen
sim_speed   = 1.0
sim_obj_y   = 120
crush_timer = 0
mx, my = 0, 0

# Screens, selections ---> sim ---> result
# Really big seciton of the code since we repeatedly call upon the same functions to make it seem like its just transitioning to another UI screen but its actually just redrawing everything with different parameters and checking for different click boxes, so the same functions are used to draw the category selection screen, object selection screen, material selection screen, simulation screen, and result screen, but with different parameters and click boxes for each one. The code is organized into separate functions for each screen to keep it clean, and the main game loop just calls the appropriate function based on the current state of the game.

def screen_cat_select():  # Category screen
    draw_bg(0); draw_particles()
    txt(screen, "CRUSH  DEPTH", F_TITLE, C_CYAN, WIDTH//2, 30)
    txt(screen, "Deep Sea Pressure Simulator", F_MED, C_CYAN, WIDTH//2, 90)
    txt(screen, "Choose an object category", F_MED, C_RED, WIDTH//2, 128)
    rects = {}
    bw, bh, gap = 200, 195, 22
    sx = WIDTH//2 - (4*bw + 3*gap)//2

    for i, cat in enumerate(CATEGORIES): # This function draws the category selection screen, it loops through the categories and draws a panel for each one with the corresponding icon and description text, it also checks if the mouse is hovering over any of the panels to change the color for interactivity, and if a category is selected it changes the color to indicate selection. It returns a dictionary of the rectangles for each category to be used for click detection.
        bx = sx + i*(bw+gap); by = 175
        panel(screen, bx, by, bw, bh, fill=C_PANEL, border=C_BORDER) # ngl i needed help a little bit with this block  because of the wall of conditionals it needed, but then i could use it for the other screens as well since the logic is the same just with different variables 
        screen.blit(CAT_ICONS[cat], (bx + bw//2 - 24, by + 14)) # draws the category icons at the top of each panel
        txt(screen, cat.upper(), F_MED, C_WHITE, bx+bw//2, by+62)
        for j, line in enumerate(CAT_DESC[cat].split("\n")): # splits the category descriptions into multiple lines and draws them onto the panel, and highlights the panel if hovered or selected
            txt(screen, line, F_TINY, C_WHITE, bx+bw//2, by+102+j*18)
        rects[cat] = pygame.Rect(bx,by,bw,bh) # once the highlight feature was figured out i was able to apply it to everything after this

    if sel_category:
        txt(screen, "[ Click again or ENTER to continue ]", F_SMALL, C_BLUE, WIDTH//2, HEIGHT-45)
    return rects

def screen_obj_select():  # Object Screen
    draw_bg(0); draw_particles()
    txt(screen, "CRUSH  DEPTH", F_LARGE, C_CYAN, WIDTH//2, 22)
    txt(screen, f"Choose an object  ( {sel_category} )", F_MED, C_BLUE, WIDTH//2, 66)

    # only show objects matching the selected category
    objs = [n for n,o in OBJECTS.items() if o["category"] == sel_category]
    rects = {}
    bw, bh, gap_x, gap_y = 390, 66, 20, 12
    sx = WIDTH//2 - (2*bw + gap_x)//2; sy = 105

    for i, name in enumerate(objs): # This function is very similar to the category selection screen, but it shows the objects instead of the categories and it filters the objects based on the selected category, it also shows the description of each object and an image of the object instead of just an icon, but the overall structure is the same with the panels and hover/selection colors and returning a dictionary of rectangles for click detection.
        if i % 2 == 0:
            bx = sx
        else:
            bx = sx + bw + gap_x
        by = sy + (i // 2) * (bh + gap_y)

        panel(screen, bx, by, bw, bh, fill=C_PANEL, border=C_BORDER) # big conditional that sets the fill and border color based on if the object is selected or hovered
        screen.blit(OBJ_IMAGES[name], (bx+6, by+bh//2-20))  # object image instead of circle
        txt(screen, name,                  F_MED,   C_WHITE, bx+58, by+8,  align="left")
        txt(screen, OBJECTS[name]["desc"], F_TINY,  C_WHITE, bx+58, by+32, align="left")
        rects[name] = pygame.Rect(bx,by,bw,bh)

    back_r = pygame.Rect(28, HEIGHT-50, 105, 32)
    panel(screen, *back_r, fill=C_PANEL, border=C_BORDER, radius=6)
    txt(screen, "<- BACK", F_SMALL, C_WHITE, back_r.centerx, back_r.y+9)
    rects["__back__"] = back_r
    if sel_object:
        txt(screen, "[ Click again or ENTER to continue ]", F_SMALL, C_BLUE, WIDTH//2, HEIGHT-42)
    return rects


def screen_mat_select():  # Material Screen
    draw_bg(0); draw_particles()
    txt(screen, "CRUSH  DEPTH", F_LARGE, C_CYAN, WIDTH//2, 22)
    txt(screen, "Choose a material", F_MED, C_BLUE, WIDTH//2, 64)
    txt(screen, f"Object: {sel_object}  |  Category: {sel_category}", F_SMALL, C_DIM, WIDTH//2, 96)
    if sel_category == "Biological":
        txt(screen, "Note: material mainly affects porous/hollow categories.", F_TINY, C_DIM, WIDTH//2, 116)

    rects = {}
    bw, bh, gap_x, gap_y = 272, 90, 22, 16
    sx = WIDTH//2 - (3*bw + 2*gap_x)//2; sy = 140

    for i, (mname, md) in enumerate(MATERIALS.items()): # Function gives the material selection descriptions and icons 
        col = i % 3
        row = i // 3 # Calculates the position of each material panel in a 3-column layout, it uses the modulus operator to determine the column (0, 1, or 2) and division to determine the row, then calculates the x and y coordinates based on the starting position and the size of the panels plus the gaps between them.
        bx = sx + col * (bw + gap_x)
        by = sy + row * (bh + gap_y)

        panel(screen, bx, by, bw, bh, fill=C_PANEL, border=C_BORDER) # Again, similar block to the category and object selection screens, it just draws panels for each material  
        screen.blit(MAT_IMAGES[mname], (bx+6, by+bh//2-20)) # image for each material
        # text shifted to bx+54 so it doesnt overlap the image
        txt(screen, mname, F_MED, C_WHITE, bx+54, by+10, align="left")
        txt(screen, f"E={md['E']/1e9:.0f}GPa  K={md['K']/1e9:.0f}GPa", F_TINY, C_WHITE, bx+54, by+36, align="left") # text descriptions for the material properties 
        txt(screen, f"sy={md['sy']/1e6:.0f}MPa  v={md['nu']}",          F_TINY, C_WHITE, bx+54, by+54, align="left")
        rects[mname] = pygame.Rect(bx,by,bw,bh)

    back_r = pygame.Rect(28, HEIGHT-50, 105, 32)
    panel(screen, *back_r, fill=C_PANEL, border=C_BORDER, radius=6)
    txt(screen, "<- BACK", F_SMALL, C_WHITE, back_r.centerx, back_r.y+9)
    rects["__back__"] = back_r
    if sel_material:
        txt(screen, "[ Click again or ENTER to dive ]", F_SMALL, C_BLUE, WIDTH//2, HEIGHT-42)
    return rects

def draw_depth_meter(depth, target):
    px, py, pw, ph = WIDTH-172, 16, 155, HEIGHT-32
    panel(screen, px, py, pw, ph, alpha=210)
    txt(screen, "DEPTH",                             F_SMALL, C_CYAN,        px+pw//2, py+10)
    txt(screen, f"{int(depth):,}m",                  F_MED,   C_WHITE,       px+pw//2, py+32) # Text in the depth meter 
    txt(screen, f"{pressure_at(depth)/1e6:.2f} MPa", F_SMALL, (170,210,255), px+pw//2, py+58)
    txt(screen, depth_zone(depth), F_TINY, ZONE_COLORS.get(depth_zone(depth), C_DIM), px+pw//2, py+78)
    if target is not None:
        txt(screen, "Crush at:",         F_TINY,  C_DIM, px+pw//2, py+100)
        txt(screen, f"{int(target):,}m", F_SMALL, C_RED, px+pw//2, py+116)
    bx  = px + 22
    bt  = py + 142
    bw2 = 18
    bh2 = ph - 160
    pygame.draw.rect(screen, (15,35,75), (bx,bt,bw2,bh2))
    if target is not None and target > 0: # function to draw the rectangle that fills up as you get closer to the crushing depth
        fill = int(bh2 * min(depth / (target*1.02), 1.0))
        pygame.draw.rect(screen, C_CYAN, (bx,bt,bw2,fill))
        pygame.draw.line(screen, C_RED, (bx-5,bt+bh2-1),(bx+bw2+5,bt+bh2-1), 2)
        txt(screen, "CRUSH", F_TINY, C_RED, px+pw//2, bt+bh2+3)
    pygame.draw.rect(screen, C_CYAN, (bx,bt,bw2,bh2), 1)

def screen_sinking(): # This is the main sim screen
    global sim_depth, sim_obj_y, crush_timer, state
    if crush_timer == 0:
        sim_depth = min(sim_depth + sim_speed, sim_target * 1.02) # The depth increases over time depending how big the crushing depth is and modifies the sim speed variable so that it doesnt take so long
        sim_obj_y = min(HEIGHT - 100, sim_obj_y + 0.4)

    draw_bg(sim_depth); draw_particles() # drawing the particles on the screen
    cx = WIDTH//2 - 90; cy = int(sim_obj_y) # position of the object in the sim 

    if crush_timer == 0:
        screen.blit(OBJ_IMAGES[sel_object], (cx - 24, cy - 24)) # drawing the object image in the sim screen 
        txt(screen, sel_object.upper(), F_TINY, (180,220,255), cx, cy+34)
    else:
        # crush animation — expanding ring that fades out
        t = min(crush_timer/60, 1.0)
        r = int(t*60)
        if r > 0:
            pygame.draw.circle(screen, OBJECTS[sel_object]["color"], (cx,cy), r, max(1,int(4*(1-t))))
        if crush_timer < 15: 
            fl = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA) # red flash that fills the screen and very quickly fades out using crush timer in place of alpha value, starts out full then over 15 frames becomes fully transparent
            fl.fill((220,60,60, int(160*(1-crush_timer/15))))
            screen.blit(fl, (0,0))

    draw_depth_meter(sim_depth, sim_target)
    if crush_timer == 0 and sim_depth >= sim_target: # when the depth reaches the crushing depth, it starts the crush timer which triggers the crush animation and then after a certain amount of time it transitions to the result screen
        crush_timer = 1
    if crush_timer > 0:
        crush_timer += 1
        if crush_timer > 100:
            state = "result"

def screen_result():
    draw_bg(sim_depth); draw_particles()
    draw_depth_meter(sim_depth, sim_target)

    rd = result_data
    does_crush = rd["crush_depth"] is not None
    pw, ph = 545, 390 
    px = WIDTH//2 - pw//2 - 40; py = HEIGHT//2 - ph//2
    panel(screen, px, py, pw, ph, alpha=218, radius=14)
# drawing the result panel
    title = "CRUSHED!" if does_crush else "SURVIVES ALL DEPTHS" # putting the text onto it and deterining if it is crushed or not
    txt(screen, title, F_LARGE, C_RED if does_crush else C_CYAN, px+pw//2, py+16)
    pygame.draw.line(screen, C_BORDER, (px+18,py+58),(px+pw-18,py+58), 1)

    txt(screen, f"Object   : {sel_object}",  F_MED,   C_WHITE, px+20, py+68,  align="left")
    txt(screen, f"Material : {sel_material}", F_SMALL, C_DIM,   px+20, py+94,  align="left") # wall of text that just shows the selected object and material, and the category, then a line, then the formula name, then the formula with values plugged in, then another line, then the note about the result. all left aligned and spaced out nicely
    txt(screen, f"Category : {sel_category}", F_SMALL, C_DIM,   px+20, py+112, align="left")
    pygame.draw.line(screen, C_BORDER, (px+18,py+134),(px+pw-18,py+134), 1)

    txt(screen, rd["formula_name"], F_MED, C_BLUE, px+pw//2, py+144)
    multiline(screen, rd["formula_str"], F_TINY,  (170,210,255), px+20, py+168, 18)
    pygame.draw.line(screen, C_BORDER, (px+18,py+248),(px+pw-18,py+248), 1) # drawing the lines that separate the sections of the result panel
    multiline(screen, rd["result_note"], F_SMALL, C_WHITE, px+20, py+260, 22)

    again_r   = pygame.Rect(px+20,     py+ph-50, 190, 36)
    restart_r = pygame.Rect(px+pw-210, py+ph-50, 190, 36) # two buttons at the bottom of the result screen 

    panel(screen, *again_r, fill=C_PANEL, border=C_BORDER, radius=7) # giving the buttons interations and changing their color when hovered over 
    txt(screen, "SWAP MATERIAL", F_TINY, C_WHITE, again_r.centerx, again_r.y+11) 

    panel(screen, *restart_r, fill=C_PANEL, border=C_BORDER, radius=7) # same thing for this restart button literally just cmd c+v
    txt(screen, "NEW OBJECT", F_TINY, C_WHITE, restart_r.centerx, restart_r.y+11)
    return again_r, restart_r

# START SIMULATION FINALLY AHAHAHHA
def start_simulation():
    global sim_depth, sim_target, sim_speed, sim_obj_y, crush_timer, state, result_data
    rd = calculate(sel_object, sel_material)
    result_data = rd
    sim_depth = 0.0
    sim_obj_y = 120
    crush_timer = 0
    # if it never crushes we still want to animate it going to max depth
    sim_target = rd["crush_depth"] if rd["crush_depth"] is not None else MAX_OCEAN_DEPTH
    sim_speed  = max(0.5, sim_target / 600)
    state = "sinking"

# main
def main():
    global state, sel_category, sel_object, sel_material, mx, my # funny global variables hehe
    cat_rects = {}; obj_rects = {}; mat_rects = {} # sets empty dictionaries for the rectangles of each screen for some reason, i was pulling my hair out for why main didnt wanna work but this was what i was missing apparently and it works so i dont care
    res_btns  = (pygame.Rect(0,0,1,1), pygame.Rect(0,0,1,1))

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos() # get mouse coordinates for clicks 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # checks for mouse clicks and changes the state of game based on where the user clicks
                if state == "cat_select":
                    for cat, r in cat_rects.items():
                        if r.collidepoint(mx,my):
                            if sel_category == cat: state = "obj_select"; sel_object = None # if you click the same category again it confirms your selection and moves on to the object selection screen, if you click a different category it just changes the selected category without moving on, allowing you to change your mind without having to click a separate back button
                            else:                   sel_category = cat
                elif state == "obj_select":
                    for name, r in obj_rects.items():
                        if r.collidepoint(mx,my): # same thing for the object 
                            if name == "__back__":   state = "cat_select"
                            elif sel_object == name:
                                # biological objects skip material selection since material doesnt matter for them
                                if sel_category == "Biological": sel_material = "Steel"; start_simulation()
                                else: state = "mat_select"; sel_material = None
                            else:                    sel_object = name
                elif state == "mat_select":
                    for name, r in mat_rects.items():
                        if r.collidepoint(mx,my): # and for the material
                            if name == "__back__":     state = "obj_select"
                            elif sel_material == name: start_simulation()
                            else:                      sel_material = name
                elif state == "result": # and for the result screen buttons, one to swap material and one to choose a new object, both of which just reset the appropriate variables and change the state to redraw the correct screen
                    a_r, n_r = res_btns
                    if a_r.collidepoint(mx,my):   
                        state = "mat_select" 
                        sel_material = None # result screen has two buttons the user can interact with, one for material screen and one for category screen
                    elif n_r.collidepoint(mx,my): 
                        state = "cat_select"
                        sel_category = sel_object = sel_material = None

        # Draw active screen
        if   state == "cat_select": cat_rects = screen_cat_select()
        elif state == "obj_select": obj_rects = screen_obj_select()
        elif state == "mat_select": mat_rects = screen_mat_select() # draws the appropriate screen based on the current state and updates the rectangles for click detection
        elif state == "sinking":    screen_sinking()
        elif state == "result":     res_btns  = screen_result()

        pygame.display.flip()

if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> e2a4b8d6cee6827ccfd73d02ac2be053760660d6
