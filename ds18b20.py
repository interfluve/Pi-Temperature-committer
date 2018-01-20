import os
import time

class DS18B20:

    def temperature(self):
        for i in range(0, 3):
            with open(os.environ.get("SENSOR_PATH")) as f:
                lines = f.read().splitlines()

            # If the first line does not end with 'YES', try again.
            if lines[0][-3:] != 'YES':
                time.sleep(0.2)
                continue

            # If the second line does not have a 't=', try again.
            pos = lines[1].find('t=')
            if pos < 0:
                time.sleep(0.2)
                continue

            return float(lines[1][pos + 2:]) / 1000.0

        return None