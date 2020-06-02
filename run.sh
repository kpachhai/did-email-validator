#!/usr/bin/env bash

function start () {
    docker container stop vouch-mongo || true && docker container rm -f vouch-mongo || true
    docker run -d --name assist-mongo                     \
        -e MONGO_INITDB_ROOT_USERNAME=mongoadmin          \
        -e MONGO_INITDB_ROOT_PASSWORD=vouchmongo         \
        -p 27018:27017                                      \
        mongo

    virtualenv -p `which python3` .venv
    source .venv/bin/activate
    pip install --upgrade pip

    case `uname` in
    Linux )
        pip install -r requirements.txt
        ;;
    Darwin )
        pip install --global-option=build_ext --global-option="-I/usr/local/include" --global-option="-L/usr/local/lib" -r requirements.txt
        ;;
    *)
    exit 1
    ;;
    esac

    gunicorn -b 0.0.0.0:8000 --reload app.main:application
}

function stop () {
    docker container stop vouch-mongo || true && docker container rm -f vouch-mongo || true
    ps -ef | grep gunicorn | awk '{print $2}' | xargs kill -9
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    *)
    echo "Usage: run.sh {start|stop}"
    exit 1
esac