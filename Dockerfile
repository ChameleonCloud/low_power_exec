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
RUN pip install -r /requirements.txt && rm -f /requirements.txt

COPY collectd.conf.j2 /collectd.conf.j2
COPY collectd_wrapper.sh /collectd_wrapper.sh
COPY collector /collector
RUN pip install /collector

ENTRYPOINT ["/collectd_wrapper.sh"]
