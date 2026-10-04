#!/usr/bin/env python3
"""Generate 3 test story audios in European Portuguese via edge-tts (TEST DATA ONLY —
will be replaced by real family recordings). Then upload them to the app."""
import asyncio, os, sys

STORIES = [
    ("aldeia.mp3",
     "Eu nasci numa aldeia pequena perto de Bragança, chamada Vilarinho. "
     "A nossa casa era de pedra, com telhado de telha vermelha. No inverno fazia tanto frio "
     "que a água do poço gelava. A minha mãe acordava às cinco da manhã para fazer o pão no forno "
     "comunitário. Toda a aldeia ia lá buscar o pão quente. Eu ia com ela e comia a primeira fatia "
     "com azeite e açúcar. Era o meu lanche preferido."),
    ("viagem.mp3",
     "Em mil novecentos e setenta e quatro, vim para o Luxemburgo de comboio. "
     "A viagem demorou três dias. Eu levava uma mala de cartão com dois vestidos, uma fotografia "
     "dos meus pais e um terço. No comboio conheci outras portuguesas que também vinham ter com "
     "os maridos. Chorámos muito na fronteira. Quando cheguei à gare do Luxemburgo, o teu avô "
     "estava lá com um ramo de flores. Foi a primeira vez que vi nevar em abril."),
    ("cafe.mp3",
     "O teu avô trabalhava nas obras e eu limpava escritórios na cidade. "
     "Aos domingos, a nossa única folga, íamos ao café dos portugueses na Bonnevoie. "
     "Jogava-se às cartas, ouvia-se a rádio de Lisboa, e toda a gente falava da terra. "
     "Foi nesse café que fizemos os amigos que até hoje são a nossa família cá. "
     "A dona do café, a senhora Fátima, guardava-nos sempre a mesa do canto."),
]

async def main():
    import edge_tts
    out = "/opt/data/projet/avozdaavo/testdata"
    os.makedirs(out, exist_ok=True)
    for name, text in STORIES:
        path = os.path.join(out, name)
        if os.path.exists(path):
            continue
        tts = edge_tts.Communicate(text, "pt-PT-RaquelNeural", rate="-5%")
        await tts.save(path)
        print("saved", path)

asyncio.run(main())
print("DONE")
