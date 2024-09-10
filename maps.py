import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from noise import snoise2  # Simplex noise function
import random
from mpl_toolkits.mplot3d import Axes3D  # Import 3D plotting

# Map parameters
width, height = 200, 200  # Dimensions of the map grid
scale = 100.0  # Controls how "zoomed-in" the terrain is
elevation_intervals = np.arange(-500, 1501, 50)  # Elevation levels from -500 to 1500m in 50m intervals

# Color mapping based on elevation
def get_color(elevation):
    if elevation == 0:
        return [0, 0, 1]  # Blue for water
    elif elevation == 10:
        return [0.3, 1, 0.3]  # Green for 10
    elif elevation == 20:
        return [0, 0.5, 0]  # Darker green for 20
    elif elevation >= 150:  # Snow white for the last 3 heights
        return [1, 1, 1]  # Snow white
    elif 100 <= elevation < 150:  # Light grey to dark grey gradient for the next 5 heights
        normalized_elevation = (elevation - 100) / 50  # Normalize between 100 and 150
        return [0.8 - 0.5 * normalized_elevation, 0.8 - 0.5 * normalized_elevation, 0.8 - 0.5 * normalized_elevation]  # Light grey to dark grey
    else:  # Brown to black gradient for the rest of the heights until green
        normalized_elevation = (elevation - 30) / 70  # Normalize between 30 and 100 (adjust range accordingly)
        return [0.6 - 0.6 * normalized_elevation, 0.3 - 0.3 * normalized_elevation, 0.1 - 0.1 * normalized_elevation]  # Brown to black gradient



# Generate terrain using Simplex noise with no bias applied
def generate_terrain(width, height, scale):
    terrain = np.zeros((width, height))
    # Generate a random offset to introduce variability in the noise
    seed_x, seed_y = random.uniform(0, 1000), random.uniform(0, 1000)

    for i in range(width):
        for j in range(height):
            # Add the random seed offset to make the noise different each time
            noise_value = snoise2((i + seed_x) / scale, (j + seed_y) / scale, octaves=6, persistence=0.5, lacunarity=2.0)
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
    adjusted_terrain[(adjusted_terrain >= 50) & (adjusted_terrain <= 200)] = 10
    
    # Values between 250 and 400 become 20 (darker green)
    adjusted_terrain[(adjusted_terrain >= 250) & (adjusted_terrain <= 400)] = 20
    
    # Now iterate over the rest of the heights above 400 until 1500
    # Start remapping at 30 and increment by increasing steps
    current_value = 30
    increment = 10

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
def plot_3d_terrain(terrain, color_map):
    x = np.arange(terrain.shape[0])
    y = np.arange(terrain.shape[1])
    x, y = np.meshgrid(x, y)
    z = terrain

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    # Apply the terrain and color map to the surface
    ax.plot_surface(x, y, z, facecolors=color_map, rstride=1, cstride=1, antialiased=False)
    
    # Set labels and title
    ax.set_title('3D Terrain Map with Elevation and Colors')
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Elevation (m)')
    
    plt.show()

# Generate terrain
terrain = generate_terrain(width, height, scale)

# Adjust the terrain based on the provided rules
adjusted_terrain = adjust_terrain(terrain)

# Convert adjusted terrain to color map
color_map = terrain_to_color_map(adjusted_terrain)

# Plot the map in 3D with colors
plot_3d_terrain(adjusted_terrain, color_map)
