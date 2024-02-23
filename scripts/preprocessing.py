import re
import numpy as np


def dms_to_decimal(dms: str) -> float:
    """
    Converts DMS coordinates to decimal format, accommodating various formats including simple degrees.
    """
    if dms is None or str(dms).lower() in ["nan", ""]:
        return np.nan

    dms_cleaned = re.sub(r"\s+|~", "", dms)

    match = re.match(r"(\d+\.?\d*)°([NSWE])", dms_cleaned)
    if match:
        degrees, direction = match.groups()
        decimal = float(degrees)
        if direction in ('S', 'W'):
            decimal *= -1
        return decimal

    match = re.match(r"(\d+)°(\d+)'(\d*\.\d*)?\"?([NSWE])", dms_cleaned)
    if match:
        degrees, minutes, seconds, direction = match.groups()
        seconds = float(seconds) if seconds else 0.0
        decimal = float(degrees) + float(minutes) / 60 + seconds / 3600
        if direction in ('S', 'W'):
            decimal *= -1
        return decimal

    return np.nan


def handle_coordinates(latitude: str, longitude: str) -> tuple:
    """
    Function :
        - Converts lat/lon in degrees, minutes seconds to floating decimals (+/-)
        and returns it as a tuple of lat/lon (decimals)
    Args :
        - latitude : a string AB°CD'EF.GH"N|S
        - latitude : a string IJ°KL'MN.OP"E|W
    Returns :
        - Tuple of lat/lon (decimals)
    """

    lat_decimal = dms_to_decimal(latitude)
    lon_decimal = dms_to_decimal(longitude)

    return (lat_decimal, lon_decimal)


def remove_uncertainty(to_process: str) -> float:
    """
    Removes uncertainty or additional annotations from the string and returns the numeric part as a float.

    Args:
        to_process (str): The string to process, removing any annotations like '±' and '(n=someshit)'.

    Returns:
        float: The floating-point value extracted from the beginning of the input string.
    """

    # This pattern matches optional leading sign, digits, optional decimal point, and more digits
    match = re.match(r"[-+]?\d*\.?\d+", to_process)

    if match:
        value = match.group()
        return float(value.strip())
    else:
        return np.nan


def handle_name(name):
    """Handles name by keeping alphanumeric characters, spaces, dashes, and underscores."""
    return ''.join(filter(lambda x: x.isalnum() or x.isspace() or x == '-' or x == '_', name)).strip()


def handle_country(place):
    """handles place, gives the country (second after ,)"""
    if ',' in place:
        # Split the string at "," and keep the second part (country)
        return place.split(',')[1].strip()
    return place.strip()


def handle_mass(mass):
    """Handles mass : assume convert kg to g, handles non specified as g, returns a float"""
    numeric_value = re.sub(r'[^\d.]', '', mass)

    if 'kg' in mass.lower():
        # Convert to grams if "kg" is in the string
        return float(numeric_value) * 1000
    elif 'g' in mass.lower() or numeric_value == '':
        # Return as is if "g" is in the string or if no unit is specified
        return float(numeric_value) if numeric_value else 0
    else:
        # Assume grams if no unit is specified
        return float(numeric_value)


def handle_year(year_str):
    """Handles year (select first four numerals or returns None if unknown)"""
    match = re.search(r'\b\d{4}\b', year_str)
    if match:
        return int(match.group(0))
    return None


def handle_types(type_str):
    # Replace specific characters with desired replacements
    type_str = type_str.replace("§", "").replace("¶", "").replace("~", "-").replace("#", "")
    # Aggressively remove all types of quotation marks, including smart quotes
    type_str = type_str.replace("\"", "").replace("“", "").replace("”", "").replace("‘", "").replace("’", "")

    type_str = type_str.strip()

    if type_str == "":
        return None
    else:
        return type_str


def extract_numeric_id(name):
    """
    Extracts numeric characters from a meteorite name and converts them to an integer.
    """
    numeric_part = "".join(filter(str.isdigit, name))
    return int(numeric_part) if numeric_part else None
