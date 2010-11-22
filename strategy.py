import PlanetWars
import math
from itertools import groupby

DANGER_GROWTH_FACTOR = 5
DANGER_DISTANCE_FACTOR = 5

JUICY_DISTANCE = 0.2
JUICY_COST = 5.0

NEUTRAL = 0
MYSELF = 1
ENEMY = 2

def memo(func):
    results = {}
    def wrapper(planet):
        if planet.id not in results:
            results[planet.id] = func(planet)
        return results[planet.id]
    wrapper.invalidate = lambda planet: results.pop(planet.id, None)
    return wrapper

def DoTurn(log, pw):
    import random
    def distance(planet1, planet2):
        return pw.Distance(planet1.id, planet2.id)

    def distance_to(planet):
        return lambda other_planet: distance(planet, other_planet)

    def desirable_planets():
        planets = sorted(pw.NotMyPlanets(),
            key=lambda p: p.GrowthRate() / (p.NumShips() + 1.0), reverse=True)
        return planets

    def predict_planet(planet):
        """ Return number of turns until change owner """

        fleets = sorted([f for f in pw.Fleets() if f.DestinationPlanet() == planet.id],
            key=lambda f: f.TurnsRemaining())
        num_ships = planet.NumShips()
        owner = planet.Owner()
        event_log = [(owner, num_ships, 0)] #Owner, NumShip
        turn = 0
        for fleet_turn, fleets in groupby(fleets, key=lambda f: f.TurnsRemaining()):
            if owner != NEUTRAL:
                num_ships += (fleet_turn - turn) * planet.GrowthRate()

            for fleet in fleets:
                if fleet.Owner() != owner:
                    num_ships -= fleet.NumShips()
                else:
                    num_ships += fleet.NumShips()
                if num_ships < 0:
                    owner = fleet.Owner()
                    num_ships = -1 * num_ships
            event_log.append((owner, num_ships, fleet_turn,))
        return event_log

    for planet in desirable_planets():
        event = predict_planet(planet)[-1]
        if event[0] == MYSELF:
            continue
        for my_planet in pw.MyPlanets():
            num_ships = my_planet.NumShips()/2
            log.info('attacking %d from %d with %d', planet.id, my_planet.id, num_ships)
            pw.IssueOrder(my_planet.id, planet.id, num_ships)
        return
