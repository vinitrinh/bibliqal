# update server
apt-get update && apt-get upgrade

# installing docker
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update
apt-cache policy docker-ce
sudo apt install docker-ce

# get to project dir
cd Home
cd bibliqal

# run app on docker
docker build . vinitrinh/bibliqal
docker run -it -p 5000:5000 <image name>