# Image: awbarnes/low_power_collectd
FROM centos:7

RUN adduser apim
RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm \
  && yum -y groupinstall development \
  && yum -y install \
    collectd \
    python \
    python-devel \
    python-pip \
  && yum clean all

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# checkout the gnocchi plugin
RUN pip install git+git://github.com/ChameleonCloud/collectd-gnocchi.git@moonshot-power

COPY collectd.conf /etc/collectd.conf

# exec script
COPY ironic_ids.json /ironic_ids.json
COPY collect_readings.py /collect_readings.py

ENTRYPOINT ["collectd", "-f"]
