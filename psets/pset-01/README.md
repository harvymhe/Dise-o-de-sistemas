# ReservaU - Sistema de Gestión de Canchas Deportivas

Implementación del dominio para el sistema **ReservaU**, diseñado bajo los principios de **Clean Architecture** y **Domain-Driven Design (DDD)**.

## Requerimientos Funcionales (RF) Implementados
El sistema valida y ejecuta de forma determinista los siguientes flujos mediante una simulación:
1. **RF-01**: Gestión de perfiles de usuario (Estudiantes y Capitanes de equipo).
2. **RF-02**: Regla de Prioridad Horaria mediante el patrón de diseño *Strategy*.
3. **RF-03 & RF-06**: Máquina de estados para reservas (Activa, Cancelada, No-Show según el margen de 2 horas).
4. **RF-04**: Configuración y gestión de estados de infraestructura (Canchas).
5. **RF-05**: Objetos de valor inmutables para el control de rangos horarios.
6. **RF-07**: Resolución automática de conflictos por solapamiento de horarios y prioridades.
7. **RF-08**: Sistema de penalizaciones automáticas (Strikes) y suspensión de usuarios al acumular 3 faltas.

## Ejecución de Docker
Para ejecutar la simulación de manera portable sin necesidad de configurar un entorno de Python localmente:

```bash
docker build -t reservau-app .
docker run --rm reservau-app