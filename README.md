# Build docker container
sudo docker build -t chatroom-cont .
# Run container
sudo docker run -p 5000:5000 -e FLASK_APP=chatroom -e FLASK_ENV=development chatroom-cont:latest
