from fastapi import FastAPI, Request, Form, UploadFile, File
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
from app.ai import decompose_requirements, find_related_requirements
from app.trello_client import TrelloClient
from app.models import init_db, SessionLocal, Requirement, RequirementGroup

app = FastAPI()
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()
trello = TrelloClient()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit")
async def submit(request: Request, subject: str = Form(...), project_name: str = Form(...), body: str = Form(...), files: list[UploadFile] = File(None)):
    try:
        saved_files = []
        if files:
            for f in files:
                if f.filename == "":
                    continue
                path = os.path.join(UPLOAD_DIR, f.filename)
                with open(path, "wb") as out:
                    content = await f.read()
                    out.write(content)
                saved_files.append(path)

        requirements = decompose_requirements(subject, body)

        db = SessionLocal()
        for req in requirements:
            group_name = req.get("group") or "General"
            group = db.query(RequirementGroup).filter(RequirementGroup.name == group_name, RequirementGroup.project_name == project_name).first()
            if not group:
                group = RequirementGroup(name=group_name, project_name=project_name or None)
                db.add(group)
                db.commit()
                db.refresh(group)
            r = Requirement(title=req.get("title"), description=req.get("description"), group_id=group.id)
            db.add(r)
            db.commit()
            db.refresh(r)
            
            # Find related requirements (previous changes to same feature)
            related = find_related_requirements(db, group_name, project_name, exclude_requirement_id=r.id)
            
            # Build card description with related requirements
            card_desc = f"{r.description}\n\n"
            if related:
                card_desc += f"**Related Requirements ({len(related)}):**\n"
                for rel in related:
                    if rel.trello_card_url:
                        # Add clickable link to the related Trello card
                        card_desc += f"- [{rel.title}]({rel.trello_card_url})\n"
                    else:
                        card_desc += f"- {rel.title}\n"
            else:
                card_desc += "(No previous requirements for this feature)"
            
            # Create Trello card with enhanced description and project name label
            try:
                card = trello.create_card(r.title, card_desc, label_name=project_name if project_name else None)
                card_id = card.get("id") if isinstance(card, dict) else None
                card_url = card.get("url") if isinstance(card, dict) else None
            except Exception as e:
                print(f"Error creating Trello card: {e}")
                card_id = None
                card_url = None
            
            # Store Trello card ID and URL for future linking
            r.trello_card_id = card_id
            r.trello_card_url = card_url
            db.commit()
            
            for path in saved_files:
                try:
                    trello.attach_file(card_id=card_id, file_path=path)
                except Exception as e:
                    print(f"Error attaching file to Trello card: {e}")

        db.close()
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        print(f"Error in submit endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise


@app.get("/requirements/{group_name}", response_class=HTMLResponse)
def view_related_requirements(request: Request, group_name: str):
    """View all requirements for a given feature group."""
    db = SessionLocal()
    group = db.query(RequirementGroup).filter(RequirementGroup.name == group_name).first()
    
    if not group:
        return HTMLResponse("<p>Group not found</p>", status_code=404)
    
    requirements = db.query(Requirement).filter(Requirement.group_id == group.id).all()
    db.close()
    
    return templates.TemplateResponse(
        "requirements.html",
        {
            "request": request,
            "group_name": group_name,
            "requirements": requirements
        }
    )
