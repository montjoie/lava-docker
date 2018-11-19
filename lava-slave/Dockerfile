FROM baylibre/lava-slave-base:latest

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install cu conmux

COPY configs/lava-slave /etc/lava-dispatcher/lava-slave

COPY configs/tftpd-hpa /etc/default/tftpd-hpa

COPY scripts/ /usr/local/bin/
RUN chmod a+x /usr/local/bin/*
COPY conmux/ /etc/conmux/

# Caution to not use any port between the Linux dynamic port range: 32768-60999
RUN find /usr/lib/python3/dist-packages/ -iname constants.py | xargs sed -i 's,XNBD_PORT_RANGE_MIN.*,XNBD_PORT_RANGE_MIN=61950,'
RUN find /usr/lib/python3/dist-packages/ -iname constants.py | xargs sed -i 's,XNBD_PORT_RANGE_MAX.*,XNBD_PORT_RANGE_MAX=62000,'

#conmux need cu >= 1.07-24 See https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=336996
RUN echo "deb http://deb.debian.org/debian/ testing main" >> /etc/apt/sources.list.d/testing.list
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install cu
RUN rm /etc/apt/sources.list.d/testing.list

RUN apt-get -y install ser2net
COPY ser2net.conf /etc

# ser2net > 3.2 is only availlable from sid
RUN echo "deb http://deb.debian.org/debian/ sid main" >> /etc/apt/sources.list.d/sid.list
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install ser2net
RUN rm /etc/apt/sources.list.d/sid.list
RUN apt-get update

RUN apt-get -y install lavacli

COPY phyhostname /root/
COPY scripts/setup.sh .

COPY lava-patch/ /root/lava-patch
RUN cd /usr/lib/python3/dist-packages && for patch in $(ls /root/lava-patch/*patch) ; do patch -p1 < $patch || exit $?;done

COPY devices/ /root/devices/
COPY tags/ /root/tags/
COPY deviceinfo/ /root/deviceinfo/

RUN if [ -x /usr/local/bin/extra_actions ] ; then /usr/local/bin/extra_actions ; fi

RUN apt-get -y install screen openssh-server
RUN ssh-keygen -q -f /root/.ssh/id_rsa
RUN cat /root/.ssh/id_rsa.pub > /root/.ssh/authorized_keys
COPY lava-screen.conf /root/

COPY zmq_auth/ /etc/lava-dispatcher/certificates.d/

RUN git clone https://github.com/montjoie/NRC.git
RUN cp NRC/powerman.sh /usr/local/bin
RUN chmod 755 /usr/local/bin/powerman.sh
RUN cp NRC/ci-client.py /usr/local/bin
RUN chmod 755 /usr/local/bin/ci-client.py
COPY nrc.cfg /usr/local/bin

RUN git clone https://github.com/baylibre-acme/acme-cli.git /root/acme-cli
RUN cp /root/acme-cli/acme-cli /usr/local/bin
RUN chmod 755 /usr/local/bin/acme-cli

RUN git clone https://github.com/ondrej1024/crelay.git
RUN apt-get -y install build-essential libusb-1.0-0-dev libhidapi-dev libftdi-dev
RUN cd crelay/src && make && cp crelay /usr/bin/ && chmod +x /usr/bin/crelay
COPY scripts/crelay_power /usr/bin/
RUN chmod +x /usr/bin/crelay_power

# install custom ser2net
RUN wget https://download.sourceforge.net/ser2net/ser2net-3.5.tar.gz
RUN tar xzf ser2net-3.5.tar.gz
COPY ser2net.patch /root/
RUN cd ser2net-3.5 && patch -p1 < /root/ser2net.patch && ./configure && make && cp ser2net /usr/sbin/

RUN apt-get -y install python-pip python-cffi
COPY brainstem /brainstem
RUN chmod 755 /brainstem/install.sh
RUN /brainstem/install.sh

COPY cambrionix cbrxd-arm-0.11.0b742.tar.gz /cambrionix/
RUN cd /cambrionix/ && tar xzf cbrxd-arm-0.11.0b742.tar.gz && ls -l

EXPOSE 69/udp 80

CMD /start.sh
