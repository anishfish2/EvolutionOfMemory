import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

# Function to find the nearest object in a section within the circle using numpy
def find_nearest_object_in_sector(center, radius, sector_start, sector_end, objects):
    print(sector_start, sector_end, objects)
    min_distance = float('inf')
    nearest_object = None

    for obj in objects:
        obj_point = np.array(obj)

        # Check if the object is within the circle
        if np.linalg.norm(obj_point - center) <= radius:
            # Calculate the angle of the object relative to the center
            angle = np.arctan2(obj_point[1] - center[1], obj_point[0] - center[0])

            # Convert angle to degrees
            obj_angle = np.degrees(angle)

            # Normalize the object angle to be in the range [0, 360)
            normalized_obj_angle = obj_angle % 361

            # Normalize the sector angles to be in the range [0, 360)
            normalized_sector_start = sector_start % 361
            normalized_sector_end = sector_end % 361
            if sector_start == 315:
                print(obj, normalized_obj_angle)
            # Check if the object angle is within the sector
            if normalized_sector_start <= normalized_obj_angle <= normalized_sector_end:
                
                distance = np.linalg.norm(obj_point - center)
                if distance < min_distance:
                    min_distance = distance
                    nearest_object = obj

    return nearest_object

# Function to check nearest objects in each section within the circle using numpy
def check_nearest_objects(center, radius, objects, num_sections):
    nearest_objects = []

    for i in range(num_sections):
        sector_start = i * 360 / num_sections
        sector_end = (i + 1) * 360 / num_sections

        # Find the nearest object in the sector within the circle
        nearest_object = find_nearest_object_in_sector(center, radius, sector_start, sector_end, objects)
        nearest_objects.append(nearest_object)

    return nearest_objects

# Function to get label position in a circular sector
def get_label_position(center, radius, angle_start, angle_end):
    angle_mid = (angle_start + angle_end) / 2
    label_x = center[0] + 1.2 * radius * np.cos(np.radians(angle_mid))
    label_y = center[1] + 1.2 * radius * np.sin(np.radians(angle_mid))
    return label_x, label_y

# Example usage
center_point = (0, 0)
circle_radius = 5
objects_to_check = [(2, 2), (-3, 1), (1, -4), (-4, -3), (3, -3), (5, 4), (-2, -1), (-5, 2), (1, 2), (-2, 3), (4, -2), (-1, -5)]
num_sections = 8

nearest_objects = check_nearest_objects(center_point, circle_radius, objects_to_check, num_sections)

# Plot the circular sectors, nearest objects, and labels
fig, ax = plt.subplots()
circle = plt.Circle(center_point, circle_radius, fill=False, color='b', linestyle='dashed')
ax.add_patch(circle)

for i in range(num_sections):
    start_angle = i * 360 / num_sections
    end_angle = (i + 1) * 360 / num_sections
    sector = Wedge(center_point, circle_radius, start_angle, end_angle, fill=False, color='r', linestyle='dashed')
    ax.add_patch(sector)

    # Plot the nearest object in each sector
    obj = nearest_objects[i]
    if obj:
        ax.plot(obj[0], obj[1], marker='o', markersize=8, color='green')
        print(f"Closest object in sector {i+1}: {obj}")

    # Label the sectors
    label_x, label_y = get_label_position(center_point, circle_radius, start_angle, end_angle)
    ax.text(label_x, label_y, f'Sector {i+1}', fontsize=8, ha='center', va='center')

# Plot the original objects
for obj in objects_to_check:
    ax.plot(obj[0], obj[1], marker='o', markersize=8, color='black')

ax.set_aspect('equal', adjustable='datalim')
plt.show()
