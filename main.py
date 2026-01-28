import numpy as np

class SmartCityBrain:
    def __init__(self):
        self.battery_cap = 1000.0  # kWh
        self.soc = 500.0           # Current State of Charge (kWh)
        self.min_soc = 0.2 * self.battery_cap
        self.max_soc = 0.9 * self.battery_cap
        self.wear_cost = 0.08      # $ per kWh discharged (battery wear)
        self.shed_penalty = 2.0    # $ per kWh (High penalty to prevent frequent outages)

    def process_step(self, demand, solar, grid_price):
        net_demand = demand - solar
        cost = 0.0
        action = ""

        # Case 1: Surplus Energy (Solar > Demand)
        if net_demand <= 0:
            surplus = abs(net_demand)
            charge_amt = min(surplus, self.max_soc - self.soc)
            self.soc += charge_amt
            action = "CHARGING"
            cost = 0.0
        
        # Case 2: Deficit (Demand > Solar)
        else:
            # Sub-case: High Grid Price (Arbitrage)
            if grid_price > (self.wear_cost + 0.10) and self.soc > self.min_soc:
                available_batt = self.soc - self.min_soc
                discharge_amt = min(net_demand, available_batt)
                self.soc -= discharge_amt
                net_demand -= discharge_amt
                cost += discharge_amt * self.wear_cost
                action = "BATT_DISCH"
            
            # Sub-case: Buy remaining from Grid
            if net_demand > 0:
                # If Grid is insanely expensive, trigger Load Shedding
                if grid_price >= 1.00:
                    shed_amt = net_demand
                    cost += shed_amt * self.shed_penalty
                    action += " + LOAD_SHED"
                else:
                    cost += net_demand * grid_price
                    action += " + GRID_BUY"
        
        return round(cost, 2), action

# --- Simulation & Stability Test ---
brain = SmartCityBrain()
standard_grid_cost = 0.0
smart_grid_cost = 0.0

# Simulating 24 steps (1 hour each)
for t in range(24):
    d = 500  # Avg Demand
    s = 600 if 8 < t < 16 else 0 # Solar midday
    # Simulate a price spike at t=12
    p = 1.00 if t == 12 else 0.15 
    
    # Standard Grid (No Solar/Battery)
    standard_grid_cost += d * p
    
    # Smart Grid
    step_cost, _ = brain.process_step(d, s, p)
    smart_grid_cost += step_cost

savings = ((standard_grid_cost - smart_grid_cost) / standard_grid_cost) * 100
