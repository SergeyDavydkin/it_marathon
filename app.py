from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Tuple
import math
import uvicorn

app = FastAPI()

# ---------- Модели данных ----------
class GravityAssist(BaseModel):
    velocity_gain: float = Field(..., gt=0)
    fuel_consumption: int = Field(..., gt=0)
    time_to_execute: int = Field(..., gt=0)

class Body(BaseModel):
    id: str
    gravity_assists: List[GravityAssist] = []

class Edge(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    distance: float = Field(..., gt=0)

    class Config:
        populate_by_name = True

class RobinsonRequest(BaseModel):
    mass_shuttle: float = Field(..., gt=0)
    mass_fuel_unit: float = Field(..., gt=0)
    power_per_unit: float = Field(..., gt=0)
    oxygen_time: int = Field(..., gt=0)
    total_fuel: int = Field(..., gt=0)
    fuel_consumption: float = Field(..., gt=0)
    bodies: List[Body] = []
    edges: List[Edge]

# ---------- Вспомогательные функции ----------
def compute_acceleration(mass_shuttle: float, current_fuel: int, mass_fuel_unit: float, power_per_unit: float) -> float:
    """Вычисление ускорения"""
    total_mass = mass_shuttle + current_fuel * mass_fuel_unit
    return power_per_unit / total_mass

def compute_brake_time(initial_speed: float, mass_shuttle: float, initial_fuel: int, 
                      mass_fuel_unit: float, power_per_unit: float) -> Tuple[float, int]:
    """Расчет торможения"""
    fuel_used = 0
    time_spent = 0.0
    speed = initial_speed
    fuel = initial_fuel
    
    while speed > 0 and fuel > 0:
        acc = compute_acceleration(mass_shuttle, fuel, mass_fuel_unit, power_per_unit)
        dt_needed = speed / acc
        
        if dt_needed <= 1.0:
            time_spent += 1.0
            fuel_used += 1
            speed = 0
            break
        else:
            time_spent += 1.0
            fuel_used += 1
            fuel -= 1
            speed -= acc * 1.0
            if speed < 0:
                speed = 0
    
    return time_spent, fuel_used

def compute_ascent_phase(initial_fuel: int, mass_shuttle: float, mass_fuel_unit: float, 
                        power_per_unit: float, total_distance: float) -> Tuple[float, int, float, float]:
    """Разгон с учетом ограничения половины пути"""
    fuel_for_ascent = initial_fuel // 2  # Целочисленное деление
    
    if fuel_for_ascent == 0:
        return 0.0, 0, 0.0, 0.0
    
    fuel_burned = 0
    time_elapsed = 0.0
    distance_covered = 0.0
    speed = 0.0
    fuel = initial_fuel
    half_distance = total_distance / 2.0
    
    for _ in range(fuel_for_ascent):
        if fuel <= 0:
            break
        acc = compute_acceleration(mass_shuttle, fuel, mass_fuel_unit, power_per_unit)
        fuel -= 1
        fuel_burned += 1
        time_elapsed += 1.0
        distance_covered += speed * 1.0 + 0.5 * acc * 1.0
        speed += acc * 1.0
        
        if distance_covered > half_distance:
            break
    
    return speed, fuel_burned, time_elapsed, distance_covered

def simulate_direct_flight(request: RobinsonRequest, distance: float) -> Tuple[bool, float]:
    """Симуляция прямого полета"""
    mass_shuttle = request.mass_shuttle
    mass_fuel_unit = request.mass_fuel_unit
    power_per_unit = request.power_per_unit
    oxygen_time = request.oxygen_time
    total_fuel = request.total_fuel
    fuel_consumption = request.fuel_consumption
    
    # Взлет
    launch_fuel = int(fuel_consumption * mass_shuttle)
    if launch_fuel > total_fuel:
        return False, 0
    
    fuel_remaining = total_fuel - launch_fuel
    total_time = 0.0
    
    # Разгон
    speed, fuel_used, time_ascent, dist_ascent = compute_ascent_phase(
        fuel_remaining, mass_shuttle, mass_fuel_unit, power_per_unit, distance
    )
    fuel_remaining -= fuel_used
    total_time += time_ascent
    
    if fuel_remaining < 0 or total_time > oxygen_time:
        return False, 0
    
    # Инерционный полет
    remaining_distance = distance - dist_ascent
    if remaining_distance > 0:
        if speed <= 0:
            return False, 0
        coast_time = remaining_distance / speed
        total_time += coast_time
    
    if total_time > oxygen_time:
        return False, 0
    
    # Торможение
    if speed > 0:
        brake_time, brake_fuel = compute_brake_time(speed, mass_shuttle, fuel_remaining, 
                                                    mass_fuel_unit, power_per_unit)
        total_time += brake_time
        fuel_remaining -= brake_fuel
        
        if fuel_remaining < 0 or total_time > oxygen_time:
            return False, 0
    
    return True, total_time

# ---------- API эндпоинт ----------
@app.post("/api/v1/robinson_cruise")
async def robinson_cruise(request: RobinsonRequest):
    try:
        # Валидация: проверяем наличие start_point и rescue_point
        has_start = False
        has_rescue = False
        direct_distance = None
        
        for edge in request.edges:
            if (edge.from_ == "start_point" and edge.to == "rescue_point") or \
               (edge.from_ == "rescue_point" and edge.to == "start_point"):
                direct_distance = edge.distance
                has_start = True
                has_rescue = True
            
            if edge.from_ == "start_point" or edge.to == "start_point":
                has_start = True
            if edge.from_ == "rescue_point" or edge.to == "rescue_point":
                has_rescue = True
        
        if not has_start or not has_rescue:
            return {"status": "incorrect_input"}
        
        # Проверка валидности входных данных
        if request.total_fuel <= 0 or request.oxygen_time <= 0:
            return {"status": "incorrect_input"}
        
        # Пробуем прямой маршрут
        if direct_distance is not None:
            can_reach, flight_time = simulate_direct_flight(request, direct_distance)
            if can_reach:
                return {
                    "can_reach": True,
                    "min_flight_time": round(flight_time, 1),
                    "route": ["start_point", "rescue_point"]
                }
        
        # Для маршрутов через промежуточные тела
        return {"can_reach": False}
        
    except Exception as e:
        print(f"Error details: {e}")
        return {"status": "incorrect_input"}

# ---------- Запуск сервера ----------
if __name__ == "__main__":
    print("Запуск сервера на http://0.0.0.0:8000")
    print("Доступный эндпоинт: POST /api/v1/robinson_cruise")
    print("Нажмите CTRL+C для остановки сервера")
    print("-" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
