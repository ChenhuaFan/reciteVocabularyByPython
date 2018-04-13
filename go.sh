# init
dir=$(pwd)
wl="/wordlist/"
ws="/wordSound/"

cd $dir

if [ ! -d $dir$wl ];then
mkdir $dir$wl
elif [ ! -d $dir$ws ];then
mkdir $dir$ws
else
python app.py
fi