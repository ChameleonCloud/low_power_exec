# image: dell_exec
# Python script to collect power usage (in wattage) and temperature readings (in celsius) from Dell out of band controllers


FROM python:3.5.2
ADD dell_nodes.json /dell_nodes.json
ADD collect_dell_readings.py /collect_dell_readings.py

CMD ["python", "/collect_dell_readings.py"]
