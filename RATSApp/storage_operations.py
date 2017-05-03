# storage_operations.py
# this is where we will put all the functions that interact with local storage and gdrive

#builtins
import pickle, os

#google drive
import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


def get_credentials(user_data_dir):
    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/drive-python-quickstart.json
    SCOPES = 'https://www.googleapis.com/auth/drive'
    CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'Drive API Python Quickstart'

    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(user_data_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')
    print(credential_path)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def import_config(path):
    if path is not None:
        file = open(path, u'rb')
        for line in file.readlines():
            key, value = line.split(u':')
            value = value.strip()
            if key == u'tournament':
                tournament = [key, value]
            elif key == u'time_cap':
                time_cap = [key, value]
            elif key == u'point_cap':
                point_cap = [key, value]
            elif key == u'timeouts':
                timeouts = [key, value]
            # elif key == u'divisions':
            #    divisions = value.split(u'|')
            #    tournament_divisions = ['tournament_divisions',divisions]
            else:
                pass
                # print(key,value)
        file.close()

        # tournament = hierarch.Tournament(tournament=tournament,
        #                                  point_cap=point_cap,
        #                                  time_cap=time_cap)

        tournament_data = [tournament, point_cap, time_cap, timeouts, ['year', 2017]]

        return tournament_data
    else:
        return None

def store_game_pickle(game,path):
    pickle.dump(game, open(path, 'wb'))
    #print('#saving_game# ' + path)


def retrieve_game_pickle(path):
    pass
    # return game


def upload_csv(path):
    pass


def read_tournament_config(path):
    pass
    # return tournament_data


def read_teamlist(path):
    # soon to be replaced with scrape
    pass
    # return teamlist