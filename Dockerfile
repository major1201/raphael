FROM centos:7
LABEL name="raphael" \
    description="raphael image" \
    create-date="20180927" \
    modify-date="20181022"

RUN mkdir /opt/raphael
WORKDIR /opt/raphael
ADD . .
RUN yum install -y epel-release \
&& yum install -y python34 python34-devel python34-pip python34-crypto gcc \
&& pip3 install -r requirements.txt

EXPOSE 8000

CMD ["/usr/bin/python3", "/opt/raphael/wsgi.py"]
