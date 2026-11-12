from .db import Base, engine, SessionLocal
from .models import Organization, User, Membership, Customer, Order, AIAgent
from .security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    if not db.query(Organization).filter_by(name="Northstar Retail").first():
        org = Organization(name="Northstar Retail")
        db.add(org)
        db.flush()
        user = User(
            email="admin@northstar.test",
            full_name="Northstar Demo Admin",
            password_hash=hash_password("DemoPassword123!"),
        )
        db.add(user)
        db.flush()
        db.add(Membership(organization_id=org.id, user_id=user.id, role="org_admin"))
        c1 = Customer(
            organization_id=org.id,
            name="Jordan Lee",
            email="jordan.lee@example.test",
            phone="+1-555-0101",
            verification_last4="4821",
        )
        c2 = Customer(
            organization_id=org.id,
            name="Avery Morgan",
            email="avery.morgan@example.test",
            phone="+1-555-0102",
            verification_last4="1937",
        )
        db.add_all([c1, c2])
        db.flush()
        db.add_all(
            [
                Order(
                    organization_id=org.id,
                    customer_id=c1.id,
                    order_number="NS-10482",
                    item="Northstar Pro 14 Laptop",
                    status="in_transit",
                    estimated_delivery="Nov 8",
                ),
                Order(
                    organization_id=org.id,
                    customer_id=c2.id,
                    order_number="NS-10519",
                    item="Wireless Noise-Canceling Headphones",
                    status="processing",
                    estimated_delivery="Nov 11",
                ),
            ]
        )
        db.add(
            AIAgent(
                organization_id=org.id,
                name="Northstar Support",
                description="Retail order and product support",
                instructions="Be helpful. Verify identity before discussing order details. Use knowledge evidence and escalate uncertainty.",
                status="published",
            )
        )
        db.commit()
        print("Seeded Northstar demo tenant.")
    else:
        print("Seed data already exists; no changes made.")
finally:
    db.close()
