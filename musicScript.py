from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLineEdit, QProgressBar, QLabel, 
                            QFileDialog, QComboBox, QHBoxLayout, QCheckBox)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon
import sys
import os
import yt_dlp
import requests
import zipfile
import shutil
import platform

def ffmpeg_kur():
    try:
        # FFmpeg'in yüklü olup olmadığını kontrol et
        if shutil.which('ffmpeg'):
            return True
            
        print("FFmpeg kuruluyor...")
        sistem = platform.system().lower()
        
        if sistem == "windows":
            # FFmpeg indirme URL'i
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            zip_path = "ffmpeg.zip"
            
            # FFmpeg'i indir
            response = requests.get(ffmpeg_url, stream=True)
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Zip dosyasını çıkar
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("ffmpeg")
            
            # FFmpeg'i sistem yoluna ekle
            ffmpeg_path = os.path.abspath("ffmpeg/ffmpeg-master-latest-win64-gpl/bin")
            if ffmpeg_path not in os.environ['PATH']:
                os.environ['PATH'] += os.pathsep + ffmpeg_path
            
            # Geçici dosyaları temizle
            os.remove(zip_path)
            return True
            
        elif sistem == "linux":
            # Linux için otomatik kurulum
            os.system("sudo apt-get update && sudo apt-get install -y ffmpeg")
            return True
            
        elif sistem == "darwin":  # macOS
            # Homebrew ile kurulum
            os.system("brew install ffmpeg")
            return True
            
        return False
        
    except Exception as e:
        print(f"FFmpeg kurulumu sırasında hata: {str(e)}")
        return False

