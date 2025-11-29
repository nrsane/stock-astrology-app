import swisseph as swe
from datetime import datetime
import math

class KPChartCalculator:
    def __init__(self):
        # Set ephemeris path
        swe.set_ephe_path()
        self.kp_ayanamsha = swe.SIDM_KRISHNAMURTI
        
    def calculate_stock_birth_chart(self, symbol, listing_date, listing_time="10:00", 
                                  exchange_lat=19.0750, exchange_lon=72.8777):
        """
        Calculate KP birth chart for stock listing
        """
        try:
            # Parse listing time
            if isinstance(listing_time, str):
                time_parts = listing_time.split(':')
                listing_hour = int(time_parts[0])
                listing_minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            else:
                listing_hour, listing_minute = 10, 0
            
            # Create datetime object
            listing_dt = datetime(
                listing_date.year, listing_date.month, listing_date.day,
                listing_hour, listing_minute
            )
            
            # Convert to Julian Day
            jd = swe.julday(
                listing_dt.year, listing_dt.month, listing_dt.day,
                listing_dt.hour + listing_dt.minute/60.0
            )
            
            # Set ayanamsha
            swe.set_sid_mode(self.kp_ayanamsha)
            
            # Calculate houses using Placidus system
            cusps, ascmc = swe.houses_ex(
                jd, exchange_lat, exchange_lon, b'P', swe.FLG_SIDEREAL
            )
            
            # Get planet positions
            planets = {}
            planet_map = {
                swe.SUN: 'Sun', swe.MOON: 'Moon', swe.MARS: 'Mars',
                swe.MERCURY: 'Mercury', swe.JUPITER: 'Jupiter',
                swe.VENUS: 'Venus', swe.SATURN: 'Saturn',
                swe.URANUS: 'Uranus', swe.NEPTUNE: 'Neptune',
                swe.PLUTO: 'Pluto', swe.MEAN_NODE: 'Rahu'
            }
            
            for planet_code, planet_name in planet_map.items():
                flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
                ret, position = swe.calc_ut(jd, planet_code, flags)
                planets[planet_name] = {
                    'longitude': position[0],
                    'latitude': position[1],
                    'distance': position[2],
                    'speed_longitude': position[3]
                }
            
            # Calculate Ketu (180 degrees from Rahu)
            rahu_long = planets['Rahu']['longitude']
            ketu_long = (rahu_long + 180) % 360
            planets['Ketu'] = {
                'longitude': ketu_long,
                'latitude': 0,
                'distance': 0,
                'speed_longitude': planets['Rahu']['speed_longitude']
            }
            
            # Calculate house positions for planets
            house_positions = self._calculate_house_positions(cusps, planets)
            
            return {
                'symbol': symbol,
                'listing_datetime': listing_dt.isoformat(),
                'cusps': [float(c) for c in cusps[:12]],
                'ascendant': float(ascmc[0]),
                'planets': planets,
                'house_positions': house_positions
            }
            
        except Exception as e:
            print(f"Error calculating chart: {e}")
            return None
    
    def _calculate_house_positions(self, cusps, planets):
        """Determine which house each planet is in"""
        house_positions = {}
        
        for planet_name, planet_data in planets.items():
            longitude = planet_data['longitude']
            house_num = self._find_house_number(longitude, cusps)
            house_positions[planet_name] = house_num
            
        return house_positions
    
    def _find_house_number(self, longitude, cusps):
        """Find house number for given longitude"""
        longitude = longitude % 360
        
        for i in range(12):
            start_cusp = cusps[i]
            end_cusp = cusps[(i + 1) % 12]
            
            if end_cusp < start_cusp:
                if longitude >= start_cusp or longitude < end_cusp:
                    return i + 1
            else:
                if start_cusp <= longitude < end_cusp:
                    return i + 1
        
        return 1
