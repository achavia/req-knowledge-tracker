import requests
import time

time.sleep(2)
url = "http://127.0.0.1:8000/submit"
data = {
    "subject": "Project B Items 05/06/2026",
    "body": "RSS Page\n- Add status filter\n- Update export format\n\nAccommodation Page\n- Add dismiss button\n\nUser Management\n- Add lock account feature"
}
resp = requests.post(url, data=data)
print('status', resp.status_code)
print('location', resp.headers.get('location'))
print('text snippet:', resp.text[:400])
