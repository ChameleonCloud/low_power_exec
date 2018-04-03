# image: low_power_exec
# Python script to collect power usage (in wattage) from low-power nodes in an HP Moonshot 1500 Chassis using iLO commands over SSH to the chassis controller.


from python:3.5.2
add requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
add ironic_ids.json /ironic_ids.json
add collect_power.py /collect_power.py

CMD ["python", "/collect_power.py"]
