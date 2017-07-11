wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i --force-depends google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb
LATEST=$(wget -q -O - http://chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget http://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
rm chromedriver_linux64.zip
mkdir browser_driver
mv chromedriver browser_driver/
virtualenv env
source env/bin/activate
pip install -r requirements.txt
cd browser_driver
sudo ln -s $PWD/chromedriver /usr/local/bin/chromedriver
