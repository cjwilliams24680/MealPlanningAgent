from datetime import datetime


# Used to make the meals weather-appropriate and add a little bit of differentiation to the prompt week-to-week.
def get_seasonal_report():
    now = datetime.now()
    month_name = now.strftime("%B")
    month_num = now.month

    # Season list (indexed 0-3)
    seasons = ["Winter", "Spring", "Summer", "Autumn"]

    # Weather descriptions for each season
    weather_data = {
        "Winter": "Expect cold temperatures, frosty mornings, and the occasional flurry of snow.",
        "Spring": "The days are getting longer and you'll see flowers beginning to bloom.",
        "Summer": "It's time for sunshine, warm breeze, and plenty of outdoor activities.",
        "Autumn": "The air is turning crisp and the leaves are putting on a colorful show.",
    }

    # The math trick: (month % 12 // 3)
    # Dec(12), Jan(1), Feb(2) map to 0 (Winter)
    # Mar(3), Apr(4), May(5) map to 1 (Spring)
    # Jun(6), Jul(7), Aug(8) map to 2 (Summer)
    # Sep(9), Oct(10), Nov(11) map to 3 (Autumn)
    season_idx = month_num % 12 // 3
    season = seasons[season_idx]
    description = weather_data[season]

    return f"It's {month_name} and {season} is here! {description}"
