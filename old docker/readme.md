# docker_homework Проверять только на том же хосте где запушены все контейнеры.
# 1 Лекция команды:
docker build -t front:v1 .
docker run -p 80:80 -d ID
# 2 Лекция команды :
# создание образов
docker build -f Dockerfile.front -t front .
docker build -f Dockerfile.bd -t database .
docker build -f Dockerfile.back -t back .

#    Запуск образов
#  Обратите внимание что все докеры и композ имеют переменные  в env.list и запускаются с применением файла переменных.
 
docker network create backend

docker run --network=backend --name database \
--env-file ./env.list -d database

docker run --name back -p 8081:8081 \
--env-file ./env.list  -d back

docker run --network=backend --name front -it --env-file ./env.list \
-p 80:80 -d front

# 3 Лекция
docker-compose up -d

# Вспомогательные при дебаге

docker image rm $(docker images -a -q)
docker stop id
docker rm id id id
docket ps
docker images
docker exec -it id sh
docker logs id
docker inspect id
docker port id
systemctl start docker
docker rmi -f id
docker image rmi -f id
docker-compose up -d
netstat -ntlp
apt install net-tools