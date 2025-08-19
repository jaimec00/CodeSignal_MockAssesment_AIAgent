from dataclasses import dataclass, field
from bisect import bisect_right, insort
from typing import List, Tuple, Callable

class OpSeq:
    _next = 0
    @classmethod
    def next(cls):
        cls._next += 1
        return cls._next

@dataclass
class EventLog:
    events: List[Tuple[int, int, float|int|str]] = field(default_factory=list)
    _key: Callable = lambda x: (x[0], x[1])

    def append(self, ts, op_id, val):
        insort(self.events, (ts, op_id, val), key=self._key)

    def get_at(self, ts):
        if ts is None: # get latest:
            return self.events[-1][-1] if self.events else None
        idx = bisect_right(self.events, (ts, float("inf"), None), key=self._key) - 1
        return self.events[idx][-1]

    def rollback(self, ts):
        idx = bisect_right(self.events, (ts, float("inf"), None), key=self._key)
        self.events = self.events[:idx]

@dataclass
class Package:
    pid: str
    create_ts: int
    delivered_ts: EventLog=field(default_factory=EventLog)
    weight: EventLog=field(default_factory=EventLog)
    destination: EventLog=field(default_factory=EventLog)

    @classmethod
    def create(cls, pid, weight, destination, create_ts):
        p = cls(pid=pid, create_ts=create_ts)
        op = OpSeq.next()
        p.delivered_ts.append(create_ts, op, float("inf"))
        p.weight.append(create_ts, op, weight)
        p.destination.append(create_ts, op, destination)
        return p

    # getters
    def get_weight(self, ts):
        return self.weight.get_at(ts)
    def get_dest(self, ts):
        return self.destination.get_at(ts)
    def get_deliver_time(self, ts):
        return self.delivered_ts.get_at(ts)

    # setters
    def set_weight(self, new_weight, ts):
        op = OpSeq.next()
        self.weight.append(ts, op, new_weight)
    def set_dest(self, new_dest, ts):
        op = OpSeq.next()
        self.destination.append(ts, op, new_dest)
    def set_delivery_ts(self, ts):
        op = OpSeq.next()
        self.delivered_ts.append(ts, op, ts)
        
    # helpers
    def exists(self, ts):
        if ts is None or self.create_ts is None:
            return True
        else:
            return self.create_ts <= ts < self.get_deliver_time(ts)

    def rollback(self, ts):
        self.delivered_ts.rollback(ts)
        self.weight.rollback(ts)
        self.destination.rollback(ts)

