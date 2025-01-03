cd ../
sudo docker run --name test-mongo --rm -p 27017:27017 -d mongo:latest

sudo docker run --name test-postgres \
        --rm -p 5432:5432 \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=OBJ_COUNT \
        -v postgres:/var/lib/postgresql/data \
        -d postgres:latest