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
            
    except Exception as e:
        print(f"Error seeding DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
