from datetime import datetime, timezone, timedelta
import uuid
import jwt
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .config import settings
from .db import Base, engine, get_db
from .models import (
    AIAgent,
    AuditEvent,
    Conversation,
    Customer,
    Membership,
    Order,
    SupportTicket,
    User,
)
from .security import create_token, current_identity, require_roles, verify_password

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="VoiceSphere AI 2.0 API",
    version="2.0.0",
    description="Tenant-aware contact center demo API. Mock voice mode does not stream audio.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TicketIn(BaseModel):
    customer_id: int
    subject: str = Field(min_length=4, max_length=180)
    description: str = Field(min_length=5, max_length=5000)
    priority: str = "normal"


class VerifyIn(BaseModel):
    email: str
    last4: str = Field(pattern=r"^\d{4}$")


class AgentIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = ""
    instructions: str = ""
    greeting: str = "Thanks for calling Northstar Retail."
    voice: str = "alloy"
    language: str = "en-US"


@app.get("/health")
def health():
    return {"status": "ok", "voice_mode": settings.voice_mode}


@app.post("/api/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username.lower()).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    membership = db.query(Membership).filter_by(user_id=user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="No organization membership")
    return {
        "access_token": create_token(user, membership),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "role": membership.role,
            "organization_id": membership.organization_id,
        },
    }


@app.get("/api/auth/me")
def me(identity=Depends(current_identity)):
    user, membership = identity
    return {
        "id": user.id,
        "name": user.full_name,
        "email": user.email,
        "role": membership.role,
        "organization_id": membership.organization_id,
    }


@app.get("/api/dashboard")
def dashboard(identity=Depends(current_identity), db: Session = Depends(get_db)):
    _, m = identity
    oid = m.organization_id
    return {
        "organization": "Northstar Retail",
        "metrics": {
            "customers": db.query(Customer).filter_by(organization_id=oid).count(),
            "orders": db.query(Order).filter_by(organization_id=oid).count(),
            "open_tickets": db.query(SupportTicket)
            .filter_by(organization_id=oid, status="open")
            .count(),
            "active_conversations": db.query(Conversation)
            .filter_by(organization_id=oid, status="active")
            .count(),
        },
        "voice_mode": settings.voice_mode,
        "demo_data": True,
    }


@app.get("/api/customers")
def customers(identity=Depends(current_identity), db: Session = Depends(get_db)):
    _, m = identity
    return [
        {"id": c.id, "name": c.name, "email": c.email, "phone": c.phone}
        for c in db.query(Customer)
        .filter_by(organization_id=m.organization_id)
        .order_by(Customer.id)
        .all()
    ]


@app.post("/api/tools/verify-customer")
def verify_customer(
    body: VerifyIn, identity=Depends(current_identity), db: Session = Depends(get_db)
):
    user, m = identity
    c = (
        db.query(Customer)
        .filter(
            Customer.organization_id == m.organization_id,
            Customer.email == body.email.lower(),
        )
        .first()
    )
    if not c or c.verification_last4 != body.last4:
        raise HTTPException(status_code=401, detail="Customer verification failed")
    token = jwt.encode(
        {
            "sub": str(c.id),
            "org": m.organization_id,
            "purpose": "customer_verification",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        settings.app_secret_key,
        algorithm="HS256",
    )
    db.add(
        AuditEvent(
            organization_id=m.organization_id,
            user_id=user.id,
            action="customer.verified",
            resource_type="customer",
            resource_id=str(c.id),
        )
    )
    db.commit()
    return {
        "verified": True,
        "verification_token": token,
        "customer": {"id": c.id, "name": c.name},
    }


def verified_customer(token: str, org: int):
    try:
        p = jwt.decode(token, settings.app_secret_key, algorithms=["HS256"])
        if p.get("purpose") != "customer_verification" or int(p["org"]) != org:
            raise ValueError()
        return int(p["sub"])
    except Exception:
        raise HTTPException(
            status_code=401, detail="Valid customer verification is required"
        )


@app.get("/api/tools/orders/{order_number}")
def order_status(
    order_number: str,
    verification_token: str = Header(..., alias="X-Customer-Verification"),
    identity=Depends(current_identity),
    db: Session = Depends(get_db),
):
    _, m = identity
    cid = verified_customer(verification_token, m.organization_id)
    o = (
        db.query(Order)
        .filter_by(
            organization_id=m.organization_id,
            customer_id=cid,
            order_number=order_number,
        )
        .first()
    )
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "order_number": o.order_number,
        "item": o.item,
        "status": o.status,
        "estimated_delivery": o.estimated_delivery,
    }


@app.get("/api/orders")
def orders(identity=Depends(current_identity), db: Session = Depends(get_db)):
    _, m = identity
    return [
        {
            "id": o.id,
            "order_number": o.order_number,
            "customer_id": o.customer_id,
            "item": o.item,
            "status": o.status,
            "estimated_delivery": o.estimated_delivery,
        }
        for o in db.query(Order).filter_by(organization_id=m.organization_id).all()
    ]


@app.get("/api/tickets")
def tickets(identity=Depends(current_identity), db: Session = Depends(get_db)):
    _, m = identity
    return [
        {
            "id": t.id,
            "customer_id": t.customer_id,
            "subject": t.subject,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "created_at": t.created_at.isoformat(),
        }
        for t in db.query(SupportTicket)
        .filter_by(organization_id=m.organization_id)
        .order_by(SupportTicket.id.desc())
        .all()
    ]


