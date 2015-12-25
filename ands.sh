#!/usr/bin/env bash
python=/home/milan/venv/ands/bin/python
appengine=/home/milan/google_appengine
work=/home/milan/work

usage()
{
    echo 'usage: ./ands.sh options:<d|u>'
    echo 'Use -d for development server, -u for deployment'
}

update=0

while getopts 'du' opt
do
    case $opt in
        d)
            ;;
        u)
            update=1
            ;;
        *)
            usage
            exit 1
    esac
done

if [ $update -ne 0 ]; then
    echo 'Deploy to Google'
    # exec $python $appengine/appcfg.py update .
else
    echo 'Running development server'
    exec $python $appengine/dev_appserver.py --host 127.0.0.1 --storage_path=$work/andsnews_storage/ .
