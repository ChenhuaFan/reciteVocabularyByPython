# init
dir=$(pwd)
wl="/wordList/"
ws="/wordSound/"

cd $dir

if [ ! -d $dir$wl ];then
mkdir $dir$wl
elif [ ! -d $dir$ws ];then
mkdir $dir$ws
fi
python app.py