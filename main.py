import os
from dotenv import load_dotenv
from strands import Agent, tool
from strands_tools import calculator

load_dotenv()

@tool
def check_kids_schedule(activity_name: str, day_of_week: str, time_slot: str) -> str:
    """Verifica si hay conflictos en la agenda semanal de los niños (Gerardo de 5 años: natación, ajedrez, futbol, karate 2x semana; Isabella de 2 años: guardería)."""
    schedule = {
        "Lunes": ["Guardería (Isabella)", "Ajedrez (Gerardo - 6:00 PM)"],
        "Martes": ["Guardería (Isabella)", "Karate (Gerardo - 4:00 PM)"],
        "Miércoles": ["Guardería (Isabella)", "Ajedrez (Gerardo - 6:00 PM)"],
        "Jueves": ["Guardería (Isabella)", "Karate (Gerardo - 4:00 PM)"],
        "Viernes": ["Guardería (Isabella)", "Futbol (Gerardo - 5:00 PM)"],
        "Sábado": ["Natación (Gerardo - 11:00 AM)"],
    }
    
    day = day_of_week.lower()
    if day in schedule:
        existing_activities = schedule[day]
        for act in existing_activities:
            if time_slot.lower() in act.lower() or day in ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]:
                return f"CONFLICTO DE AGENDA el {day} a las {time_slot}: Ya se encuentra programado '{act}' para los niños. Choca con la nueva actividad propuesta: '{activity_name}'."
    return f"Agenda libre el {day} para la actividad: '{activity_name}'."

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