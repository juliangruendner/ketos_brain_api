pip3 install -r requirements.txt
chmod +x wait-for-it.sh
./wait-for-it.sh db:5432
python3 dockerAPI.py