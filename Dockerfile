FROM python:3.11.5

ENV HOME /root
WORKDIR /Users/thoaria/Desktop/プログラミング/WebAppProject

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python server.py