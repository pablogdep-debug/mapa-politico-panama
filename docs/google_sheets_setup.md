# Configuración privada de Google Sheets

La aplicación usa una cuenta de servicio y secretos de Streamlit. Ninguna
credencial debe guardarse en Git.

1. En Google Cloud, crea o elige un proyecto.
2. Activa **Google Sheets API**.
3. Crea una cuenta de servicio y descarga temporalmente su clave JSON.
4. Crea dos hojas privadas:
   - `Brújula Democrática — Respuestas anónimas`, con pestaña `responses`.
   - `Brújula Democrática — Correos`, con pestaña `subscribers`.
5. Comparte ambas hojas con el `client_email` de la cuenta de servicio como
   editor.
6. Copia los IDs de las hojas desde sus URL.
7. Usa [secrets.example.toml](secrets.example.toml) como guía y coloca los
   valores reales:
   - localmente en `.streamlit/secrets.toml`;
   - en producción, en **Streamlit Community Cloud > App settings > Secrets**.
8. Elimina de tu equipo el JSON descargado cuando ya hayas copiado sus valores
   al gestor de secretos.
9. Reinicia la aplicación. En la primera escritura, si la pestaña está vacía,
   la aplicación añadirá los encabezados. Si ya contiene encabezados, deben
   coincidir exactamente con el contrato de la aplicación.
10. Completa un cuestionario de prueba y verifica una fila en `responses`.
    Después registra un correo de prueba y verifica que `subscribers` contenga
    únicamente correo, fecha de consentimiento, origen y estado.

Si los secretos faltan o hay un problema de acceso, el resultado político
seguirá mostrándose y la interfaz permitirá reintentar. No se mostrará un éxito
falso.
