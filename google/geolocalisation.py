import googlemaps

class Geolocalisation:
    # https://developers.google.com/maps/gmp-get-started?authuser=1
    # https://console.cloud.google.com/google/maps-apis/overview?onboard=true&project=genealogyofmypho-1551225532925&authuser=1&consoleReturnUrl=https:%2F%2Fcloud.google.com%2Fmaps-platform%2F%3Fapis%3Dmaps%26project%3Dgenealogyofmypho-1551225532925&consoleUI=CLOUD

    __country = ''
    __administrative_area_level_1 = ''
    __administrative_area_level_2 = ''
    __locality = ''
    __route = ''
    __street_number = ''
    __postal_code = ''


    def __init__(self,googleMap,longitude,latitude):
        self.__googlemap = googleMap
        self.__longitude = longitude
        self.__latitude = latitude

    def __str__(self):
        self.__extractLocation()
        #return self.country+',\n'+self.administrative_area_level_1+',\n'+self.administrative_area_level_2+',\n'+self.locality+',\n'+self.street_number+'\n'+self.route+',\n'+self.postal_code
        return self.__country+',\n'+self.__locality+',\n'+self.__street_number+'\n'+self.__route+',\n'+self.__postal_code

    def __getLocation(f):
        def wrapper(*args):
            args[0].__extractLocation()
            return f(*args)

        return wrapper

    @__getLocation
    def country(self):
        return self.__country

    @__getLocation
    def locality(self):
        return self.__locality

    @__getLocation
    def street_number(self):
        return self.__street_number

    @__getLocation
    def route(self):
        return self.__route

    @__getLocation
    def postal_code(self):
        return self.__postal_code

    def __extractLocation(self):
        if(len(self.__country)>0):
            return
        address = self.__googlemap.reverse_geocode((self.__longitude, self.__latitude))
        for info in address:
            for detail in info['address_components']:

                if('country' in detail['types']):
                    self.__country = detail['long_name']

                if('administrative_area_level_1' in detail['types']):
                    if(len(self.__administrative_area_level_1) > len(detail['long_name']) or len(self.__administrative_area_level_1)==0):
                        self.__administrative_area_level_1 = detail['long_name']

                if('administrative_area_level_2' in detail['types']):
                    if(len(self.__administrative_area_level_2) > len(detail['long_name']) or len(self.__administrative_area_level_2)==0):
                        self.__administrative_area_level_2 = detail['long_name']

                if('locality' in detail['types']):
                    self.__locality = detail['long_name']


                if 'street_number' in detail['types']:
                    self.__street_number = detail['long_name']

                if 'route' in detail['types']:
                    self.__route = detail['long_name']

                if 'postal_code' in detail['types']:
                    if len(self.__postal_code) < len(detail['long_name']):
                        self.__postal_code =  detail['long_name']