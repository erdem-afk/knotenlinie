"""İtalya'nın kendi 1985–2004 (Mc 3,1) ayarı: zaman-havuzu çekirdeği (varyant B). Kural: AE/KURAL.md."""
from knotenlinie.ortak_zemin.arayuz import ayar_tabani
from knotenlinie.ortak_zemin.veri import VERI, katalog_oku
from . import ceza as Z
from .bolge import yaz


def main():
    cat = katalog_oku(VERI / 'ortak/italya_katalog_le2015.csv')
    grid = ayar_tabani('italya', son='2006-01-01').izgara
    k = Z.italya_havuz_kur(cat, grid)
    yol = VERI / 'ortak/hiyerarsi/cekirdek_italya_1985_2004.json'
    yaz(k, yol)
    print({a: round(b, 5) for a, b in k['parametreler'].items()}, 'dallanma', k['dallanma'], k['basari'], flush=True)
    print(yol)


if __name__ == '__main__':
    main()
