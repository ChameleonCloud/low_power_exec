# image: low_power_exec
# Python script to collect power usage (in wattage) and temperature readings (in celsius) FROM low-power nodes in an HP Moonshot 1500 Chassis using iLO commands over SSH to the chassis controller.


FROM python:3.5.2
ADD requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
ADD ironic_ids.json /ironic_ids.json
ADD collect_readings.py /collect_readings.py

CMD ["python", "/collect_readings.py"]
