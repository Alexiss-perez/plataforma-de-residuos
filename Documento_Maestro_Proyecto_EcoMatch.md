# Documento Maestro del Proyecto: Plataforma EcoMatch ♻️

Este documento es la **fuente de verdad** para todo el equipo. Define qué vamos a construir, cómo lo vamos a hacer, los roles de cada integrante y los criterios con los que seremos evaluados.

---

## 1. Visión del Proyecto

**EcoMatch** es una plataforma web de economía circular enfocada en la reducción de residuos. Su objetivo es conectar de forma inteligente a generadores de residuos (constructoras, pymes, personas) con receptores que puedan aprovecharlos (ONGs, plantas de reciclaje, otras pymes).

El "cerebro" de la plataforma es un **Agente de IA (orquestador logístico)** potenciado por el modelo **GLM 5.2**, capaz de entender las ofertas de residuos, buscar *matches* en la base de datos, lidiar con ambigüedades en la información del usuario y coordinar la logística.

---

## 2. Criterios de Éxito (Rúbrica de Evaluación)

Todo el desarrollo debe estar enfocado en maximizar este puntaje:
*   **30% - Tareas exitosas/correctas:** El flujo principal (publicar residuo -> hacer match -> coordinar retiro) debe funcionar sin errores.
*   **25% - Comportamiento del agente y autonomía:** El agente debe guiar al usuario para completar el proceso sin necesidad de intervención humana.
*   **15% - Uso de herramientas y orquestación:** El agente debe consumir APIs externas (ej. Base de datos, API de Mapas para logística).
*   **10% - Gestión de la ambigüedad y fallos:** Si un usuario da información incompleta (ej. *"Tengo madera"*), el agente debe repreguntar inteligentemente (*"¿Es madera tratada o virgen? ¿Cuántos kilos tienes?"*).
*   **10% - Fiabilidad y prevención de alucinaciones:** El agente **NUNCA** debe inventar empresas, direcciones o leyes. Solo opera con los datos reales que le provee nuestro Backend.
*   **5% - Experiencia de usuario (UX):** Interfaz limpia, accesible y fácil de entender.
*   **5% - Creatividad:** Propuesta de valor innovadora en la solución logística.

---

## 3. Arquitectura del Sistema

La plataforma se dividirá en 3 capas principales:

1.  **Frontend (Interfaz Web):** Pantallas de registro, panel de control de la empresa y la interfaz de chat (o formulario asistido) donde interactúan con el Agente.
2.  **Backend (API & Base de Datos):** El servidor que almacena los usuarios, el inventario de residuos, y maneja la seguridad (Login/Tokens).
3.  **Capa de Inteligencia Artificial (GLM 5.2):** Se comunica con el backend. Recibe el texto del usuario, extrae las intenciones (parsing), decide si necesita usar herramientas (Function Calling) y devuelve respuestas estructuradas.

---

## 4. El Agente de IA: "EcoMatch"

**Flujo de Trabajo del Agente:**
1.  **Ingreso:** El usuario escribe *"Tenemos escombros de una demolición en Av. Principal 123"*.
2.  **Análisis (GLM 5.2):** El modelo detecta que es una *oferta de residuo*. Detecta material (*escombros*) y dirección, pero nota que falta el volumen.
3.  **Gestión de Ambigüedad:** El agente responde: *"Perfecto. Para encontrar el transporte adecuado, ¿podrías indicarme el volumen aproximado en metros cúbicos o toneladas?"*.
4.  **Uso de Herramientas:** Una vez completados los datos, el agente invoca una función del Backend: `buscar_receptores(material="escombros", radio_km=10)`.
5.  **Cierre:** El agente presenta las opciones reales que devolvió la base de datos y pregunta si el usuario desea agendar el retiro.

---

## 5. Roles y Responsabilidades del Equipo (7 Integrantes)

Para lograr el éxito, cada integrante es dueño de una pieza clave:

*   **1. Project Manager / Product Owner:** Administra el tablero de tareas (GitHub Projects). Asegura que nadie se desvíe del MVP (Producto Mínimo Viable) y que todas las tareas sumen puntos a la rúbrica.
*   **2. Ingeniero de IA (Especialista en GLM 5.2):** Dueño del *System Prompt*. Diseña cómo el modelo razona, configura el *Function Calling* para que el modelo entienda cómo buscar en la base de datos, y asegura la política de "Cero Alucinaciones".
*   **3. Desarrollador Backend:** Diseña la base de datos relacional (Usuarios, Ofertas, Demandas, Transacciones) y crea los *endpoints* (API REST) que consumirán el Frontend y el Agente.
*   **4. Desarrollador Frontend:** Construye la página web. Debe enfocarse en que el chat o interacción con el agente sea fluido (manejo de estados de carga, errores, diseño responsivo).
*   **5. Ingeniero de Integraciones:** Investiga, obtiene *API Keys* y conecta servicios de terceros. (Ej. Google Maps API para mostrar rutas entre generador y receptor, o SendGrid para enviar emails de confirmación).
*   **6. Diseñador UX/UI:** Dibuja los *wireframes* (bocetos) antes de programar. Define la paleta de colores (ej. tonos verdes/tierra) y la disposición de los botones para una buena Experiencia de Usuario (5%).
*   **7. QA, Tester & DevOps:** Configura el repositorio de GitHub (protección de ramas). Realiza pruebas de estrés chateando con el agente con frases confusas para verificar que la "Gestión de Ambigüedad" funciona correctamente (10%).

---

## 6. Flujo de Trabajo (Metodología)

*   **Herramientas Base:** GitHub para código y tareas. OpenCode como asistente de programación en sus editores locales.
*   **Regla de Ramas:**
    *   `main` (o `master`): Solo contiene código funcional y probado. Nadie programa aquí directamente.
    *   Nuevas tareas: Se crea una rama (ej. `feature/login-ui`, `backend/db-schema`).
    *   Una vez terminada la tarea, se abre un **Pull Request (PR)** para que otro integrante del equipo revise el código antes de unirlo a `main`.

---

## 7. Plan de Acción Inmediato (Sprint 1)

Para arrancar HOY, estas son las primeras tareas por rol:

*   **[ PM ]**: Crear la Organización en GitHub, los repositorios vacío y el tablero Kanban con estas tareas.
*   **[ UX/UI ]**: Crear el boceto en Figma o papel de 3 pantallas clave: Login, Dashboard, e Interfaz de Chat con el Agente.
*   **[ Backend ]**: Definir en un documento el diagrama de la Base de Datos (qué columnas tendrá la tabla `User` y la tabla `Residuo`).
*   **[ Frontend ]**: Inicializar el proyecto base (ej. usando Vite/React o el framework elegido) y subir el *Hello World* al repositorio.
*   **[ IA ]**: Abrir un entorno de pruebas para GLM 5.2 (Playground o un script local de Python) y empezar a escribir el *System Prompt* base para ver cómo reacciona el modelo a textos de reciclaje.
*   **[ Integraciones ]**: Buscar qué API gratuita servirá mejor para calcular distancias (Google Maps, OpenStreetMap, Mapbox) y crear la cuenta.
*   **[ QA/DevOps ]**: Redactar un documento con 10 "casos de prueba" difíciles (prompts confusos) que usaremos más adelante para evaluar al agente.
