import time
import threading

class TrafficSignalController:
    """
    Manages the traffic light cycles at a given intersection and handles 
    Emergency Vehicle Preemption (Priority Mode).
    """
    def __init__(self, intersection_id="INT-001"):
        self.intersection_id = intersection_id
        
        # Initial standard system cycle (North/South Green, East/West Red)
        self.lanes = {
            "NORTH": "GREEN",
            "SOUTH": "GREEN",
            "EAST": "RED",
            "WEST": "RED"
        }
        
        self.priority_active = False
        self.priority_lane = None
        self.last_transition_time = time.time()
        
        print(f"[CONTROLLER {self.intersection_id}] System initialized. Normal cycle active.")
        
    def activate_priority(self, ambulance_lane):
        """
        Switches the intersection to prioritize the incoming ambulance lane in <500ms.
        Simulates the logic shown in "Backend Architecture - Signal Controller".
        """
        if self.priority_active and self.priority_lane == ambulance_lane:
            # Already active for this lane
            return self.lanes

        print(f"[CONTROLLER] PRIORITY ACTIVATED: Clearing intersection for {ambulance_lane} lane.")
        self.priority_active = True
        self.priority_lane = ambulance_lane
        
        # Step 1: Safe Transition phase
        # Any currently green lane that is NOT the ambulance lane goes YELLOW first
        transition_needed = False
        for lane, state in self.lanes.items():
            if state == "GREEN" and lane != ambulance_lane:
                self.lanes[lane] = "YELLOW"
                transition_needed = True
                
        if transition_needed:
            print(f"[CONTROLLER] Transitioning: {self.lanes}")
            # In a real environment, we'd sleep synchronously or asynchronously to let traffic clear.
            # time.sleep(2.0) 
        
        # Step 2: Lockdown & Priority Green
        for lane in self.lanes.keys():
            if lane == ambulance_lane:
                self.lanes[lane] = "GREEN"
            else:
                self.lanes[lane] = "RED"
                
        self.last_transition_time = time.time()
        print(f"[CONTROLLER] Priority Status Secured: {self.lanes}")
        
        return self.lanes

    def deactivate_priority(self):
        """
        Reverts the system to standard algorithmic traffic cycle after ambulance exit.
        """
        if not self.priority_active:
            return self.lanes
            
        print("[CONTROLLER] Ambulance cleared. Reverting to standard traffic flow cycle.")
        self.priority_active = False
        self.priority_lane = None
        
        # Revert to a safe default (e.g., North/South)
        self.lanes = {
            "NORTH": "GREEN",
            "SOUTH": "GREEN",
            "EAST": "RED",
            "WEST": "RED"
        }
        
        self.last_transition_time = time.time()
        print(f"[CONTROLLER] System Normalized: {self.lanes}")
        return self.lanes
        
    def get_status(self):
        """
        Returns real-time telemetry array for the frontend Dashboard.
        """
        return {
            "intersection_id": self.intersection_id,
            "priority_mode": self.priority_active,
            "priority_lane": self.priority_lane,
            "signals": self.lanes,
            "uptime_seconds": round(time.time() - self.last_transition_time, 2)
        }

# Example Usage
if __name__ == "__main__":
    controller = TrafficSignalController()
    controller.activate_priority("WEST")
    time.sleep(1)
    print(controller.get_status())
    controller.deactivate_priority()
