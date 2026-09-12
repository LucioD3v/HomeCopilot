"""Legacy CLI prototype. The supported product entry point is app.py."""

import os
import re
import unicodedata
from dotenv import load_dotenv
from strands import Agent, tool
from strands_tools import calculator

load_dotenv()

@tool
def check_kids_schedule(activity_name: str, day_of_week: str, time_slot: str) -> str:
    """Detecta solapamientos reales entre actividades del mismo día."""
    schedule = {
        "lunes": [("Guardería (Isabella)", 8 * 60, 15 * 60)],
        "martes": [("Guardería (Isabella)", 8 * 60, 15 * 60), ("Karate (Gerardo)", 16 * 60, 17 * 60)],
        "miercoles": [("Guardería (Isabella)", 8 * 60, 15 * 60), ("Ajedrez (Gerardo)", 18 * 60, 19 * 60)],
        "jueves": [("Guardería (Isabella)", 8 * 60, 15 * 60), ("Karate (Gerardo)", 16 * 60, 17 * 60)],
        "viernes": [("Guardería (Isabella)", 8 * 60, 15 * 60), ("Futbol (Gerardo)", 17 * 60, 18 * 60)],
        "sabado": [("Natación (Gerardo)", 11 * 60, 12 * 60)],
    }

    day = _normalize_day(day_of_week)
    proposed_start, proposed_end = _parse_time_range(time_slot)
    if proposed_start is None:
        return f"No pude interpretar el horario '{time_slot}' para el día {day_of_week}."

    for activity, start, end in schedule.get(day, []):
        if proposed_start < end and start < proposed_end:
            return (
                f"CONFLICTO DE AGENDA el {day_of_week} de {time_slot}: "
                f"'{activity}' ocupa el intervalo {start // 60:02d}:{start % 60:02d}-"
                f"{end // 60:02d}:{end % 60:02d}. "
                f"Choca con '{activity_name}'."
            )
    return f"Agenda libre el {day_of_week} para la actividad: '{activity_name}'."


def _normalize_day(day_of_week: str) -> str:
    normalized = unicodedata.normalize("NFD", day_of_week.strip().lower())
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def _parse_time_range(time_slot: str) -> tuple[int | None, int | None]:
    matches = re.findall(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", time_slot.lower())
    if not matches:
        return None, None

    times = []
    for hour_text, minute_text, meridiem in matches[:2]:
        hour = int(hour_text)
        minute = int(minute_text or 0)
        if meridiem == "pm" and hour < 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0
        if hour > 23 or minute > 59:
            return None, None
        times.append(hour * 60 + minute)

    start = times[0]
    end = times[1] if len(times) == 2 else start + 60
    if end <= start:
        end += 12 * 60 if end == start else 24 * 60
    return start, end

@tool
def check_home_office_workload(task_description: str, estimated_hours: float) -> str:
    """Evalúa si una tarea del hogar o logística puede integrarse en la jornada de trabajo remoto sin descuidar las entregas profesionales."""
    max_daily_chores_hours = 2.0
    if estimated_hours > max_daily_chores_hours:
        return f"ALERTA DE CARGA MENTAL: La tarea '{task_description}' requiere {estimated_hours} horas, superando el límite diario de {max_daily_chores_hours}h asignado a tareas del hogar durante la jornada de Home Office. Sugiero delegar o posponer."
    return f"Distribución de tiempo óptima: '{task_description}' ({estimated_hours}h) cabe perfectamente en los espacios libres de la jornada laboral en casa."

def main():
    print("--- 🛡️ Inicializando HomeCopilot (Strands SDK + Claude) ---")
    
    agent = Agent(
        model="global.anthropic.claude-sonnet-4-6",
        system_prompt="""Eres HomeCopilot, un agente autónomo de logística familiar y reducción de carga mental para padres que trabajan desde casa.
        Conoces perfectamente la estructura familiar:
        - Gerardo (5 años): Tiene clases de natación, ajedrez, futbol y karate (2 veces por semana: martes y jueves).
        - Isabella (2 años): Asiste a la guardería de lunes a viernes.
        - Trabajas desde casa, por lo que debes equilibrar llamadas de trabajo, tareas del hogar y las idas y venidas de las actividades de los niños.
        Actúa de forma proactiva, detecta choques de horarios entre las actividades de los niños y alerta si las tareas del hogar saturan la jornada laboral. Sé conversacional, natural y ofrece soluciones útiles.""",
        tools=[calculator, check_kids_schedule, check_home_office_workload]
    )

    print("\n¡Hola! Soy HomeCopilot. Estoy listo para ayudarte a coordinar el día.")
    print("(Escribe 'salir' para terminar la conversación)\n")
    
    # Bucle infinito para mantener la conversación activa
    while True:
        prompt_usuario = input("[Tú]: ")
        
        # Condición para salir del programa
        if prompt_usuario.lower() in ['salir', 'exit', 'quit']:
            print("\n[HomeCopilot]: ¡Hasta luego! Que tengas un excelente día y un turno productivo.")
            break
            
        # El agente procesa la entrada y responde
        response = agent(prompt_usuario)
        print(f"\n[HomeCopilot]:\n{response}\n")

if __name__ == "__main__":
    main()