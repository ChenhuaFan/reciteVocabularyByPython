# init
$dir=pwd
$wl="/wordlist/"
$ws="/wordSound/"

if [ ! -d $dir$wl ];then
mkdir /wordlist
elif [ ! -d $dir$ws ];then
mkdir /wordSound
else
python app.py
fi