# GUÍA MAESTRA DE AUTOMATIZACIÓN 100% PARA CLEMENT VANE
## Publicación Continua y Multiplicación en Twitter/X, Hashnode, Reddit y Medium

---

### 1. BUFFER (Twitter / X Automático)
Ya conectaste Twitter y Substack en Buffer. Para que cada nuevo ensayo o los 10 ensayos actuales salgan automáticamente a Twitter:

1. **Activar el Feed RSS en Buffer Publish:**
   - En tu Chrome abierto en Buffer (`https://publish.buffer.com`), ve a **Content / Feeds** (o en la barra lateral izquierda bajo el canal de Twitter de `@clementvane`).
   - Si no está agregado, añade el feed nativo de Substack:
     `https://clementvane.substack.com/feed`
   - Buffer detectará automáticamente los 10 artículos existentes en el feed.
2. **Programación Automática (Queue):**
   - En la pestaña de configuración del canal en Buffer, define la frecuencia (ej. 2 o 3 publicaciones diarias).
   - Haz clic en **"Add to Queue"** sobre los 10 ensayos detectados. Buffer los irá despachando automáticamente a `@clementvane` con su título, enlace y vista previa sin que tengas que tocar nada más.

---

### 2. HASHNODE (GitHub Integration Backup / Headless CMS)
Hashnode eliminó el importador RSS en su UI web y bloqueó las consultas anónimas de GraphQL. La forma oficial y 100% automatizada que utiliza la comunidad de desarrolladores en GitHub es:

* **Sincronización por GitHub Repo (Markdown Nativo):**
  1. Hashnode permite conectar un repositorio de GitHub para publicar automáticamente mediante commits (`Hashnode Backup / GitHub Integration`).
  2. Cada archivo `.md` de la carpeta `/home/juan/Datos/Datos Juan/Documentos/his former partner/Caso Joseph/` con frontmatter se sincroniza directamente y Hashnode lo publica al detectar el commit.
  3. Puedes conectar tu repositorio en: `https://hashnode.com/settings/integrations`.

---

### 3. ZAPIER / MAKE / IFTTT (El Conector Global Gratuito)
Para una automatización "Set & Forget" (configura una vez y olvídate para siempre):

1. **Trigger:** **RSS by Zapier** (o IFTTT RSS).
   - Feed URL: `https://clementvane.substack.com/feed`
2. **Acción 1:** **Twitter / X** -> Publicar Tweet:
   `New dispatch by Clement Vane: {{title}} {{link}} #Bioregionalism #Ecology`
3. **Acción 2:** **Reddit** -> Publicar Link Post en `r/bioregionalism` o en tu perfil `u/ClementVane`.
4. **Acción 3:** **Medium** -> Create Story (con canonical URL apuntando a Substack).

Cada vez que nuestro script `publish_all_essays.py` o un subagente redacte y publique un nuevo ensayo en Substack, la cadena entera se disparará automáticamente en todas las redes.

---

### 4. REPOSITORIO DE CONTROL LOCAL
* **Publicador Substack 1-Clic:** `python3 /home/juan/Datos/Datos\ Juan/Documentos/his former partner/Caso\ Joseph/publish_all_essays.py`
* **Catálogo Maestro:** [00_INDEX_AND_PUBLISHING_GUIDE.md](file:///home/juan/Datos/Datos%20Juan/Documentos/his former partner/Caso%20Joseph/00_INDEX_AND_PUBLISHING_GUIDE.md)
* **Plantillas de Hilos X:** [twitter_distribution_kit.md](file:///home/juan/Datos/Datos%20Juan/Documentos/his former partner/Caso%20Joseph/twitter_distribution_kit.md)
* **Kit de Reddit:** [reddit_syndication_kit.md](file:///home/juan/Datos/Datos%20Juan/Documentos/his former partner/Caso%20Joseph/reddit_syndication_kit.md)
