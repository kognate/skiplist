# Deviations from Solution

The database is loaded using a python script. This script uploads the images to
S3, draws the boxes, and reformats the supplied json to make it easier
to work with given the front end.  This makes the node/express server really
simple.

This was done because, quite frankly, image manipulation in Python is
much easier to do.  It also maps closer to how I would handle these
kinds of problems.  Serving the images from S3 is cleaner and easier
than serving them from one of the other containers. It also opens the
door for a CDN to serve the images should there be a lot of them.

# To Run The System

You'll need to set the following environment variables:

```
export AWS_SECRET_ACCESS_KEY=<YOUR AWS SECRET KEY>
export AWS_ACCESS_KEY_ID=<YOUR AWS ACCESS KEY>
```

These are needed to setup the S3 bucket.  The bucket name is specified in
the env var `S3_BUCKET`

The mongodb config is specified by the following three env vars:

```
export MONGO_USERNAME=<sets the admin username for the mongodb>
export MONGO_PASSWORD=<sets the password to use for mongodb>
export MONGO_DB_NAME=<sets the database to use>
```

After setting these env vars, you can run

```
$ make run
```

in the base directory. This will build the docker containers, import the
image data from the file `data.json` and start the containers.  When this
completes you can point your web browser to http://localhost:8888/

and you should see the React Application displaying the application and it
should look something like this:

![screenshot][skiplist.png]