class Answer:
    def __init__(self):
        self.pkgs = {}

    def run(self, method: str, *args, **kwargs): # do not edit this method
        return getattr(self, method)(*args, **kwargs)

    def pkg_exists(self, pid, ts):
        return pid in self.pkgs and self.pkgs[pid].exists(ts)

    def _checks(self, old_pid=None, new_pid=None, tracking_id=None, weight=None, destination=None, ts=None):
        if ts is not None:
            if ts < 0:
                raise ValueError
        if old_pid is not None:
            if not self.pkg_exists(old_pid, ts):
                raise KeyError
        if new_pid is not None:
            if new_pid in self.pkgs:
                raise ValueError
        if tracking_id is not None:
            if not tracking_id:
                raise ValueError
        if weight is not None:
            if weight<0 or not isinstance(weight, int):
                raise ValueError
        if destination is not None:
            if not destination:
                raise ValueError

    # ---------------------- level1
    def PKG_CREATE(self, tracking_id: str, weight: int, destination: str):
        '''
        description:    Create a new package record in the registry.
        params:         tracking_id (str):  unique identifier; must be a non-empty string
                        weight (int):       package weight in grams; must be >= 0
                        destination (str):  non-empty destination string
        returns:        None:               on success
        raises:         ValueError          if tracking_id already exists, or if any parameter is invalid
        notes:          Store only the latest state per tracking_id. This method must not overwrite existing records.
        '''
        self.PKG_CREATE_AT(None, tracking_id, weight, destination)

    def PKG_GET(self, tracking_id: str):
        '''
        description:    Retrieve an existing package's current state.
        params:         tracking_id (str):  unique identifier
        returns:        list | None:        [weight (int), destination (str)] if found; otherwise None
        raises:         None
        notes:          The return type is a 2-element list to ensure a deterministic order for tests.
        '''
        return self.PKG_GET_AT(None, tracking_id)

    def PKG_SET_WEIGHT(self, tracking_id: str, weight: int):
        '''
        description:    Update the weight of an existing package.
        params:         tracking_id (str):  unique identifier; must already exist
                        weight (int):       new weight in grams; must be >= 0
        returns:        None
        raises:         KeyError            if tracking_id does not exist
                        ValueError          if weight is invalid (< 0)
        notes:          No rounding; accept only integers.
        '''
        self.PKG_SET_WEIGHT_AT(None, tracking_id, weight)

    def PKG_REDIRECT(self, tracking_id: str, destination: str):
        '''
        description:    Update the destination of an existing package.
        params:         tracking_id (str):  unique identifier; must already exist
                        destination (str):  non-empty destination string
        returns:        None
        raises:         KeyError            if tracking_id does not exist
                        ValueError          if destination is empty
        notes:          Destination comparisons are case-sensitive; store exactly as provided.
        '''
        self.PKG_REDIRECT_AT(None, tracking_id, destination)

    def PKG_LIST_BY_DEST(self, destination: str):
        '''
        description:    Retrieve all tracking_ids for packages going to a given destination.
        params:         destination (str):  non-empty destination string
        returns:        list[str]:          list of tracking_ids sorted in ascending order
        raises:         ValueError          if destination is empty
        notes:          Return [] if no packages match.
        '''
        self._checks(destination=destination)
        return sorted([pkg for pkg in self.pkgs if self.pkgs[pkg].get_dest(None)==destination])

    # ----------------------------- level 2

    def PKG_TOP_N_HEAVIEST(self, n: int):
        '''
        description:    Return the top N heaviest packages currently in the registry.
        params:         n (int):            number of packages to return; must be >= 0
        returns:        list[list]:         list of [tracking_id, weight, destination]
                                            sorted by weight descending, then tracking_id ascending
        raises:         ValueError          if n < 0
        notes:          If n > number of packages, return all of them.
        '''
        self._checks(weight=n) # same reqs as weight
        found = []
        for pkg in self.pkgs.values():
            insort(found, [pkg.pid, pkg.get_weight(None), pkg.get_dest(None)], key=lambda x: (-x[1], x[2]))
        return found[:n]


    def PKG_AVG_WEIGHT(self):
        '''
        description:    Calculate the average weight of all packages.
        params:         none
        returns:        float | None:       average weight (float) if packages exist; None if registry empty
        raises:         None
        notes:          Division must be float division; round to 2 decimal places.
        '''
        
        count = len(self.pkgs)
        tot = sum(pkg.get_weight(None) for pkg in self.pkgs.values())
        return round(tot/count, 2) if count else None

    # -------------------------- level 3

    def PKG_CREATE_AT(self, timestamp: int, tracking_id: str, weight: int, destination: str):
        '''
        description:    Create a package with an initial state that becomes effective at the given timestamp.
        params:         timestamp (int):    event time in seconds; must be >= 0
                        tracking_id (str):  unique identifier; non-empty
                        weight (int):       initial weight in grams; must be >= 0
                        destination (str):  non-empty destination string
        returns:        None
        raises:         ValueError          if timestamp < 0, tracking_id is empty, destination is empty,
                                            weight < 0, or the package was already created before (duplicate id)
        notes:          Each tracking_id can be created at most once (across all times).
                        Creation does not guarantee visibility at earlier times (e.g., querying before creation returns None).
        '''
        self._checks(new_pid=tracking_id, tracking_id=tracking_id, weight=weight, destination=destination, ts=timestamp)
        self.pkgs[tracking_id] = Package.create(pid=tracking_id, weight=weight, destination=destination, create_ts=timestamp)

    def PKG_SET_WEIGHT_AT(self, timestamp: int, tracking_id: str, weight: int):
        '''
        description:    Record a weight change at the given timestamp.
        params:         timestamp (int):    event time in seconds; must be >= 0
                        tracking_id (str):  must refer to an existing (created) package id
                        weight (int):       new weight in grams; must be >= 0
        returns:        None
        raises:         ValueError          if timestamp < 0 or weight < 0
                        KeyError            if tracking_id has not been created
        notes:          Events may be added out of order relative to other events. They still affect queries
                        for times on/after their timestamps but never before creation.
        '''
        self._checks(old_pid=tracking_id, weight=weight, ts=timestamp)
        self.pkgs[tracking_id].set_weight(weight, timestamp)

    def PKG_REDIRECT_AT(self, timestamp: int, tracking_id: str, destination: str):
        '''
        description:    Record a destination change at the given timestamp.
        params:         timestamp (int):    event time in seconds; must be >= 0
                        tracking_id (str):  must refer to an existing (created) package id
                        destination (str):  non-empty destination string
        returns:        None
        raises:         ValueError          if timestamp < 0 or destination is empty
                        KeyError            if tracking_id has not been created
        notes:          Destination strings are case-sensitive; store exactly as provided.
        '''
        self._checks(old_pid=tracking_id, destination=destination, ts=timestamp)
        self.pkgs[tracking_id].set_dest(destination, timestamp)

    def PKG_MARK_DELIVERED_AT(self, timestamp: int, tracking_id: str):
        '''
        description:    Mark the package as delivered (no longer active) starting at the given timestamp.
        params:         timestamp (int):    event time in seconds; must be >= 0
                        tracking_id (str):  must refer to an existing (created) package id
        returns:        None
        raises:         ValueError          if timestamp < 0
                        KeyError            if tracking_id has not been created
        notes:          For any query time t where t >= delivery timestamp, the package is considered not present.
                        Queries for t before delivery continue to reflect prior state.
        '''
        self._checks(old_pid=tracking_id, ts=timestamp)
        self.pkgs[tracking_id].set_delivery_ts(timestamp)


    def PKG_GET_AT(self, timestamp: int, tracking_id: str):
        '''
        description:    Retrieve the package state as of the specified timestamp.
        params:         timestamp (int):    query time in seconds; must be >= 0
                        tracking_id (str):  unique identifier
        returns:        list | None:        [weight (int), destination (str)] if the package existed and was not delivered as of timestamp;
                                            otherwise None (not yet created or already delivered)
        raises:         ValueError          if timestamp < 0
        notes:          Apply the latest event at or before the timestamp for each attribute (weight, destination).
                        If multiple events share the same timestamp, apply them in insertion order.
        '''
        self._checks(ts=timestamp)
        if self.pkg_exists(tracking_id, timestamp):
            return [self.pkgs[tracking_id].get_weight(timestamp), self.pkgs[tracking_id].get_dest(timestamp)]

    # -----------------------------------------------level4
    def ROLLBACK(self, timestamp: int):
        '''
        description:    Roll back the entire registry to the state as of the given timestamp.
        params:         timestamp (int):    point in time (>= 0) to restore system state
        returns:        None
        raises:         ValueError          if timestamp < 0
        notes:          - After rollback, all queries must behave as if no events after 'timestamp' exist.
                        - This affects all packages simultaneously.
                        - Future events that were "rolled back" are discarded permanently.
                        - State at exactly 'timestamp' must be preserved (i.e., events with time == timestamp remain).
        '''
        self._checks(ts=timestamp)
        to_pop = [pkg for pkg in self.pkgs if self.pkgs[pkg].create_ts>timestamp]
        for pkg in to_pop:
            self.pkgs.pop(pkg)
        for pkg in self.pkgs.values():
            pkg.rollback(timestamp)
