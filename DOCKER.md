### Additional Steps and Notes

#### Calculating Physical Cores

You need to calculate `NUM_PHYSICAL_CORES` to set `OMP_NUM_THREADS` and `TENSORFLOW_INTRA_OP_PARALLELISM`. You can pass it as an environment variable when running `docker-compose` by setting NUM_PHYSICAL_CORES=<cores> in .env file:

```bash
$(($(lscpu | grep "Core(s) per socket:" | awk '{print $4}') * $(lscpu | grep "Socket(s):" | awk '{print $2}')))
```

Alternatively, you can run the docker_run.sh

```bash
source docker_run.sh
```

#### Adjusting Environment Variables

- In the `app` service, make sure to set the correct environment variables depending on whether you want to use MongoDB or PostgreSQL.
- Comment out the unused database service in the `depends_on` section if you're only using one database.

#### `model_config.config`

Ensure that you have a `model_config.config` file in the `./tmp/model` directory with the appropriate content to configure TensorFlow Serving. An example `model_config.config`:

```protobuf
model_config_list: {
  config: {
    name: 'rfcn'
    base_path: '/models/rfcn'
    model_platform: 'tensorflow'
  }
}
```

---

### Running the Containers

1. **Build and start the services:**

   ```bash
   docker-compose up --build
   ```

2. **Start services in the background:**

   ```bash
   docker-compose up -d
   ```

3. **Stopping services:**

   ```bash
   docker-compose down
   ```

---


### Cleanup Commands

To ensure a clean setup, you can add a `clean.sh` script to automate the cleanup process:

```bash
#!/bin/bash

sudo docker-compose down --volumes --remove-orphans
sudo docker rm -f tfserving test-mongo test-postgres object-counter-app mongo-db object-counter-postgres
sudo docker rmi -f object-counter-app postgres:latest mongo:latest
```

Make sure to make the script executable:

```bash
chmod +x clean.sh
```

---

### Notes

- **Model Files:** The model files are included in the Docker image built from the `Dockerfile`. This allows TensorFlow Serving to access the model directly.
- **Database Choice:** Since only one database should be active at a time, ensure that you comment out the unused database service and related environment variables in the `docker-compose.yml`.
- **Environment Variables:** Adjust the environment variables in the `docker-compose.yml` and `Dockerfile` as needed for your specific setup.
- **Ports:** Exposed ports can be adjusted if there are conflicts or specific requirements.

---
