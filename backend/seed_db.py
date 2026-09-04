import asyncio
import csv
import os
from datetime import datetime, timezone

from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.models.agent import Agent
from app.models.complaint import Complaint
from app.models.team import Team
from app.models.ticket import Ticket
from app.models.user import User

async def seed():
    print("Connecting to database and initializing schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if users already seeded
        from sqlalchemy import select
        res = await session.execute(select(User))
        if res.scalars().first():
            print("Database already seeded with users!")
            return

        print("Seeding Users...")
        admin = User(
            name="System Admin",
            email="admin@demo.com",
            password_hash=get_password_hash("123456"),
            role="admin",
        )
        user = User(
            name="Citizen Demo",
            email="user@demo.com",
            password_hash=get_password_hash("123456"),
            role="user",
        )
        session.add_all([admin, user])
        await session.flush()

        print("Seeding Teams...")
        team_names = [
            ("Technical Support", "Handles bugs, crashes, server issues"),
            ("Billing Support", "Handles payment, invoice, refund queries"),
            ("Delivery Support", "Handles delayed packages and shipping"),
            ("Service Support", "Handles staff and overall service quality"),
            ("Account Support", "Handles login, credentials, security"),
            ("General Support", "Handles miscellaneous inquiries"),
        ]
        teams_map = {}
        for name, desc in team_names:
            t = Team(name=name, description=desc)
            session.add(t)
            await session.flush()
            teams_map[name] = t.id

        print("Seeding Agents...")
        agents_data = [
            ("Alex Chen", "alex@support.demo", "Technical Support", "Python, AWS, BugTriaging", "Available", 2),
            ("Sarah Jenkins", "sarah@support.demo", "Billing Support", "Invoicing, Refunds, Stripe", "Available", 1),
            ("Marcus Brody", "marcus@support.demo", "Delivery Support", "Logistics, Tracking, Courier", "Available", 3),
            ("Elena Rostova", "elena@support.demo", "Service Support", "Customer Experience, Escalation", "Available", 2),
            ("Devon Vance", "devon@support.demo", "Account Support", "OAuth, Passwords, Security", "Available", 1),
        ]
        agents_map = {}
        for name, email, team_name, skills, avail, workload in agents_data:
            tid = teams_map.get(team_name)
            a = Agent(name=name, email=email, team_id=tid, skills=skills, availability=avail, current_workload=workload)
            session.add(a)
            await session.flush()
            agents_map[team_name] = a.id

        print("Seeding Complaints & Tickets from CSV...")
        csv_path = "C:/Users/TempAdmin/Complaint-Management-System/frontend/complaints.csv"
        statuses = ["Registered", "Assigned", "In Progress", "Resolved"]
        
        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            idx = 0
            for row in reader:
                cid = row.get("complaint_id") or f"CMP-{10001+idx}"
                text = row.get("complaint_text", "Complaint logged.")
                cat = row.get("category", "Other")
                prio = row.get("priority", "Medium")
                comp = row.get("complexity", "Medium")
                rec_team = row.get("recommended_team", f"{cat} Support" if f"{cat} Support" in teams_map else "General Support")
                
                # Assign status deterministically based on index for rich variety in admin dashboard
                status = statuses[idx % len(statuses)]
                
                c = Complaint(
                    complaint_id=cid,
                    complaint_text=text,
                    category=cat,
                    priority=prio,
                    complexity=comp,
                    recommended_team=rec_team,
                    user_id=user.id,
                )
                session.add(c)
                await session.flush()

                t_team_id = teams_map.get(rec_team, teams_map.get("General Support"))
                t_agent_id = agents_map.get(rec_team, None)

                t = Ticket(
                    ticket_number=f"TKT-{cid.split('-')[1] if '-' in cid else idx+1}",
                    complaint_id=cid,
                    category=cat,
                    priority=prio,
                    status=status,
                    assigned_team_id=t_team_id,
                    assigned_agent_id=t_agent_id,
                    resolution_information="Auto-resolved according to SLA protocols." if status == "Resolved" else None,
                    resolved_at=datetime.now(timezone.utc) if status == "Resolved" else None,
                )
                session.add(t)
                idx += 1
                if idx % 100 == 0:
                    await session.commit()
                    print(f"Seeded {idx} complaints...")

        await session.commit()
        print(f"Successfully seeded database with {idx} complaints, teams, agents, and demo users!")

if __name__ == "__main__":
    asyncio.run(seed())
