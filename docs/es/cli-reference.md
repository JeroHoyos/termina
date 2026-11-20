# Referencia de comandos

[English](../cli-reference.md) | **Español**

Los comandos hacen el mismo trabajo que la app y el panel web.

## Correr un comando

Desde la carpeta `termina`:

```powershell
.\studio <comando>
```

Desde la carpeta de charlas:

```powershell
uv run --no-project termina/engine/studio.py <comando>
```

El motor usa solo la biblioteca estándar de Python. No necesita un entorno de proyecto.

## Comandos para la lista de charlas

| Comando | Resultado |
| --- | --- |
| `studio` | Abre el panel web en el navegador. |
| `studio panel --no-browser` | Arranca el panel web sin abrir el navegador. |
| `studio talks [--json]` | Lista las charlas con la carpeta de cada una. |
| `studio import <archivo> [--in <carpeta>] [--folder <nombre>] [--json]` | Hace una charla desde un archivo de PowerPoint (`.pptx`) o de Beamer (`.tex`). Cada página pasa a ser una diapositiva. |
| `studio open <carpeta> [--json]` | Agrega a la lista la charla que está en `<carpeta>`. |
| `studio new-talk "<título>" [opciones]` | Crea una charla con una diapositiva de título y una de cierre. |
| `studio help` | Muestra la ayuda. |

Opciones de `new-talk`:

| Opción | Por defecto | Resultado |
| --- | --- | --- |
| `--about "<texto>"` | vacío | De qué trata la charla. |
| `--language <código>` | `es` | El idioma de las diapositivas, por ejemplo `en`. |
| `--in <carpeta>` | la carpeta de charlas | La carpeta donde queda la charla nueva. Escribe la ruta completa. |
| `--folder <nombre>` | `charla-<título>` | El nombre de la carpeta de la charla. |
| `--json` | | Escribe el resultado como JSON. |

## Comandos para una charla

`<charla>` es el nombre que da `studio talks`, por ejemplo `charla-git`. El prefijo `charla-` es
opcional. `<diapositiva>` es el nombre o el número de una diapositiva en `studio <charla> list`.

