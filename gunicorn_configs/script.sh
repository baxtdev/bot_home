ln -s /var/www/bot_home/gunicorn_configs/telegram_bot_1.service /etc/systemd/system/
ln -s /var/www/bot_home/gunicorn_configs/telegram_bot_2.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl start telegram_bot_1
sudo systemctl enable telegram_bot_1
sudo systemctl start telegram_bot_2
sudo systemctl enable telegram_bot_2