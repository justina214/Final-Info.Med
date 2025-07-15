from fhir.resources.location import Location
from fhir.resources.address import Address

def create_location_resource(nombre, comuna):
    location = Location()
    location.name = nombre
    location.address = Address()
    location.address.city = "Ciudad Autónoma de Buenos Aires"
    location.address.district = f"Comuna {comuna}"
    location.address.country = "Argentina"
    return location
