'''
This is the object that is used in run_test_cases.py, read the run method docstring for an explanation
'''

class Lot:
    def __init__(self, levels, spots_per_level):
        self.cars = {}
        self.levels = {level: Level(spots_per_level) for level in range(1, levels+1)}
        self.num_spots = levels*spots_per_level
        self.rate_per_minute = 0
        self.free_minutes = 0

    def park(self, plate, timestamp=0):
        for level_idx, level in self:
            if level.available > 0:
                spot = level.park(plate)
                self.cars[plate] = [level_idx, spot, timestamp]
                return [level_idx, spot]

    def __iter__(self):
        for level in range(1, len(self.levels)+1):
            yield level, self.levels[level]

    def leave(self, plate):
        level, spot, timestamp = self.cars.pop(plate)
        self.levels[level].available += 1
        self.levels[level].spots[spot].plate = ""
        return timestamp

    def transfer(self, plate, new_level, new_spot, timestamp=0):
        old_level, old_spot, old_time = self.cars.pop(plate)
        self.levels[old_level].available += 1
        self.levels[old_level].spots[old_spot].plate = ""
        self.cars[plate] = [new_level, new_spot, timestamp]
        self.levels[new_level].spots[new_spot].plate = plate
        self.levels[new_level].available -= 1 

class Level:
    def __init__(self, spots):
        self.available = spots
        self.spots = {spot: Spot() for spot in range(1, spots+1)}

    def park(self, plate):
        for spot_idx, spot in self:
            if not spot.plate:
                spot.plate = plate
                self.available -= 1
                return spot_idx

    def __iter__(self):
        for spot in range(1, len(self.spots) + 1):
            yield spot, self.spots[spot]

class Spot:
    def __init__(self):
        self.plate = ""

class Answer:
    def __init__(self):
        pass

    def run(self, method: str, *args, **kwargs):
        '''
        the run method is what is called in the run_test_cases.py file
        it receives the method name, a list of args, and a dict of kwargs. 
        make sure to implement the appropriate methods in Answer.
        
        you may create other classes, but you still need a wrapper for the methods 
        in Answer that calls the method of the custom class, and make sure 
        to instantiate the custom class if you choose to do this
        '''
        return getattr(self, method)(*args, **kwargs)


    def LOT_INIT(self, levels, spots_per_level):
        self.lot = Lot(levels, spots_per_level) 
        self.levels = levels
        self.spots_per_level = spots_per_level
        return self.lot.num_spots

    def PARK(self, plate):

        if plate in self.lot.cars:
            return "ALREADY_PARKED"
        if self.AVAILABLE()==0:
            return None

        return self.lot.park(plate)

    def LEAVE(self, plate):
        if plate not in self.lot.cars:
            return False
        else:
            self.lot.leave(plate)
            return True

    def SPOT_OF(self, plate):
        level, spot, timestamp = self.lot.cars.get(plate, [None,None,None])
        if level is None:
            return None

        return [level, spot]

    def AVAILABLE(self):
        return self.lot.num_spots - len(self.lot.cars)

    def SEARCH(self, prefix, limit):

        if limit <= 0:
            return []

        return sorted([car for car in self.lot.cars if car.startswith(prefix)])[:limit]

    def EXPORT(self):
        header = "plate,level,spot\n"
        csv_str = header

        for level_idx, level in self.lot:
            for spot_idx, spot in level:
                if spot.plate:
                    csv_str += f"{spot.plate},{level_idx},{spot_idx}\n"

        if header==csv_str:
            return header
        
        return csv_str.rstrip()

    def PARK_AT(self, timestamp, plate):
        if plate in self.lot.cars:
            return "ALREADY_PARKED"
        if self.AVAILABLE()==0:
            return None

        return self.lot.park(plate, timestamp)


    def LEAVE_AT(self, timestamp, plate):
        if plate not in self.lot.cars:
            return None

        entry_timestamp = self.lot.leave(plate)
        minutes = max(0, timestamp-entry_timestamp)
        fee = self.lot.rate_per_minute*max(0, minutes-self.lot.free_minutes) # price per minute * minutes

        return {"minutes": minutes, "fee": fee}

    def CONFIGURE_PRICING(self, rate_per_minute, free_minutes):
        self.lot.rate_per_minute = rate_per_minute
        self.lot.free_minutes = free_minutes
        return True
    
    def TRANSFER(self, plate, new_level, new_spot):

        # checks
        level = self.lot.levels.get(new_level, None)
        if level is None:
            return "OUT_OF_RANGE"
        spot = level.spots.get(new_spot, None)
        if spot is None:
            return "OUT_OF_RANGE"
        if plate not in self.lot.cars:
            return "NOT_FOUND"
        if spot.plate:
            if spot.plate == plate:
                return True
            return "OCCUPIED"

        # transfer
        self.lot.transfer(plate, new_level, new_spot)
        return True