@app.post("/api/tools/tickets", status_code=201)
def create_ticket(
    body: TicketIn,
    identity=Depends(
        require_roles("platform_admin", "org_admin", "supervisor", "support_agent")
    ),
    db: Session = Depends(get_db),
):
    user, m = identity
    c = (
        db.query(Customer)
        .filter_by(id=body.customer_id, organization_id=m.organization_id)
        .first()
    )
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    t = SupportTicket(
        organization_id=m.organization_id,
        customer_id=c.id,
        subject=body.subject,
        description=body.description,
        priority=body.priority,
    )
    db.add(t)
    db.flush()
    db.add(
        AuditEvent(
            organization_id=m.organization_id,
            user_id=user.id,
            action="ticket.created",
            resource_type="ticket",
            resource_id=str(t.id),
        )
    )
    db.commit()
    db.refresh(t)
    return {
        "id": t.id,
        "subject": t.subject,
        "status": t.status,
        "priority": t.priority,
    }


@app.get("/api/agents")
def agents(identity=Depends(current_identity), db: Session = Depends(get_db)):
    _, m = identity
    return [
        {
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "instructions": a.instructions,
            "greeting": a.greeting,
            "voice": a.voice,
            "language": a.language,
            "status": a.status,
            "version": a.version,
        }
        for a in db.query(AIAgent).filter_by(organization_id=m.organization_id).all()
    ]


@app.post("/api/agents", status_code=201)
def create_agent(
    body: AgentIn,
    identity=Depends(require_roles("platform_admin", "org_admin", "supervisor")),
    db: Session = Depends(get_db),
):
    user, m = identity
    a = AIAgent(organization_id=m.organization_id, **body.model_dump())
    db.add(a)
    db.flush()
    db.add(
        AuditEvent(
            organization_id=m.organization_id,
            user_id=user.id,
            action="agent.created",
            resource_type="agent",
            resource_id=str(a.id),
        )
    )
    db.commit()
    db.refresh(a)
    return {"id": a.id, "name": a.name, "status": a.status, "version": a.version}


@app.patch("/api/agents/{agent_id}/publish")
def publish_agent(
    agent_id: int,
    identity=Depends(require_roles("platform_admin", "org_admin", "supervisor")),
    db: Session = Depends(get_db),
):
    user, m = identity
    a = (
        db.query(AIAgent)
        .filter_by(id=agent_id, organization_id=m.organization_id)
        .first()
    )
    if not a:
        raise HTTPException(404, "Agent not found")
    a.status = "published"
    a.version += 1
    db.add(
        AuditEvent(
            organization_id=m.organization_id,
            user_id=user.id,
            action="agent.published",
            resource_type="agent",
            resource_id=str(a.id),
        )
    )
    db.commit()
    return {"id": a.id, "status": a.status, "version": a.version}


@app.post("/api/voice/sessions", status_code=201)
def create_voice_session(
    agent_id: int | None = None,
    identity=Depends(current_identity),
    db: Session = Depends(get_db),
):
    _, m = identity
    agent = None
    if agent_id is not None:
        agent = (
            db.query(AIAgent)
            .filter_by(
                id=agent_id, organization_id=m.organization_id, status="published"
            )
            .first()
        )
        if not agent:
            raise HTTPException(404, "Published agent not found")
    room = "vs-" + uuid.uuid4().hex[:16]
    conv = Conversation(
        organization_id=m.organization_id,
        agent_id=agent.id if agent else None,
        room_name=room,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    if (
        settings.voice_mode == "livekit"
        and settings.livekit_url
        and settings.livekit_api_key
        and settings.livekit_api_secret
    ):
        try:
            from livekit import api as lkapi

            token = (
                lkapi.AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
                .with_identity("customer-" + uuid.uuid4().hex[:8])
                .with_grants(
                    lkapi.VideoGrants(
                        room_join=True, room=room, can_publish=True, can_subscribe=True
                    )
                )
                .with_room_config(
                    lkapi.RoomConfiguration(
                        agents=[
                            lkapi.RoomAgentDispatch(agent_name="voicesphere-support")
                        ]
                    )
                )
                .to_jwt()
            )
            return {
                "conversation_id": conv.id,
                "room": room,
                "server_url": settings.livekit_url,
                "token": token,
                "mode": "livekit",
                "warning": "LiveKit transport token only; voice worker/providers must also be configured.",
            }
        except ImportError:
            raise HTTPException(
                503, "Install optional voice dependencies to issue LiveKit tokens"
            )
    return {
        "conversation_id": conv.id,
        "room": room,
        "mode": "mock",
        "warning": "Offline demo only: no microphone transport, transcription, LLM, TTS, or audio recording is active.",
    }


@app.get("/api/audit")
def audit(
    identity=Depends(
        require_roles("platform_admin", "org_admin", "supervisor", "read_only_analyst")
    ),
    db: Session = Depends(get_db),
):
    _, m = identity
    return [
        {
            "id": e.id,
            "action": e.action,
            "resource_type": e.resource_type,
            "resource_id": e.resource_id,
            "created_at": e.created_at.isoformat(),
        }
        for e in db.query(AuditEvent)
        .filter_by(organization_id=m.organization_id)
        .order_by(AuditEvent.id.desc())
        .limit(100)
        .all()
    ]


@app.post("/api/voice/sessions/{conversation_id}/end")
def end_voice_session(
    conversation_id: int,
    identity=Depends(current_identity),
    db: Session = Depends(get_db),
):
    _, membership = identity
    conversation = (
        db.query(Conversation)
        .filter_by(id=conversation_id, organization_id=membership.organization_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversation.status = "ended"
    db.commit()
    return {"id": conversation.id, "status": conversation.status}
