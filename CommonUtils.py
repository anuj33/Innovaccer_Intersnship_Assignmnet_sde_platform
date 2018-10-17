import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pymysql
import config


class CommonUtils:

    db_handle = pymysql.connect(host=config.db_cred.get("host"), user=config.db_cred.get("username"), passwd=config.db_cred.get("password"), db=config.db_cred.get("db_name"),
                             cursorclass=pymysql.cursors.DictCursor)
    @staticmethod
    def send_email( to_addr_list,subject, message,smtpserver='smtp.gmail.com'):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        html = "<html><body>{}</body></html>".format(message)
        part2 = MIMEText(html, 'html')
        msg.attach(part2)
        s = smtplib.SMTP_SSL(smtpserver)
        s.login(config.smtp_server.get("username"), config.smtp_server.get("password"))
        s.sendmail(config.smtp_server.get("from_address"), to_addr_list, msg.as_string())
        s.quit()

    @staticmethod
    def insert_data_in_mysql(email_address, tv_series_list):
        try:
            with CommonUtils.db_handle.cursor() as cursor:
                sql = "INSERT INTO `user_tv_series_info` (`mail_id`, `preferred_tv_series`) VALUES ('{}', '{}')".format(email_address,  json.dumps(tv_series_list))
                cursor.execute(sql)
                CommonUtils.db_handle.commit()
        finally:
            pass