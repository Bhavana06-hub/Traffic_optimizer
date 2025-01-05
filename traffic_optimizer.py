import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import random
import numpy as np
from typing import List, Dict, Any

# Constants
ROAD_IDS = [1, 2, 3, 4]
ROAD_ORDER = [2, 4, 3, 1]  # Right, Bottom, Left, Top
SIGNAL_COLORS = {"red": "#FF0000", "yellow": "#FFFF00", "green": "#00FF00"}
LANE_COLORS = {"low": "#90EE90", "medium": "#FFA500", "high": "#FF4500"}
CAR_COLORS = ["#1E90FF", "#32CD32", "#FFD700", "#FF69B4"]

# Define road structure with updated signal times
roads: List[Dict[str, Any]] = [
    {"road_id": 1, "signal_color": "red", "timer": 0, "signal_time": 15, "traffic_density": "low", "ambulance": False},
    {"road_id": 2, "signal_color": "red", "timer": 0, "signal_time": 25, "traffic_density": "high", "ambulance": False},
    {"road_id": 3, "signal_color": "red", "timer": 0, "signal_time": 20, "traffic_density": "medium", "ambulance": False},
    {"road_id": 4, "signal_color": "red", "timer": 0, "signal_time": 20, "traffic_density": "medium", "ambulance": False}
]

# Initialize car positions
car_positions: Dict[int, List[Dict[str, Any]]] = {
    road_id: [
        {
            "x": random.uniform(0, 7),
            "is_ambulance": (road_id == 2 and i == 0),
            "color": random.choice(CAR_COLORS)
        }
        for i in range(10 if roads[road_id-1]["traffic_density"] == "high" 
                       else 7 if roads[road_id-1]["traffic_density"] == "medium" else 4)
    ]
    for road_id in ROAD_IDS
}

def update_signals() -> None:
    ambulance_road = next((road for road in roads if road["ambulance"]), None)

    if ambulance_road and ambulance_road["road_id"] == 2:
        # If there's an ambulance on the right-side road, keep it green
        if is_ambulance_crossing_junction(2):
            return
    current_green_road = next((road for road in roads if road["signal_color"] == "green"), None)

    if current_green_road:
        current_green_road["timer"] += 1
        if current_green_road["timer"] >= current_green_road["signal_time"]:
            current_green_road["signal_color"] = "red"
            current_green_road["timer"] = 0
            current_green_index = ROAD_ORDER.index(current_green_road["road_id"])
            next_green_id = ROAD_ORDER[(current_green_index + 1) % 4]
            roads[next_green_id - 1]["signal_color"] = "green"
    else:
        roads[ROAD_ORDER[0] - 1]["signal_color"] = "green"

    for road in roads:
        if road["signal_color"] != "green":
            road["signal_color"] = "red"

def draw_roads_and_signals():
    ax.add_patch(patches.Rectangle((-1, -1), 2, 2, color="#4A4A4A", zorder=1))

    road_width = 1.5
    for road in roads:
        road_id = road["road_id"]
        if road_id in [1, 3]:  # Vertical roads
            ax.add_patch(patches.Rectangle((-road_width/2, -5 if road_id == 1 else 1), road_width, 4, color="#787878", zorder=0))
            ax.add_line(plt.Line2D([-0.05, -0.05], [-5 if road_id == 1 else 1, -1 if road_id == 1 else 5], color="white", linestyle=(0, (5, 5)), zorder=2))
            ax.add_line(plt.Line2D([0.05, 0.05], [-5 if road_id == 1 else 1, -1 if road_id == 1 else 5], color="white", linestyle=(0, (5, 5)), zorder=2))
        else:  # Horizontal roads
            ax.add_patch(patches.Rectangle((-5 if road_id == 4 else 1, -road_width/2), 4, road_width, color="#787878", zorder=0))
            ax.add_line(plt.Line2D([-5 if road_id == 4 else 1, -1 if road_id == 4 else 5], [-0.05, -0.05], color="white", linestyle=(0, (5, 5)), zorder=2))
            ax.add_line(plt.Line2D([-5 if road_id == 4 else 1, -1 if road_id == 4 else 5], [0.05, 0.05], color="white", linestyle=(0, (5, 5)), zorder=2))

    light_positions = [(-0.5, 1), (1, 0.5), (0.5, -1), (-1, -0.5)]
    for road, pos in zip(roads, light_positions):
        ax.add_patch(patches.Circle(pos, 0.2, facecolor="#333333", edgecolor="white", linewidth=2, zorder=3))
        ax.add_patch(patches.Circle(pos, 0.15, facecolor=SIGNAL_COLORS[road["signal_color"]], zorder=4))

        # Add timer text
        if road["signal_color"] == "green":
            remaining_time = road["signal_time"] - road["timer"]
            ax.text(pos[0], pos[1], str(remaining_time), color="white", fontweight="bold", ha="center", va="center", zorder=5)