class IndirmeThread(QThread):
    ilerleme_sinyali = pyqtSignal(int)
    durum_sinyali = pyqtSignal(str)
    tamamlandi_sinyali = pyqtSignal(bool)
    toplam_dosya_sinyali = pyqtSignal(int)
    mevcut_dosya_sinyali = pyqtSignal(int)

    def __init__(self, url, hedef_klasor, format_type, is_playlist):
        super().__init__()
        self.url = url
        self.hedef_klasor = hedef_klasor
        self.format_type = format_type
        self.is_playlist = is_playlist

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            toplam_bytes = d.get('total_bytes', 0)
            indirilen_bytes = d.get('downloaded_bytes', 0)
            if toplam_bytes and indirilen_bytes:
                yuzde = int((indirilen_bytes / toplam_bytes) * 100)
                self.ilerleme_sinyali.emit(yuzde)

    def run(self):
        try:
            if not ffmpeg_kur():
                self.durum_sinyali.emit("FFmpeg kurulumu başarısız oldu!")
                self.tamamlandi_sinyali.emit(False)
                return

            if not os.path.exists(self.hedef_klasor):
                os.makedirs(self.hedef_klasor)

            format_ayarlari = {
                'MP3': {'format': 'bestaudio/best',
                       'postprocessors': [{
                           'key': 'FFmpegExtractAudio',
                           'preferredcodec': 'mp3',
                           'preferredquality': '192',
                       }]},
                'MP4': {'format': 'best'},
                'WAV': {'format': 'bestaudio/best',
                       'postprocessors': [{
                           'key': 'FFmpegExtractAudio',
                           'preferredcodec': 'wav',
                       }]},
                'M4A': {'format': 'bestaudio/best',
                       'postprocessors': [{
                           'key': 'FFmpegExtractAudio',
                           'preferredcodec': 'm4a',
                       }]},
            }

            secili_format = format_ayarlari[self.format_type]
            ydl_opts = {
                **secili_format,
                'progress_hooks': [self.progress_hook],
                'outtmpl': os.path.join(self.hedef_klasor, '%(title)s.%(ext)s'),
            }

            if self.is_playlist:
                self.durum_sinyali.emit("Playlist bilgileri alınıyor...")
                with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
                    playlist_info = ydl.extract_info(self.url, download=False)
                    toplam_video = len(playlist_info['entries'])
                    self.toplam_dosya_sinyali.emit(toplam_video)

            self.durum_sinyali.emit("İndirme başlıyor...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.is_playlist:
                    playlist_info = ydl.extract_info(self.url, download=True)
                    for i, entry in enumerate(playlist_info['entries'], 1):
                        self.mevcut_dosya_sinyali.emit(i)
                else:
                    ydl.download([self.url])

            self.durum_sinyali.emit("İndirme tamamlandı!")
            self.tamamlandi_sinyali.emit(True)

        except Exception as e:
            self.durum_sinyali.emit(f"Hata oluştu: {str(e)}")
            self.tamamlandi_sinyali.emit(False)

class MuzikIndirici(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Müzik İndirici")
        self.setGeometry(100, 100, 800, 300)
        
        # Ana düzeni tanımla
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)  # layout değişkenini tanımla
        
        # URL girişi
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("YouTube müzik/playlist linkini yapıştırın")
        layout.addWidget(self.url_input)
        
        # Format seçimi ve playlist checkbox'ı için yatay düzen
        format_layout = QHBoxLayout()
        
        # Format seçimi
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP3", "MP4", "WAV", "M4A"])
        format_layout.addWidget(QLabel("Format:"))
        format_layout.addWidget(self.format_combo)
        
        # Playlist checkbox'ı
        self.playlist_check = QCheckBox("Playlist")
        format_layout.addWidget(self.playlist_check)
        
        layout.addLayout(format_layout)
        
        # Konum seçimi
        konum_layout = QHBoxLayout()
        self.konum_label = QLabel("İndirme Konumu:")
        self.konum_input = QLineEdit()
        self.konum_input.setText(os.path.join(os.path.expanduser("~"), "Downloads"))
        self.konum_button = QPushButton("Gözat")
        self.konum_button.clicked.connect(self.konum_sec)
        
        konum_layout.addWidget(self.konum_label)
        konum_layout.addWidget(self.konum_input)
        konum_layout.addWidget(self.konum_button)
        layout.addLayout(konum_layout)
        
        # İndirme butonu
        self.indir_button = QPushButton("İndir")
        self.indir_button.clicked.connect(self.indirmeyi_baslat)
        layout.addWidget(self.indir_button)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Playlist ilerleme çubuğu
        self.playlist_progress = QProgressBar()
        self.playlist_progress.setVisible(False)
        layout.addWidget(self.playlist_progress)
        
        # Durum etiketi
        self.durum_label = QLabel("Hazır")
        layout.addWidget(self.durum_label)

    def konum_sec(self):
        konum = QFileDialog.getExistingDirectory(self, "İndirme Konumu Seç")
        if konum:
            self.konum_input.setText(konum)

    def indirmeyi_baslat(self):
        url = self.url_input.text()
        if not url:
            self.durum_label.setText("Lütfen bir URL girin!")
            return
        
        self.indir_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.playlist_progress.setValue(0)
        self.playlist_progress.setVisible(self.playlist_check.isChecked())
        
        self.indirme_thread = IndirmeThread(
            url, 
            self.konum_input.text(),
            self.format_combo.currentText(),
            self.playlist_check.isChecked()
        )
        
        self.indirme_thread.ilerleme_sinyali.connect(self.ilerlemeyi_guncelle)
        self.indirme_thread.durum_sinyali.connect(self.durumu_guncelle)
        self.indirme_thread.tamamlandi_sinyali.connect(self.indirme_tamamlandi)
        self.indirme_thread.toplam_dosya_sinyali.connect(self.playlist_toplam_ayarla)
        self.indirme_thread.mevcut_dosya_sinyali.connect(self.playlist_ilerleme_guncelle)
        
        self.indirme_thread.start()

    def ilerlemeyi_guncelle(self, yuzde):
        self.progress_bar.setValue(yuzde)

    def durumu_guncelle(self, mesaj):
        self.durum_label.setText(mesaj)

    def indirme_tamamlandi(self, basarili):
        self.indir_button.setEnabled(True)
        if basarili:
            self.progress_bar.setValue(100)

    def playlist_toplam_ayarla(self, toplam):
        self.playlist_progress.setMaximum(toplam)

    def playlist_ilerleme_guncelle(self, mevcut):
        self.playlist_progress.setValue(mevcut)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Uygulama ikonu ayarla
    icon_path = os.path.join(os.path.dirname(__file__), "gizli.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    pencere = MuzikIndirici()
    pencere.show()
    sys.exit(app.exec_()) 