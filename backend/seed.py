from sqlalchemy.orm import Session
from backend import models, database, auth

def seed_db():
    db = database.SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            print("Creating default admin user...")
            hashed_pwd = auth.get_password_hash("admin123")
            admin_user = models.User(
                username="admin",
                password_hash=hashed_pwd,
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created: admin / admin123")
        else:
            print("Admin user already exists.")

        # --- Seed Templates ---
        templates = [
            {
                "name": "采购审批流程 (Purchase Approval)",
                "graph_json": {
                    "nodes": [
                        {"id": "开始节点 (Start)"},
                        {"id": "部门经理审批 (Manager Approval)"},
                        {"id": "财务审核 (Finance Review)"},
                        {"id": "总经理批准 (GM Approval)"},
                        {"id": "结束 (End)"}
                    ]
                }
            },
            {
                "name": "员工请假流程 (Leave Application)",
                "graph_json": {
                    "nodes": [
                        {"id": "提交申请 (Submit)"},
                        {"id": "直属主管审批 (Supervisor Approval)"},
                        {"id": "人事备案 (HR Filing)"},
                        {"id": "结束 (End)"}
                    ]
                }
            },
            {
                "name": "合同签署流程 (Contract Signing)",
                "graph_json": {
                    "nodes": [
                        {"id": "起草合同 (Draft)"},
                        {"id": "法务审核 (Legal Review)"},
                        {"id": "财务确认 (Finance Check)"},
                        {"id": "签署归档 (Sign & Archive)"},
                        {"id": "结束 (End)"}
                    ]
                }
            }
        ]

        for t_data in templates:
            existing = db.query(models.WorkflowTemplate).filter(models.WorkflowTemplate.name == t_data["name"]).first()
            if not existing:
                print(f"Creating template: {t_data['name']}")
                template = models.WorkflowTemplate(
                    name=t_data["name"],
                    graph_json=t_data["graph_json"],
                    version=1
                )
                db.add(template)
            else:
                print(f"Template already exists: {t_data['name']}")
        
        db.commit()

        # --- Seed Instances and Executions (for Dashboard) ---
        # Only seed if no instances exist to avoid duplication on re-run
        # instance_count = db.query(models.WorkflowInstance).count()
        # FORCE SEED: Clear existing instances first to ensure fresh data
        db.query(models.NodeExecution).delete()
        db.query(models.WorkflowInstance).delete()
        db.commit()
        
        print("Seeding sample instances and execution data...")
        import random
        from datetime import timedelta, datetime
        
        # Fetch all templates
        all_templates = db.query(models.WorkflowTemplate).all()
        
        # Create completed instances
        for _ in range(15):
            t = random.choice(all_templates)
            start_time = datetime.now() - timedelta(days=random.randint(1, 10))
            end_time = start_time + timedelta(hours=random.randint(2, 24))
            
            instance = models.WorkflowInstance(
                template_id=t.id,
                current_node_id=None,
                status=models.WorkflowStatus.COMPLETED,
                start_time=start_time,
                end_time=end_time
            )
            db.add(instance)
            db.flush() # get ID
            
            # Add some executions
            nodes = t.graph_json.get("nodes", [])
            for node in nodes:
                actual = random.randint(300, 3600)
                predicted = actual + random.randint(-600, 600)
                if predicted < 0: predicted = 300
                
                execution = models.NodeExecution(
                    instance_id=instance.id,
                    node_id=node["id"],
                    executed_by=admin.id if admin else 1,
                    status=models.NodeStatus.COMPLETED,
                    start_time=start_time,
                    end_time=start_time + timedelta(seconds=actual),
                    predicted_duration=predicted,
                    actual_duration=actual
                )
                db.add(execution)
                start_time += timedelta(seconds=actual + 60) # Next node starts after previous
        
        # Create active instances
        for _ in range(5):
            t = random.choice(all_templates)
            start_time = datetime.now() - timedelta(hours=random.randint(0, 5))
            nodes = t.graph_json.get("nodes", [])
            current_node = nodes[random.randint(0, len(nodes)-2)] # Not the end node
            
            instance = models.WorkflowInstance(
                template_id=t.id,
                current_node_id=current_node["id"],
                status=models.WorkflowStatus.RUNNING,
                start_time=start_time
            )
            db.add(instance)
            db.flush()
            
            # Add active execution
            pred = random.randint(600, 3000)
            execution = models.NodeExecution(
                instance_id=instance.id,
                node_id=current_node["id"],
                executed_by=admin.id if admin else 1,
                status=models.NodeStatus.RUNNING,
                start_time=datetime.now() - timedelta(minutes=random.randint(5, 30)),
                predicted_duration=pred
            )
            db.add(execution)
        db.commit()
        print("Sample instance data seeded.")
            
    except Exception as e:
        print(f"Error seeding DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
