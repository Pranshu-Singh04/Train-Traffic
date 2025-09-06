from shapely.geometry import LineString, Point
import math

def haversine_m(a, b):
    """
    Calculates the great-circle distance between two points on the earth in meters.
    :param a: A tuple or list of [lon, lat] for point 1.
    :param b: A tuple or list of [lon, lat] for point 2.
    :return: Distance in meters.
    """
    lat1, lon1 = a[1], a[0]
    lat2, lon2 = b[1], b[0]
    R = 6371000  # Radius of Earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))

def get_chainage(station_point, line_coords):
    """
    Finds the chainage of a station along a polyline.
    :param station_point: A shapely Point object for the station.
    :param line_coords: A list of [lon, lat] pairs for the main line.
    :return: The chainage in meters, or None if an error occurs.
    """
    # Create the Shapely LineString from the coordinates
    line = LineString(line_coords)

    # Convert coordinates to a simplified 2D space for distance calculations
    # This is a common practice to find the nearest point on a line.
    # The actual distance will be calculated using the haversine formula later.
    line_2d = [(c[0], c[1]) for c in line_coords]

    # Find the nearest point on the line to the station
    nearest_on_line = line.project(station_point)
    nearest_point_on_line = line.interpolate(nearest_on_line)

    # Find the index of the segment on the original coordinate list
    # The segment is defined by the two points it lies between.
    for i in range(len(line_coords) - 1):
        segment = LineString([line_2d[i], line_2d[i+1]])
        if segment.contains(nearest_point_on_line) or segment.boundary.contains(nearest_point_on_line):
            # Calculate the cumulative distance up to the start of the segment
            cum_dist = 0.0
            for j in range(i):
                cum_dist += haversine_m(line_coords[j], line_coords[j+1])

            # Add the distance from the start of the segment to the nearest point
            dist_to_nearest = haversine_m(line_coords[i], [nearest_point_on_line.x, nearest_point_on_line.y])
            return cum_dist + dist_to_nearest
    
    return None

# --- Example Usage ---

# Example main_line coordinates (lon, lat pairs) for a hypothetical road/railway
main_line_coords = [
    [-74.0059, 40.7128], # Start Point (e.g., Lower Manhattan)
    [-73.9865, 40.7580],
    [-73.9712, 40.7831],
    [-73.9675, 40.8093], # End Point (e.g., Central Park North)
]

# Example station coordinates (lon, lat)
station_a = Point(-73.98, 40.77)  # A station somewhere along the line
station_b = Point(-74.01, 40.715) # Another station near the start

# Calculate chainage for each station
chainage_a = get_chainage(station_a, main_line_coords)
chainage_b = get_chainage(station_b, main_line_coords)

print(f"The chainage of station A is: {chainage_a:} meters")
print(f"The chainage of station B is: {chainage_b:} meters")