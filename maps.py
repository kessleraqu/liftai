import numpy as np
from stl import mesh  # numpy-stl library
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from noise import snoise2  # Simplex noise function
import random
from mpl_toolkits.mplot3d import Axes3D  # Import 3D plotting
from plyfile import PlyData, PlyElement

# Map parameters
width, height = 200, 200  # Dimensions of the map grid
scale = 100.0  # Controls how "zoomed-in" the terrain is
elevation_intervals = np.arange(-500, 1501, 50)  # Elevation levels from -500 to 1500m in 50m intervals

# Color mapping based on elevation
def get_color(elevation):
    if elevation == 0:
        return [0, 0, 1]  # Blue for water
    elif 1 <= elevation <= 100:
        # Vivid light green transitioning to brownish
        normalized_elevation = (elevation - 1) / 99  # Normalize between 0 and 1
        return [0.4 + 0.6 * normalized_elevation, 1 - 0.4 * normalized_elevation, 0.2 + 0.3 * normalized_elevation]  # Vivid light green to more brownish
    elif 100 < elevation <= 350:
        # Gradient from light brown to dirt brown
        normalized_elevation = (elevation - 100) / 250  # Normalize between 0 and 1
        return [0.9 - 0.4 * normalized_elevation, 0.7 - 0.3 * normalized_elevation, 0.5 - 0.3 * normalized_elevation]  # Light brown to dirt brown
    elif 350 < elevation <= 600:
        # Gradient from dirt brown to stone gray
        normalized_elevation = (elevation - 350) / 250  # Normalize between 0 and 1
        return [0.5 + 0.3 * normalized_elevation, 0.4 + 0.2 * normalized_elevation, 0.3 + 0.3 * normalized_elevation]  # Dirt brown to stone gray
    else:
        return [1, 1, 1]  # Snow white





# Generate terrain using Simplex noise with no bias applied
def generate_terrain(width, height, scale):
    terrain = np.zeros((width, height))
    # Generate a random offset to introduce variability in the noise
    seed_x, seed_y = random.uniform(0, 1000), random.uniform(0, 1000)
    sFactor = 0.8

    for i in range(width):
        for j in range(height):
            # Add the random seed offset to make the noise different each time
            noise_value = snoise2((i + seed_x) / (scale * sFactor), (j + seed_y) / (scale * sFactor), octaves=6, persistence=1, lacunarity=1.3)
            # Normalize noise value (-1 to 1) to fit the elevation range
            normalized_value = (noise_value + 1) / 2  # Convert to a range of (0, 1)
            
            # Map normalized noise to the elevation range -500 to 1500
            elevation = np.interp(normalized_value, [0, 1], [-500, 1500])
            elevation = round(elevation / 50) * 50  # Quantize to 50m intervals
            terrain[i, j] = elevation
    return terrain

# Apply elevation adjustments as per the user's requirement
def adjust_terrain(terrain):
    adjusted_terrain = terrain.copy()
    
    # Apply changes: every value lower than 0 becomes 0
    adjusted_terrain[adjusted_terrain < 0] = 0
    
    # Values between 50 and 200 become 10 (green)
    adjusted_terrain[(adjusted_terrain >= 50) & (adjusted_terrain <= 200)] = 1
    
    # Values between 250 and 400 become 20 (darker green)
    adjusted_terrain[(adjusted_terrain >= 250) & (adjusted_terrain <= 300)] = 2

    # Values between 250 and 400 become 20 (even darker green)
    adjusted_terrain[(adjusted_terrain >= 350) & (adjusted_terrain <= 400)] = 3
    
    # Now iterate over the rest of the heights above 400 until 1500
    # Start remapping at 30 and increment by increasing steps
    current_value = 4
    increment = 4

    for elevation in range(450, 1501, 50):
        adjusted_terrain[adjusted_terrain == elevation] = current_value
        current_value += increment
        increment += 5  # Increment increases by 5 for each iteration
    
    return adjusted_terrain

# Map terrain to color
def terrain_to_color_map(terrain):
    color_map = np.zeros((terrain.shape[0], terrain.shape[1], 3))  # RGB color map
    for i in range(terrain.shape[0]):
        for j in range(terrain.shape[1]):
            elevation = terrain[i, j]
            color_map[i, j] = get_color(elevation)
    return color_map

# 3D Visualization of Terrain with Color Mapping
def plot_3d_terrain_pixel(terrain, color_map):
    # Generate grid for terrain (X, Y coordinates)
    x = np.arange(terrain.shape[0])
    y = np.arange(terrain.shape[1])
    x, y = np.meshgrid(x, y)
    z = terrain

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    # Use plot_surface with all points (pixel-based, no interpolation)
    ax.plot_surface(x, y, z, facecolors=color_map, rstride=1, cstride=1, antialiased=True)  # Set rstride and cstride to 1 for full resolution

    # Set equal aspect ratio for X, Y, Z
    ax.set_box_aspect([1, 1, 0.35])  # Adjust Z scaling to avoid exaggerated height
    
    # Set axis labels and title
    ax.set_title('High-Quality Pixel-Based 3D Terrain Map')
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Elevation (m)')
    
    # Set fixed axis limits
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 200)
    ax.set_zlim(0, 700)

    # Set tick intervals
    ax.set_xticks(np.arange(0, 201, 25))  # X ticks from 0 to 200 in steps of 25
    ax.set_yticks(np.arange(0, 201, 25))  # Y ticks from 0 to 200 in steps of 25
    ax.set_zticks(np.arange(0, 701, 100))  # Z ticks from 0 to 700 in steps of 100

    # Optionally, invert Y-axis to start (0,0) in bottom-left corner
    ax.invert_yaxis()

    plt.show()
terrain = generate_terrain(width, height, scale)

# Adjust the terrain based on the provided rules
adjusted_terrain = adjust_terrain(terrain)

# Convert adjusted terrain to color map
color_map = terrain_to_color_map(adjusted_terrain)

# Plot the map in 3D with colors
plot_3d_terrain_pixel(adjusted_terrain, color_map)


