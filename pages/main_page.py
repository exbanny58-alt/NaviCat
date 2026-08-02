# pages/main_page.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView


class MainPage(QWidget):
    """Главная страница с DayzM и крутёлкой через WebEngine"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)
        
        # Надпись DayzM матовый серый (в точности DayzM)
        title = QLabel("DayZM")
        title.setStyleSheet("""
            color: #888888;
            font-size: 90px;
            font-weight: 900;
            background-color: transparent;
            font-family: 'Segoe UI', Arial, sans-serif;
            letter-spacing: 8px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Крутёлка через WebEngine
        self.web_view = QWebEngineView()
        self.web_view.setFixedSize(130, 130)
        self.web_view.setStyleSheet("background-color: transparent;")
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.transparent)
        
        html = """
        <html>
        <head>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                }
                
                body {
                    background: transparent !important;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    width: 100vw;
                }
                
                .loader {
                    position: relative;
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                    perspective: 800px;
                }
                
                .inner {
                    position: absolute;
                    box-sizing: border-box;
                    width: 100%;
                    height: 100%;
                    border-radius: 50%;  
                }
                
                .inner.one {
                    left: 0%;
                    top: 0%;
                    animation: rotate-one 1s linear infinite;
                    border-bottom: 4px solid #EFEFFA;
                }
                
                .inner.two {
                    right: 0%;
                    top: 0%;
                    animation: rotate-two 1s linear infinite;
                    border-right: 4px solid #EFEFFA;
                }
                
                .inner.three {
                    right: 0%;
                    bottom: 0%;
                    animation: rotate-three 1s linear infinite;
                    border-top: 4px solid #EFEFFA;
                }
                
                @keyframes rotate-one {
                    0% { transform: rotateX(35deg) rotateY(-45deg) rotateZ(0deg); }
                    100% { transform: rotateX(35deg) rotateY(-45deg) rotateZ(360deg); }
                }
                
                @keyframes rotate-two {
                    0% { transform: rotateX(50deg) rotateY(10deg) rotateZ(0deg); }
                    100% { transform: rotateX(50deg) rotateY(10deg) rotateZ(360deg); }
                }
                
                @keyframes rotate-three {
                    0% { transform: rotateX(35deg) rotateY(55deg) rotateZ(0deg); }
                    100% { transform: rotateX(35deg) rotateY(55deg) rotateZ(360deg); }
                }
            </style>
        </head>
        <body>
            <div class="loader">
                <div class="inner one"></div>
                <div class="inner two"></div>
                <div class="inner three"></div>
            </div>
        </body>
        </html>
        """
        
        self.web_view.setHtml(html)
        layout.addWidget(self.web_view, 0, Qt.AlignmentFlag.AlignCenter)