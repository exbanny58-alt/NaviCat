import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QStackedWidget, QToolTip
)
from PyQt6.QtCore import Qt, QPoint, QByteArray, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QIcon, QPixmap, QFont
from PyQt6.QtSvg import QSvgRenderer


class SVGIcon:
    """Класс для создания SVG иконок"""

    # Иконка для Сервера
    @staticmethod
    def create_server_icon(color="#aaaaaa"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14" id="Database-Subtract-1--Streamline-Core-Remix" height="14" width="14">
            <g id="Free Remix/Computer Devices/database-subtract-1--raid-storage-code-disk-programming-database-array-hard-disc-minus">
                <path id="Union" fill="{color}" fill-rule="evenodd" d="M6.125 0C4.54943 0 3.09476 0.245066 2.01112 0.662757 1.47137 0.870806 0.99174 1.13387 0.636234 1.45785 0.280705 1.78185 0.000359243 2.21559 0 2.74398v6.76101c0 0.49 0.240691 0.90041 0.559158 1.21521 0.315975 0.3123 0.742512 0.5675 1.221962 0.7729 0.9617 0.4121 2.25908 0.6758 3.69041 0.7411 0.34482 0.0157 0.6371 -0.2511 0.65282 -0.5959 0.01572 -0.3448 -0.25106 -0.6371 -0.59588 -0.6528 -1.3293 -0.0606 -2.46942 -0.3047 -3.25506 -0.6414 -0.39423 -0.1689 -0.66882 -0.34817 -0.83556 -0.51297 -0.16424 -0.16234 -0.18785 -0.27157 -0.18785 -0.32614V7.85054c0.23304 0.13334 0.48947 0.25199 0.76112 0.3567C3.09476 8.62493 4.54943 8.87 6.125 8.87s3.03024 -0.24507 4.1139 -0.66276c0.2716 -0.10471 0.5281 -0.22336 0.7611 -0.3567v1.65445c0 0.06934 -0.0441 0.24034 -0.3699 0.47957 -0.2782 0.20434 -0.3382 0.59544 -0.1339 0.87364 0.2043 0.2783 0.5955 0.3382 0.8737 0.1339 0.4735 -0.3476 0.8801 -0.8453 0.8801 -1.48711V2.745c0 -0.52885 -0.2805 -0.96294 -0.6362 -1.28715 -0.3555 -0.32398 -0.8352 -0.587044 -1.3749 -0.795093C9.15524 0.245066 7.70057 0 6.125 0ZM1.4782 6.48824C1.27733 6.30519 1.25 6.18157 1.25 6.125V4.47055c0.23304 0.13333 0.48947 0.25198 0.76112 0.35669C3.09476 5.24493 4.54943 5.49 6.125 5.49s3.03024 -0.24507 4.1139 -0.66276c0.2716 -0.10471 0.5281 -0.22336 0.7611 -0.35669V6.125c0 0.05657 -0.0273 0.18019 -0.2282 0.36324 -0.2011 0.18329 -0.5269 0.37705 -0.9825 0.55264 -0.90698 0.3496 -2.20231 0.57912 -3.6643 0.57912 -1.46199 0 -2.75732 -0.22952 -3.6643 -0.57912 -0.45555 -0.17559 -0.78137 -0.36935 -0.9825 -0.55264ZM8.25 12.5c-0.41421 0 -0.75 0.3358 -0.75 0.75s0.33579 0.75 0.75 0.75h5c0.4142 0 0.75 -0.3358 0.75 -0.75s-0.3358 -0.75 -0.75 -0.75h-5Z" clip-rule="evenodd" stroke-width="1"></path>
            </g>
        </svg>'''

    # Иконка для Клиента
    @staticmethod
    def create_client_icon(color="#aaaaaa"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14" id="Ai-Gaming-Spark--Streamline-Core-Remix" height="14" width="14">
            <g id="Free Remix/Artificial Intelligence/ai-gaming-spark--remote-control-controller-technology-artificial-intelligence-ai">
                <path id="Union" fill="{color}" fill-rule="evenodd" d="M9.56056 0.6564C9.74805 -0.214503 10.9809 -0.220724 11.176 0.649356l0.0253 0.112754c0.2386 1.06349 1.0796 1.87059 2.1254 2.0556 0.8978 0.15883 0.8978 1.45575 0 1.61458 -1.0458 0.18501 -1.8868 0.99211 -2.1254 2.0556l-0.0253 0.11276c-0.1951 0.87008 -1.42795 0.86385 -1.61544 -0.00705l-0.02082 -0.09675C9.3099 5.42923 8.46979 4.61603 7.42214 4.4307c-0.89608 -0.15853 -0.89609 -1.45287 0 -1.61139C8.46979 2.63397 9.3099 1.82077 9.53973 0.753153l0.48877 0.105227 -0.48876 -0.105228L9.56056 0.6564ZM4.0703 6.43762c0.34517 0 0.625 0.27983 0.625 0.625v0.53052h0.53051c0.34518 0 0.625 0.27982 0.625 0.625s-0.27982 0.625 -0.625 0.625H4.6953v0.53038c0 0.34518 -0.27983 0.625 -0.625 0.625 -0.34518 0 -0.625 -0.27982 -0.625 -0.625v-0.53038h-0.53038c-0.34518 0 -0.625 -0.27982 -0.625 -0.625s0.27982 -0.625 0.625 -0.625h0.53038v-0.53052c0 -0.34517 0.27982 -0.625 0.625 -0.625Zm-2.40627 0.88822c0.13022 -1.17198 1.12085 -2.05863 2.30004 -2.05863h1.26582c0.34518 0 0.625 -0.27982 0.625 -0.625s-0.27982 -0.625 -0.625 -0.625H3.96407c-1.81613 0 -3.341832 1.36557 -3.54239 3.1706L0.0178418 10.8223C-0.170507 12.5175 1.15641 14 2.86198 14c1.08391 0 2.07479 -0.6124 2.55953 -1.5819l0.17937 -0.3587h2.13839l0.17937 0.3587C8.40338 13.3876 9.39426 14 10.4782 14c1.7055 0 3.0325 -1.4825 2.8441 -3.1777l-0.3578 -3.22034c-0.0381 -0.34306 -0.3471 -0.59027 -0.6902 -0.55215 -0.3431 0.03812 -0.5903 0.34713 -0.5522 0.69019l0.3579 3.2204c0.106 0.9547 -0.6413 1.7896 -1.6018 1.7896 -0.61048 0 -1.16853 -0.3449 -1.44153 -0.8909l-0.35211 -0.7042c-0.10587 -0.2118 -0.32229 -0.3455 -0.55902 -0.3455H5.21461c-0.23673 0 -0.45315 0.1337 -0.55902 0.3455l-0.35212 0.7042c-0.273 0.546 -0.83105 0.8909 -1.44149 0.8909 -0.96056 0 -1.70786 -0.8349 -1.60178 -1.7896l0.40383 -3.63456Z" clip-rule="evenodd" stroke-width="1"></path>
            </g>
        </svg>'''

    # Иконка для Модов
    @staticmethod
    def create_mods_icon(color="#aaaaaa"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14" id="Shipment-Check--Streamline-Core-Remix" height="14" width="14">
            <g id="Free Remix/Shipping/shipment-check--shipping-parcel-shipment-check-approved">
                <path id="Union" fill="{color}" fill-rule="evenodd" d="M6.375 0.307983H3.38268c-0.57955 0 -1.10725 0.333862 -1.35547 0.857567L0.54818 4.28615c-0.038832 0.08193 -0.054032 0.17136 -0.046175 0.25887C0.500677 4.56165 0.5 4.57847 0.5 4.59545v7.16445c0 0.4106 0.1631 0.8043 0.453421 1.0947 0.290319 0.2903 0.684079 0.4534 1.094659 0.4534h9.90382c0.4106 0 0.8044 -0.1631 1.0947 -0.4534 0.2903 -0.2904 0.4534 -0.6841 0.4534 -1.0947V4.59545c0 -0.01697 -0.0007 -0.03379 -0.002 -0.05042 0.0079 -0.08752 -0.0073 -0.17695 -0.0462 -0.25888l-1.479 -3.1206c-0.2482 -0.523705 -0.7759 -0.857567 -1.3555 -0.857567H7.625l0 4.692307h4.625v6.75961c0 0.0791 -0.0314 0.1549 -0.0873 0.2108 -0.0559 0.0559 -0.1317 0.0873 -0.2108 0.0873H2.04808c-0.07906 0 -0.15488 -0.0314 -0.21078 -0.0873 -0.0559 -0.0559 -0.0873 -0.1317 -0.0873 -0.2108V5.00029h4.625l0 -4.692307ZM9.75022 7.37471c0.20694 -0.27626 0.15075 -0.66798 -0.12551 -0.87493 -0.27626 -0.20694 -0.66798 -0.15075 -0.87493 0.12551L6.4258 9.72769l-1.30109 -0.97463c-0.27626 -0.20695 -0.66798 -0.15076 -0.87493 0.12551 -0.20694 0.27626 -0.15075 0.66798 0.12551 0.87492L6.1766 11.1028c0.13267 0.0994 0.29938 0.142 0.46346 0.1185 0.16408 -0.0235 0.31209 -0.1113 0.41147 -0.244l2.69869 -3.60259Z" clip-rule="evenodd" stroke-width="1"></path>
            </g>
        </svg>'''

    # Иконка для Редакторов
    @staticmethod
    def create_editors_icon(color="#aaaaaa"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14" id="Cut--Streamline-Core-Remix" height="14" width="14">
            <g id="Free Remix/Interface Essential/cut--coupon-cut-discount-price-prices-scissors">
                <path id="Union" fill="{color}" fill-rule="evenodd" d="M1.625 3.25c0 -0.89746 0.72754 -1.625 1.625 -1.625s1.625 0.72754 1.625 1.625 -0.72754 1.625 -1.625 1.625 -1.625 -0.72754 -1.625 -1.625ZM3.25 0.375C1.66218 0.375 0.375 1.66218 0.375 3.25c0 1.30908 0.87493 2.41382 2.07193 2.76134l1.69963 0.97582 -1.70247 1.00233C1.24855 8.33793 0.375 9.44195 0.375 10.75c0 1.5878 1.28718 2.875 2.875 2.875s2.875 -1.2872 2.875 -2.875c0 -1.11445 -0.6341 -2.0808 -1.5612 -2.55793l0.83013 -0.48874 2.78482 1.59886c0.29935 0.17187 0.68134 0.06853 0.85321 -0.23082 0.17187 -0.29935 0.06852 -0.68134 -0.23083 -0.85321L6.63341 6.97359l6.68369 -3.935c0.2974 -0.17513 0.3966 -0.55823 0.2215 -0.85568 -0.1751 -0.29746 -0.5582 -0.39662 -0.8557 -0.2215L5.38604 6.25742l-0.80159 -0.46022C5.5003 5.31641 6.125 4.35616 6.125 3.25 6.125 1.66218 4.83782 0.375 3.25 0.375Zm4.49023 10c-0.34517 0 -0.625 0.2798 -0.625 0.625s0.27983 0.625 0.625 0.625h1.5c0.34518 0 0.625 -0.2798 0.625 -0.625s-0.27982 -0.625 -0.625 -0.625h-1.5Zm3.99997 0c-0.3451 0 -0.625 0.2798 -0.625 0.625s0.2799 0.625 0.625 0.625h1.5c0.3452 0 0.625 -0.2798 0.625 -0.625s-0.2798 -0.625 -0.625 -0.625h-1.5ZM1.625 10.75c0 -0.89746 0.72754 -1.625 1.625 -1.625s1.625 0.72754 1.625 1.625c0 0.8975 -0.72754 1.625 -1.625 1.625s-1.625 -0.7275 -1.625 -1.625Z" clip-rule="evenodd" stroke-width="1"></path>
            </g>
        </svg>'''

    # Иконка для Настроек (шестерёнка)
    @staticmethod
    def create_settings_icon(color="#aaaaaa"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14" id="Cog-1--Streamline-Core-Remix" height="14" width="14">
            <g id="Free Remix/Interface Essential/cog-1--work-loading-cog-gear-settings-machine">
                <path id="Union" fill="{color}" fill-rule="evenodd" d="m6.5979 -0.000976562 -0.00184 0.000005483C6.27256 -0.0000154972 5.95689 0.0986183 5.69039 0.282012c-0.26638 0.183318 -0.47122 0.442783 -0.5877 0.744438l-0.00014 0.00037 -0.34101 0.88026 -1.06947 0.607 -0.94323 -0.14388 0.00002 -0.00009 -0.0102 -0.00138c-0.31554 -0.04283 -0.63669 0.00911 -0.92263 0.14923 -0.28595 0.14011 -0.52379 0.36207 -0.68329 0.63767l-0.00001 0 -0.00171 0.00298 -0.390693 0.68372c-0.16309 0.27913 -0.238155 0.60102 -0.21532 0.92356 0.022936 0.32398 0.14357 0.63339 0.34598 0.8874l-0.000009 0.00001 0.00229 0.00283 0.597202 0.74053V7.608l-0.58148 0.74079c-0.201436 0.25362 -0.321489 0.56225 -0.344365 0.88536 -0.022835 0.32255 0.052233 0.64445 0.215328 0.92355l0.390687 0.6837 -0.00001 0 0.00172 0.003c0.15951 0.2756 0.39735 0.4976 0.6833 0.6377 0.28594 0.1401 0.60709 0.192 0.92263 0.1492l0.00001 0.0001 0.01017 -0.0016 0.9412 -0.1435 1.05114 0.6047 0.34175 0.8822 0.00006 0.0002c0.11647 0.3017 0.32134 0.5613 0.58778 0.7446 0.2665 0.1834 0.58217 0.2821 0.90567 0.283l0.00184 0h0.82398l0.00184 0c0.3235 -0.0009 0.63917 -0.0996 0.90566 -0.283 0.26642 -0.1833 0.47127 -0.4428 0.58775 -0.7445l0.0001 -0.0003 0.34175 -0.8822 1.05112 -0.6047 0.9412 0.1435 0 0.0001 0.0102 0.0014c0.3155 0.0428 0.6367 -0.0091 0.9226 -0.1492 0.286 -0.1401 0.5238 -0.3621 0.6833 -0.6377l0.0017 -0.003 0.3907 -0.6836c0.1631 -0.27919 0.2382 -0.60109 0.2154 -0.92365 -0.023 -0.32398 -0.1436 -0.63339 -0.346 -0.88739l0 -0.00001 -0.0023 -0.00284 -0.5972 -0.74053V6.39205l0.5815 -0.74079c0.2014 -0.25362 0.3215 -0.56225 0.3443 -0.88537 0.0229 -0.32254 -0.0522 -0.64443 -0.2153 -0.92356l-0.3907 -0.68372 -0.0017 -0.00298c-0.1595 -0.2756 -0.3973 -0.49756 -0.6833 -0.63767 -0.2859 -0.14012 -0.6071 -0.19206 -0.9226 -0.14923l0 -0.00009 -0.0102 0.00156 -0.9412 0.14357L9.23936 1.909l-0.34175 -0.88218 -0.00009 -0.00025C8.78104 0.724866 8.57619 0.465355 8.30977 0.282012c-0.2665 -0.1833937 -0.58217 -0.2820274972 -0.90567 -0.282985821h-0.00184L6.5979 -0.000976562ZM6.59905 1.24903h0.80206c0.07145 0.00035 0.14115 0.0222 0.20002 0.06271 0.05907 0.04065 0.10448 0.09818 0.13029 0.16507l0.0003 0.00078 0.4218 1.08882c0.0516 0.13321 0.14728 0.24472 0.27111 0.31597l1.43214 0.82397c0.12278 0.07064 0.26593 0.09748 0.40593 0.07612l1.1512 -0.1756c0.0686 -0.00856 0.1384 0.00309 0.2006 0.03357 0.063 0.03087 0.1154 0.07966 0.1508 0.14023l0.0006 0.0011 0.3907 0.68366 -0.0001 0.00003 0.0039 0.00664c0.0365 0.06205 0.0533 0.13371 0.0483 0.20551 -0.0051 0.07181 -0.0319 0.14038 -0.0767 0.19668l-0.0029 0.00359 -0.716 0.91226c-0.0864 0.11008 -0.1334 0.24597 -0.1334 0.38591V7.824c0 0.14276 0.0489 0.28122 0.1385 0.39234l0.7334 0.90941 0.0009 0.00108c0.0443 0.0561 0.0707 0.12425 0.0758 0.1956 0.0051 0.0718 -0.0118 0.14346 -0.0482 0.20552l-0.0001 -0.00003 -0.0038 0.00669 -0.3906 0.68369 -0.0007 0.0011c-0.0353 0.0606 -0.0878 0.1093 -0.1508 0.1402 -0.0622 0.0305 -0.1319 0.0421 -0.2006 0.0336l-1.1512 -0.1756c-0.14 -0.0214 -0.28313 0.0055 -0.40591 0.0761l-1.43214 0.824c-0.12383 0.0712 -0.21951 0.1827 -0.27112 0.3159l-0.42179 1.0889 -0.0003 0.0007c-0.02581 0.0669 -0.07122 0.1245 -0.13029 0.1651 -0.05886 0.0405 -0.12855 0.0624 -0.2 0.0627h-0.82172c-0.07145 -0.0003 -0.14114 -0.0222 -0.2 -0.0627 -0.05907 -0.0406 -0.10448 -0.0982 -0.13029 -0.1651l-0.0003 -0.0007 -0.42179 -1.0889c-0.05161 -0.1332 -0.14729 -0.2447 -0.27112 -0.3159l-1.43215 -0.824c-0.12277 -0.0706 -0.2659 -0.0975 -0.40593 -0.0761l-1.15115 0.1756c-0.06869 0.0085 -0.13842 -0.0031 -0.20064 -0.0336 -0.06298 -0.0309 -0.11544 -0.0796 -0.15078 -0.1402l-0.00065 -0.0011 -0.39066 -0.68369 0.00004 -0.00002 -0.0039 -0.00664c-0.03648 -0.06206 -0.05329 -0.13372 -0.04821 -0.20552 0.00509 -0.07181 0.03182 -0.14038 0.07668 -0.19668l0.00002 0.00001 0.00283 -0.0036 0.71607 -0.91226c0.0864 -0.11008 0.13337 -0.24597 0.13337 -0.3859V6.17605c0 -0.14276 -0.04888 -0.28122 -0.13849 -0.39235l-0.73426 -0.91048c-0.04435 -0.05609 -0.07078 -0.12426 -0.07583 -0.19561 -0.00509 -0.0718 0.01172 -0.14346 0.0482 -0.20551l0.00004 0.00002 0.00382 -0.00669 0.39131 -0.68478c0.03535 -0.06056 0.0878 -0.10934 0.15079 -0.14021 0.06221 -0.03048 0.13194 -0.04213 0.20064 -0.03357l1.15114 0.1756c0.13879 0.02117 0.28066 -0.005 0.40276 -0.0743l1.45176 -0.82398c0.12534 -0.07113 0.22224 -0.1834 0.2743 -0.31778l0.42179 -1.08882 0.0003 -0.00078c0.02581 -0.06689 0.07122 -0.12442 0.13029 -0.16507 0.05887 -0.04051 0.12857 -0.06236 0.20002 -0.06271ZM4.75008 7c0 0.44501 0.13196 0.88002 0.3792 1.25003 0.24723 0.37002 0.59863 0.6584 1.00977 0.8287 0.41113 0.1703 0.86353 0.21486 1.29999 0.12804 0.43645 -0.08682 0.83737 -0.30111 1.15203 -0.61578 0.31467 -0.31467 0.52896 -0.71558 0.61578 -1.15203 0.08682 -0.43646 0.04226 -0.88886 -0.12804 -1.3 -0.17029 -0.41113 -0.45868 -0.76253 -0.82869 -1.00976 -0.37001 -0.24724 -0.80503 -0.3792 -1.25004 -0.3792 -0.59673 0 -1.16903 0.23706 -1.59099 0.65901 -0.42195 0.42196 -0.65901 0.99426 -0.65901 1.59099Z" clip-rule="evenodd" stroke-width="1"></path>
            </g>
        </svg>'''

    # Иконка стрелки влево (для сворачивания)
    @staticmethod
    def create_arrow_left_icon(color="#aaaaaa"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" fill="{color}"/>
        </svg>'''

    # Иконка стрелки вправо (для разворачивания)
    @staticmethod
    def create_arrow_right_icon(color="#aaaaaa"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z" fill="{color}"/>
        </svg>'''

    # Иконки заголовка
    @staticmethod
    def create_close_icon(color="#ffffff"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="{color}"/>
        </svg>'''

    @staticmethod
    def create_minimize_icon(color="#ffffff"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M19 13H5v-2h14v2z" fill="{color}"/>
        </svg>'''

    @staticmethod
    def create_maximize_icon(color="#ffffff"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z" fill="{color}"/>
        </svg>'''

    @staticmethod
    def create_restore_icon(color="#ffffff"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M19 9h-4V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2h4v4c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2v-8c0-1.1-.9-2-2-2zm-8 8H5V5h8v4h-4c-1.1 0-2 .9-2 2v4h4v2zm4-4v4h-4v-4h4zm4 4h-2v-4h-4V9h6v8z" fill="{color}"/>
        </svg>'''

    @staticmethod
    def svg_to_icon(svg_string, size=24):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        renderer = QSvgRenderer(QByteArray(svg_string.encode()))
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.drag_pos = None
        self.setFixedHeight(44)
        self.setStyleSheet("background-color: #1a1a1a;")

        # Кнопка-стрелка
        self.toggle_btn = QPushButton()
        self.toggle_btn.setIcon(SVGIcon.svg_to_icon(SVGIcon.create_arrow_left_icon("#aaaaaa"), size=20))
        self.toggle_btn.setIconSize(QSize(20, 20))
        self.toggle_btn.setToolTip("Свернуть меню")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 4px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.toggle_btn.clicked.connect(self.parent.toggle_menu)

        # Кнопки управления
        self.minimize_btn = QPushButton()
        self.maximize_btn = QPushButton()
        self.close_btn = QPushButton()
        self.setup_buttons()

        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.parent.close)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 14, 0)
        layout.setSpacing(8)
        layout.addStretch()
        layout.addWidget(self.toggle_btn)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
        self.setLayout(layout)

    def setup_buttons(self):
        btn_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 4px;
                min-width: 28px;
                min-height: 28px;
                max-width: 28px;
                max-height: 28px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """
        close_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 4px;
                min-width: 28px;
                min-height: 28px;
                max-width: 28px;
                max-height: 28px;
            }
            QPushButton:hover {
                background-color: #e81123;
                border-radius: 4px;
            }
        """
        close_svg = SVGIcon.create_close_icon("#ffffff")
        minimize_svg = SVGIcon.create_minimize_icon("#ffffff")
        maximize_svg = SVGIcon.create_maximize_icon("#ffffff")
        restore_svg = SVGIcon.create_restore_icon("#ffffff")
        self.close_icon = SVGIcon.svg_to_icon(close_svg)
        self.minimize_icon = SVGIcon.svg_to_icon(minimize_svg)
        self.maximize_icon = SVGIcon.svg_to_icon(maximize_svg)
        self.restore_icon = SVGIcon.svg_to_icon(restore_svg)
        self.close_btn.setIcon(self.close_icon)
        self.minimize_btn.setIcon(self.minimize_icon)
        self.maximize_btn.setIcon(self.maximize_icon)
        self.minimize_btn.setStyleSheet(btn_style)
        self.maximize_btn.setStyleSheet(btn_style)
        self.close_btn.setStyleSheet(close_style)
        icon_size = 16
        self.close_btn.setIconSize(QSize(icon_size, icon_size))
        self.minimize_btn.setIconSize(QSize(icon_size, icon_size))
        self.maximize_btn.setIconSize(QSize(icon_size, icon_size))

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_btn.setIcon(self.maximize_icon)
        else:
            self.parent.showMaximized()
            self.maximize_btn.setIcon(self.restore_icon)

    def update_toggle_icon(self, expanded):
        if expanded:
            icon = SVGIcon.svg_to_icon(SVGIcon.create_arrow_left_icon("#aaaaaa"), size=20)
            self.toggle_btn.setToolTip("Свернуть меню")
        else:
            icon = SVGIcon.svg_to_icon(SVGIcon.create_arrow_right_icon("#aaaaaa"), size=20)
            self.toggle_btn.setToolTip("Развернуть меню")
        self.toggle_btn.setIcon(icon)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.parent.move(self.parent.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()


class MatteBlackWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 1000, 650)

        # Состояние меню - по умолчанию свёрнуто
        self.menu_expanded = False
        self.menu_width_expanded = 160
        self.menu_width_collapsed = 64

        # Главный вертикальный макет
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Шапка
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Разделитель под шапкой
        separator_top = QFrame()
        separator_top.setFrameShape(QFrame.Shape.HLine)
        separator_top.setFrameShadow(QFrame.Shadow.Sunken)
        separator_top.setStyleSheet("background-color: #333333; max-height: 1px;")
        main_layout.addWidget(separator_top)

        # Основная горизонтальная часть
        self.main_hbox = QHBoxLayout()
        self.main_hbox.setContentsMargins(0, 0, 0, 0)
        self.main_hbox.setSpacing(0)

        # ---- Левая панель (меню) ----
        self.menu_panel = QWidget()
        self.menu_panel.setFixedWidth(self.menu_width_expanded)
        self.menu_panel.setStyleSheet("background-color: #1a1a1a;")
        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(10, 20, 10, 20)
        menu_layout.setSpacing(8)

        # Пункты меню
        self.menu_buttons = []
        menu_items = [
            ("Сервер", SVGIcon.create_server_icon),
            ("Клиент", SVGIcon.create_client_icon),
            ("Моды", SVGIcon.create_mods_icon),
            ("Редакторы", SVGIcon.create_editors_icon),
        ]

        for i, (name, icon_func) in enumerate(menu_items):
            btn = QPushButton(name)
            btn.setObjectName(f"menu_{i}")
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            svg = icon_func("#aaaaaa")
            icon = SVGIcon.svg_to_icon(svg, size=24)
            btn.setIcon(icon)
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #aaaaaa;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 15px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                    color: #ffffff;
                }
                QPushButton:checked {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border-left: 3px solid #ffffff;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.on_menu_clicked(idx))
            menu_layout.addWidget(btn)
            self.menu_buttons.append(btn)

        menu_layout.addStretch()

        # Настройки
        settings_btn = QPushButton("Настройки")
        settings_btn.setObjectName("menu_settings")
        settings_btn.setCheckable(True)
        settings_btn.setAutoExclusive(True)
        svg_settings = SVGIcon.create_settings_icon("#aaaaaa")
        icon_settings = SVGIcon.svg_to_icon(svg_settings, size=24)
        settings_btn.setIcon(icon_settings)
        settings_btn.setIconSize(QSize(24, 24))
        settings_btn.setToolTip("Настройки")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #aaaaaa;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QPushButton:checked {
                background-color: #2a2a2a;
                color: #ffffff;
                border-left: 3px solid #ffffff;
            }
        """)
        settings_btn.clicked.connect(lambda checked: self.on_menu_clicked(4))
        menu_layout.addWidget(settings_btn)
        self.menu_buttons.append(settings_btn)

        self.menu_panel.setLayout(menu_layout)

        # ---- Вертикальный разделитель ----
        self.separator_vertical = QFrame()
        self.separator_vertical.setFrameShape(QFrame.Shape.VLine)
        self.separator_vertical.setFrameShadow(QFrame.Shadow.Sunken)
        self.separator_vertical.setStyleSheet("background-color: #333333; max-width: 1px;")

        # ---- Правая панель (контент) ----
        content_panel = QWidget()
        content_panel.setStyleSheet("background-color: #1a1a1a;")
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: transparent;")

        # Создаём страницы
        all_items = menu_items + [("Настройки", SVGIcon.create_settings_icon)]
        for i, (name, _) in enumerate(all_items):
            page = QWidget()
            page.setStyleSheet("background-color: transparent;")
            page_layout = QVBoxLayout()
            page_layout.setContentsMargins(30, 30, 30, 30)
            label = QLabel(f"<h1 style='color: #cccccc;'>{name}</h1>"
                           f"<p style='color: #666666;'>Контент для страницы «{name}»</p>"
                           f"<p style='color: #555555;'>Здесь может быть ваша информация.</p>")
            label.setAlignment(Qt.AlignmentFlag.AlignTop)
            label.setWordWrap(True)
            page_layout.addWidget(label)
            page_layout.addStretch()
            page.setLayout(page_layout)
            self.content_stack.addWidget(page)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.content_stack)
        content_panel.setLayout(content_layout)

        # Собираем горизонтальную часть
        self.main_hbox.addWidget(self.menu_panel)
        self.main_hbox.addWidget(self.separator_vertical)
        self.main_hbox.addWidget(content_panel)

        main_layout.addLayout(self.main_hbox)
        self.setLayout(main_layout)

        # Применяем начальное состояние (свёрнутое)
        self.apply_menu_state()

        # По умолчанию выбираем первый пункт
        self.menu_buttons[0].setChecked(True)
        self.on_menu_clicked(0)

    def apply_menu_state(self):
        width = self.menu_width_expanded if self.menu_expanded else self.menu_width_collapsed
        self.menu_panel.setFixedWidth(width)
        self.title_bar.update_toggle_icon(self.menu_expanded)

        for btn in self.menu_buttons:
            if self.menu_expanded:
                btn.setText(btn.toolTip())
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #aaaaaa;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-size: 15px;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #2a2a2a;
                        color: #ffffff;
                    }
                    QPushButton:checked {
                        background-color: #2a2a2a;
                        color: #ffffff;
                        border-left: 3px solid #ffffff;
                    }
                """)
            else:
                btn.setText("")
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #aaaaaa;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 0px;
                        font-size: 0px;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #2a2a2a;
                        color: #ffffff;
                    }
                    QPushButton:checked {
                        background-color: #2a2a2a;
                        color: #ffffff;
                        border-left: 3px solid #ffffff;
                    }
                """)
                btn.setIconSize(QSize(24, 24))

    def toggle_menu(self):
        self.menu_expanded = not self.menu_expanded
        self.apply_menu_state()

    def on_menu_clicked(self, index):
        self.content_stack.setCurrentIndex(index)
        icon_functions = [
            SVGIcon.create_server_icon,
            SVGIcon.create_client_icon,
            SVGIcon.create_mods_icon,
            SVGIcon.create_editors_icon,
            SVGIcon.create_settings_icon
        ]
        for i, btn in enumerate(self.menu_buttons):
            color = "#ffffff" if i == index else "#aaaaaa"
            svg = icon_functions[i](color)
            icon = SVGIcon.svg_to_icon(svg, size=24)
            btn.setIcon(icon)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Тень (оставлена для красоты, но без скругления)
        shadow_color = QColor(0, 0, 0, 80)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(10, 10, self.width() - 20, self.height() - 20)
        # Основная рамка
        painter.setBrush(QBrush(QColor(26, 26, 26)))
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.drawRect(0, 0, self.width(), self.height())
        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos'):
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget { background-color: transparent; }")
    QToolTip.setFont(QFont("Segoe UI", 9))
    window = MatteBlackWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()