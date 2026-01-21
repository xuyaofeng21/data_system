from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"

class WorkflowStatus(str, enum.Enum):
    RUNNING = "Running"
    COMPLETED = "Completed"
    TERMINATED = "Terminated"

class NodeStatus(str, enum.Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(20), default=UserRole.OPERATOR)

    executions = relationship("NodeExecution", back_populates="executor")
    logs = relationship("SystemLog", back_populates="user")

class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    graph_json = Column(JSON) # Stores nodes and edges definition
    version = Column(Integer, default=1)
    is_deleted = Column(Integer, default=0) # 0: Active, 1: Deleted
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    instances = relationship("WorkflowInstance", back_populates="template")

class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"))
    current_node_id = Column(String(50), nullable=True)
    status = Column(String(20), default=WorkflowStatus.RUNNING)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)

    template = relationship("WorkflowTemplate", back_populates="instances")
    executions = relationship("NodeExecution", back_populates="instance")

class NodeExecution(Base):
    __tablename__ = "node_executions"

    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(Integer, ForeignKey("workflow_instances.id"))
    node_id = Column(String(50)) # Corresponds to ID in graph_json
    executed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(String(20), default=NodeStatus.PENDING)
    
    predicted_duration = Column(Integer, nullable=True) # In seconds
    actual_duration = Column(Integer, nullable=True)    # In seconds

    instance = relationship("WorkflowInstance", back_populates="executions")
    executor = relationship("User", back_populates="executions")

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100)) # e.g., "LOGIN", "CREATE_TEMPLATE"
    details = Column(Text, nullable=True) # JSON or text details
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="logs")
