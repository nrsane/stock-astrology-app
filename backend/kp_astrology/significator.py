class KPSignificator:
    def __init__(self):
        self.nakshatra_length = 13.333333333333334
        self.sign_length = 30.0
        
        self.sign_lords = [
            'Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury',
            'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter'
        ]
        
        self.nakshatra_lords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu',
                               'Jupiter', 'Saturn', 'Mercury'] * 3
    
    def find_house_significators(self, birth_chart, house_number):
        """Find KP significators for a specific house"""
        if house_number < 1 or house_number > 12:
            return None
            
        house_cusp = birth_chart['cusps'][house_number - 1]
        
        # Get sign lord
        sign_index = int(house_cusp / self.sign_length)
        sign_lord = self.sign_lords[sign_index]
        
        # Get star lord
        nakshatra_index = int(house_cusp / self.nakshatra_length)
        star_lord = self.nakshatra_lords[nakshatra_index]
        
        # Get sub lord
        sub_lord = self._calculate_sub_lord(house_cusp)
        
        # Find planets occupying this house
        occupants = self._find_house_occupants(birth_chart, house_number)
        
        # Combine all significators
        all_significators = list(set([sign_lord, star_lord, sub_lord] + occupants))
        
        return {
            'house': house_number,
            'cuspal_sign_lord': sign_lord,
            'cuspal_star_lord': star_lord,
            'cuspal_sub_lord': sub_lord,
            'occupying_planets': occupants,
            'all_significators': all_significators
        }
    
    def _calculate_sub_lord(self, longitude):
        """Simplified sub-lord calculation"""
        nakshatra_index = int(longitude / self.nakshatra_length)
        sub_lords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu',
                    'Jupiter', 'Saturn', 'Mercury']
        return sub_lords[nakshatra_index % 9]
    
    def _find_house_occupants(self, birth_chart, house_number):
        """Find planets occupying the given house"""
        occupants = []
        house_positions = birth_chart['house_positions']
        
        for planet, house in house_positions.items():
            if house == house_number:
                occupants.append(planet)
                
        return occupants