def update_car_positions(road_id: int) -> None:
    road = roads[road_id - 1]
    cars = car_positions[road_id]

    # Sort cars based on their position (descending order for roads 1 and 2, ascending for roads 3 and 4)
    cars.sort(key=lambda car: car["x"], reverse=(road_id in [1, 2]))

    min_distance = 1.5  # Minimum distance between cars

    for i, car in enumerate(cars):
        can_move = is_path_clear(road_id, car["x"])

        if road["signal_color"] == "green" and can_move:
            car["x"] += 0.05  # Reduced speed for smoother movement
        elif car["is_ambulance"]:
            # Ambulance can move slowly even on red signal if path is clear
            if can_move:
                car["x"] += 0.03

        # Ensure cars maintain a minimum distance
        if i > 0:
            prev_car = cars[i-1]
            if road_id in [1, 2]:
                if car["x"] > prev_car["x"] - min_distance:
                    car["x"] = prev_car["x"] - min_distance
            else:
                if car["x"] < prev_car["x"] + min_distance:
                    car["x"] = prev_car["x"] + min_distance

        # Wrap around logic
        if road_id in [1, 2]:
            if car["x"] < 0:
                car["x"] = 10
        else:
            if car["x"] > 10:
                car["x"] = 0

        if car["is_ambulance"]:
            road["ambulance"] = car["x"] <= 10 and car["x"] >= 0

    # Ensure ambulance stays at the front of the queue
    ambulance = next((car for car in cars if car["is_ambulance"]), None)
    if ambulance:
        non_ambulance_cars = [car for car in cars if not car["is_ambulance"]]
        if non_ambulance_cars:
            if road_id in [1, 2]:
                max_x = max(car["x"] for car in non_ambulance_cars)
                if ambulance["x"] < max_x:
                    ambulance["x"] = min(max_x + min_distance, 10)
            else:
                min_x = min(car["x"] for car in non_ambulance_cars)
                if ambulance["x"] > min_x:
                    ambulance["x"] = max(min_x - min_distance, 0)
def draw_cars() -> None:
    for road_id, cars in car_positions.items():
        for car in cars:
            color = "#FF0000" if car["is_ambulance"] else car["color"]
            if road_id in [1, 3]:  # Vertical roads
                y = car["x"] - 5 if road_id == 1 else 5 - car["x"]
                x_offset = -0.2 if road_id == 1 else 0.2
                # Car body
                ax.add_patch(patches.Rectangle((x_offset - 0.1, y - 0.2), 0.2, 0.4, facecolor=color, edgecolor="black", linewidth=1, zorder=5))
                # Wheels
                ax.add_patch(patches.Circle((x_offset - 0.07, y - 0.15), 0.03, facecolor="black", zorder=6))
                ax.add_patch(patches.Circle((x_offset + 0.07, y - 0.15), 0.03, facecolor="black", zorder=6))
                ax.add_patch(patches.Circle((x_offset - 0.07, y + 0.15), 0.03, facecolor="black", zorder=6))
                ax.add_patch(patches.Circle((x_offset + 0.07, y + 0.15), 0.03, facecolor="black", zorder=6))
                # Windows
                ax.add_patch(patches.Rectangle((x_offset - 0.07, y - 0.05), 0.14, 0.1, facecolor="lightblue", edgecolor="black", linewidth=0.5, zorder=6))
                if car["is_ambulance"]:
                    ax.text(x_offset, y, "+", color="white", fontweight="bold", ha="center", va="center", zorder=7, fontsize=8)
            else:  # Horizontal roads
                x = car["x"] - 5 if road_id == 4 else 5 - car["x"]
                y_offset = 0.2 if road_id == 2 else -0.2
                # Car body
                ax.add_patch(patches.Rectangle((x - 0.2, y_offset - 0.1), 0.4, 0.2, facecolor=color, edgecolor="black", linewidth=1, zorder=5))
                # Wheels
                ax.add_patch(patches.Circle((x - 0.15, y_offset - 0.07), 0.03, facecolor="black", zorder=6))
                ax.add_patch(patches.Circle((x - 0.15, y_offset + 0.07), 0.03, facecolor="black", zorder=6))
                ax.add_patch(patches.Circle((x + 0.15, y_offset - 0.07), 0.03, facecolor="black", zorder=6))
                ax.add_patch(patches.Circle((x + 0.15, y_offset + 0.07), 0.03, facecolor="black", zorder=6))
                # Windows
                ax.add_patch(patches.Rectangle((x - 0.05, y_offset - 0.07), 0.1, 0.14, facecolor="lightblue", edgecolor="black", linewidth=0.5, zorder=6))
                if car["is_ambulance"]:
                    ax.text(x, y_offset, "+", color="white", fontweight="bold", ha="center", va="center", zorder=7, fontsize=8)




