import datetime
import os
import urllib.parse
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from strands import Agent, tool
from strands_tools import calculator

load_dotenv()

# --- DETECCIÓN REAL DE DÍA Y FECHA ---
now = datetime.datetime.now()
days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
days_en = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

current_day_es = days_es[now.weekday()]
current_day_en = days_en[now.weekday()]
current_date_str = now.strftime("%Y-%m-%d")

# --- GESTIÓN DE IDIOMA Y TRADUCCIONES UI ---
if "language" not in st.session_state:
  st.session_state.language = "Español"

language = st.sidebar.selectbox(
    "🌐 Language / Idioma",
    ["English", "Español"],
    index=0 if st.session_state.language == "English" else 1,
)

if language != st.session_state.language:
  st.session_state.language = language
  st.session_state.last_agent_response = ""
  st.rerun()

is_es = language == "Español"

T = {
    "Español": {
        "page_title": (
            "HomeCopilot - Agente Universal de Logística de Vida"
        ),
        "settings": "⚙️ Configuración",
        "sync": "Tu contexto personal",
        "email_ph": "tu.correo@empresa.com",
        "btn_sync": "Activar mi espacio de trabajo",
        "btn_disc": "Desconectar Correo",
        "work_loc": "Ubicación y Trayecto",
        "work_where": "¿Dónde trabajas hoy?",
        "home_lbl": "Home Office 🏠",
        "pres_lbl": "Presencial / Híbrido 🏢",
        "home_addr_lbl": "📍 Dirección de Origen (Casa)",
        "dest_addr_lbl": "📍 Dirección de Destino (Oficina)",
        "phone_lbl": "Teléfono",
        "groups_lbl": "Grupos detectados:",
        "btn_wa_conn": "Vincular WhatsApp",
        "btn_wa_disc": "Desconectar WhatsApp",
        "mod_title": "Módulos de Vida",
        "num_mods": "Cantidad de módulos",
        "save_mods": "💾 Guardar y Evaluar Módulos",
        "reset": "🗑️ Restablecer Todo",
        "main_agenda": (
            "📅 Agenda Laboral y Módulos de Vida Sincronizados"
        ),
        "diag_title": "🤖 Diagnóstico Logístico",
        "alert_box": "Alerta Emitida",
        "view_live": "🗺️ Ver Ruta en Vivo",
        "wa_draft_lbl": "Borrador WhatsApp:",
        "reschedule_btn": "📅 Reagendar Llamada",
        "send_btn": "📤 Enviar a",
        "chat_prompt": "Escribe una instrucción sobre tu agenda...",
        "action_log": "🛠️ Bitácora de Acciones",
        "no_actions": "Sin ejecuciones de herramientas aún.",
        "map_title": "🗺️ Monitoreo de Tráfico en Tiempo Real",
        "close_map": "✅ Cerrar Mapa",
        "success_mods": (
            "✅ Módulos guardados y analizados correctamente."
        ),
        "success_call": "✅ Llamada movida a las 17:30.",
        "success_msg": "✅ Mensaje enviado a",
    },
    "English": {
        "page_title": "HomeCopilot - Universal Life Logistics Agent",
        "settings": "⚙️ Settings",
        "sync": "Your personal context",
        "email_ph": "your.email@company.com",
        "btn_sync": "Activate my workspace",
        "btn_disc": "Disconnect Email",
        "work_loc": "Location & Route",
        "work_where": "Where are you working today?",
        "home_lbl": "Home Office 🏠",
        "pres_lbl": "On-site / Hybrid 🏢",
        "home_addr_lbl": "📍 Origin Address (Home)",
        "dest_addr_lbl": "📍 Destination Address (Office)",
        "phone_lbl": "Phone Number",
        "groups_lbl": "Detected Groups:",
        "btn_wa_conn": "Connect WhatsApp",
        "btn_wa_disc": "Disconnect WhatsApp",
        "mod_title": "Life Modules",
        "num_mods": "Number of modules",
        "save_mods": "💾 Save & Evaluate Modules",
        "reset": "🗑️ Reset All",
        "main_agenda": "📅 Work Agenda & Synchronized Life Modules",
        "diag_title": "🤖 Logistics Diagnosis",
        "alert_box": "Alert Issued",
        "view_live": "🗺️ View Live Route",
        "wa_draft_lbl": "WhatsApp Draft:",
        "reschedule_btn": "📅 Reschedule Call",
        "send_btn": "📤 Send to",
        "chat_prompt": "Type an instruction about your schedule...",
        "action_log": "🛠️ Action Log (Telemetry)",
        "no_actions": "No tool calls executed yet.",
        "map_title": "🗺️ Real-Time Traffic Navigation",
        "close_map": "✅ Close Map",
        "success_mods": "✅ Modules saved and analyzed successfully.",
        "success_call": "✅ Call moved to 17:30.",
        "success_msg": "✅ Message sent to",
    },
}

t = T[language]

st.set_page_config(
    page_title=t["page_title"],
    page_icon="🛡️",
    layout="wide",
)

