from google.geolocalisation import Geolocalisation, googlemaps

def test_geolocalisation():
    #todo put api key in configuration
    gmaps = googlemaps.Client(key='AIzaSyD6W9Nf4DGnMDT4mxw_BhqRlj-LLtQzk0U')
    localisation = Geolocalisation(gmaps,45.444522, -73.2525112)
    assert localisation.country() == "Canada"
    assert localisation.locality() == "Richelieu"
    assert localisation.street_number() == "398-310"
    assert localisation.route() == "10e Av"
    assert localisation.postal_code() == "J3L 3P7"

    assert str(localisation) == "Canada,\nRichelieu,\n398-310\n10e Av,\nJ3L 3P7"

