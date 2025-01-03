sudo docker-compose down --volumes --remove-orphans
sudo docker rm -f tfserving test-mongo test-postgres object-counter-app mongo-db object-counter-postgres
sudo docker rmi -f object-counter-app postgres:latest mongo:latest