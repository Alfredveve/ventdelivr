from django.conf import settings
import math
import random

class GoogleMapsService:
    """
    Service to handle Google Maps interactions (Geocoding, Distance Matrix).
    Currently uses MOCK data to avoid API key requirements for development.
    """
    
    @staticmethod
    def geocode_address(address):
        """
        Mock geocoding: Returns random coordinates near a central point (e.g., Paris or a generic city)
        In production, this would call Google Maps Geocoding API.
        """
        # Center point (e.g., Downtown)
        base_lat = 48.8566
        base_lng = 2.3522
        
        # Add random offset
        lat_offset = random.uniform(-0.05, 0.05)
        lng_offset = random.uniform(-0.05, 0.05)
        
        return {
            'lat': base_lat + lat_offset,
            'lng': base_lng + lng_offset
        }

    @staticmethod
    def calculate_distance(origin_lat, origin_lng, dest_lat, dest_lng):
        """
        Calculates Haversine distance between two points in Kilometers.
        """
        if not all([origin_lat, origin_lng, dest_lat, dest_lng]):
            return 0.0
        
        # Convert to float if Decimal
        origin_lat = float(origin_lat)
        origin_lng = float(origin_lng)
        dest_lat = float(dest_lat)
        dest_lng = float(dest_lng)
            
        R = 6371  # Earth radius in km
        
        dlat = math.radians(dest_lat - origin_lat)
        dlng = math.radians(dest_lng - origin_lng)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + \
            math.cos(math.radians(origin_lat)) * math.cos(math.radians(dest_lat)) * \
            math.sin(dlng / 2) * math.sin(dlng / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return round(distance, 2)

    @staticmethod
    def calculate_delivery_cost(distance_km):
        """
        Calculates delivery cost based on distance.
        Base fee: 500
        Per km: 100
        """
        base_fee = 500.00
        per_km_rate = 100.00
        
        cost = base_fee + (distance_km * per_km_rate)
        return round(cost, 2)
