#!/usr/bin/env python3.7

import requests, urllib3

def main():
    dc_post = dict()

    # dc_post['rfid'] = ''
    # dc_post['ruid'] = '8mJMTmQFfsh6QAY7sb8wI0RW7yPKKp7A' # phantom 4

    dc_post['rfid'] = '6360215e'
    dc_post['ruid'] = 't8LagYA0UknEIvSy3QMDPm0G1lOpraws' # lab

    # dc_post['rfid'] = '021170dc'
    # dc_post['ruid'] = 'OWdHNFsllhXBpMR4gf2souKdr4FmGfB8' # phantom 3

    # dc_post['rfid'] = ''
    # dc_post['ruid'] = 'gRfm0oIwpwOeHKyxPqYNIR9Ak1D5BIbs'

    clnt = requests.session()
    try:
        resp = clnt.get('http://127.0.0.1:8000/smartlock/unlock')
        dc_post['csrfmiddlewaretoken'] = clnt.cookies['csrftoken']
        resp = clnt.post('http://127.0.0.1:8000/smartlock/unlock',
                         headers=dict(Referer='http://127.0.0.1:8000/smartlock/unlock'),
                         data=dc_post)
        print(resp)
        print(resp.content[-1000:])
        with open('/tmp/resp.html', 'wb') as fout:
            fout.write(resp.content)
    except (urllib3.exceptions.NewConnectionError, requests.exceptions.ConnectionError) as ex:
        print('→ Exception:', ex)


if __name__ == '__main__':
    main()
