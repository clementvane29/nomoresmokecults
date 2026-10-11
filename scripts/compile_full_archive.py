import sqlite3
import json
import os
import glob
import re

SQLITE_PATH = '/home/juan/Datos/Datos Juan/Documentos/his former partner/Familia JEJ/fb_extraction/data/joe_brewer_posts.sqlite'
SOLO_FB_DIR = '/home/juan/Datos/Datos Juan/Documentos/his former partner/Familia JEJ/Solo facebook'
PRUEBAS_DIR = '/home/juan/Datos/Datos Juan/Documentos/his former partner/Joe Brewer Benchmark/Pruebas'
OUTPUT_JSON = '/home/juan/Datos/Datos Juan/ProyectosSoftware/NoMoreSmokeCults/evidence/facebook_audit/JOE_BREWER_PUBLIC_FOOTPRINT_ARCHIVE.json'
OUTPUT_MD = '/home/juan/Datos/Datos Juan/ProyectosSoftware/NoMoreSmokeCults/evidence/facebook_audit/JOE_BREWER_PUBLIC_FOOTPRINT_ARCHIVE.md'

print("Iniciando compilacion exhaustiva del archivo forense...")

# 1. Leer SQLite
conn = sqlite3.connect(SQLITE_PATH)
c = conn.cursor()
c.execute('SELECT post_id, permalink, date_iso, timestamp_raw, content, media_urls, reactions_count, comments_count, shares_count, comments_data FROM facebook_posts ORDER BY date_iso ASC')
fb_rows = c.fetchall()

posts_by_url = {}
all_items = []

for row in fb_rows:
    post_id, permalink, date_iso, timestamp_raw, content, media_urls, reactions, comments, shares, comments_data = row
    media_list = []
    if media_urls:
        try:
            media_list = json.loads(media_urls)
        except Exception:
            media_list = [media_urls]
            
    parsed_comments = []
    if comments_data:
        try:
            parsed_comments = json.loads(comments_data)
        except Exception:
            parsed_comments = [{"raw": comments_data}]

    item = {
        "id": post_id or f"fb_{date_iso}_{len(all_items)}",
        "platform": "Facebook",
        "author": "Joseph Allen Brewer ('Joe Brewer')",
        "date_iso": date_iso,
        "timestamp_raw": timestamp_raw,
        "permalink": permalink,
        "content_en": content,
        "content_es": "",
        "media_urls": media_list,
        "metrics": {
            "reactions": reactions,
            "comments": comments,
            "shares": shares
        },
        "comments": parsed_comments,
        "forensic_classification": "",
        "forensic_file": "",
        "source": "fb_extraction_sqlite"
    }
    if permalink:
        posts_by_url[permalink] = item
    all_items.append(item)

print(f"Indexados {len(all_items)} registros desde SQLite.")

# 2. Enriquecer con los expedientes analizados y transcritos
txt_files = glob.glob(os.path.join(SOLO_FB_DIR, "*.txt"))
txt_files = [f for f in txt_files if not os.path.basename(f).startswith('INDICE')]

enriched_count = 0
for txt_path in txt_files:
    fname = os.path.basename(txt_path)
    try:
        with open(txt_path, 'r', encoding='utf-8', errors='ignore') as tf:
            content_raw = tf.read()
    except Exception as e:
        continue
    
    date_match = re.search(r'Fecha de Publicación:\s*([^\n\r]+)', content_raw)
    url_match = re.search(r'URL / Enlace Directo:\s*([^\n\r]+)', content_raw)
    class_match = re.search(r'Tipificación de Conducta:\s*([^\n\r]+)', content_raw)
    img_match = re.search(r'Archivo de Captura Forense:\s*([^\n\r]+)', content_raw)
    
    en_match = re.search(r'2\. TRANSCRIPCIÓN ÍNTEGRA ORIGINAL \(EN INGLÉS\)\s*-+\s*([\s\S]*?)(?=3\. TRADUCCIÓN ÍNTEGRA AL ESPAÑOL|$)', content_raw)
    es_match = re.search(r'3\. TRADUCCIÓN ÍNTEGRA AL ESPAÑOL\s*-+\s*([\s\S]*?)(?=4\. VALORACIÓN JURÍDICA|$)', content_raw)
    
    post_date = date_match.group(1).strip() if date_match else fname[:10]
    post_url = url_match.group(1).strip() if url_match else ""
    forensic_class = class_match.group(1).strip() if class_match else ""
    forensic_img = img_match.group(1).strip() if img_match else fname.replace('.txt', '.png')
    text_en = en_match.group(1).strip() if en_match else ""
    text_es = es_match.group(1).strip() if es_match else ""
    
    found = False
    if post_url and post_url in posts_by_url:
        it = posts_by_url[post_url]
        if text_en and len(text_en) > len(it["content_en"]):
            it["content_en"] = text_en
        it["content_es"] = text_es
        it["forensic_classification"] = forensic_class
        it["forensic_file"] = fname
        found = True
        enriched_count += 1
    else:
        for it in all_items:
            if it["date_iso"] == post_date and (text_en[:60] in it["content_en"] or it["content_en"][:60] in text_en):
                if text_en and len(text_en) > len(it["content_en"]):
                    it["content_en"] = text_en
                it["content_es"] = text_es
                it["forensic_classification"] = forensic_class
                it["forensic_file"] = fname
                if post_url and not it["permalink"]:
                    it["permalink"] = post_url
                found = True
                enriched_count += 1
                break
                
    if not found:
        new_item = {
            "id": f"forensic_fb_{post_date}_{len(all_items)}",
            "platform": "Facebook (Forense Titulado)",
            "author": "Joseph Allen Brewer ('Joe Brewer')",
            "date_iso": post_date,
            "timestamp_raw": post_date,
            "permalink": post_url,
            "content_en": text_en,
            "content_es": text_es,
            "media_urls": [forensic_img],
            "metrics": {"reactions": "N/A", "comments": "N/A", "shares": "N/A"},
            "comments": [],
            "forensic_classification": forensic_class,
            "forensic_file": fname,
            "source": "solo_facebook_forensic"
        }
        all_items.append(new_item)
        enriched_count += 1

