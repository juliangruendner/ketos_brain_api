pip3 install -r requirements.txt
chmod +x wait-for-it.sh
./wait-for-it.sh db:5432 --timeout=0
# python3 mlServiceAPI.py
sudo uwsgi --ini mlServiceApi-uwsgi.ini
# uwsgi --http 0.0.0.0:5000 --processes 4 --threads 4 --mount /root/src=mlServiceAPI:app --manage-script-name --wsgi-file mlServiceAPI.py --callable app --master --plugin python3