"""Deney H'nin ortak beklenen(...) imzası; ayarsız sessiz varsayılan yok."""
from __future__ import annotations

import json

import pandas as pd

from .model import Parametreler, ArkaPlan, EEPAS
from .janus import ETASModel, Janus

_MODEL = None


def yapilandir(model):
    """EEPAS, ETASModel veya Janus nesnesini ortak çağrıya bağla."""
    global _MODEL
    if not isinstance(model,(EEPAS,ETASModel,Janus)):
        raise TypeError('EEPAS/ETASModel/Janus gerekli')
    _MODEL = model
    return model.beklenen


def dosyadan(yol, tur='janus'):
    """Yalnız <=2010 ayarı taşıyan JSON'dan bağımsız bir callable oluştur."""
    with open(yol,encoding='utf-8') as f:
        cfg = json.load(f)
    # İzlenen C/olcum.json da aynı parametre paketini taşır.
    cfg = cfg.get('italya_model',cfg)
    if pd.Timestamp(cfg['ayar_bitis']) > pd.Timestamp('2011-01-01',tz='UTC'):
        raise ValueError('İç doğrulama ayarı <=2010 olmalı')
    if not cfg.get('hazir',False):
        raise ValueError('Yakınsamamış bölgesel ayar yüklenmez')
    bg = ArkaPlan(cfg['kutu'],pd.DataFrame(cfg['ppe_merkezler'],columns=['boylam','enlem']),
                  cfg['ppe_bant'],cfg.get('ppe_duzgun_pay',.05))
    ep = EEPAS(Parametreler(**cfg['eepas']['parametreler']),cfg['kutu'],bg)
    if tur=='eepas':
        return ep.beklenen
    et = ETASModel(cfg['etas']['parametreler'],cfg['etas']['m0'],cfg['etas']['b'],cfg['kutu'],bg)
    if tur=='etas':
        return et.beklenen
    if tur!='janus':
        raise ValueError('tur: eepas, etas veya janus')
    return Janus(ep,et,cfg['janus']['agirlik']).beklenen


def beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar):
    """[başlangıç,bitiş) hücre/büyüklük kutusu başına beklenen olay sayısı."""
    if _MODEL is None:
        raise RuntimeError('Önce yapilandir(model); ya da dosyadan(...,tur=...) kullanın')
    return _MODEL.beklenen(baslangic,bitis,gecmis,izgara,m_kenarlar)
