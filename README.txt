Server Scripts by beni in 18/19

Install this stuff  for the display:

python or python 3

sudo apt-get install python-pip python3-pip
sudo apt-get install libjpeg-dev

pip install spidev
pip install pillow

git clone "myself" :)

sudo apt-get install screen

###################################
Update script

Edit crontab:
sudo crontab -e

Add update script there at the end:
30 9 * * * myscript.sh

