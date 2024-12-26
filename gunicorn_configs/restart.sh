sudo systemctl daemon-reload
sudo systemctl restart gunicorn.socket gunicorn.service telegram_bot_1.service telegram_bot_2.service
sudo sudo nginx -t && sudo systemctl restart nginx