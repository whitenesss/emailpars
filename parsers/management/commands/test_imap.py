from imapclient import IMAPClient



def test_imap_connection(email, password):
    try:
        with IMAPClient('imap.yandex.ru') as server:
            server.login(email, password)
            server.select_folder('INBOX')
            print("Successfully connected and logged in!")
            response = server.search(['ALL'])
            print(f"Number of messages: {len(response)}")
    except Exception as e:
        print(f"An error occurred: {e}")



test_imap_connection('purenkov.alex@yandex.ru', 'jcyhmvakfgrfmwrm')
