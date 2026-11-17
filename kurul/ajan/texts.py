"""Fixed texts the worker posts without a model call, in Turkish and English."""

from __future__ import annotations

T = {
    "ack": {
        "tr": "{addr}soruyu {qid} olarak kaydettim. Defterimizde daha önce sınanıp sınanmadığına bakıyorum; "
              "kayıtta cevabı varsa birazdan buraya yazarım, yoksa bir sınama planı taslağı getiririm.",
        "en": "{addr}recorded as {qid}. I am checking our ledger for earlier work on this; if the record "
              "answers it I will post the answer here shortly, otherwise I will bring a draft test plan.",
    },
    "queued": {
        "tr": "Plan donduruldu. Koşu proje ekibinin sırasına alındı; sonuç bu konuya yazılacak.",
        "en": "The plan is frozen. The run is queued for the project team; the result will be posted in "
              "this thread.",
    },
    "not_testable": {
        "tr": "{addr}bundan sınanabilir bir soru çıkaramadım. Bir not ekleyerek yeniden iletebilirsiniz.",
        "en": "{addr}I could not make a testable question out of this. You can forward it again with a note.",
    },
    "neutral": {
        "tr": "Bu konuda şu an güvenle yazabileceğim bir cevabım yok; proje ekibi bakacak.",
        "en": "I do not have an answer I can post with confidence right now; the project team will look at it.",
    },
    "unclear_answer": {
        "tr": "Not aldım. Soruyu notunuzla yeniden okuyorum.",
        "en": "Noted. I am reading the question again with your note.",
    },
    "review_failed": {
        "tr": "Bağımsız inceleme planda dondurmadan önce düzeltilmesi gereken noktalar buldu: {issues} "
              "Plan yeniden onayınıza gelecek.",
        "en": "The independent review found points to fix before freezing: {issues} The plan will come back "
              "for your approval.",
    },
    "running": {
        "tr": "Plan bağımsız incelemeden geçti ve donduruldu. Koşu başladı.",
        "en": "The plan passed independent review and is frozen. The run has started.",
    },
    "run_failed": {
        "tr": "Koşu tamamlanamadı; proje ekibi bakacak ve sonucu bu konuya yazacak.",
        "en": "The run could not be completed; the project team will look at it and post here.",
    },
}

LANG_NAME = {"tr": "Turkish", "en": "English"}


def text(key: str, lang: str, **kw) -> str:
    s = T[key]["tr" if lang == "tr" else "en"].format(**kw)
    # Capitalise the first letter when the address prefix is empty.
    return s[:1].upper() + s[1:] if s else s
