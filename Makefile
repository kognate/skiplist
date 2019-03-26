.PHONEY: start_mongo import_files run build all
all: run

build:
	docker build . -f Dockerfile-server -t puppy_server
	docker build . -f Dockerfile-client -t web
	docker build . -f Dockerfile-importer -t import_files
start_mongo: build
	docker run -d --rm --name mongodbserver -e MONGO_INITDB_ROOT_USERNAME=${MONGO_USERNAME} -e MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD} mongo
import_files: start_mongo
	aws s3 mb s3://${S3_BUCKET}
	aws s3 website s3://${S3_BUCKET} --index-document index.html --error-document error.html
	docker run -it --rm -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e S3_BUCKET=${S3_BUCKET} -e MONGO_DB_NAME=${MONGO_DB_NAME} -e MONGO_URL=mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@mongodbserver:27017 --link mongodbserver import_files
run: import_files
	docker run -d --name puppy_server --link mongodbserver -e PORT=8080 -e MONGO_URL=mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@mongodbserver:27017 -e MONGO_DB_NAME=${MONGO_DB_NAME} puppy_server
	docker run -d --link puppy_server -p 8888:80 web

