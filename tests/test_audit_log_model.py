"""Tests for AuditLog model."""
import pytest
from datetime import datetime
from models.user import User
from models.audit_log import AuditLog
from app.extensions import db


class TestAuditLogModel:
    """Test suite for AuditLog model."""
    
    def test_audit_log_creation(self, app):
        """Test creating an audit log entry with required fields."""
        with app.app_context():
            # Create a user first
            user = User(
                email='audit@example.com',
                password_hash='hashed_password'
            )
            db.session.add(user)
            db.session.commit()
            
            # Create audit log entry
            log = AuditLog(
                user_id=user.id,
                action='login',
                resource_type='user',
                resource_id=user.id,
                ip_address='192.168.1.1',
                user_agent='Mozilla/5.0'
            )
            db.session.add(log)
            db.session.commit()
            
            assert log.id is not None
            assert log.user_id == user.id
            assert log.action == 'login'
            assert log.resource_type == 'user'
            assert log.resource_id == user.id
            assert str(log.ip_address) == '192.168.1.1'
            assert log.user_agent == 'Mozilla/5.0'
            assert log.created_at is not None
    
    def test_audit_log_without_user(self, app):
        """Test creating an audit log without a user (unauthenticated action)."""
        with app.app_context():
            log = AuditLog(
                action='failed_login',
                resource_type='user',
                ip_address='10.0.0.1',
                user_agent='curl/7.68.0'
            )
            db.session.add(log)
            db.session.commit()
            
            assert log.id is not None
            assert log.user_id is None
            assert log.action == 'failed_login'
    
    def test_audit_log_without_resource_id(self, app):
        """Test creating an audit log without a resource ID."""
        with app.app_context():
            user = User(
                email='noresource@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            log = AuditLog(
                user_id=user.id,
                action='view_dashboard',
                resource_type='dashboard',
                ip_address='172.16.0.1'
            )
            db.session.add(log)
            db.session.commit()
            
            assert log.resource_id is None
    
    def test_audit_log_different_actions(self, app):
        """Test different audit log actions."""
        with app.app_context():
            user = User(
                email='actions@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            actions = [
                'login',
                'logout',
                'upload_resume',
                'delete_resume',
                'create_analysis',
                'view_analysis',
                'export_pdf',
                'update_profile'
            ]
            
            for action in actions:
                log = AuditLog(
                    user_id=user.id,
                    action=action,
                    resource_type='user',
                    ip_address='192.168.1.1'
                )
                db.session.add(log)
            
            db.session.commit()
            
            # Verify all actions were logged
            for action in actions:
                found = AuditLog.query.filter_by(action=action).first()
                assert found is not None
                assert found.action == action
    
    def test_audit_log_different_resource_types(self, app):
        """Test different resource types."""
        with app.app_context():
            user = User(
                email='resources@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            resource_types = ['user', 'resume', 'analysis', 'api_key', 'contact_submission']
            
            for resource_type in resource_types:
                log = AuditLog(
                    user_id=user.id,
                    action='create',
                    resource_type=resource_type,
                    ip_address='192.168.1.1'
                )
                db.session.add(log)
            
            db.session.commit()
            
            # Verify all resource types were logged
            for resource_type in resource_types:
                found = AuditLog.query.filter_by(resource_type=resource_type).first()
                assert found is not None
                assert found.resource_type == resource_type
    
    def test_audit_log_user_relationship(self, app):
        """Test relationship between AuditLog and User."""
        with app.app_context():
            user = User(
                email='relationship@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            log = AuditLog(
                user_id=user.id,
                action='login',
                resource_type='user',
                ip_address='192.168.1.1'
            )
            db.session.add(log)
            db.session.commit()
            
            # Test forward relationship
            assert log.user.email == 'relationship@example.com'
            
            # Test backward relationship
            assert user.audit_logs.count() == 1
            assert user.audit_logs.first().action == 'login'
    
    def test_audit_log_user_deletion_set_null(self, app):
        """Test that user_id is set to NULL when user is deleted."""
        with app.app_context():
            user = User(
                email='setnull@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            log = AuditLog(
                user_id=user.id,
                action='login',
                resource_type='user',
                ip_address='192.168.1.1'
            )
            db.session.add(log)
            db.session.commit()
            
            log_id = log.id
            
            # Delete user
            db.session.delete(user)
            db.session.commit()
            
            # Verify log still exists but user_id is NULL
            remaining_log = AuditLog.query.get(log_id)
            assert remaining_log is not None
            assert remaining_log.user_id is None
            assert remaining_log.action == 'login'
    
    def test_audit_log_multiple_per_user(self, app):
        """Test that a user can have multiple audit log entries."""
        with app.app_context():
            user = User(
                email='multiple@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            logs = []
            for i in range(5):
                log = AuditLog(
                    user_id=user.id,
                    action=f'action_{i}',
                    resource_type='user',
                    ip_address='192.168.1.1'
                )
                logs.append(log)
            
            db.session.add_all(logs)
            db.session.commit()
            
            assert user.audit_logs.count() == 5
    
    def test_audit_log_ipv6_address(self, app):
        """Test storing IPv6 address."""
        with app.app_context():
            user = User(
                email='ipv6@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            log = AuditLog(
                user_id=user.id,
                action='login',
                resource_type='user',
                ip_address='2001:0db8:85a3:0000:0000:8a2e:0370:7334'
            )
            db.session.add(log)
            db.session.commit()
            
            assert log.ip_address is not None
            assert '2001:db8:85a3::8a2e:370:7334' in str(log.ip_address)  # PostgreSQL normalizes IPv6
    
    def test_audit_log_to_dict(self, app):
        """Test converting audit log to dictionary."""
        with app.app_context():
            user = User(
                email='dict@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            log = AuditLog(
                user_id=user.id,
                action='upload_resume',
                resource_type='resume',
                resource_id=123,
                ip_address='192.168.1.100',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            )
            db.session.add(log)
            db.session.commit()
            
            log_dict = log.to_dict()
            
            assert log_dict['id'] == log.id
            assert log_dict['user_id'] == user.id
            assert log_dict['action'] == 'upload_resume'
            assert log_dict['resource_type'] == 'resume'
            assert log_dict['resource_id'] == 123
            assert log_dict['ip_address'] == '192.168.1.100'
            assert log_dict['user_agent'] == 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            assert 'created_at' in log_dict
    
    def test_audit_log_repr(self, app):
        """Test string representation of audit log."""
        with app.app_context():
            user = User(
                email='repr@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            log = AuditLog(
                user_id=user.id,
                action='delete_resume',
                resource_type='resume',
                ip_address='192.168.1.1'
            )
            db.session.add(log)
            db.session.commit()
            
            expected = f'<AuditLog delete_resume by user {user.id} at {log.created_at}>'
            assert repr(log) == expected
    
    def test_audit_log_timestamps(self, app):
        """Test that timestamps are set correctly."""
        with app.app_context():
            log = AuditLog(
                action='system_event',
                resource_type='system',
                ip_address='127.0.0.1'
            )
            db.session.add(log)
            db.session.commit()
            
            assert isinstance(log.created_at, datetime)
    
    def test_audit_log_query_by_action(self, app):
        """Test querying logs by action."""
        with app.app_context():
            user = User(
                email='query@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            login_log = AuditLog(
                user_id=user.id,
                action='login',
                resource_type='user',
                ip_address='192.168.1.1'
            )
            logout_log = AuditLog(
                user_id=user.id,
                action='logout',
                resource_type='user',
                ip_address='192.168.1.1'
            )
            db.session.add_all([login_log, logout_log])
            db.session.commit()
            
            # Query login actions
            login_logs = AuditLog.query.filter_by(action='login').all()
            assert len(login_logs) == 1
            assert login_logs[0].action == 'login'
    
    def test_audit_log_query_by_user(self, app):
        """Test querying logs by user."""
        with app.app_context():
            user1 = User(email='user1@example.com', password_hash='hash')
            user2 = User(email='user2@example.com', password_hash='hash')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            log1 = AuditLog(
                user_id=user1.id,
                action='login',
                resource_type='user',
                ip_address='192.168.1.1'
            )
            log2 = AuditLog(
                user_id=user1.id,
                action='logout',
                resource_type='user',
                ip_address='192.168.1.1'
            )
            log3 = AuditLog(
                user_id=user2.id,
                action='login',
                resource_type='user',
                ip_address='192.168.1.2'
            )
            db.session.add_all([log1, log2, log3])
            db.session.commit()
            
            # Query logs for user1
            user1_logs = AuditLog.query.filter_by(user_id=user1.id).all()
            assert len(user1_logs) == 2
            
            # Query logs for user2
            user2_logs = AuditLog.query.filter_by(user_id=user2.id).all()
            assert len(user2_logs) == 1
    
    def test_audit_log_long_user_agent(self, app):
        """Test storing a long user agent string."""
        with app.app_context():
            long_user_agent = 'A' * 1000  # 1000 character user agent
            
            log = AuditLog(
                action='api_request',
                resource_type='api',
                ip_address='192.168.1.1',
                user_agent=long_user_agent
            )
            db.session.add(log)
            db.session.commit()
            
            assert len(log.user_agent) == 1000
            assert log.user_agent == long_user_agent
