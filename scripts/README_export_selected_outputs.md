Exportar notebook a HTML manteniendo sólo outputs seleccionados

Uso

- Marca las celdas de código que quieres mantener con la etiqueta `export_output` (añádela en la metadata > tags), o añade `"export_output": true` en la metadata de la celda.
- Alternativamente: coloca al inicio de la celda de código un comentario `#mostar` o `#mostrar` — el script detectará ese comentario y tratará la celda como etiquetada.
- Ejecuta el script desde PowerShell:

Comportamiento respecto al código
- El script elimina (vacía) el contenido de todas las celdas de código antes de ejecutar `nbconvert`.
- Resultado: el HTML final **no mostrará** bloques de código; solo conservará el texto (celdas Markdown) y los outputs de las celdas marcadas con `#mostrar` o la tag `export_output`.

```powershell
python .\scripts\export_selected_outputs.py --notebook .\Informe_Final_(4).ipynb --output .\Informe_filtrado.html --tag export_output
```

Parámetros
- `--notebook` (`-n`): ruta al archivo `.ipynb` de entrada.
- `--output` (`-o`): ruta al archivo `.html` de salida.
- `--tag` (`-t`): etiqueta a buscar en las celdas (por defecto `export_output`).

Notas
- El script requiere `nbformat` y `nbconvert` (ya incluidos en `requirements.txt` de este repositorio).
- El script crea una copia temporal del notebook con los outputs limpiados y usa `nbconvert` para generar el HTML.
