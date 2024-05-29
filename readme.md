python -m venv venv
pip install -r requirements.txt


cd .\Python_BlumClicker\
mitmproxy -s proxy.py
python main.py


mitmproxy
Manual Installation
Double-click the P12 file to start the import wizard.
Select a certificate store location. This determines who will trust the certificate – only the current Windows user or everyone on the machine. Click Next.
Click Next again.
Leave Password blank and click Next.
Select Place all certificates in the following store, then click Browse, and select Trusted Root Certification Authorities.
Click OK and Next.
Click Finish.
Click Yes to confirm the warning dialog.