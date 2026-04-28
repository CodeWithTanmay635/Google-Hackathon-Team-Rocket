def predict_traffic(area, time):
    
    # Convert to lowercase for easy comparison
    area = area.lower()
    time = time.lower()

    # Determine time period
    rush_morning = any(t in time for t in ['8', '9', '10'])
    rush_evening = any(t in time for t in ['17', '18', '19', '5pm', '6pm'])
    night = any(t in time for t in ['22', '23', '0', '1', '2', '3', 'night'])
    afternoon = any(t in time for t in ['12', '13', '14', '15', 'noon'])

    # Determine area type
    busy_area = any(a in area for a in [
        'market', 'station', 'hospital', 'school',
        'college', 'mall', 'chowk', 'bazaar'
    ])
    highway = any(a in area for a in ['highway', 'nh', 'bypass', 'ring road'])
    residential = any(a in area for a in ['colony', 'nagar', 'society', 'layout'])

    # Predict congestion
    if night:
        level = 'Low'
        suggestion = 'Roads are clear, safe to travel'
    elif rush_morning or rush_evening:
        if busy_area:
            level = 'Very High'
            suggestion = 'Avoid this route, heavy traffic expected'
        elif highway:
            level = 'High'
            suggestion = 'Expect delays, consider alternate route'
        else:
            level = 'Medium'
            suggestion = 'Moderate traffic, allow extra time'
    elif afternoon:
        if busy_area:
            level = 'Medium'
            suggestion = 'Moderate traffic near busy areas'
        else:
            level = 'Low'
            suggestion = 'Roads are fairly clear'
    else:
        level = 'Low'
        suggestion = 'Normal traffic conditions'

    # Alternate route suggestion
    alternate = get_alternate_route(area, level)

    return {
        'area': area,
        'time': time,
        'congestion_level': level,
        'suggestion': suggestion,
        'alternate_route': alternate
    }


def get_alternate_route(area, level):
    if level in ['High', 'Very High']:
        return f"Consider taking a parallel road or inner lanes near {area}"
    return "Current route is fine"

if __name__ == '__main__':
    print(predict_traffic('market chowk', '8am'))
    print(predict_traffic('highway nh9', '6pm'))
    print(predict_traffic('residential colony', 'night'))