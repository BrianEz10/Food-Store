# 🚨 IMPORTANTE LEER: Memoria de IA (Engram)

Este proyecto utiliza **Engram** como sistema de memoria persistente para los agentes de Inteligencia Artificial (IA). 

Esto significa que todas las decisiones de arquitectura, correcciones de bugs importantes, comandos y convenciones del equipo se guardan en la carpeta oculta `.engram/` para que la IA tenga el contexto completo de todo lo que se hizo antes, sin importar quién lo hizo.

---

## 🚀 1. Instalación de Engram
Para que la memoria funcione en tu computadora local, primero tenés que tener instalado el motor de Engram.

**Usando Go (Cualquier sistema):**
```bash
go install github.com/Gentleman-Programming/engram/cmd/engram@latest
```

---

## 🧠 2. Cómo importar el cerebro del proyecto
Cuando clonas este repositorio por primera vez, tu IA local no sabe nada del proyecto. Para inyectarle todo el historial a tu computadora, ejecutá este comando estando en la raíz del proyecto:

```bash
engram sync --import
```

> **Nota:** Engram es inteligente. Si ejecutás este comando varias veces, **no duplicará los datos**. El sistema verifica qué información ya tenés cargada en tu base global y solo insertará lo que sea nuevo.

---

## 💾 3. Cómo compartir tus nuevos cambios
Cuando termines de trabajar y tu IA haya guardado nuevas memorias (o si vos forzaste un guardado de decisiones), tenés que exportar esa nueva memoria para que nosotros también la tengamos.

Antes de hacer tu commit habitual, corré:

```bash
engram sync
```

Esto va a actualizar la carpeta `.engram/` con tu progreso. Luego, simplemente subílo a Git:

```bash
git add .engram/
git commit -m "chore: sync IA memory"
git push
```

---

## 🔍 Comandos útiles
Si querés curiosear qué cosas se decidieron en la IA o qué memorias existen, podés abrir la interfaz interactiva en la consola ejecutando:

```bash
engram tui
```

---

## 💬 4. Cómo pedirle a la IA que use la memoria
Una vez que hayas instalado e importado la memoria (Pasos 1 y 2), para que la IA sepa qué tiene que hacer, pegá este prompt al inicio de un nuevo chat:

> **"Hola. Estoy trabajando en el proyecto Food Store. Por favor, usá tu herramienta de Engram para buscar las memorias relacionadas con este proyecto (buscá por los nombres 'brian-palacios' o 'food-store') y haceme un resumen detallado de lo que se hizo hasta ahora y qué es lo próximo que tenemos que programar según el mapa de cambios."**
