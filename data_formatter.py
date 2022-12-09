import os
import json
import socket
from urllib.request import urlopen
import requests

def format_json(file):
    counter, modified = 0, list()
    with open(file) as f:
        with open(file.replace('.json', '') + '_formatted.json', 'w') as ff:
            ff.write('{\n')
            for line in f.readlines():
                if line == '{\n':
                    for mod_line in modified:
                        ff.write(mod_line)
                    counter += 1
                    modified = ['\t"' + str(counter) + '" : {\n']
                    continue
                if line == '}\n':
                    modified.append('\t},\n')
                    continue
                modified.append('\t' + line.replace('ObjectId', '').replace('(', '').replace(')', '').replace('NumberInt', ''))
            ff.write('}')

def embed_origin_countries(filepath):
    with open(filepath, 'r') as f:
        with open(filepath.replace('.json', '') + '_embedded_ips.json', 'w') as ff:
            for line in f.readlines():
                try:
                    if ('.net' in line or '.org' in line or '.io' in line or '.co' in line or '.us' in line) and 'URL Does Not Exist' not in line:
                        ip = socket.gethostbyname(line.split('"')[1])
                        response = requests.get(f'https://ipinfo.io/{ip}?token=ad53a847fa5420').json()
                        location_data = {
                            "ip": ip,
                            "city": response.get("city"),
                            "region": response.get("region"),
                            "country": response.get("country"),
                            "timezone": response.get("timezone"),
                            "loc": response.get("loc"),
                            "postal": response.get("postal")
                        }
                        ff.write(line)
                        for key, value in location_data.items():
                            ff.write('\t\t\t\t"' + str(key) + '" : "' + str(value) + '",\n')
                    else:
                        ff.write(line)
                except Exception as e:
                    print(str(e))
                    ff.write(line)
                    # if 'http://' not in line.split('"')[1] or 'https://' not in line.split('"')[1]:
                    #     response = urlopen('http://' + line.split('"')[1])
                    # else:
                    #     response = urlopen('http://' + line.split('"')[1])

                    

if __name__ == '__main__':
    # files = os.listdir('db_dumps')
    # for file in files:
    #     if 'formatted' not in file and '.bson' not in file and 'metadata' not in file and file != '.DS_Store':
    #         format_json('db_dumps/' + file)
    embed_origin_countries('db_dumps/virus_total_results_formatted.json')
