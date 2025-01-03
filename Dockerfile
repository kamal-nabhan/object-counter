# Use an official Python runtime as a parent image  
FROM python:3.8-slim  
  
# Set the working directory in the container  
WORKDIR /app  
  
# Install wget and other required packages  
RUN apt-get update && apt-get install -y \  
    wget \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*  
  
# Copy the requirements file into the container  
COPY requirements.txt .  
  
# Install any needed packages specified in requirements.txt  
RUN pip install --no-cache-dir -r requirements.txt  
  
# Copy the rest of the application code  
COPY . .  
  
# Download and set up the TensorFlow model  
RUN mkdir -p /app/tmp/model/rfcn/1 && \  
    wget https://storage.googleapis.com/intel-optimized-tensorflow/models/v1_8/rfcn_resnet101_fp32_coco_pretrained_model.tar.gz && \  
    tar -xzvf rfcn_resnet101_fp32_coco_pretrained_model.tar.gz -C /app/tmp && \  
    rm rfcn_resnet101_fp32_coco_pretrained_model.tar.gz && \  
    chmod -R 777 /app/tmp/rfcn_resnet101_coco_2018_01_28 && \  
    mv /app/tmp/rfcn_resnet101_coco_2018_01_28/saved_model/saved_model.pb /app/tmp/model/rfcn/1 && \  
    rm -rf /app/tmp/rfcn_resnet101_coco_2018_01_28  
  
# Expose port (if needed)  
EXPOSE 5000  
  
# Set environment variables (adjust as needed)  
ENV ENV=prod  
ENV DATABASE=postgres  
ENV db_url=postgresql://postgres:postgres@postgres:5432/OBJ_COUNT  
  
# Command to run when the container starts  
CMD ["python", "-m", "counter.entrypoints.webapp"]  
