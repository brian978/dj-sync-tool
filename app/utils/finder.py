from app.models.Offset import Offset


def closest(number: float, values: list[float]):
    closest_value = None
    closest_distance = None

    for value in values:
        distance = abs(value - number)

        if closest_distance is None or distance < closest_distance:
            closest_distance = distance
            closest_value = value

    return closest_value


def closest_offset(number: float, offsets: list[Offset]):
    closest_value = None
    closest_distance = None

    for offset in offsets:
        distance = offset.distance_to_source(number)

        if closest_distance is None or distance < closest_distance:
            closest_distance = distance
            closest_value = offset

    return closest_value
