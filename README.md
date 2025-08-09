# App Scraping

## ¿Qué hace?

Esta app automatiza las consultas que normalmente harías manualmente en las páginas oficiales:

- **SIMIT**: Busca comparendos y multas de tránsito
- **Antecedentes Policía**: Revisa si tienes antecedentes penales

Todo desde una interfaz oscura y moderna.

## Requisitos

- Python 3.7+
- Chrome o Chromium instalado
- Un poco de paciencia para el CAPTCHA de la Policía

## Instalación

1. Clona este repositorio:

```bash
git clone <tu-repo>
cd appscraping
```

2. Instala las dependencias:

```bash
pip install -r app/requirements.txt
```

1. Ejecuta la aplicación:

```bash
cd app
python app.py
```

1. Abre tu navegador en `http://localhost:5000`

## Cómo usar

1. Llena el formulario con tus datos
2. Selecciona qué quieres consultar (o déjalo todo marcado)
3. Dale click a "Consultar"
4. Para la consulta de Policía, tendrás que resolver el CAPTCHA manualmente
5. Espera los resultados y descarga el PDF si quieres

## Importante

- Esta app usa Selenium, así que verás ventanas del navegador abriéndose
- La consulta de Policía requiere interacción manual para el CAPTCHA
- Los datos no se guardan en ningún lado, solo en la sesión mientras usas la app

## Estructura

```
C:\USERS\USUARIO\DOCUMENTS\APPSCRAPING

├───app
│   ├───CSS
│   ├───data
│   ├───static
│   │   └───pdfs
│   ├───templates
└───pdfs
```

## Problemas comunes

**El navegador no se abre**: Asegúrate de tener Chrome instalado.

**No funciona el CAPTCHA**: Es manual, tienes que resolverlo tú mismo cuando aparezca la ventana.

**Error de dependencias**: Revisa que instalaste todo con `pip install -r requirements.txt`.

## Contribuir

Si encuentras bugs o tienes ideas para mejorar, dejamelo saber.
