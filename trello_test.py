import os
from dotenv import load_dotenv
from app.trello_client import TrelloClient

if __name__ == '__main__':
    # Load .env file
    load_dotenv()
    
    key = os.getenv('TRELLO_KEY')
    token = os.getenv('TRELLO_TOKEN')
    list_id = os.getenv('TRELLO_LIST_ID')
    print('TRELLO_KEY set:', bool(key))
    print('TRELLO_TOKEN set:', bool(token))
    print('TRELLO_LIST_ID set:', bool(list_id))
    tc = TrelloClient()
    if not (tc.key and tc.token and tc.list_id):
        print('Missing Trello configuration. Set TRELLO_KEY, TRELLO_TOKEN, TRELLO_LIST_ID and try again.')
        raise SystemExit(1)
    card = tc.create_card('Test card from req-knowledge-tracker', 'This is a test card created by automated test.')
    print('create_card response:', card)
    cid = card.get('id') if isinstance(card, dict) else None
    if cid:
        # create a small temp file and attach
        path = 'trello_test_attachment.txt'
        with open(path, 'w') as f:
            f.write('Attachment from test')
        attach = tc.attach_file(card_id=cid, file_path=path)
        print('attach response:', attach)
    else:
        print('No card id returned; cannot attach files.')