| Comando | Resultado |
| --- | --- |
| `studio <charla> list` | Lista las diapositivas con su estado. Es el comando por defecto. |
| `studio <charla> status` | Escribe el estado de la charla como JSON. |
| `studio <charla> info [--json]` | Muestra los campos de `talk.manimrs`. |
| `studio <charla> info --<campo> "<valor>"` | Cambia campos de `talk.manimrs`: `title`, `about`, `author`, `language`, `resolution`. |
| `studio <charla> forget` | Quita la charla de la lista. Los archivos de la charla no cambian. |
| `studio <charla> render <diapositiva>...` | Renderiza solo esas diapositivas. |
| `studio <charla> render --pending` | Renderiza las diapositivas que no están al día. |
| `studio <charla> render --all` | Renderiza todas las diapositivas. |
| `studio <charla> present [<diapositiva>]` | Presenta las diapositivas que tienen video, desde `<diapositiva>`. |
| `studio <charla> export [--pdf]` | Hace el paquete HTML y su `.zip`, o un PDF con una página por pausa. |
| `studio <charla> export --mp4 [<diapositiva>]` | Hace un video de la charla, o de una diapositiva. Un bucle se reproduce una vez. |
| `studio <charla> export --gif <diapositiva>` | Hace un GIF de una diapositiva, de 960 píxeles de ancho. |
| `studio <charla> stills <diapositiva> [--width <píxeles>]` | Hace una imagen PNG del final de cada pausa. |
| `studio <charla> notes` | Lista los cambios pedidos en la revisión. |
| `studio <charla> note <diapositiva> "<texto>"` | Escribe una petición de cambio para la diapositiva. |
| `studio <charla> note <diapositiva> --approve` | Aprueba la diapositiva. |
| `studio <charla> note <diapositiva> --clear` | Quita la revisión de la diapositiva. |
| `studio <charla> new "<nombre>" [--after <diapositiva>]` | Crea, registra y pone una diapositiva nueva en la charla. |
| `studio <charla> place slide_<nombre> [--after <diapositiva>]` | Pone en `main.py` una diapositiva ya registrada. |
| `studio <charla> move <diapositiva> --after <diapositiva>` | Mueve una diapositiva. Usa `--first` para dejarla de primera. |
| `studio <charla> rename <diapositiva> "<nombre nuevo>"` | Renombra una diapositiva y sus videos. |
| `studio <charla> group <diapositiva> "<nombre>"` | Empieza un grupo de diapositivas en la diapositiva. Sin nombre, quita el grupo que empieza ahí. |
| `studio <charla> duplicate <diapositiva> ["<nombre nuevo>"]` | Hace una copia de una diapositiva después de ella. Sin nombre, la copia es `<diapositiva>_copy`. |
| `studio <charla> hide <diapositiva>` | Comenta la llamada de una diapositiva en `main.py`. La charla no la muestra. Su archivo y sus videos se quedan. |
| `studio <charla> source <diapositiva> [--from <archivo>]` | Escribe el código de una diapositiva como JSON. Con `--from`, cambia el código por el contenido de `<archivo>`. No acepta código con un error de sintaxis. |
| `studio <charla> find "<texto>" [--replace "<texto>"]` | Busca texto en las diapositivas y en las notas del orador, y escribe las coincidencias como JSON. Con `--replace`, reemplaza cada coincidencia. |
| `studio <charla> speaker [--pause <n>] <diapositiva> ["<texto>"]` | Guarda las notas del orador de una diapositiva. Sin texto, las quita. Con `--pause`, las notas son solo de esa pausa (desde 1). |
| `studio <charla> theme [<nombre>]` | Muestra los colores de las diapositivas, o los cambia: `dark`, `light`, `night` o `paper`. |
| `studio <charla> info --numbers on` | Pone un número de página en cada diapositiva. Usa `off` para quitarlo. |
| `studio <charla> export --narrated` | Hace un video donde una voz dice las notas del orador de cada pausa. |
| `studio <charla> objects <diapositiva>` | Escribe lo que muestra una diapositiva renderizada en cada pausa, como JSON. |
| `studio <charla> move-object <diapositiva> --pause <n> --index <n> --by=<dx,dy>` | Mueve un objeto de una diapositiva. La pausa y el índice salen de `objects` (desde 0). La distancia va en unidades de Manim. |
| `studio <charla> retext <diapositiva> "<viejo>" "<nuevo>"` | Cambia un texto de una diapositiva en su código. |
| `studio <charla> insert <diapositiva> --kind <tipo> --pause <n> --at=<x,y>` | Agrega un elemento a una diapositiva: `text`, `formula`, `rectangle`, `circle`, `arrow`, `sphere`, `cube`, `axes`, o `picture` con `--file <ruta>`. |
| `studio <charla> export --pptx` | Hace un archivo de PowerPoint. Cada pausa es una página con su video y las notas del orador. |
| `studio <charla> export --package` | Hace un `.zip` con el código y los videos de la charla, para otro Termina. |
| `studio <charla> restore <diapositiva>` | Quita el comentario de la llamada de una diapositiva en `main.py`. |
| `studio <charla> delete <diapositiva>` | Quita una diapositiva. Su archivo va a la papelera. |
| `studio <charla> resolution <diapositiva> <valor>` | Fija la resolución de una diapositiva: `480p`, `720p`, `1080p` o `default`. |

Opciones para una charla:

| Opción | Comandos | Resultado |
| --- | --- | --- |
| `--quality 480p\|720p\|1080p` | `render` | La resolución del render. Por defecto es la de la charla. Una diapositiva con resolución propia la conserva. |
| `--line <número>` | `move`, `rename`, `group`, `duplicate`, `hide`, `restore`, `delete`, `resolution`, `speaker` | Elige la diapositiva por su línea en `main.py` (desde 0). También sirve para una diapositiva comentada. |
| `--case`, `--word`, `--regex` | `find` | Las mayúsculas deben coincidir. Solo palabras completas. El texto es una expresión regular. |
| `--json` | `info`, `new`, `talks`, `open`, `new-talk`, `import` | Escribe el resultado como JSON. |

## Ejemplos

Renderizar dos diapositivas a 480p:

```powershell
.\studio git render 3 git_diff --quality 480p
```

Agregar una diapositiva después de `git_diff`:

```powershell
.\studio git new "git stash" --after git_diff
```

## Errores

Si un comando no puede hacer su trabajo, escribe `Error:` y la causa, y termina con un código
distinto de cero. El motor no cambia archivos cuando la entrada no es correcta.
