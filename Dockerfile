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
COPY collectd.d/ /etc/collectd.d/
RUN mkdir /etc/collectd.d/enabled

COPY ironic_ids.json /ironic_ids.json
COPY collect_readings.py /collect_readings.py
COPY collect_corsa.py /collect_corsa.py
COPY collectd_wrapper.sh /collectd_wrapper.sh

ENTRYPOINT ["/collectd_wrapper.sh"]
