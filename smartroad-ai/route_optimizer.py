import math

class RouteOptimizer:
    """
    Route Optimizer module for SmartRoad AI.
    Calculates the most efficient path for the ambulance to the nearest medical facility,
    integrating with the signal priority system across multiple intersections.
    """
    def __init__(self):
        # Database of simulated nearby hospitals with geographic coordinates (lat, lon)
        self.hospitals = {
            "Solapur Medical College & Hospital": (17.6599, 75.9064),
            "Apollo Emergency Care Unit": (17.6710, 75.9200),
            "Metro Multi-specialty Trauma Center": (17.6405, 75.8900),
            "City Care Hospital": (17.6650, 75.9120)
        }
        print("[ROUTE OPTIMIZER] Loaded hospital location matrix.")
    
    def calculate_distance(self, loc1, loc2):
        """
        Calculates approximate distance between two lat/lon coordinates natively.
        Uses Euclidean math scaled for approximate kilometers.
        """
        lat1, lon1 = loc1
        lat2, lon2 = loc2
        
        # Rough approximation mapping: 1 coordinate degree is ~ 111 km
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        distance_km = math.sqrt(dlat**2 + dlon**2) * 111.0
        
        return distance_km
        
    def find_nearest_hospital(self, current_location=(17.6500, 75.9000)):
        """
        Scans hospital database, computes distances, and selects the nearest facility.
        Calculates Estimated Time of Arrival (ETA) considering standard ambulance priority speed.
        """
        print(f"[ROUTE OPTIMIZER] Computing optimal route from {current_location}...")
        
        best_hospital = None
        min_distance = float('inf')
        
        for name, coords in self.hospitals.items():
            dist = self.calculate_distance(current_location, coords)
            if dist < min_distance:
                min_distance = dist
                best_hospital = name
                best_coords = coords
                
        # Simulated ETA calculation: 
        # Assume ambulance averages 50 km/h in dense city traffic *with* signal priority
        eta_minutes = round((min_distance / 50.0) * 60.0, 1)
        
        print(f"[ROUTE OPTIMIZER] Target Locked: {best_hospital} | ETA: {eta_minutes} mins")
                
        return {
            "nearest_hospital": best_hospital,
            "hospital_coordinates": best_coords,
            "distance_km": round(min_distance, 2),
            "estimated_eta_mins": eta_minutes,
            "status": "ROUTE OPTIMIZED"
        }

# Example Usage
if __name__ == "__main__":
    optimizer = RouteOptimizer()
    target = optimizer.find_nearest_hospital(current_location=(17.6530, 75.9010))
    print("Optimization Payload:", target)
