import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from noise import snoise2  # Simplex noise function
import random

# Map parameters
width, height = 200, 200  # Dimensions of the map grid
scale = 100.0  # Controls how "zoomed-in" the terrain is
elevation_intervals = np.arange(-500, 1501, 50)  # Elevation levels from -500 to 1500m in 50m intervals

# Color mapping based on elevation
def get_color(elevation):
    if elevation <= 0:
        return [0, 0, 1]  # Blue for water
    elif 50 <= elevation <= 400:
        # Gradient from light green to dark green (simulating grass/plains)
        normalized_elevation = (elevation - 50) / 350  # Normalize between 50 and 400
        return [0.5 - 0.3 * normalized_elevation, 1 - 0.5 * normalized_elevation, 0.5 - 0.2 * normalized_elevation]  # Light green to dark green
    elif 450 <= elevation <= 900:
        # Gradient from dark yellow to brown (simulating mountain/earth/dirt)
        normalized_elevation = (elevation - 450) / 450  # Normalize between 450 and 900
        return [0.6 - 0.4 * normalized_elevation, 0.5 - 0.5 * normalized_elevation, 0.1]  # Dark yellow to brown
    elif 900 < elevation <= 1000:
        # Gradient from grey to dark grey (simulating rocks)
        normalized_elevation = (elevation - 900) / 100  # Normalize between 900 and 1000
        return [0.6 - 0.3 * normalized_elevation, 0.6 - 0.3 * normalized_elevation, 0.6 - 0.3 * normalized_elevation]  # Grey gradient
    elif elevation > 1000:
        return [1, 1, 1]  # Snow white

# Generate terrain using Simplex noise with a random seed and scaling
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

# Map terrain to color
def terrain_to_color_map(terrain):
    color_map = np.zeros((terrain.shape[0], terrain.shape[1], 3))  # RGB color map
    for i in range(terrain.shape[0]):
        for j in range(terrain.shape[1]):
            elevation = terrain[i, j]
            color_map[i, j] = get_color(elevation)
    return color_map

# Generate dynamic legend based on the current map
def generate_legend(terrain):
    unique_elevations = np.unique(terrain)
    legend_elements = []
    
    for elevation in unique_elevations:
        color = get_color(elevation)
        label = f'{int(elevation)}m'  # Display the exact elevation in meters
        legend_elements.append(Patch(facecolor=color, edgecolor='k', label=label))
    
    return legend_elements

# Generate and display the terrain map with a dynamic legend
def plot_with_dynamic_legend(terrain, color_map):
    fig, ax = plt.subplots()
    ax.imshow(color_map)
    ax.set_title("Random Pixel Map - Elevation and Color")
    ax.axis('off')  # Turn off the axis

    # Generate dynamic legend based on terrain
    legend_elements = generate_legend(terrain)

    # Add the legend
    ax.legend(handles=legend_elements, loc='upper right', title="Elevation (m)")

    plt.show()

# Generate terrain and color map
terrain = generate_terrain(width, height, scale)
color_map = terrain_to_color_map(terrain)

# Plot the map with a dynamic legend
plot_with_dynamic_legend(terrain, color_map)
