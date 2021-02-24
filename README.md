# pdf_to_email
ネットワークフォルダに保存されたPDF(複合機が受信したFAX)をOCRを使ってメール送信する

## How to install on Windows 10

24時間稼働するWindows10に以下をインストールする。
- Python3
- [Tesseract (64bit)](https://github.com/UB-Mannheim/tesseract/wiki)
- [Poppler](http://blog.alivate.com.au/poppler-windows/)

この記事を執筆時点のPopplerの最新バージョンは0.68.0だがうまく動作しなかったので、サンプルコードでは0.67.0を使用している。

Pythonのインストールを終えたら、コマンドプロンプトで以下をインストールする。
```
python -m pip install pdf2image
python -m pip install pyocr
python -m pip install watchdog
```

Pythonスクリプトとpoppler-0.xx.0フォルダ、imgフォルダを同じ階層に置く。
