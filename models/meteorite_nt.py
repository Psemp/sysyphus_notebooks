from collections import namedtuple

fields = ["name", "status", "year", "place", "type", "mass", "MetBull", "GoogleEarth", "notes", "URL"]
Meteorite_nt = namedtuple("Meteorite", field_names=fields)
