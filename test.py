

try:

    raise Exception('time to restart')
except Exception as ecc:
    if 'time to restart' in str(ecc):
        print(1)