print(f"Enriquecidos o anadidos {enriched_count} registros de evidencia forense detallada.")

# 3. Patreon
patreon_file = os.path.join(PRUEBAS_DIR, '2026-08-02 - patreon_liberacion_financiera_y_bienes_comunes.txt')
if os.path.exists(patreon_file):
    try:
        raw_p = open(patreon_file, 'r', encoding='utf-8', errors='ignore').read()
        all_items.append({
            "id": "patreon_2026_08_02",
            "platform": "Patreon / Crowdfunding",
            "author": "Joseph Allen Brewer ('Joe Brewer')",
            "date_iso": "2026-08-02",
            "timestamp_raw": "2026-08-02",
            "permalink": "https://www.patreon.com/joe_brewer",
            "content_en": raw_p,
            "content_es": "Llamado a liberacion financiera, despojo de responsabilidades y captura de fondos para supuestos bienes comunes comunitarios bajo control autocratico.",
            "media_urls": ["2026-08-02 - patreon_liberacion_financiera_y_bienes_comunes.png"],
            "metrics": {"reactions": "N/A", "comments": "N/A", "shares": "N/A"},
            "comments": [],
            "forensic_classification": "Captacion de Fondos y Evasion de Responsabilidades Financieras",
            "forensic_file": "2026-08-02 - patreon_liberacion_financiera_y_bienes_comunes.txt",
            "source": "patreon_evidence"
        })
    except Exception:
        pass

all_items.sort(key=lambda x: str(x.get("date_iso", "")))

# Guardar JSON
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(all_items, f, indent=2, ensure_ascii=False)
print(f"Guardado archivo JSON unificado con {len(all_items)} elementos en {OUTPUT_JSON}")

# Guardar MD
with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
    f.write("# 🏛️ EXPEDIENTE FORENSE Y REGISTRO DIGITAL PÚBLICO INTEGRAL\n")
    f.write("## RASTRO DOCUMENTAL COMPLETO DE JOSEPH ALLEN BREWER ('JOE BREWER')\n")
    f.write("### Auditoría Forense Periodística y Material Probatorio — Desk Clement Vane\n\n")
    f.write(f"- **Total de publicaciones y registros indexados:** {len(all_items)}\n")
    f.write("- **Período analizado:** 2022 — 2026\n")
    f.write("- **Plataformas documentadas:** Facebook, Patreon, Substack y Declaraciones Públicas.\n")
    f.write("- **Finalidad:** Desmitificación, perfilamiento de modus operandi, preservación probatoria para autoridades e investigación de interés público.\n\n")
    f.write("---\n\n")
    
    for i, it in enumerate(all_items, 1):
        f.write(f"### [{i:03d}] {it['date_iso']} | {it['platform']} | {it.get('forensic_classification') or 'Declaración Pública'}\n\n")
        f.write(f"- **URL / Permalink:** {it.get('permalink') or 'N/A'}\n")
        f.write(f"- **Fecha / Timestamp:** {it.get('timestamp_raw')}\n")
        if it.get('forensic_file'):
            f.write(f"- **Archivo Forense Original:** `{it.get('forensic_file')}`\n")
        if it.get('media_urls'):
            f.write(f"- **Adjuntos / Multimedia:** {', '.join(it['media_urls'])}\n")
        if it.get('metrics'):
            m = it['metrics']
            f.write(f"- **Métricas de Interacción:** Reacciones: {m.get('reactions')}, Comentarios: {m.get('comments')}, Compartidos: {m.get('shares')}\n")
        
        f.write("\n#### 📜 Contenido Completo Original (Inglés):\n```text\n")
        f.write(it.get('content_en', '').strip())
        f.write("\n```\n\n")
        
        if it.get('content_es'):
            f.write("#### 🌐 Traducción / Síntesis Forense (Español):\n")
            f.write(it.get('content_es', '').strip())
            f.write("\n\n")
            
        if it.get('comments'):
            f.write("#### 💬 Comentarios e Interacciones Destacadas:\n")
            for c_idx, c_obj in enumerate(it['comments'][:5], 1):
                txt = c_obj.get("text", str(c_obj))
                f.write(f"> **{c_idx}.** {txt.strip()}\n>\n")
            f.write("\n")
            
        f.write("---\n\n")

print(f"Guardado expediente Markdown en {OUTPUT_MD}")
