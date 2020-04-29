import unittest
import sys
from sqlalchemy import false

# pip3 install google-api-python-client-py3


from unittest import TestCase

class test_google_photo(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_getPeoples(self):
        from os.path import join, dirname

        from googleapiclient.discovery import build
        from httplib2 import Http
        from oauth2client import file, client, tools
        SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'

        store = file.Storage(join(dirname(__file__), 'token-for-google.json'))
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(join(dirname(__file__), 'client_id.json', SCOPES))
            creds = tools.run_flow(flow, store)
        google_photos = build('photoslibrary', 'v1', http=creds.authorize(Http()))

        day, month, year = ('0', '6', '2019')  # Day or month may be 0 => full month resp. year
        date_filter = [{"day": day, "month": month, "year": year}]  # No leading zeroes for day an month!
        nextpagetoken = 'Dummy'
        while nextpagetoken != '':
            nextpagetoken = '' if nextpagetoken == 'Dummy' else nextpagetoken
            results = google_photos.mediaItems().search(
                body={"filters": {"dateFilter": {"dates": [{"day": day, "month": month, "year": year}]}},
                      "pageSize": 10, "pageToken": nextpagetoken}).execute()
            # The default number of media items to return at a time is 25. The maximum pageSize is 100.
            items = results.get('mediaItems', [])
            nextpagetoken = results.get('nextPageToken', '')
            for item in items:
                print(f"{item['filename']} {item['mimeType']} '{item.get('description', '- -')}'"
                      f" {item['mediaMetadata']['creationTime']}\nURL: {item['productUrl']}")



    def test_list_albums(self):
        #from __future__ import print_function
        from apiclient.discovery import build
        from httplib2 import Http
        from oauth2client import file, client, tools

        # Setup the Photo v1 API
        SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'

        # see https://console.cloud.google.com/apis/credentials?pli=1 to generate credentials.json file
        store = file.Storage('credentials.json')
        print(store)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            # flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('photoslibrary', 'v1', http=creds.authorize(Http()))

        # Call the Photo v1 API
        results = service.albums().list(
            pageSize=10, fields="nextPageToken,albums(id,title)").execute()
        items = results.get('albums', [])
        if not items:
            print('No albums found.')
        else:
            print('Albums:')
            for item in items:
                print('{0} ({1})'.format(item['title'].encode('utf8'), item['id']))