# --- ESTILOS CSS (TÍTULO MÁS ARRIBA) ---
st.markdown(
    """
    <style>
    header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], footer {
        display: none !important;
    }

    .stApp {
        margin-top: 0px !important;
    }

    .main .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
      padding-top: 0 !important;
    }

    [data-testid="stMainBlockContainer"] {
      padding-top: 0.75rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
      padding-top: 0.5rem !important;
    }

    [data-testid="stSidebar"] hr {
      margin: 0.35rem 0 0.65rem 0 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
      margin-top: 0.45rem !important;
      margin-bottom: 0.45rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
      gap: 0.5rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
      margin-top: -0.25rem !important;
    }

    .main hr {
      margin: 0.65rem 0 1rem 0 !important;
    }
    .stDataFrame, .stCodeBlock { width: 100% !important; }

    .agent-response-box {
        padding: 20px 24px;
        background-color: #1e293b;
        border-left: 6px solid #3b82f6;
        border-radius: 8px;
        margin-top: 15px;
        color: #f8fafc;
        width: 100% !important;
        box-sizing: border-box;
    }
    
    .proactive-card-alert {
        background-color: #450a0a;
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 16px;
        margin-top: 12px;
        color: #fca5a5;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- INICIALIZACIÓN DE SESIÓN (STATE) ---
if "timeline_events" not in st.session_state:
  st.session_state.timeline_events = []

if "agent_actions" not in st.session_state:
  st.session_state.agent_actions = []

if "decision_trace" not in st.session_state:
  st.session_state.decision_trace = []

if "email_connected" not in st.session_state:
  st.session_state.email_connected = False

if "user_email" not in st.session_state:
  st.session_state.user_email = ""

if "wa_connected" not in st.session_state:
  st.session_state.wa_connected = False

if "wa_phone" not in st.session_state:
  st.session_state.wa_phone = ""

if "selected_wa_group" not in st.session_state:
  st.session_state.selected_wa_group = (
      "Karate Parents 🥋" if not is_es else "Papás Karate 🥋"
  )

if "life_modules" not in st.session_state:
  st.session_state.life_modules = []

if "last_agent_response" not in st.session_state:
  st.session_state.last_agent_response = ""

if "draft_wa_message" not in st.session_state:
  st.session_state.draft_wa_message = ""

if "travel_time_min" not in st.session_state:
  st.session_state.travel_time_min = 0

if "baseline_travel_time_min" not in st.session_state:
  st.session_state.baseline_travel_time_min = 0

if "contingency_delay_min" not in st.session_state:
  st.session_state.contingency_delay_min = 0

if "contingency_scenario" not in st.session_state:
  st.session_state.contingency_scenario = "Día normal"

if "contingency_plan" not in st.session_state:
  st.session_state.contingency_plan = None

if "plan_approved" not in st.session_state:
  st.session_state.plan_approved = False

if "user_schedule_text" not in st.session_state:
  st.session_state.user_schedule_text = ""

if "real_incident_text" not in st.session_state:
  st.session_state.real_incident_text = ""

if "user_travel_time_min" not in st.session_state:
  st.session_state.user_travel_time_min = 30


def record_decision_step(step: str, detail: str, status: str = "done") -> None:
  """Stores a human-readable audit trail of the agent decision cycle."""
  st.session_state.decision_trace.append({
      "step": step,
      "detail": detail,
      "status": status,
  })


def parse_user_schedule(schedule_text: str) -> list[dict]:
  """Parses user-provided schedule rows without inventing calendar data."""
  events = []
  for raw_line in schedule_text.splitlines():
    line = raw_line.strip()
    if not line:
      continue
    parts = [part.strip() for part in line.split("|")]
    if len(parts) < 2:
      events.append({
          "Horario": "Por confirmar",
          "Evento / Tarea": line,
          "Categoría": "Usuario",
          "Estado": "📝 Proporcionado por usuario",
      })
      continue
    events.append({
        "Horario": parts[0],
        "Evento / Tarea": parts[1],
        "Categoría": parts[2] if len(parts) > 2 else "Usuario",
        "Estado": "📝 Proporcionado por usuario",
    })
  return events


def get_actionable_modules() -> list[dict]:
  """Returns only family modules with enough data for an external action."""
  return [
      module
      for module in st.session_state.life_modules
      if module.get("desc")
      and module.get("sede_1", {}).get("direccion")
      and module.get("sede_1", {}).get("rutina")
      and module["sede_1"]["direccion"] != "No specified"
  ]


# --- HERRAMIENTAS STRANDS SDK (@tool) ---
@tool
def send_email_reminder(
    recipient_email: str, subject: str, message_body: str
) -> str:
  """Sends or logs an email reminder about logistics."""
  if st.session_state.get("contingency_plan") and not st.session_state.get(
      "plan_approved"
  ):
    return "BLOCKED: email requires explicit human approval of the contingency plan."
  action_log = f"📧 [EMAIL TOOL]: Email sent to '{recipient_email}' | Subject: '{subject}'"
  st.session_state.agent_actions.append(action_log)
  return f"Email sent to {recipient_email}: {subject}"


@tool
def modify_calendar_event(
    event_name: str, new_time: str, category: str, status_update: str
) -> str:
  """Modifies or inserts a calendar event."""
  if st.session_state.get("contingency_plan") and not st.session_state.get(
      "plan_approved"
  ):
    return "BLOCKED: calendar changes require explicit human approval of the contingency plan."
  updated = False
  for item in st.session_state.timeline_events:
    if event_name.lower() in item["Evento / Tarea"].lower():
      item["Horario"] = new_time
      item["Categoría"] = category
      item["Estado"] = status_update
      updated = True
      break

  if not updated:
    st.session_state.timeline_events.append({
        "Horario": new_time,
        "Evento / Tarea": event_name,
        "Categoría": category,
        "Estado": status_update,
    })
  action_log = (
      f"⚙️ [CALENDAR TOOL]: Event '{event_name}' rescheduled to {new_time}"
  )
  st.session_state.agent_actions.append(action_log)
  return f"Event '{event_name}' rescheduled to {new_time}."


@tool
def prepare_whatsapp_carpool_message(
    module_desc: str, group_target: str
) -> str:
  """Prepares a draft message for the WhatsApp group."""
  if not get_actionable_modules():
    return (
        "BLOCKED: a family member, venue address, and schedule are required before preparing a WhatsApp message."
    )
  if st.session_state.get("contingency_plan") and not st.session_state.get(
      "plan_approved"
  ):
    return "BLOCKED: message preparation requires explicit human approval of the contingency plan."
  if is_es:
    msg = f"Hola a todos en {group_target} 👋, respecto a la actividad de '{module_desc}', se me cruza con una junta laboral por el tráfico. ¿Alguien me apoya con el traslado? ¡Muchas gracias! 🚗"
  else:
    msg = f"Hello everyone in {group_target} 👋, regarding '{module_desc}', I have a conflict with a work meeting due to traffic. Could anyone support me with the ride? Thank you so much! 🚗"

  st.session_state.draft_wa_message = msg
  action_log = f"📱 [WHATSAPP TOOL]: Draft prepared for '{group_target}'"
  st.session_state.agent_actions.append(action_log)
  return msg


def build_contingency_plan(
    delay_min: int,
    scenario: str,
    travel_time_min: int,
    language: str,
) -> dict:
  """Builds a deterministic, explainable response to a logistics disruption."""
  effective_travel = travel_time_min + delay_min
  severe_delay = effective_travel >= 45 or scenario in {
      "Cuidador cancela" if language == "Español" else "Caregiver cancels",
      "Reunión se extiende" if language == "Español" else "Meeting runs long",
  }
  if language == "Español":
    if scenario == "Día normal" and delay_min == 0:
      title = "Ruta estable"
      reason = "No hay una contingencia activa. Mantengo la agenda y monitoreo el traslado."
    elif scenario == "Tráfico +20 min":
      title = "Retraso de tráfico detectado"
      reason = f"El traslado estimado sube a {effective_travel} minutos y reduce el margen entre compromisos."
    elif scenario == "Reunión se extiende":
      title = "Reunión extendida"
      reason = "La reunión invade el bloque de traslado y puede provocar una llegada tardía a la actividad familiar."
    elif scenario == "Cuidador cancela":
      title = "Cobertura de traslado perdida"
      reason = "El responsable previsto ya no está disponible; hay que activar una alternativa humana."
    else:
      title = "Contingencia detectada"
      reason = f"El cambio actual eleva el traslado a {effective_travel} minutos."

    actions = [
        "Conservar la actividad familiar como compromiso prioritario.",
        "Preparar un mensaje de apoyo para el grupo seleccionado.",
    ]
    if severe_delay:
      actions.insert(0, "Proponer mover la llamada laboral al siguiente bloque disponible.")
    else:
      actions.insert(0, "Mantener la llamada y salir con un margen de 15 minutos.")
    return {
        "title": title,
        "reason": reason,
        "actions": actions,
        "travel_time": effective_travel,
        "severity": "Alta" if severe_delay else "Media" if delay_min else "Baja",
        "requires_approval": severe_delay or delay_min > 0,
    }

  if scenario == "Normal day" and delay_min == 0:
    title = "Route stable"
    reason = "No active contingency. The schedule remains unchanged while travel is monitored."
  elif scenario == "Traffic +20 min":
    title = "Traffic delay detected"
    reason = f"Estimated travel rises to {effective_travel} minutes, reducing the margin between commitments."
  elif scenario == "Meeting runs long":
    title = "Meeting extended"
    reason = "The meeting overlaps the travel window and may cause a late arrival to the family activity."
  elif scenario == "Caregiver cancels":
    title = "Ride coverage lost"
    reason = "The planned caregiver is unavailable, so a human backup must be activated."
  else:
    title = "Contingency detected"
    reason = f"The current change increases travel to {effective_travel} minutes."

  actions = [
      "Keep the family activity as the priority commitment.",
      "Prepare a support request for the selected group.",
  ]
  if severe_delay:
    actions.insert(0, "Propose moving the work call to the next available block.")
  else:
    actions.insert(0, "Keep the call and leave with a 15-minute buffer.")
  return {
      "title": title,
      "reason": reason,
      "actions": actions,
      "travel_time": effective_travel,
      "severity": "High" if severe_delay else "Medium" if delay_min else "Low",
      "requires_approval": severe_delay or delay_min > 0,
  }


@tool
def evaluate_contingency(
    scenario: str, delay_minutes: int, baseline_travel_minutes: int
) -> str:
  """Evaluates a disruption and returns an explainable plan for human approval."""
  language = st.session_state.get("language", "Español")
  plan = build_contingency_plan(
      delay_minutes, scenario, baseline_travel_minutes, language
  )
  st.session_state.contingency_plan = plan
  st.session_state.plan_approved = False
  record_decision_step(
      "Tool selected",
      f"evaluate_contingency evaluated '{scenario}' with {delay_minutes} additional minutes.",
  )
  record_decision_step(
      "Plan ready",
      f"{plan['severity']} severity; human approval required before external actions.",
      "waiting",
  )
  return (
      f"{plan['title']}. {plan['reason']} "
      f"Recommended actions: {'; '.join(plan['actions'])}. "
      "Do not execute external actions until the user approves the plan."
  )


# --- PANEL LATERAL (SIDEBAR) ---
with st.sidebar:
  st.header(t["settings"])

  st.markdown("---")

  st.subheader(f"🔗 {t['sync']}")
  email_input = st.text_input(
      "Correo electrónico" if is_es else "Email Address",
      value=st.session_state.user_email,
      placeholder=t["email_ph"],
  )

  st.text_area(
      "Compromisos de hoy" if is_es else "Today's commitments",
      key="user_schedule_text",
      height=130,
      placeholder=(
          "Una línea por compromiso: hora | actividad | categoría\n"
          "09:00-10:00 | Reunión con cliente | Trabajo\n"
          "17:00-18:00 | Fútbol de Ana | Familia"
          if is_es
          else "One commitment per line: time | activity | category\n"
          "09:00-10:00 | Client meeting | Work\n"
          "17:00-18:00 | Ana's soccer | Family"
      ),
  )
  st.caption(
      "Estos datos son tuyos: el agente no agrega eventos automáticamente."
      if is_es
      else "These are your own data: the agent does not add events automatically."
  )
  if st.session_state.email_connected:
    if st.button(
        "🔄 Actualizar mi agenda" if is_es else "🔄 Update my schedule",
        use_container_width=True,
    ):
      st.session_state.timeline_events = parse_user_schedule(
          st.session_state.user_schedule_text
      )
      st.session_state.agent_actions.append(
          "🔄 [USER CONTEXT]: Personal schedule updated."
      )
      st.rerun()

  if not st.session_state.email_connected:
    if st.button(t["btn_sync"], type="primary", use_container_width=True):
      st.session_state.email_connected = True
      st.session_state.user_email = email_input.strip() or "Sesión local"
      st.session_state.timeline_events = parse_user_schedule(
          st.session_state.user_schedule_text
      )
      record_decision_step(
          "Context loaded",
          "Personal schedule loaded without invented events.",
      )
      st.session_state.agent_actions.append(
          "🔗 [USER CONTEXT]: Personal schedule loaded without invented events."
      )
      st.rerun()
  else:
    st.success(f"🟢 {st.session_state.user_email}")
    if st.button(t["btn_disc"], use_container_width=True):
      st.session_state.email_connected = False
      st.session_state.timeline_events = []
      st.rerun()

  st.markdown("---")

  st.subheader(f"🏢 {t['work_loc']}")
  work_mode = st.radio(t["work_where"], [t["home_lbl"], t["pres_lbl"]])

  origin_address = st.text_input(
      t["home_addr_lbl"],
      value="",
      placeholder=(
        "Ej. tu dirección de casa"
          if is_es
        else "Ex. your home address"
      ),
  )

  destination_address = ""
  if work_mode == t["pres_lbl"]:
    destination_address = st.text_input(
        t["dest_addr_lbl"],
        value="",
        placeholder=(
            "Ej. Paseo de la Reforma 250, CDMX"
            if is_es
            else "Ex. Paseo de la Reforma 250, CDMX"
        ),
    )

  st.markdown("---")

  st.subheader("📱 WhatsApp")
  wa_input = st.text_input(
      t["phone_lbl"],
      value=st.session_state.wa_phone,
      placeholder="+52 55 1234 5678",
  )

  available_groups = (
      [
          "Grupo Escuela 🏫",
          "Papás Karate 🥋",
          "Comunidad Runners 🏃‍♂️",
          "Vecinos & Seguridad 🏠",
          "Natación Club Cañada 🏊‍♂️",
      ]
      if is_es
      else [
          "School Group 🏫",
          "Karate Parents 🥋",
          "Runners Community 🏃‍♂️",
          "Neighbors & Security 🏠",
          "Swimming Club Cañada 🏊‍♂️",
      ]
  )

  if st.session_state.wa_connected:
    st.session_state.selected_wa_group = st.selectbox(
        t["groups_lbl"], available_groups, index=1
    )
    st.success(f"🟢 WhatsApp: {st.session_state.wa_phone}")
    if st.button(t["btn_wa_disc"], use_container_width=True):
      st.session_state.wa_connected = False
      st.session_state.wa_phone = ""
      st.rerun()
  else:
    st.selectbox(
        t["groups_lbl"],
        (
            ["⚠️ Ingresa celular..."]
            if is_es
            else ["⚠️ Enter phone number..."]
        ),
        disabled=True,
    )
    if st.button(t["btn_wa_conn"], type="primary", use_container_width=True):
      if wa_input and len(wa_input) >= 8:
        st.session_state.wa_connected = True
        st.session_state.wa_phone = wa_input
        st.session_state.agent_actions.append(
            f"📱 [WHATSAPP SYNC]: Synchronized ({wa_input})."
        )
        st.rerun()

  st.markdown("---")

  st.subheader(f"🎯 {t['mod_title']}")

  if is_es:
    MODULE_CONFIGS = {
        "Familiar": {
            "label_desc": "Nombre del Hijo / Responsable",
            "ph_desc": "Ej. Gerardo (Hijo)",
            "label_loc": "📍 Dirección Sede 1 (Ej. Dojo Karate)",
            "ph_loc": "Ej. Dojo Cañada, Av. Revolución 45",
            "ph_rut": "Ej. Martes y Jueves - 16:30",
        },
        "Hobby / Deporte": {
            "label_desc": "Nombre del Hobby / Deporte",
            "ph_desc": "Ej. Entrenamiento de Carrera",
            "label_loc": "📍 Dirección Sede 1",
            "ph_loc": "Ej. Pista El Sope, Chapultepec",
            "ph_rut": "Ej. Lunes y Miércoles - 18:00",
        },
        "Mascota": {
            "label_desc": "Mascota / Actividad",
            "ph_desc": "Ej. Bruno (Veterinaria)",
            "label_loc": "📍 Dirección Sede 1",
            "ph_loc": "Ej. VetCare Insurgentes Sur 300",
            "ph_rut": "Ej. Todos los días - 08:00",
        },
        "Desarrollo Personal": {
            "label_desc": "Proyecto / Actividad",
            "ph_desc": "Ej. Redacción Artículo Técnico",
            "label_loc": "📍 Ubicación / Sede 1",
            "ph_loc": "Ej. Biblioteca Vasconcelos",
            "ph_rut": "Ej. Viernes - 17:00 a 19:00",
        },
    }
  else:
    MODULE_CONFIGS = {
        "Family": {
            "label_desc": "Child / Family Name",
            "ph_desc": "Ex. Gerardo",
            "label_loc": "📍 Venue 1 Address (Ex. Karate Dojo)",
            "ph_loc": "Ex. Dojo Cañada, 45 Revolution Ave.",
            "ph_rut": "Ex. Tuesday and Thursday - 16:30",
        },
        "Hobby / Sport": {
            "label_desc": "Hobby / Sport Name",
            "ph_desc": "Ex. Running Training",
            "label_loc": "📍 Venue 1 Address",
            "ph_loc": "Ex. El Sope Track",
            "ph_rut": "Ex. Monday and Wednesday - 18:00",
        },
        "Pet": {
            "label_desc": "Pet / Activity",
            "ph_desc": "Ex. Bruno (Vet)",
            "label_loc": "📍 Venue 1 Address",
            "ph_loc": "Ex. VetCare Clinic",
            "ph_rut": "Ex. Every day - 08:00",
        },
        "Personal Development": {
            "label_desc": "Project / Personal Activity",
            "ph_desc": "Ex. Writing Technical Article",
            "label_loc": "📍 Location / Venue 1",
            "ph_loc": "Ex. Vasconcelos Library",
            "ph_rut": "Ex. Friday - 17:00 to 19:00",
        },
    }

  num_modules = st.number_input(
      t["num_mods"], min_value=1, max_value=5, value=1, step=1
  )

  current_modules = []
  for i in range(int(num_modules)):
    st.markdown(f"**Module #{i+1}**")
    cat_key = f"mod_cat_{i}"
    m_tipo = st.selectbox(
        f"Category #{i+1}", list(MODULE_CONFIGS.keys()), key=cat_key
    )

    cfg = MODULE_CONFIGS[m_tipo]

    m_desc = st.text_input(
        f"{cfg['label_desc']} #{i+1}",
        placeholder=cfg["ph_desc"],
        key=f"mod_desc_{i}_{m_tipo}",
    )

    m_loc_1 = st.text_input(
        f"{cfg['label_loc']} #{i+1}",
        placeholder=cfg["ph_loc"],
        key=f"mod_loc1_{i}_{m_tipo}",
    )
    m_rut_1 = st.text_area(
        (
            f"⏰ Horario Sede 1 #{i+1}"
            if is_es
            else f"⏰ Venue 1 Schedule #{i+1}"
        ),
        placeholder=cfg["ph_rut"],
        key=f"mod_rut1_{i}_{m_tipo}",
    )

    has_second_venue = st.checkbox(
        (
            f"➕ Agregar 2da Sede / Actividad para #{i+1}"
            if is_es
            else f"➕ Add 2nd Venue / Activity for #{i+1}"
        ),
        key=f"has_sec_{i}_{m_tipo}",
    )

    m_loc_2, m_rut_2 = "", ""
    if has_second_venue:
      m_loc_2 = st.text_input(
          (
              f"📍 Dirección Sede 2 #{i+1}"
              if is_es
              else f"📍 Venue 2 Address #{i+1}"
          ),
          placeholder=(
              "Ej. Club Cañada, Av. Conscripto 120"
              if is_es
              else "Ex. Second venue address"
          ),
          key=f"mod_loc2_{i}_{m_tipo}",
      )
      m_rut_2 = st.text_area(
          (
              f"⏰ Horario Sede 2 #{i+1}"
              if is_es
              else f"⏰ Venue 2 Schedule #{i+1}"
          ),
          placeholder=(
              "Ej. Miércoles y Viernes - 18:00"
              if is_es
              else "Ex. Wednesday and Friday"
          ),
          key=f"mod_rut2_{i}_{m_tipo}",
      )

    if m_desc:
      current_modules.append({
          "tipo": m_tipo,
          "desc": m_desc,
          "sede_1": {
              "direccion": m_loc_1 if m_loc_1 else "No specified",
              "rutina": m_rut_1,
          },
          "sede_2": (
              {"direccion": m_loc_2, "rutina": m_rut_2}
              if has_second_venue and m_loc_2
              else None
          ),
      })


  def run_agent_execution(
      prompt_text: str,
      work_mode_val,
      origin_addr_val,
      dest_addr_val,
      lang_val,
      incident_text: str = "",
      travel_time_override: int | None = None,
  ):
    st.session_state.decision_trace = []
    record_decision_step(
      "Context received",
      "Agenda, locations, family modules, travel estimate, and user incident loaded.",
    )
    formatted_list = []
    for m in st.session_state.life_modules:
      venues_str = (
          f"Sede 1: {m['sede_1']['direccion']} ({m['sede_1']['rutina']})"
          if is_es
          else f"Venue 1: {m['sede_1']['direccion']} ({m['sede_1']['rutina']})"
      )
      if m["sede_2"]:
        venues_str += (
            f" | Sede 2: {m['sede_2']['direccion']} ({m['sede_2']['rutina']})"
            if is_es
            else f" | Venue 2: {m['sede_2']['direccion']} ({m['sede_2']['rutina']})"
        )
      formatted_list.append(f"- [{m['tipo']}] {m['desc']} | {venues_str}")

    modules_formatted = (
        "\n".join(formatted_list)
        if st.session_state.life_modules
        else ("No hay módulos registrados." if is_es else "No modules registered.")
    )

    target_group = (
        st.session_state.selected_wa_group
        if st.session_state.wa_connected
        else ("Grupo de Apoyo" if is_es else "Support Group")
    )

    actionable_modules = get_actionable_modules()
    st.session_state.draft_wa_message = ""
    if actionable_modules:
      first_mod = actionable_modules[0]["desc"]
      if is_es:
        st.session_state.draft_wa_message = f"Hola a todos en {target_group} 👋, respecto a la actividad de '{first_mod}', tengo un cruce con una junta laboral por el tráfico. ¿Alguien me apoya con el traslado? ¡Muchas gracias! 🚗"
      else:
        st.session_state.draft_wa_message = f"Hello everyone in {target_group} 👋, regarding '{first_mod}', I have a conflict with a work meeting due to traffic. Could anyone support me with the ride? Thank you so much! 🚗"
    else:
      record_decision_step(
          "Action blocked",
          "WhatsApp draft withheld because a family activity name, address, and schedule are incomplete.",
          "waiting",
      )

    st.session_state.baseline_travel_time_min = (
      travel_time_override
      if travel_time_override is not None
      else st.session_state.user_travel_time_min
    )
    st.session_state.travel_time_min = (
        st.session_state.baseline_travel_time_min
        + st.session_state.contingency_delay_min
    )
    record_decision_step(
      "Constraints evaluated",
      f"Travel reference calculated at {st.session_state.travel_time_min} minutes.",
    )

    user_schedule = st.session_state.user_schedule_text.strip() or (
      "No schedule entered by the user."
      if not is_es
      else "El usuario no ingresó compromisos."
    )
    incident_context = incident_text.strip() or (
      "No active incident reported."
      if not is_es
      else "No se reportó una incidencia activa."
    )

    evaluate_contingency(
      incident_context,
      st.session_state.contingency_delay_min,
      st.session_state.baseline_travel_time_min,
    )

    sys_prompt = f"""You are HomeCopilot, an autonomous life logistics agent powered by Strands SDK and Claude 3.5 Sonnet on Amazon Bedrock.
CRITICAL TEMPORAL CONTEXT:
- TODAY IS EXACTLY: {current_day_es} ({current_day_en}), Date: {current_date_str}.
- Check the recurring schedule of the Life Modules against TODAY ({current_day_es} / {current_day_en}).
- MANDATORY LANGUAGE RULE: You MUST write your entire response, headings, tables, recommendations, and analysis strictly in {lang_val}. If {lang_val} is English, do NOT output Spanish. If {lang_val} is Español, do NOT output English.

USER CONTEXT:
- Selected Language: {lang_val}
- User Email: {st.session_state.user_email}
- Work Modality: {work_mode_val}
- User Origin Address (Home): {origin_addr_val if origin_addr_val else 'Not specified'}
- User Office Destination: {dest_addr_val if dest_addr_val else 'Not specified (Home Office mode)'}
- WhatsApp Connected: {st.session_state.wa_connected} ({st.session_state.wa_phone})
- Target WhatsApp Group: {target_group}
- Active contingency scenario: {st.session_state.contingency_scenario}
- Additional delay: {st.session_state.contingency_delay_min} minutes
- Estimated Traffic Travel Time: {st.session_state.travel_time_min} minutes.
- User-reported incident: {incident_context}
- User-provided commitments (treat as source of truth):
{user_schedule}

LOGISTICS REASONING:
1. Compare work events with Life Modules (analyzing both Venue 1 and Venue 2 locations if present).
2. Note whether the life module venues occur TODAY ({current_day_es} / {current_day_en}).
3. Factor in exact multi-point addresses for traffic analysis between origin ({origin_addr_val}), office, and multi-venues.
4. Call `evaluate_contingency` with the user's reported incident and delay before recommending any action.
5. Only prepare a WhatsApp message when a family activity has a name, venue address, and schedule. Otherwise explain what information is missing.
6. Produce a concise plan with: problem, cause, options, recommendation, risk, and actions requiring approval.
7. Never claim that an email, calendar change, or WhatsApp message was executed. External actions require explicit user approval in the interface.
8. Speak directly in {lang_val} in a clear, professional, helpful tone.

USER LIFE MODULES:
{modules_formatted}
"""

    agent = Agent(
        model="global.anthropic.claude-sonnet-4-6",
        system_prompt=sys_prompt,
        tools=[
            calculator,
            evaluate_contingency,
            send_email_reminder,
            modify_calendar_event,
            prepare_whatsapp_carpool_message,
        ],
    )

    response = agent(prompt_text)
    st.session_state.last_agent_response = str(response)
    if not st.session_state.contingency_plan:
      record_decision_step(
          "Plan ready",
          "The agent returned a recommendation; approval is required for consequential actions.",
          "waiting",
      )


  if st.button(t["save_mods"], type="primary", use_container_width=True):
    st.session_state.life_modules = current_modules
    st.session_state.draft_wa_message = ""
    if st.session_state.email_connected:
      with st.spinner(
          "🤖 Actualizando módulos y evaluando logística..."
          if is_es
          else "🤖 Updating modules and evaluating logistics..."
      ):
        eval_prompt = (
            f"He actualizado mis módulos de vida. Evalúa mi agenda para hoy ({current_day_en} / {current_day_es}), verifica el tráfico desde {origin_address} hasta las sedes de las actividades y dame recomendaciones detalladas en {language}."
            if is_es
            else f"I have updated my Life Modules. Evaluate my schedule for today ({current_day_en}), check traffic from {origin_address} to the activity venues, and give detailed recommendations in {language}."
        )
        run_agent_execution(
            eval_prompt,
            work_mode,
            origin_address,
            destination_address,
            language,
        )
    st.success(t["success_mods"])
    st.rerun()

  st.markdown("---")
  if st.button(t["reset"], use_container_width=True):
    st.session_state.clear()
    st.rerun()


# --- POPUP MAPA DE TRÁFICO ---
@st.dialog(t["map_title"])
def show_traffic_map(origen, destino):
  valid_origen = (
      origen if (origen and origen != "Origen") else "Origin not specified"
  )
  valid_destino = (
      destino
      if (destino and destino != "Destination")
      else "Destination not specified"
  )

  st.markdown(
      f"**📍 Origen / Origin:** {valid_origen}  ──🚗──>  **🏁 Destino / Destination:** {valid_destino}"
  )
  st.error(
      f"⚠️ **{('Referencia ingresada por ti:' if is_es else 'Your entered reference:')}** **{st.session_state.travel_time_min} {'minutos' if is_es else 'minutes'}**."
  )
  st.info(
      "Google Maps muestra abajo su propio cálculo de ruta y tráfico. Esa cifra puede diferir de tu referencia."
      if is_es
      else "Google Maps shows its own route and traffic calculation below. That value can differ from your reference."
    )

  orig_encoded = urllib.parse.quote(valid_origen)
  dest_encoded = urllib.parse.quote(valid_destino)

  map_url = f"https://maps.google.com/maps?saddr={orig_encoded}&daddr={dest_encoded}&output=embed"

  components.iframe(map_url, height=380, scrolling=True)
  if st.button(t["close_map"], use_container_width=True):
    st.rerun()


# --- TÍTULO PRINCIPAL ---
date_display = (
    f"{current_day_es}, {now.strftime('%d')} de {['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'][now.month-1]} de {now.year}"
    if is_es
    else f"{current_day_en}, {now.strftime('%B %d, %Y')}"
)

st.markdown(
    """
    <div style="margin-top: -10px; margin-bottom: 0px;">
        <h1 style="color: #ffffff; font-size: 2.2rem; font-weight: 700; display: flex; align-items: center; gap: 12px; margin: 0; padding: 0; line-height: 1.2;">
            🛡️ HomeCopilot: Autonomous Life Logistics Agent
        </h1>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 6px; margin-bottom: 15px;">
            Track: Everyday Agents | Powered by Strands SDK & Amazon Bedrock (Claude 3.5 Sonnet) | Today: <b>%s</b>
        </p>
    </div>
    <hr style="margin: 5px 0 20px 0; border-color: #334155;">
"""
    % (date_display),
    unsafe_allow_html=True,
)

# --- VISTA PRINCIPAL ---
st.subheader(t["main_agenda"])

if st.session_state.email_connected:
  if st.session_state.timeline_events:
    df_timeline = pd.DataFrame(st.session_state.timeline_events)
    st.dataframe(df_timeline, use_container_width=True, hide_index=True)
  else:
    st.success(
        "✅ Contexto personal activo. Añade compromisos en el panel lateral para completar tu agenda."
        if is_es
        else "✅ Personal context active. Add commitments in the sidebar to complete your schedule."
    )
else:
  st.info(
      "👈 Activa tu espacio de trabajo en el panel lateral para comenzar."
      if is_es
      else "👈 Activate your workspace in the sidebar to begin."
  )

st.markdown("---")

# --- CONTEXTO REAL Y GATE DE APROBACION ---
st.subheader(
  "🧭 Situación real de hoy" if is_es else "🧭 Your real situation today"
)
st.caption(
    "Cuéntale al agente qué está pasando ahora. El plan se propone primero; ninguna acción externa se ejecuta sin tu aprobación."
  if is_es
    else "Tell the agent what is happening now. The plan is proposed first; no external action runs without your approval."
)
incident_text = st.text_area(
    "¿Qué está pasando? (opcional)" if is_es else "What is happening? (optional)",
    key="real_incident_text",
    placeholder=(
        "Ej. Mi reunión se extendió 30 minutos y debo recoger a mi hija en la escuela."
        if is_es
        else "Ex. My meeting ran 30 minutes over and I need to pick up my daughter from school."
    ),
)
travel_col, run_col = st.columns([1, 1])
with travel_col:
  real_travel_time = st.number_input(
      "Tu estimación de traslado (minutos)"
      if is_es
      else "Your travel estimate (minutes)",
      min_value=0,
      max_value=300,
      value=st.session_state.user_travel_time_min,
      step=5,
  )
  st.caption(
      "Este dato alimenta el análisis del agente; Google Maps mostrará su propia estimación."
      if is_es
      else "This value feeds the agent analysis; Google Maps will show its own estimate."
    )
with run_col:
  st.markdown("<br>", unsafe_allow_html=True)
  analyze_label = "⚡ Analizar mi día" if is_es else "⚡ Analyze my day"
  if st.button(analyze_label, type="primary", use_container_width=True):
    st.session_state.user_travel_time_min = int(real_travel_time)
    st.session_state.contingency_delay_min = 0
    st.session_state.contingency_scenario = incident_text.strip() or (
        "Día normal" if is_es else "Normal day"
    )
    plan = build_contingency_plan(
        0,
        st.session_state.contingency_scenario,
        int(real_travel_time),
        language,
    )
    st.session_state.contingency_plan = plan
    st.session_state.plan_approved = False
    st.session_state.travel_time_min = int(real_travel_time)
    st.session_state.agent_actions.append(
        "🧭 [REAL CONTEXT]: User situation submitted for analysis."
    )
    with st.spinner(
        "🤖 El agente está analizando tu día..."
        if is_es
        else "🤖 Agent is analyzing your day..."
    ):
      run_agent_execution(
          (
              "Analiza mi situación real actual, mi agenda y mis módulos familiares. "
              "Llama a evaluate_contingency usando la incidencia que reporté. Devuelve un diagnóstico, alternativas, recomendación y acciones que requieren aprobación."
              if is_es
              else "Analyze my current real situation, schedule, and family modules. "
              "Call evaluate_contingency using my reported incident. Return a diagnosis, alternatives, recommendation, and approval-required actions."
          ),
          work_mode,
          origin_address,
          destination_address,
          language,
          incident_text,
          int(real_travel_time),
      )
    st.rerun()

if st.session_state.contingency_plan:
  plan = st.session_state.contingency_plan
  severity_color = {
    "Alta": "#ef4444",
    "High": "#ef4444",
    "Media": "#f59e0b",
    "Medium": "#f59e0b",
  }.get(plan["severity"], "#22c55e")
  st.markdown(
    f"""
    <div style="border: 1px solid {severity_color}; border-left: 6px solid {severity_color}; border-radius: 8px; padding: 16px; margin: 12px 0; background: #172033;">
    <h4 style="margin: 0 0 8px 0;">{plan['title']} · {plan['severity']}</h4>
    <p style="margin: 0 0 8px 0;"><b>{'Por qué importa' if is_es else 'Why it matters'}:</b> {plan['reason']}</p>
    <p style="margin: 0 0 6px 0;"><b>{'Plan recomendado' if is_es else 'Recommended plan'}:</b></p>
    <ul style="margin-top: 0;">{''.join(f'<li>{action}</li>' for action in plan['actions'])}</ul>
    <p style="margin: 8px 0 0 0;">🚗 {'Traslado efectivo' if is_es else 'Effective travel'}: <b>{plan['travel_time']} min</b> · {'Aprobación requerida' if is_es else 'Approval required'}: <b>{'Sí' if is_es else 'Yes'}</b></p>
    </div>
    """,
    unsafe_allow_html=True,
  )
  approval_col, discard_col = st.columns(2)
  with approval_col:
    approve_label = "✅ Aprobar plan y habilitar acciones" if is_es else "✅ Approve plan and enable actions"
    if st.button(approve_label, type="primary", use_container_width=True):
      st.session_state.plan_approved = True
      st.session_state.agent_actions.append(
          "✅ [HUMAN APPROVAL]: Contingency plan approved."
      )
      st.rerun()
  with discard_col:
    discard_label = "Descartar plan" if is_es else "Discard plan"
    if st.button(discard_label, use_container_width=True):
      st.session_state.contingency_plan = None
      st.session_state.plan_approved = False
      st.rerun()
  if st.session_state.plan_approved:
    for trace_item in st.session_state.decision_trace:
      if trace_item["status"] == "waiting":
        trace_item["status"] = "approved"
    st.success(
        "Plan aprobado. Ya puedes ejecutar las acciones propuestas desde los controles inferiores."
        if is_es
        else "Plan approved. You can now execute the proposed actions from the controls below."
    )

if st.session_state.decision_trace:
  with st.expander(
      "🧠 Ciclo de decisión del agente" if is_es else "🧠 Agent decision cycle",
      expanded=True,
  ):
    st.caption(
        "Diferenciador: HomeCopilot hace visible cómo pasa del contexto a una decisión auditable."
        if is_es
        else "Differentiator: HomeCopilot makes the path from context to an auditable decision visible."
    )
    trace_labels = {
        "done": "✅",
        "waiting": "⏳",
        "approved": "🟢",
    }
    for trace_item in st.session_state.decision_trace:
      marker = trace_labels.get(trace_item["status"], "•")
      st.markdown(
          f"{marker} **{trace_item['step']}** — {trace_item['detail']}"
      )

st.markdown("---")

if st.session_state.last_agent_response:
  st.markdown(f"### {t['diag_title']}")
  st.markdown(
      f"<div class='agent-response-box'>"
      f"{st.session_state.last_agent_response}</div>",
      unsafe_allow_html=True,
  )

  if st.session_state.life_modules:
    m_active = st.session_state.life_modules[0]
    activity_dest = (
        m_active["sede_2"]["direccion"]
        if m_active["sede_2"]
        else m_active["sede_1"]["direccion"]
    )
  else:
    activity_dest = (
        destination_address if destination_address else "Destino no especificado"
    )

  st.markdown(
      f"""
        <div class='proactive-card-alert'>
            <h4>📧 {t['alert_box']}</h4>
            <p>{('Origen:' if is_es else 'Origin:')} <b>{origin_address if origin_address else ('No especificado' if is_es else 'Not specified')}</b> ➔ {('Destino:' if is_es else 'Destination:')} <b>{activity_dest}</b> | {('Referencia de traslado:' if is_es else 'Travel reference:')} <b>{st.session_state.travel_time_min} {'mins' if is_es else 'mins'}</b>.</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  col_map_btn, col_actions = st.columns([1, 2])

  with col_map_btn:
    if st.button(t["view_live"], use_container_width=True):
      show_traffic_map(origin_address, activity_dest)

  with col_actions:
    actionable_modules = get_actionable_modules()
    if not st.session_state.draft_wa_message and actionable_modules:
      if is_es:
        st.session_state.draft_wa_message = f"Hola a todos, respecto a '{actionable_modules[0]['desc']}', tengo un conflicto laboral por el tráfico. ¿Alguien me ayuda con el traslado? 🚗"
      else:
        st.session_state.draft_wa_message = f"Hello everyone, regarding '{actionable_modules[0]['desc']}', I have a work conflict due to traffic. Can anyone help me with the ride? 🚗"

    wa_msg_text = st.text_area(t["wa_draft_lbl"], value=st.session_state.draft_wa_message)
    if not actionable_modules:
      st.warning(
          "Completa nombre, dirección y horario de una actividad familiar antes de preparar un mensaje."
          if is_es
          else "Complete a family activity name, address, and schedule before preparing a message."
      )

    c1, c2 = st.columns(2)
    with c1:
      if st.button(t["reschedule_btn"], type="primary", use_container_width=True):
        if st.session_state.contingency_plan and not st.session_state.plan_approved:
          st.warning(
              "Aprueba primero el plan de contingencia."
              if is_es
              else "Approve the contingency plan first."
          )
        else:
          for item in st.session_state.timeline_events:
            if "16:00" in item["Evento / Tarea"] or "16:00" in item["Horario"]:
              item["Horario"] = "17:30 - 18:30"
              item["Estado"] = (
                  "🔄 Reagendado" if is_es else "🔄 Rescheduled"
              )
          st.session_state.agent_actions.append(
              "⚙️ [USER CONFIRMED]: Call moved to 17:30."
          )
          st.success(t["success_call"])
          st.rerun()

    with c2:
      target_g = (
          st.session_state.selected_wa_group
          if st.session_state.wa_connected
          else ("Grupo" if is_es else "Group")
      )
      if st.button(f"{t['send_btn']} {target_g}", use_container_width=True):
        if st.session_state.contingency_plan and not st.session_state.plan_approved:
          st.warning(
              "Aprueba primero el plan de contingencia."
              if is_es
              else "Approve the contingency plan first."
          )
        elif not actionable_modules:
          st.warning(
              "No se puede enviar: falta información de la actividad familiar."
              if is_es
              else "Cannot send: family activity information is incomplete."
          )
        elif not st.session_state.wa_connected:
          st.error(
              "👈 Vincula tu WhatsApp primero."
              if is_es
              else "👈 Connect your WhatsApp first."
          )
        else:
          action_log_entry = (
              f"📱 [WHATSAPP TOOL]: Message sent to '{target_g}':"
              f' "{wa_msg_text}"'
          )
          st.session_state.agent_actions.append(action_log_entry)
          st.success(f"{t['success_msg']} {target_g}.")
          st.rerun()

# --- BITÁCORA DE ACCIONES (ACTION LOG) ---
st.markdown("---")
st.subheader(t["action_log"])

log_container = st.container()
with log_container:
  log_html = """
    <div style="max-height: 180px; overflow-y: auto; background-color: #0f172a; padding: 12px; border-radius: 8px; border: 1px solid #334155; font-family: monospace; font-size: 0.85rem;">
    """
  if st.session_state.agent_actions:
    for action in reversed(st.session_state.agent_actions):
      log_html += (
          f'<div style="color: #38bdf8; margin-bottom: 4px;">&gt; {action}</div>'
      )
  else:
    log_html += f'<div style="color: #64748b;">{t["no_actions"]}</div>'
  log_html += "</div>"
  st.markdown(log_html, unsafe_allow_html=True)