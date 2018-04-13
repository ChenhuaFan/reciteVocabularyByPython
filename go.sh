# init
dir=$(pwd)
wl="/wordlist/"
ws="/wordSound/"

cd $dir

if [ ! -d $wl ];then
pwd
mkdir /wordList
elif [ ! -d $ws ];then
pwd
mkdir /wordSound
else
python app.py
fi