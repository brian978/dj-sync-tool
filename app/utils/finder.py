def closest(number: float, values: list[float]):
    closest_value = None
    closest_distance = None

    for value in values:
        distance = abs(value - number)

        if closest_distance is None or distance < closest_distance:
            closest_distance = distance
            closest_value = value

    return closest_value
