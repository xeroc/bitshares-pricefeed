FROM python:3

WORKDIR /usr/src/app

COPY . .

RUN python3 setup.py install

VOLUME ["/conf", "/root/.local/share/bitshares"] 

CMD [ "/usr/local/bin/bitshares-pricefeed", "--configfile", "/config/config.yaml", "update" ]