def is_ambulance_crossing_junction(road_id: int) -> bool:
    for car in car_positions[road_id]:
        if car["is_ambulance"]:
            if road_id in [1, 3]:  # Vertical roads
                return -1 <= car["x"] - 5 <= 1 if road_id == 1 else -1 <= 5 - car["x"] <= 1
            else:  # Horizontal roads
                return -1 <= car["x"] - 5 <= 1 if road_id == 4 else -1 <= 5 - car["x"] <= 1
    return False
def is_path_clear(road_id: int, car_x: float) -> bool:
    for other_car in car_positions[road_id]:
        if other_car["x"] > car_x and other_car["x"] - car_x < 1.0:  # Increased safe distance
            return False
    return True

def handle_ambulance_priority() -> None:
    ambulance_road = next((road for road in roads if road["ambulance"]), None)
    if ambulance_road:
        if ambulance_road["road_id"] == 2:  # Right-side road
            if ambulance_road["signal_color"] != "green" or is_ambulance_crossing_junction(2):
                # Set all other roads to red
                for road in roads:
                    if road["road_id"] != 2:
                        road["signal_color"] = "red"
                        road["timer"] = 0
                # Set the right-side road to green
                ambulance_road["signal_color"] = "green"
                ambulance_road["timer"] = 0
        else:
            # For other roads, just set the ambulance road to green
            if ambulance_road["signal_color"] != "green":
                current_green_road = next((r for r in roads if r["signal_color"] == "green"), None)
                if current_green_road:
                    current_green_road["signal_color"] = "red"
                    current_green_road["timer"] = 0
                ambulance_road["signal_color"] = "green"
                ambulance_road["timer"] = 0

def update(frame: int) -> None:
    update_signals()
    handle_ambulance_priority()
    ax.clear()
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_facecolor("#E6E6E6")
    ax.axis('off')
    draw_roads_and_signals()
    for road_id in ROAD_IDS:
        update_car_positions(road_id)
    draw_cars()
    ax.set_title("AI-based Traffic Management System", fontsize=16, fontweight='bold', fontname='Times New Roman')

    legend_elements = [
        patches.Patch(facecolor="#FF0000", edgecolor="black", label="Ambulance"),
        patches.Patch(facecolor="#1E90FF", edgecolor="black", label="Regular Vehicle"),
        patches.Patch(facecolor="#FF0000", edgecolor="white", label="Red Signal"),
        patches.Patch(facecolor="#FFFF00", edgecolor="white", label="Yellow Signal"),
        patches.Patch(facecolor="#00FF00", edgecolor="white", label="Green Signal")
    ]
    ax.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(1.3, 1), fontsize=8)

# Initialize plot
fig, ax = plt.subplots(figsize=(12, 10))
plt.subplots_adjust(right=0.85)

# Create animation
ani = FuncAnimation(fig, update, frames=200, interval=50, repeat=True, blit=False)

plt.show()