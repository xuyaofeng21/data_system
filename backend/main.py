from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from . import models, schemas, database, auth, prediction

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Business Process Data Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper: Log Action ---
def log_action(db: Session, user_id: int, action: str, details: str = None):
    log = models.SystemLog(user_id=user_id, action=action, details=details)
    db.add(log)
    db.commit()

# --- Auth ---
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    
    # Log Login
    log_action(db, user.id, "LOGIN", "User logged in successfully")
    
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, password_hash=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    log_action(db, new_user.id, "REGISTER", f"New user registered: {user.username}")
    
    return new_user

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.get("/users", response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can list users")
    return db.query(models.User).all()

@app.delete("/users/{id}")
def delete_user(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
    db.delete(user)
    db.commit()
    
    log_action(db, current_user.id, "DELETE_USER", f"Deleted user: {user.username}")
    
    return {"status": "success"}

# --- Process Templates ---
@app.post("/templates", response_model=schemas.TemplateResponse)
def create_template(template: schemas.TemplateCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create templates")
    new_template = models.WorkflowTemplate(name=template.name, graph_json=template.graph_json)
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    
    log_action(db, current_user.id, "CREATE_TEMPLATE", f"Created template: {template.name}")
    
    return new_template

@app.get("/templates", response_model=list[schemas.TemplateResponse])
def get_templates(db: Session = Depends(database.get_db)):
    return db.query(models.WorkflowTemplate).filter(models.WorkflowTemplate.is_deleted == 0).all()

@app.put("/templates/{id}", response_model=schemas.TemplateResponse)
def update_template(id: int, template: schemas.TemplateCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update templates")
    
    db_template = db.query(models.WorkflowTemplate).filter(models.WorkflowTemplate.id == id, models.WorkflowTemplate.is_deleted == 0).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Version control: Increment version
    db_template.version += 1
    db_template.name = template.name
    db_template.graph_json = template.graph_json
    
    db.commit()
    db.refresh(db_template)
    
    log_action(db, current_user.id, "UPDATE_TEMPLATE", f"Updated template: {template.name} to v{db_template.version}")
    
    return db_template

@app.delete("/templates/{id}")
def delete_template(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete templates")
        
    db_template = db.query(models.WorkflowTemplate).filter(models.WorkflowTemplate.id == id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Soft Delete Implementation
    db_template.is_deleted = 1
    db.commit()
    
    log_action(db, current_user.id, "DELETE_TEMPLATE", f"Soft deleted template id: {id}")
    
    return {"status": "success"}

# --- Process Instances ---
@app.post("/instances", response_model=schemas.InstanceResponse)
def start_instance(instance_in: schemas.InstanceCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    template = db.query(models.WorkflowTemplate).filter(models.WorkflowTemplate.id == instance_in.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Logic to start first node
    nodes = template.graph_json.get("nodes", [])
    if not nodes:
        raise HTTPException(status_code=400, detail="Invalid template: no nodes")
    
    start_node = nodes[0] # Simplification: Assume linear or ordered list for now
    
    new_instance = models.WorkflowInstance(
        template_id=template.id,
        current_node_id=start_node["id"],
        status=models.WorkflowStatus.RUNNING
    )
    db.add(new_instance)
    db.commit()
    db.refresh(new_instance)

    # Predict duration
    pred = prediction.predictor.predict(start_node["id"], current_user.id, datetime.now())

    # Create first execution record
    execution = models.NodeExecution(
        instance_id=new_instance.id,
        node_id=start_node["id"],
        executed_by=current_user.id,
        status=models.NodeStatus.RUNNING,
        start_time=datetime.now(),
        predicted_duration=pred
    )
    db.add(execution)
    db.commit()
    
    log_action(db, current_user.id, "START_INSTANCE", f"Started instance {new_instance.id} from template {template.name}")

    return new_instance

@app.get("/instances", response_model=list[schemas.InstanceResponse])
def get_instances(db: Session = Depends(database.get_db)):
    return db.query(models.WorkflowInstance).all()

@app.post("/instances/{id}/complete_node")
def complete_node(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    instance = db.query(models.WorkflowInstance).filter(models.WorkflowInstance.id == id).first()
    if not instance or instance.status != models.WorkflowStatus.RUNNING:
        raise HTTPException(status_code=404, detail="Instance not found or not running")

    # Find current execution
    execution = db.query(models.NodeExecution).filter(
        models.NodeExecution.instance_id == id,
        models.NodeExecution.status == models.NodeStatus.RUNNING
    ).first()

    if execution:
        execution.end_time = datetime.now()
        execution.status = models.NodeStatus.COMPLETED
        # Calculate actual duration
        duration = (execution.end_time - execution.start_time).total_seconds()
        execution.actual_duration = int(duration)
        db.commit()

        # Retrain model periodically (simplification: just call train)
        # In production this would be async
        try:
            prediction.predictor.train(db)
        except:
            pass

    # Move to next node
    # Find next node in template
    template = instance.template
    nodes = template.graph_json.get("nodes", [])
    current_node_index = -1
    for i, node in enumerate(nodes):
        if node["id"] == instance.current_node_id:
            current_node_index = i
            break
    
    if current_node_index != -1 and current_node_index < len(nodes) - 1:
        next_node = nodes[current_node_index + 1]
        instance.current_node_id = next_node["id"]
        
        # Create new execution for next node
        pred = prediction.predictor.predict(next_node["id"], current_user.id, datetime.now())
        new_exec = models.NodeExecution(
            instance_id=instance.id,
            node_id=next_node["id"],
            executed_by=current_user.id, # Simplification: Auto-assigned to current user or need assignment logic
            status=models.NodeStatus.RUNNING,
            start_time=datetime.now(),
            predicted_duration=pred
        )
        db.add(new_exec)
    else:
        # Finish process
        instance.status = models.WorkflowStatus.COMPLETED
        instance.end_time = datetime.now()
        instance.current_node_id = None

    db.commit()
    log_action(db, current_user.id, "COMPLETE_TASK", f"Completed node in instance {id}")
    return {"status": "success"}

@app.get("/dashboard/stats")
def get_stats(db: Session = Depends(database.get_db)):
    total_instances = db.query(models.WorkflowInstance).count()
    active_instances = db.query(models.WorkflowInstance).filter(models.WorkflowInstance.status == models.WorkflowStatus.RUNNING).count()
    
    # Prediction accuracy stats
    executions = db.query(models.NodeExecution).filter(models.NodeExecution.actual_duration != None).all()
    accuracy_data = []
    for ex in executions:
        accuracy_data.append({
            "id": ex.id,
            "actual": ex.actual_duration,
            "predicted": ex.predicted_duration
        })

    return {
        "total_instances": total_instances,
        "active_instances": active_instances,
        "accuracy_data": accuracy_data
    }

@app.get("/analytics/benchmarks")
def get_benchmarks(db: Session = Depends(database.get_db)):
    # Ensure model is trained (lazy training if needed, though usually done on completion)
    if not prediction.predictor.is_trained:
        prediction.predictor.train(db)
        
    return prediction.predictor.get_metrics()

# --- System Logs API ---
@app.get("/logs")
def get_system_logs(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Only admin should see all logs, but for simplicity/demo allow all or restrict
    # if current_user.role != "admin": ...
    logs = db.query(models.SystemLog).order_by(models.SystemLog.created_at.desc()).limit(100).all()
    return [{
        "id": l.id,
        "user": l.user.username if l.user else "System",
        "action": l.action,
        "details": l.details,
        "created_at": l.created_at
    } for l in logs]
