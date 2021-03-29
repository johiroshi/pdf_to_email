import os, sys
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import pyocr
import pyocr.builders
import re
import smtplib
import email
from email.mime.text import MIMEText
from email.utils import formatdate
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from os.path import basename
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import time
import datetime

path_tesseract = "C:\\Program Files\\Tesseract-OCR"
poppler_dir = Path(__file__).parent.absolute() / "poppler-0.67.0/bin"
MAIL_ADDRESS = "youraddress@gmail.com"
PASSWORD = "password"
from_address = MAIL_ADDRESS
to_address = "info@company.co.jp"
wdDirectory = '\\\\SHARED-FOLDER\\fax'

# poppler/binを環境変数PATHに追加する
os.environ["PATH"] += os.pathsep + str(poppler_dir)

class ChangeHandler(FileSystemEventHandler):

    # 作成された時のイベント
    def on_created(self, event):
        file_path = event.src_path
        print(datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S') + "：新しいファイルを検出しました。")
        print("パス： " + file_path)
        file_name = os.path.basename(file_path)
        root, ext = os.path.splitext(file_path)
        if ext == ".pdf":
            print("PDFファイルです。OCR処理を開始します")
            converPDFAndSendEMail(file_path)
        else:
            print("PDFではありません。")

def converPDFAndSendEMail(pdf_file_path):
    pdf_path = Path(pdf_file_path)

    # PDF -> Image に変換（150dpi）
    pages = convert_from_path(str(pdf_path), 150)

    # 画像ファイルを１ページずつ保存
    image_dir = Path(wdDirectory + "\\pdf_to_email\\img")
    for i, page in enumerate(pages):
        file_name = pdf_path.stem + "_{:02d}".format(i + 1) + ".png"
        image_path = image_dir / file_name
        page.save(str(image_path), "PNG")

    if path_tesseract not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"] += os.pathsep + path_tesseract

    # OCRエンジンの取得
    tools = pyocr.get_available_tools()
    tool = tools[0]

    img_org = Image.open(image_path)

    # ＯＣＲ実行
    builder = pyocr.builders.TextBuilder()
    result = tool.image_to_string(img_org, lang="jpn", builder=builder)
    result = re.sub(r"\n+", "", result)
    result = re.sub('([あ-んア-ン一-龥ー、。]) +((?=[あ-んア-ン一-龥ー、。]))',
          r'\1\2', result)

    type = "注文書" if len(re.findall('注文書|発注書|注文申し上げます', result)) > 0 else "不明"
    type = "見積書" if len(re.findall('見積', result)) > 0 else "不明"

    print("種類： " + type)

    sender = "不明"
    if len(re.findall('会社名1|会社名2|会社名3', result)) > 0:
        if len(re.findall('会社名1', result)) > 0:
            sender = "会社名1"
        elif len(re.findall('会社名2', result)) > 0:
            sender = "会社名2"
        elif len(re.findall('会社名3', result)) > 0:
            sender = "会社名3"

    print("送信元： " + sender)

    smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.ehlo()
    smtpobj.login(MAIL_ADDRESS, PASSWORD)

    body_msg = "送信元：" + sender + "\n種類：" + type + "\nファイル名：" + basename(pdf_file_path) + "\nOCRによるテキスト全文：\n\n" + result

    msg = MIMEMultipart()
    msg['Subject'] = "Faxを受信しました（" + type + "）"
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Date'] = formatdate()
    msg.attach(MIMEText(body_msg))
    msg.preamble = 'Failed jobs list. Please see attachment'

    fp = open(pdf_file_path,'rb')
    att = email.mime.application.MIMEApplication(fp.read(),_subtype="pdf")
    fp.close()
    att.add_header('Content-Disposition','attachment',filename=basename(pdf_file_path))
    msg.attach(att)

    smtpobj.sendmail(from_address, to_address, msg.as_string())
    smtpobj.close()
    print(datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S') + "：" + to_address + " へのメール送信を完了しました。")

observer = Observer()
observer.schedule(ChangeHandler(), wdDirectory, recursive=False)
observer.start()

print("Faxフォルダの監視を開始しました")
print("Watching " + wdDirectory)

while True:
    time.sleep(5)
